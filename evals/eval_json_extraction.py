"""
Eval: verify that the model extracts structured JSON from a known user phrase.
"""
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from src.ai_agent import get_json
from src.prompts import SYSTEM_PROMPT

PHRASE = "Country: Serbia, City: Belgrade, love craft beer: yes"

EXPECTED = {
    "city": "Belgrade",
    "country": "Serbia",
    "craft_option": True,
}

def run():
    model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=PHRASE)]
    response = model.invoke(messages)

    print(f"Model output: {response.content}")

    result = get_json(response.content)
    print(f"Parsed JSON:  {result}")

    passed = (
        result is not None
        and result.get("city") == EXPECTED["city"]
        and result.get("country") == EXPECTED["country"]
        and result.get("craft_option") == EXPECTED["craft_option"]
    )

    print(f"Expected:     {EXPECTED}")
    print(f"Result: {'PASS' if passed else 'FAIL'}")
    return passed


if __name__ == "__main__":
    import sys
    sys.exit(0 if run() else 1)
