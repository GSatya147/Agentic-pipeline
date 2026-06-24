import os

from dotenv import load_dotenv
from langgraph.graph import END

from src.client import Client
from src.tools import Tools
from src.state import AgentState

load_dotenv()

def llm_call(state: AgentState) -> dict:
    print("LLM Node Executing...")

    client_obj = Client(model=os.getenv("DEEPSEEK_MODEL"))
    response = client_obj.call_llm(messages=state["messages"], tools=state["tools_schema"])

    print(f"""
        thought     : {response.get("reasoning_content", "")}
        tool calls  : {response.get("tool_calls", [])}
        response    : {response.get("content", "Execute search tool")} 
    """)

    return {"messages" : [response], "step_count" : state["step_count"] + 1}   

def final_node(state: AgentState):
    print("Final Node Executing...")

    if state["step_count"] >=10:
        print("        Tool limit has reached...")
    
    else:
        print(f"        Final Result: {state["messages"][-1].content}")
    
def tool_node(state: AgentState):
    print("Tool Node Executing")
    # print(state["messages"][-1].tool_calls[0])
    tool_name = state["messages"][-1].tool_calls[0]["name"]

    tool_obj = Tools()

    if tool_name == "calculator_tool":

        expression_query = state["messages"][-1].tool_calls[0]["args"]["expression"]
        tool_call_id = state["messages"][-1].tool_calls[0]["id"]
        expression_result = tool_obj.calculator_tool(query=expression_query)

        tool_message = {
            "role" : "tool",
            "content" : expression_result,
            "tool_call_id" : tool_call_id
        }

        print(f"""
            Calculator Executing...
            response : {expression_result} 
        """)    

        return {"messages" : [tool_message], "step_count" : state["step_count"] + 1}

    elif tool_name == "search_tool":

        search_query = state["messages"][-1].tool_calls[0]["args"]["query"]
        tool_call_id = state["messages"][-1].tool_calls[0]["id"]
        search_result = tool_obj.search_tool(query=search_query)

        tool_message = {
            "role" : "tool",
            "content" : search_result,
            "tool_call_id" : tool_call_id
        }

        print(f"""
            Web search Executing...
            response : {search_result} 
        """)    

        return {"messages" : [tool_message], "step_count" : state["step_count"] + 1}

    else:
        return {"messages" : [{"role" : "tool", "content" : "Error, unknow tool requested [use search_tool/calculator_tool]"}], "step_count" : state["step_count"] + 1}

def routing_logic(state: AgentState):
    print("Routing Node Executing...")
    response = state["messages"][-1].tool_calls

    if state["step_count"] >=10:
        return "final_node"
    
    if response:
        print(f"        Action: To Execute {response[0]["name"]}, routed towards tool node")
        return "tool_node"
    
    else:
        print(f"        Action: routed towards final node")
        return "final_node"
        
    





