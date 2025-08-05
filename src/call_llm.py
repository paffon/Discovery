from openai import AzureOpenAI
from typing import Dict, List, Literal, Union


def get_from_env(variable_name: str) -> str:
    """Retrieve variables from .env file using dotenv."""
    from dotenv import load_dotenv
    import os

    load_dotenv()
    return os.getenv(variable_name)
    
def call_llm(
    messages: Union[str, List[Dict[Literal["system", "user", "assistant"], str]]],
    temperature: float = 0.1,
    model: Literal["gpt-35-turbo", "gpt-4", "gpt-4.1", "gpt-4o", "gpt-o4-mini", "Phi-4-multimodal-instruct"] = "gpt-4"
) -> str:
    
    if type(messages) is str:
        messages = [{"role": "user", "content": messages}]
        
    api_key = get_from_env("AZURE_API_KEY")
    api_version = get_from_env("AZURE_API_VERSION")
    azure_endpoint = get_from_env("AZURE_API_BASE")
    
    client = AzureOpenAI(api_key=api_key,
                         api_version=api_version,
                         azure_endpoint=azure_endpoint,
                         timeout=30.0)
    
    # print("Calling LLM with messages:")
    # print(messages)

    response = client.chat.completions.create(model=model,
                                              messages=messages,
                                              temperature=temperature,
                                              stream=False)
    
    result = response.choices[0].message.content.strip()
    
    return result


if __name__ == "__main__":
    
    def print_messages_with_roles(messages) -> None:
        """Print messages with their roles."""
        for msg in messages:
            print(f"{msg['role'].ljust(9)}: {msg['content']}")
    
    def send_and_print(messages) -> None:
        print('\n----\n')

        """Send messages to the LLM and print the response."""
        response = call_llm(messages)
        messages.append({"role": "assistant", "content": response})
        print_messages_with_roles(messages)
    
    # Roles can be: 'system', 'assistant', 'user', 'function', 'tool', and 'developer'
    
    send_and_print([
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the capital of France?"}
        ])
    
    send_and_print([
            {"role": "system", "content": "You are a knowledgeable bot."},
            {"role": "assistant", "content": "How can I assist you today?"}
        ])
    
    send_and_print([
            {"role": "system", "content": "You are a knowledgeable bot."}
        ])
    
    send_and_print([
            {"role": "system", "content": "You are a knowledgeable bot."},
            {"role": "developer", "content": "This is a tasty burger."}
        ])

    send_and_print([
            {"role": "assistant", "content": "I will wait for the user's message, and say NOTHING util it arrives."}
        ])
