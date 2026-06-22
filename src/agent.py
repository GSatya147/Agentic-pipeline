import json
import os

from dotenv import load_dotenv
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from client import Client
from tools import Tools

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    tools_schema: list
    step_count: int

def llm_call(state: AgentState) -> dict:
    client_obj = Client(model=os.getenv("DEEPSEEK_MODEL"))
    response = client_obj.call_llm(messages=state["messages"], tools=state["tools_schema"])

    return {"messages" : [response], "step_count" : state["step_count"] + 1}

def search_tool(state: AgentState):
    tool_obj = Tools()

    args = state["messages"][-1].tool_calls[0]["args"]
    tool_call_id = state["messages"][-1].tool_calls[0]["id"]
    search_result = tool_obj.search_tool(query=args["query"])

    tool_message = {
        "role" : "tool",
        "content" : search_result,
        "tool_call_id" : tool_call_id
    }

    return {"messages" : [tool_message], "step_count" : state["step_count"] + 1}

def routing_logic(state: AgentState):
    response = state["messages"][-1].tool_calls
    if response:
        return "search_tool"
    else:
        return END
    
graph = StateGraph(AgentState)

# add nodes
graph.add_node("llm_call", llm_call)
graph.add_node("search_tool", search_tool)

# add edges
graph.add_edge(START, "llm_call")
graph.add_edge("search_tool", "llm_call")

# add conditional edges
graph.add_conditional_edges("llm_call", routing_logic)

graph = graph.compile()

user_query = input(">> ")

tool = Tools()
tools_schema = tool.add_tool_schema()

initial_state = {
    "messages" : [{
        "role" : "user",
        "content" : user_query
    }],
    "tools_schema" : tools_schema,
    "step_count" : 0
}

try:
    result = graph.invoke(initial_state)
    print(result)

except Exception as e:
    print(e)
