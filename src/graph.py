from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver 

from src.state import AgentState
from src.nodes import llm_call, tool_node, routing_logic, final_node

class AgentGraph:
    def __init__(self):
        self.graph = StateGraph(AgentState)
        self.checkpointer = InMemorySaver()
        # add nodes
        self.graph.add_node("llm_call", llm_call)
        self.graph.add_node("tool_node", tool_node)
        self.graph.add_node("final_node", final_node)

        # add edges
        self.graph.add_edge(START, "llm_call")
        self.graph.add_edge("tool_node", "llm_call")
        self.graph.add_edge("final_node", END)

        # add conditional edges
        self.graph.add_conditional_edges("llm_call", routing_logic)

        self.graph = self.graph.compile(checkpointer=self.checkpointer)

    def invoke_graph(self, user_query, initial_state, thread_id):
        config = {
            "configurable" : {
                "thread_id" : f"thread_{thread_id}"
            }
        }

        try:
            snapshot = self.graph.get_state(config=config)

            if snapshot.values:
                self.graph.invoke({"messages" : [{"role" : "user", "content" : user_query}]}, config)

            else:
                self.graph.invoke(initial_state, config)

        except Exception as e:
            print(e)

    def get_history(self, thread_id):
        config = {
            "configurable" : {
                "thread_id" : f"thread_{thread_id}"
            }
        }

        if config:
            snapshot = self.graph.get_state(config=config)

            if snapshot.values:
                print(f"History: {snapshot.values["messages"]}")
