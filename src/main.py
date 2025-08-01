

from call_llm import call_llm


def main() -> None:
    topic = input("Type a topic (or leave empty for the system to make one up): ")
    if not topic:
        topic = call_llm(messages=[{"role": "user", "content": "Please suggest a topic for discussion. It needs to be something that one can have different opinions, points of view and perhaps even have feelings about"}])
    print(f"Selected topic: {topic}")

if __name__ == "__main__":
    main()