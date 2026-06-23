from langgraph.graph import StateGraph, START, END

from src.state import AgentState
from src.nodes import llm_call, search_tool, routing_logic, final_node

class AgentGraph:
    def __init__(self):
        self.graph = StateGraph(AgentState)
        # add nodes
        self.graph.add_node("llm_call", llm_call)
        self.graph.add_node("search_tool", search_tool)
        self.graph.add_node("final_node", final_node)

        # add edges
        self.graph.add_edge(START, "llm_call")
        self.graph.add_edge("search_tool", "llm_call")
        self.graph.add_edge("final_node", END)

        # add conditional edges
        self.graph.add_conditional_edges("llm_call", routing_logic)

        self.graph = self.graph.compile()

    def invoke_graph(self, initial_state):
        try:
            self.graph.invoke(initial_state)

        except Exception as e:
            print(e)