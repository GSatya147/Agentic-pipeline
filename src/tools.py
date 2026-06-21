import os

from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

class Tools:
    def __init__(self):
        try:
            self.client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

        except Exception as e:
            print(e)

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