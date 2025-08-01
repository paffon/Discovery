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
    # Example usage
    example_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"}
    ]
    
    example_messages.append({"role": "assistant", "content": call_llm(example_messages)})
    
    for msg in example_messages:
        print(f"{msg['role'].ljust(9)}: {msg['content']}")
