import os

from dotenv import load_dotenv
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

from src.agent import Client

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    step_count: int

def llm_call(state: AgentState, tools_schema: list[dict]) -> dict:
    client_obj = Client(model=os.getenv("DEEPSEEK_MODEL"))
    response = client_obj.call_llm(messages=state["messages"], tools=tools_schema)

    return {"messages" : [response], "step_count" : state["step_count"] + 1}

def routing_logic(state: AgentState):
    pass
