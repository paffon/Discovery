from call_llm import call_llm
import yaml
from typing import List, Tuple


def get_topic() -> str:
    topic = input("Type a topic (or leave empty for the system to make one up): ")
    if not topic:
        while not topic:
            try:
                prompt = """Suggest a topic for discussion/debate.
It needs to be something that one can have different opinions, points of view and perhaps even have feelings about.
Output ONLY the requested information in YAML format.

**YAML Output Requirements:**
- The topic (string).

**Example Output:**
```yaml
topic: The impact of artificial intelligence on society
```

Note: In this example, the topic of ""The impact of artificial intelligence on society" is merely an example. You need to be more creative than that.

Generate the YAML output now:
"""
                response = call_llm(messages=prompt, temperature=2)
                yaml_str = response.split("```yaml")[1].split("```")[0].strip()
                structured_result = yaml.safe_load(yaml_str)
                assert "topic" in structured_result, "The YAML output must contain a 'topic' key."
                topic = structured_result["topic"]
            except (yaml.scanner.ScannerError, AssertionError) as e:
                print(f"Error processing YAML output: {e}\nTrying again...")
                continue
    return topic.strip()

def main() -> None:
    objective, teams_names = define_objective_and_teams()

if __name__ == "__main__":
    main()
