import os
import uuid
from typing import Annotated, List, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from phoenix.otel import register

from .config import BOT_USERNAME, MODEL_NAME
from .db import get_chat_history, save_message
from .prompts import SYSTEM_PROMPT
from .tools import find_venue, geocode_city

_phoenix_endpoint = os.environ.get('PHOENIX_COLLECTOR_ENDPOINT', 'http://localhost:6006')
register(project_name="tg-ai-bot", endpoint=f"{_phoenix_endpoint}/v1/traces", auto_instrument=True)

tools = [geocode_city, find_venue]
model = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0.1, google_api_key=os.environ['GEMINI_API_KEY'])
model_with_tools = model.bind_tools(tools)


class State(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]


def agent_node(state: State):
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}


tool_node = ToolNode(tools)

builder = StateGraph(State)
builder.add_node("agent", agent_node)
builder.add_node("tools", tool_node)
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")

# No checkpointer — history is managed via SQLite
graph = builder.compile()


async def dialog_router(
    human_input: str,
    user: dict,
    raw_input: str | None = None,
    chat_id: str | None = None,
    channel: str | None = None,
):
    if chat_id is None:
        chat_id = str(user.get('user_name', uuid.uuid4()))

    # Load history from SQLite and reconstruct message objects
    history = await get_chat_history(chat_id)
    username = user.get('user_name')
    if channel is not None:
        # Group chat: prefix human messages with @username so LLM can attribute preferences per participant
        past_messages = [
            HumanMessage(content=f"@{row['username']}: {row['message_text']}") if row["role"] == "user"
            else AIMessage(content=row["message_text"])
            for row in history
        ]
        current_message = HumanMessage(content=f"@{username}: {human_input}")
    else:
        past_messages = [
            HumanMessage(content=row["message_text"]) if row["role"] == "user"
            else AIMessage(content=row["message_text"])
            for row in history
        ]
        current_message = HumanMessage(content=human_input)

    # Save incoming user message (raw_input overrides what gets stored, human_input goes to LLM)
    await save_message(chat_id, username, "user", raw_input if raw_input is not None else human_input, channel=channel)

    result = graph.invoke({"messages": past_messages + [current_message]})

    ai_text = result["messages"][-1].content
    is_html = "<a href" in ai_text

    await save_message(chat_id, BOT_USERNAME, "assistant", ai_text, channel=channel)

    return {"is_html": is_html, "answer": ai_text}
