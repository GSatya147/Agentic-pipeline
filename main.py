
from src.tools import Tools
from src.graph import AgentGraph

tool = Tools()
tools_schema = tool.add_tool_schema()

graph = AgentGraph()

while True:
    thread_id = int(input("enter numerical id: "))
    user_query = input(">> ")

    initial_state = {
        "messages" : [{
            "role" : "user",
            "content" : user_query
        }],
        "tools_schema" : tools_schema,
        "step_count" : 0,
    }
    try:
        if user_query.lower() == "history":
            graph.get_history(thread_id=thread_id)

        else:
            graph.invoke_graph(user_query=user_query, initial_state=initial_state, thread_id=thread_id)

    except KeyboardInterrupt as k:
        print(k)
        break

    except Exception as e:
        print(e)
        break