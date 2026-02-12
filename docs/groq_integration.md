# Groq Integration Guide

This guide provides comprehensive documentation for integrating Groq's high-performance language models into your application.

## Table of Contents
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Available Models](#available-models)
- [API Reference](#api-reference)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Examples](#examples)

## Installation

1. Install the official Groq Python package:
   ```bash
   pip install groq
   ```

2. Set your API key as an environment variable:
   ```bash
   export GROQ_API_KEY='your-api-key-here'
   ```
   Or add it to your `.env` file:
   ```
   GROQ_API_KEY=your-api-key-here
   ```

## Quick Start

```python
from groq import Groq

# Initialize the client
client = Groq()

# Make a simple completion request
response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain quantum computing in simple terms"}
    ],
    temperature=0.7,
    max_tokens=150
)

print(response.choices[0].message.content)
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | Your Groq API key | Required |
| `GROQ_MODEL` | Default model to use | `openai/gpt-oss-120b` |
| `GROQ_TEMPERATURE` | Default temperature (0.0-1.0) | `0.7` |
| `GROQ_MAX_TOKENS` | Default max tokens per request | `1024` |
| `GROQ_TIMEOUT` | Request timeout in seconds | `30` |

### Client Configuration

```python
from groq import Groq

client = Groq(
    api_key="your-api-key",  # Can also be set via env var
    timeout=30.0,           # Request timeout in seconds
    max_retries=3,          # Number of retries on failure
    base_url="https://api.groq.com/openai/v1"  # API endpoint
)
```

## Available Models

| Model Name | Description | Context Window |
|------------|-------------|----------------|
| `openai/gpt-oss-120b` | High-performance GPT model | 8K tokens |
| `llama3-70b-8192` | Meta's LLaMA 3 70B | 8K tokens |
| `mixtral-8x7b-32768` | Mixtral 8x7B MoE | 32K tokens |

## API Reference

### Chat Completion

```python
response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ],
    temperature=0.7,
    max_tokens=100,
    top_p=1.0,
    stream=False,
    stop=None,
    presence_penalty=0.0,
    frequency_penalty=0.0
)
```

### Streaming

```python
stream = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
)

for chunk in stream:
    content = chunk.choices[0].delta.content or ""
    print(content, end="", flush=True)
```

## Best Practices

1. **Error Handling**
   ```python
   from groq import APIStatusError, APIConnectionError
   
   try:
       response = client.chat.completions.create(...)
   except APIStatusError as e:
       print(f"API error: {e}")
   except APIConnectionError as e:
       print(f"Connection error: {e}")
   ```

2. **Rate Limiting**
   - Implement exponential backoff for retries
   - Respect rate limits (typically 60 requests per minute)
   - Use `time.sleep()` between requests in high-volume scenarios

3. **Token Management**
   - Be mindful of context window limits
   - Implement token counting for longer conversations
   - Use `max_tokens` to control response length

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify your API key is correct
   - Check for extra whitespace in the key
   - Ensure the key is properly exported in your environment

2. **Model Not Found**
   - Verify the model name is correct
   - Check for typos in the model name
   - Ensure the model is available in your region

3. **Rate Limiting**
   - Implement exponential backoff
   - Reduce request frequency
   - Consider batching requests

### Getting Help

- [Groq Documentation](https://console.groq.com/docs)
- [API Reference](https://console.groq.com/docs/api)
- [Community Support](https://community.groq.com/)

## Examples

### Basic Chatbot

```python
from groq import Groq

def chat():
    client = Groq()
    messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    
    print("Chat with the AI (type 'quit' to exit)")
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'quit':
            break
            
        messages.append({"role": "user", "content": user_input})
        
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        assistant_message = response.choices[0].message.content
        print(f"\nAssistant: {assistant_message}")
        messages.append({"role": "assistant", "content": assistant_message})

if __name__ == "__main__":
    chat()
```

### Streaming with Context

```python
import json
from groq import Groq

def stream_with_context():
    client = Groq()
    
    # Load conversation history
    try:
        with open('conversation.json', 'r') as f:
            messages = json.load(f)
    except FileNotFoundError:
        messages = [{"role": "system", "content": "You are a helpful assistant."}]
    
    print("Chat with the AI (type 'quit' to exit)")
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'quit':
            break
            
        messages.append({"role": "user", "content": user_input})
        
        print("\nAssistant: ", end="")
        full_response = ""
        
        stream = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            temperature=0.7,
            max_tokens=500,
            stream=True
        )
        
        for chunk in stream:
            content = chunk.choices[0].delta.content or ""
            print(content, end="", flush=True)
            full_response += content
        
        messages.append({"role": "assistant", "content": full_response})
        
        # Save conversation
        with open('conversation.json', 'w') as f:
            json.dump(messages, f, indent=2)

if __name__ == "__main__":
    stream_with_context()
```

### Batch Processing

```python
from groq import Groq
from typing import List
import asyncio

async def process_batch(queries: List[str]) -> List[str]:
    client = Groq()
    results = []
    
    for query in queries:
        response = await client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": query}],
            temperature=0.7,
            max_tokens=100
        )
        results.append(response.choices[0].message.content)
        await asyncio.sleep(0.5)  # Rate limiting
    
    return results

# Example usage
queries = [
    "What is the capital of France?",
    "Explain quantum computing",
    "Tell me a joke"
]

results = asyncio.run(process_batch(queries))
for query, result in zip(queries, results):
    print(f"Q: {query}\nA: {result}\n")
```

## License

This integration is provided under the MIT License. See the [LICENSE](LICENSE) file for more details.
