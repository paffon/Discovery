from call_llm import call_llm
from pocketflow import Flow, Node


class ChatNode(Node):
    def prep(self, shared):
        if "messages" not in shared:
            welcome_message = """Hi! We're here to plan a debate. What topic did you have in mind?"""
            
            messages = {
                "role": "system",
                "content": """Your name is Discovery, a debate planning assistant.
You help users define the topic, objective, and teams for a debate.
Your ultimate goal is to help the user define a clear objective and a list of names for the teams, which will debate about the topic.
The teams should reflect all possible relevant stakeholders in the debate.
You'll engage with the user in a conversational manner, asking questions and providing suggestions.
You'll be helpful and creative, but concise and to the point.
"""
            }
            
            shared["messages"] = []
            
        
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


def define_objective_and_teams():
    shared = {}
    flow = Flow(start=chat_node)
    flow.run(shared)
    return shared.get("objective", ""), shared.get("teams_names", [])