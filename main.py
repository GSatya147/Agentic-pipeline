
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
            snapshot = graph.invoke_graph(user_query=user_query, initial_state=initial_state, thread_id=thread_id)

            if "final_node" in snapshot.next:
                print(f"Draft answer: {snapshot.values["messages"][-1].content}")

                user_pref = input(">> Approve? (y/n)")

                if user_pref.lower() == "y":
                    graph.resume_graph(thread_id)

                elif user_pref.lower() == "n":
                    modification = input(">> modified content: ")
                    graph.modify_and_resume(modification, thread_id)

    except KeyboardInterrupt as k:
        print(k)
        break

    except Exception as e:
        print(e)
        break