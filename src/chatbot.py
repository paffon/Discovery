from call_llm import call_llm
from pocketflow import Flow, Node


class ChatNode(Node):
    def prep(self, shared):
        if "messages" not in shared:
            shared["messages"] = []
            print("Start a conversation!")
        
        user_input = input("You: ")
        shared["messages"].append({"role": "user", "content": user_input})
        return shared["messages"]
    
    def exec(self, messages):
        response = call_llm(messages)
        return response

    def post(self, shared, prep_res, exec_res):
        print(f"Assistant: {exec_res}")
        
        shared["messages"].append({"role": "assistant", "content": exec_res})
        
        return "continue"
    
chat_node = ChatNode()
chat_node - "continue" >> chat_node

flow = Flow(start=chat_node)

if __name__ == "__main__":
    shared = {}
    flow.run(shared)