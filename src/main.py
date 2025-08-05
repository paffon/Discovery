from call_llm import call_llm
import yaml
from typing import Dict, List, Tuple

from pocketflow import Node, Flow
import prompts


def figure_out_who_the_moderator_is_talking_to(conversation: List[Dict[str, str]]) -> str:
    """Determine if the moderator is addressing the Israeli or Palestinian negotiators."""
    
    class DeciderNode(Node):
        def prep(self, shared):
            messages = [{"role": "system", "content": prompts.director_prompt},
                        {"role": "user", "content": shared["conversation_history"]}]
            return messages

        def exec(self, messages: List[dict]) -> str:
            response = call_llm(messages, model="gpt-4")
            yaml_str = response.split("```yaml")[1].split("```")[0].strip()
            yaml_dict = yaml.safe_load(yaml_str)
            speaker = yaml_dict.get("speaker", "Unclear")

            if speaker in ["Unknown input", "Unclear"]:
                raise ValueError("LLM returned Unclear result")
            
            return speaker

        def exec_fallback(self, prep_res, exc):
            return "Unclear"

        def post(self, shared, prep_res, exec_res):
            shared["speaker"] = exec_res
            return exec_res  # Return the actual speaker name

    decider_node = DeciderNode(max_retries=3, wait=1)

    # No flow transitions needed - just a single node that handles retries internally
    flow = Flow(start=decider_node)
    conversation_history_str = "\n".join(f"{msg['role']}: {msg['content']}" for msg in conversation)   
    shared = {"conversation_history": conversation_history_str}
    flow.run(shared)

    next_speaker = shared["speaker"]
    return next_speaker


def main() -> None:
    conversation = []
    while True:
        moderator_input = input("Moderator (Omri): ")
        
        if moderator_input.lower() in ["exit", "quit"]:
            print("Ending the debate session.")
            break
        
        conversation.append({"role": "user", "content": moderator_input})
        
        next_speaker = figure_out_who_the_moderator_is_talking_to(conversation)
        
        if next_speaker == "Unknown input":
            print("Director: The input was not understood, please rephrase.")
        elif next_speaker == "Unclear":
            print("Director: It's unclear who this statement was intended to.")
        elif next_speaker in ["Israeli", "Palestinian"]:
            print(f"Director: The next speaker is {next_speaker}.")
        elif next_speaker == "Both":
            print("Director: The question is directed to both teams.")
        elif next_speaker == "General":
            print("Director: This is a general statement, not directed to any specific team.")
        
if __name__ == "__main__":
    main()
