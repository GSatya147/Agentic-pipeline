import json
import os

from dotenv import load_dotenv
import litellm
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

load_dotenv()

class Client:
    def __init__(self, model):
        self.model = model
    
    def convert_messages(self, messages_dict):
        converted_dict = []
        for message in messages_dict:
            if isinstance(message, HumanMessage):
                converted_dict.append(
                    {
                        "role" : "user",
                        "content" : message.content
                    }
                )

            elif isinstance(message, AIMessage):
                if message.tool_calls:
                    converted_dict.append(
                        {
                            "role" : "assistant",
                            "content" : message.content,
                            "tool_calls" : [{
                                "id" : tool.get("id"),
                                "type" : "function",
                                "function" : {
                                    "name" : tool.get("name"),
                                    "arguments" : json.dumps(tool.get("args")) 
                                    # "arguments" : tool.get("args")
                                }

                            } for tool in message.tool_calls]
                        }
                    )
                
                else:
                    converted_dict.append(
                        {
                            "role" : "assistant",
                            "content" : message.content
                        }
                    )
                
            elif isinstance(message, ToolMessage):
                converted_dict.append(
                    {
                        "role" : "tool",
                        "content" : message.content,
                        "tool_call_id" : message.tool_call_id
                    }
                )

        return converted_dict

    def call_llm(self, messages, tools):
        try:
            context_messages = self.convert_messages(messages_dict=messages)

            response = litellm.completion(
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                model=self.model,
                messages=context_messages,
                tools=tools,
                )
            
            message = response.choices[0].message.model_dump()

            return message

        except Exception as e:
            print(e)
    
if __name__=="__main__":
    pass