
from src.tools import Tools
from src.graph import AgentGraph

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
graph = AgentGraph()

try:
    graph.invoke_graph(initial_state=initial_state)

except Exception as e:
    print(e)