from openai import AzureOpenAI
from typing import Dict, List, Literal


def get_from_env(variable_name: str) -> str:
    """Retrieve variables from .env file using dotenv."""
    from dotenv import load_dotenv
    import os

    load_dotenv()
    return os.getenv(variable_name)


def make_client() -> AzureOpenAI:
    api_key = get_from_env("AZURE_API_KEY")
    api_version = get_from_env("AZURE_API_VERSION")
    azure_endpoint = get_from_env("AZURE_API_BASE")
    
    client = AzureOpenAI(api_key=api_key,
                         api_version=api_version,
                         azure_endpoint=azure_endpoint,
                         timeout=30.0)
    return client


def get_response(client: AzureOpenAI, model: str, messages: List[Dict[Literal["system", "user", "assistant"], str]]) -> str:
    """Get response from the LLM."""
    response = client.chat.completions.create(model=model,
                                              messages=messages,
                                              temperature=0.1,
                                              stream=False)
    
    result = response.choices[0].message.content.strip()
    
    return result
    
def call_llm(messages: List[Dict[Literal["system", "user", "assistant"], str]]) -> str:    
    client = make_client()
    
    model = "gpt-4.1"
    
    response = get_response(client, model, messages)
    
    return response


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
