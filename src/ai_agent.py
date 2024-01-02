import os
import json
import re

from jinja2 import Template
from bs4 import BeautifulSoup
import openai
from langchain.chat_models import ChatOpenAI

from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate

from google_api import place_recommender


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


openai.api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)
prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        """
        You are an conversational chatbot.
        You must be direct, efficient, impersonal, and professional in all of your communications.
        You should ask human step by step questions from section "questions"
        You can change the order of questions if you want.
        Use only information from human messages, do not imagine answers
        When the dialog begins do not ask questions like "How can I assist you today?", ask only questions below

        questions:
        - ask the country name the user live in. If you don't know this country, gently ask again. It is country field in result JSON 
        - ask the city name the user live in. It is city field in result JSON 
        - ask does human prefer craft beer (yes or no) it is craft field in result JSON
        
        Only ask questions right before this line, but in other words, not literally

        When you have enough information from chat history, prepare final response.
        Final response should only consist of document in JSON format with the following fields: [city, country, craft_option]
        Do not add any extra words in JSON. Do not come up with prepared plan.

        For example: "city": "Moscow", "country": "Russia", "craft_option": false
        """
    ),
    MessagesPlaceholder(variable_name="history"),
    HumanMessagePromptTemplate.from_template("{input}")
])
memory = ConversationBufferMemory(return_messages=True)
chat = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True,
    prompt=prompt,
)

def dialog_router(human_input: str, user: dict):
    llm_answer = chat.predict(input=human_input)
    json_response = get_json(llm_answer)
    if json_response is not None:
        location_option = "%s, %s" % (json_response['country'], json_response['city'])
        lat_lng = place_recommender.find_place(location_option)
        recommended_place = place_recommender.get_recs(lat_lng)
        html_answer = prepare_html(recommended_place, user)
        return {'final_answer': True, 'answer': html_answer}
    else:
        return {'final answer': False, 'answer': llm_answer}

if __name__=='__main__':
    human_input = input("Start the dialog with AI bot: ")
    for k in range(10):
        answer = dialog_router(human_input=human_input, user={'name': 'Average Human'})
        if isinstance(answer, dict):
            soup = BeautifulSoup(answer['final_answer'])
            print(soup.get_text())
            break
        else:
            print(answer)
            human_input = input("Enter your response: ")
            print('\n..............\n')
    if k == 6:
        print("Conversation length overflow")
