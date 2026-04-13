import json
import re
import uuid
from typing import Annotated, List, TypedDict

from jinja2 import Template
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from phoenix.otel import register

from .config import BOT_USERNAME, MODEL_NAME
from .db import get_chat_history, save_message
from .google_api import place_recommender
from .prompts import SYSTEM_PROMPT

register(project_name="tg-ai-bot", auto_instrument=True)


def get_json(input_str) -> dict:
    """Extract json from GPT response"""
    json_pattern = re.compile(r'\{.*?\}', re.DOTALL)
    json_matches = json_pattern.findall(input_str)
    res = None
    if len(json_matches) > 0:
        res = json.loads(json_matches[0])
    return res


def prepare_html(input_json_array: dict, user: dict) -> str:
    """
    Input example
        {'name': 'Electus Bar', 'link': 'https://www.google.com/maps?q=34.6976422%2C33.0940658'}
    """
    template_str = """
    <i>Hey @{{ user['user_name'] }}! Great beer pub near you:</i> <a href="{{ place['link'] }}">{{ place['name'] }}</a>
    """
    template = Template(template_str)
    html_content = template.render(place=input_json_array, user=user)

    return html_content


model = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0.1)

class State(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    answer: str


def chat_node(state: State):
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = model.invoke(messages)
    content = response.content

    json_response = get_json(content)
    if json_response:
        location_option = f"{json_response['country']}, {json_response['city']}"
        lat_lng = place_recommender.find_place(location_option)
        if lat_lng is None:
            return {
                "messages": [AIMessage(content=content)],
                "answer": "Sorry, I couldn't locate that city. Could you double-check the country and city name?"
            }
        q = "craft beer bar" if json_response.get('craft_option') else "beer pub"
        recommended_place = place_recommender.get_recs(lat_lng, q=q)

        return {
            "messages": [AIMessage(content=content)],
            "answer": recommended_place  # caller will format HTML with user context
        }
    else:
        return {
            "messages": [AIMessage(content=content)],
            "answer": content
        }

builder = StateGraph(State)
builder.add_node("chat", chat_node)
builder.add_edge(START, "chat")
builder.add_edge("chat", END)

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
    past_messages = [
        HumanMessage(content=row["message_text"]) if row["role"] == "user"
        else AIMessage(content=row["message_text"])
        for row in history
    ]

    # Save incoming user message (raw_input overrides what gets stored, human_input goes to LLM)
    username = user.get('user_name')
    await save_message(chat_id, username, "user", raw_input if raw_input is not None else human_input, channel=channel)

    result = graph.invoke({"messages": past_messages + [HumanMessage(content=human_input)]})

    ai_text = result["answer"]
    is_html = isinstance(ai_text, dict)

    if is_html:
        ai_text = prepare_html(ai_text, user)

    await save_message(chat_id, BOT_USERNAME, "assistant", ai_text if isinstance(ai_text, str) else str(ai_text), channel=channel)

    return {"is_html": is_html, "answer": ai_text}
