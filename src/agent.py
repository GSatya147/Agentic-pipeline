import json
import os

from dotenv import load_dotenv
from typing import Annotated, TypedDict
from langchain_core.messages import ToolMessage
from langgraph.graph import END
from langgraph.graph.message import add_messages

from src.agent import Client
from src.tools import Tools

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    step_count: int

def llm_call(state: AgentState, tools_schema: list[dict]) -> dict:
    client_obj = Client(model=os.getenv("DEEPSEEK_MODEL"))
    response = client_obj.call_llm(messages=state["messages"], tools=tools_schema)

    return {"messages" : [response], "step_count" : state["step_count"] + 1}

def search_tool(state: AgentState):
    tool_obj = Tools()

    args = json.loads(state["messages"][-1].tool_calls[0]["function"]["arguments"])
    tool_call_id = json.loads(state["messages"][-1].tool_calls[0]["id"])
    search_result = tool_obj.search_tool(query=args["query"])

    ToolMessage(content=search_result, tool_call_id=tool_call_id)

    return {"messages" : [ToolMessage], "step_count" : state["step_count"] + 1}

def routing_logic(state: AgentState):
    response = state["messages"][-1].tool_calls
    if response:
        return "search_tool"
    else:
        return END
