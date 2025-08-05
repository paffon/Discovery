from call_llm import call_llm
import yaml
from typing import List, Tuple

from pocketflow import Node, Flow
import prompts


def figure_out_who_the_moderator_is_talking_to(moderator_input: str) -> str:
    """Determine if the moderator is addressing the Israeli or Palestinian negotiators."""
    
    class DeciderNode(Node):
        def prep(self, shared):
            messages = [{"role": "system", "content": prompts.director_prompt},
                        {"role": "user", "content": shared["moderator_input"]}]
            return messages

        def exec(self, messages: List[dict]) -> str:
            response = call_llm(messages, model="Phi-4-multimodal-instruct")
            try:
                yaml_str = response.split("```yaml")[1].split("```")[0].strip()
                yaml_dict = yaml.safe_load(yaml_str)
                speaker = yaml_dict.get("speaker", "unclear")
                
                if speaker == "unclear":
                    raise ValueError("LLM returned unclear result")
                
                return speaker
            except Exception as e:
                raise  # Re-raise to trigger PocketFlow's retry

        def exec_fallback(self, prep_res, exc):
            return "unclear"

        def post(self, shared, prep_res, exec_res):
            shared["speaker"] = exec_res
            return exec_res  # Return the actual speaker name

    decider_node = DeciderNode(max_retries=3, wait=1)

    # No flow transitions needed - just a single node that handles retries internally
    flow = Flow(start=decider_node)
    shared = {"moderator_input": moderator_input}
    flow.run(shared)

    next_speaker = shared["speaker"]
    return next_speaker


def main() -> None:    
    while True:
        moderator_input = input("Moderator (Omri): ")
        if moderator_input.lower() in ["exit", "quit"]:
            print("Ending the debate session.")
            break
        
        next_speaker = figure_out_who_the_moderator_is_talking_to(moderator_input)
        print("Next speaker determined:", next_speaker)
        pass
    
if __name__ == "__main__":
    main()
