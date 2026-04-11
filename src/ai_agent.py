import json
import re
import uuid
from dataclasses import dataclass
from typing import Annotated, List, TypedDict

from jinja2 import Template
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.runtime import Runtime
from langgraph.store.memory import InMemoryStore
from phoenix.otel import register

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


model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)

class State(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    final_answer: bool
    answer: str

@dataclass
class Context:
    user_id: str
    user: dict

# Initialize store and checkpointer
store = InMemoryStore()
checkpointer = MemorySaver()

def chat_node(state: State, runtime: Runtime[Context]):
    user_id = runtime.context.user_id
    user = runtime.context.user

    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = model.invoke(messages)
    content = response.content

    json_response = get_json(content)
    if json_response:
        # Save to memory store
        namespace = (user_id, "preferences")
        memory_id = str(uuid.uuid4())
        runtime.store.put(namespace, memory_id, json_response)

        # Generate recommendation
        location_option = f"{json_response['country']}, {json_response['city']}"
        lat_lng = place_recommender.find_place(location_option)
        if lat_lng is None:
            return {
                "messages": [AIMessage(content=content)],
                "final_answer": False,
                "answer": "Sorry, I couldn't locate that city. Could you double-check the country and city name?"
            }
        q = "craft beer bar" if json_response.get('craft_option') else "beer pub"
        recommended_place = place_recommender.get_recs(lat_lng, q=q)
        html_answer = prepare_html(recommended_place, user)

        return {
            "messages": [AIMessage(content=content)],
            "final_answer": True,
            "answer": html_answer
        }
    else:
        return {
            "messages": [AIMessage(content=content)],
            "final_answer": False,
            "answer": content
        }

builder = StateGraph(State, context_schema=Context)
builder.add_node("chat", chat_node)
builder.add_edge(START, "chat")
builder.add_edge("chat", END)

graph = builder.compile(store=store, checkpointer=checkpointer)

def dialog_router(human_input: str, user: dict):
    user_id = user.get('user_name', str(uuid.uuid4()))

    config = {"configurable": {"thread_id": user_id}}
    context = Context(user_id=user_id, user=user)

    result = graph.invoke(
        {"messages": [HumanMessage(content=human_input)]},
        config=config,
        context=context
    )
    return {
        "final_answer": result["final_answer"],
        "answer": result["answer"]
    }
