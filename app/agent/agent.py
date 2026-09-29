from langchain.agents import create_agent

from app.agent.prompts import SYSTEM_PROMPT
from app.agent.tools import calculator
from app.services.langchain_model import AICoreChatModel


def create_chat_agent():

    model = AICoreChatModel()

    tools = [
        calculator
    ]

    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=SYSTEM_PROMPT
    )

    return agent