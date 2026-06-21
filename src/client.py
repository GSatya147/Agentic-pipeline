import os

from dotenv import load_dotenv
import litellm

load_dotenv()

class Client:
    def __init__(self, model):
        self.model = model

    def call_llm(self, messages, tools):
        response = litellm.completion(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            model=self.model,
            messages=messages,
            tools=tools,
        )

        return response.choices[0].message
    
if __name__=="__main__":
    pass