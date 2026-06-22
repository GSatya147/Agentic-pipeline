import os

from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

class Tools:
    def __init__(self):
        self.tools_schema: list[dict] = []
        try:
            self.client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

        except Exception as e:
            print(e)

    def add_tool_schema(self):
        self.tools_schema.append({
            "type" : "function",
            "function" : {
                "name" : "web search tool",
                "description" : "use web search when the context is inadequate, or when user requests for it. Be factual about claims use the web search for confirmation whenever applicable",
                "parameters" : {
                    "type" : "object",
                    "properties" : {
                        "query" : {
                            "type" : "string",
                            "description" : "a simple string type query to perform the web search efficiently",
                        }
                    },
                    "required" : ["query"]
                }
            }
        })

        return self.tools_schema

    def search_tool(self, query):
        results = self.client.search(
            query=query,
            search_depth="basic",
        )

        llm_string = ""
        for result in results.get("results")[:3]:
            llm_string+=f"title         : {result.get("title")}\nurl         : {result.get("url")}\ncontent         : {result.get("content")}\n\n"

        return llm_string
    
if __name__=="__main__":
    tool_obj = Tools()
    result = tool_obj.search_tool(query="director of oppenheimer?")

    print(result)