from pocketflow import Flow, Node
import prompts
from call_llm import call_llm
import yaml

class OpeningNode(Node):
    def prep(self, shared):
        assert not shared, "OpeningNode should not have any shared state"
        
        general_message = "Debate starting. Israeli and Palestinian negotiators are ready to begin discussions."
        opening_statement_prompt = "Moderator: Make your opening statement, in one paragraph. Skip formalities and niceties, skip addressing the other team and the moderator, just state your position."
        
        shared["all_outputs"] = [general_message, opening_statement_prompt]
        
        print("\n".join(shared["all_outputs"]) + '\n')
        
        return shared["all_outputs"]
    
    def exec(self, prep_res):
        opening_statements = []
        hard_coded_opening_statements = {
            "Israeli": """Israel is committed to achieving a lasting peace that ensures security, prosperity, and mutual respect for both Israelis and Palestinians. Our primary goal is to maintain a secure and recognized state for the Israeli people, including the right to self-defense and control over our borders. We seek a solution that addresses the legitimate aspirations of the Palestinian people while ensuring that any future Palestinian entity is demilitarized and does not pose a threat to Israel. We are prepared to make significant compromises, but not at the expense of our fundamental security needs.""",
            "Palestinian": """Our primary goal is to achieve a just and lasting peace that ensures the establishment of an independent and sovereign Palestinian state based on the 1967 borders, with East Jerusalem as its capital. We seek the right of return for Palestinian refugees, the release of all Palestinian prisoners, and the cessation of all settlement activities. We are committed to a peaceful resolution that respects the rights and dignity of the Palestinian people and adheres to international law and UN resolutions."""
            }
        for team, sys_prompt in [("Israeli", prompts.simple_israeli_prompt),
                                 ("Palestinian", prompts.simple_palestinian_prompt)]:
            # opening_statement = call_llm([
            #     {"role": "system", "content": sys_prompt},
            #     {"role": "user", "content": "'\n".join(prep_res)}
            # ])
            opening_statement = hard_coded_opening_statements[team]
            opening_statements.append(f"{team} opening statement: {opening_statement}")
            print(f"\n{team} opening statement:\n{opening_statement}")
        
        prep_res += opening_statements
        
        return prep_res

    def post(self, shared, prep_res, exec_res):
        shared["all_outputs"] = exec_res
        return "continue"

class ModeratorSpeaksNode(Node):
    def prep(self, shared):
        assert "all_outputs" in shared, "ModeratorSpeaksNode requires 'all_outputs' in shared state"
        
        if not shared.get("mod_discussion", None):
            shared["mod_discussion"] = [{"role": "system", "content": prompts.director_prompt},
                                        {"role": "user", "content": "Discussion so far:\n\n" + "\n".join(shared["all_outputs"])}]
            print('-' * 50)
        
        shared["mod_discussion"].append(
            {"role": "user", "content": "Moderator: " + input("Moderator: ")})
        
        return shared["mod_discussion"]
    
    def exec(self, mod_discussion):
        response = call_llm(mod_discussion)
        
        return response
    
    def post(self, shared, prep_res, exec_res):
        yaml_content = exec_res.split("```yaml")[1].split("```")[0].strip()
                
        action = yaml.safe_load(yaml_content)["action"]
        
        if action == "clarify":
            clarification = yaml.safe_load(yaml_content)["clarification"]
            print(f"\nDirector: {clarification}")
            shared["mod_discussion"].append({"role": "assistant", "content": f"Director: {clarification}"})
            
        elif action == "continue":
            shared["mod_discussion"] = []
            shared["refer_to"] = yaml.safe_load(yaml_content)["refer_to"]
            shared["rephrased_statement"] = yaml.safe_load(yaml_content)["moderator_statement"]
            shared["all_outputs"].append("Moderator: " + shared["rephrased_statement"])
            
        if action != "clarify":
            print("-" * 50)
            
        return action
        
class AskSpeakNode(Node):
    def prep(self, shared):
        print(shared["all_outputs"][-1])
        
        refer_to = shared['refer_to']
        
        system_prompt = prompts.simple_israeli_prompt if refer_to == "Israeli" else prompts.simple_palestinian_prompt
        
        messages = [{"role": "system", "content": system_prompt},
                    {"role": "user", "content": '\n'.join(shared["all_outputs"])}]
        
        return messages, refer_to
        
    def exec(self, prep_res):
        messages, refer_to = prep_res
        response = call_llm(messages)
        
        print(f"\n{refer_to} team:\n{response}")
        
        return f"{refer_to} team: {response}"
    
    def post(self, shared, prep_res, exec_res):
        shared["all_outputs"].append(exec_res)
        
        # Reset the refer_to for the next round
        shared["refer_to"] = ""
        
        return "continue"
        
class ConcludeNode(Node):
    def prep(self, shared):
        messages = [{"role": "system", "content": prompts.summarizer_prompt},
                    {"role": "user", "content": '\n'.join(shared["all_outputs"])}]
        return messages
    
    def exec(self, messages):
        response = call_llm(messages)
        return response
    
    def post(self, shared, prep_res, exec_res):
        shared["summary"] = exec_res.strip()
        
def main() -> None:
    node_opening = OpeningNode()
    node_moderator_speaks = ModeratorSpeaksNode()
    node_ask_speaker = AskSpeakNode()
    node_conclude = ConcludeNode()
    
    node_opening - "continue" >> node_moderator_speaks
    node_moderator_speaks - "clarify" >> node_moderator_speaks
    node_moderator_speaks - "continue" >> node_ask_speaker
    node_moderator_speaks - "wrap_up" >> node_conclude
    node_ask_speaker - "continue" >> node_moderator_speaks
    
    shared = {}
    flow = Flow(start=node_opening)
    flow.run(shared=shared)
    
    full_debate = "\n".join(shared["all_outputs"])
    summary = shared["summary"]
    print(f"\nSummary of the debate:\n{summary}")
    
    # Save to txt file
    with open("debate_summary.txt", "w") as f:
        f.write(full_debate)
        f.write("\n\n===========================================Summary:\n")
        f.write(summary)

if __name__ == "__main__":
    main()