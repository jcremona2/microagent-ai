# MicroAgent - Ai

A lightweight framework for building and testing AI agents with support for multiple LLM providers.

## Features

- 🚀 Multi-provider support (OpenAI, Groq, OpenRouter, and more)
- 🔧 Easy configuration via environment variables
- 🧪 Comprehensive test suite
- 📦 Well-documented and type-annotated code
- 🔄 Async/await support
- 🧠 Built-in memory and context management
- ⚡ High-performance LLM inference with Groq
- 🔍 Built-in model validation and error handling

## Installation

```bash
# Clone the repository
git clone git@github.com:jcremona2/microagent.git
cd microagent

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install the package in development mode
pip install -e .[groq]  # For Groq support
# or
pip install -e .[all]   # For all providers

# Set up your environment variables
cp .env.example .env
# Edit .env with your API keys
```

## Quick Start

### Using the Groq Provider

```python
from microagent.providers.groq import GroqProvider
import os

# Initialize the provider
provider = GroqProvider(api_key=os.getenv('GROQ_API_KEY'))

# Basic chat completion
response = provider.chat_complete(
    messages=[
        {'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'user', 'content': 'Tell me a joke'}
    ],
    model='llama-3.3-70b-versatile',
    temperature=0.7,
    max_tokens=100
)

print(response.choices[0].message.content)
```

### Available Models

Here are some of the available models you can use with the Groq provider:

- `llama-3.3-70b-versatile` - High-quality, general-purpose model (default)
- `llama-3.1-8b-instant` - Faster, more lightweight option
- `meta-llama/llama-4-maverick-17b-128e-instruct` - Specialized for instruction following
- `moonshotai/kimi-k2-instruct` - Optimized for specific instruction-based tasks
- `whisper-large-v3` - For speech-to-text tasks

To see all available models:

```python
from groq import Groq

client = Groq(api_key='your-api-key')
models = client.models.list()
for model in models.data:
    print(model.id)
```

## Configuration

### Environment Variables

Create a `.env` file in the root directory with your API keys:

```env
# Required for Groq
GROQ_API_KEY=your_groq_api_key

# Optional: Override the default API endpoint if needed
# GROQ_BASE_URL=https://api.groq.com

# Other providers
OPENAI_API_KEY=your_openai_api_key
OPENROUTER_API_KEY=your_openrouter_api_key

# Optional: Default model settings
DEFAULT_MODEL=llama-3.3-70b-versatile
DEFAULT_TEMPERATURE=0.7
DEFAULT_MAX_TOKENS=1000
```

## Testing

### Running Tests

To run the test suite:

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run all tests
pytest -v

# Run only Groq integration tests
pytest -v tests/test_groq_integration.py -s

# Run with coverage report
pytest --cov=microagent --cov-report=term-missing
```

### Test Configuration

Create a `.env.test` file in the `tests` directory to configure test-specific settings:

```env
# tests/.env.test
GROQ_API_KEY=your-test-key
TEST_MODEL=llama-3.3-70b-versatile

# Optional test settings
TEST_TEMPERATURE=0.7
TEST_MAX_TOKENS=100
```

## Advanced Usage

### Streaming Responses

```python
# Streaming example
for chunk in provider.stream_chat_complete(
    messages=[{'role': 'user', 'content': 'Tell me a story about AI'}],
    model='llama-3.3-70b-versatile',
    stream=True
):
    print(chunk.choices[0].delta.content or "", end="", flush=True)
```

### Async Support

```python
import asyncio

async def main():
    provider = GroqProvider(api_key=os.getenv('GROQ_API_KEY'))
    response = await provider.achat_complete(
        messages=[{'role': 'user', 'content': 'Hello, async world!'}],
        model='llama-3.3-70b-versatile'
    )
    print(response.choices[0].message.content)

# Run the async function
asyncio.run(main())
```

### Using with LangChain

```python
from langchain.llms import Groq
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

llm = Groq(temperature=0.7, model_name="llama-3.3-70b-versatile")
prompt = PromptTemplate(
    input_variables=["topic"],
    template="Write a short poem about {topic}"
)
chain = LLMChain(llm=llm, prompt=prompt)
print(chain.run("artificial intelligence"))
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Ensure your `GROQ_API_KEY` is set correctly in your environment
   - Verify the key has the necessary permissions

2. **Model Not Found**
   - Check the model name spelling
   - Verify the model is available in your region
   - Use the `client.models.list()` method to see available models

3. **Rate Limiting**
   - Implement exponential backoff for retries
   - Consider using a queue system for high-volume applications

4. **Connection Issues**
   - Check your internet connection
   - Verify the API endpoint is reachable from your network
   - Try with a different network if possible

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to Groq for their high-performance inference platform
- Inspired by the broader AI/ML community's work on LLM tooling
- Built with ❤️ by [Your Name]
SKIP_SLOW_TESTS=false
```

## Project Structure

```
microagent/
├── microagent/               # Main package
│   ├── __init__.py           # Package initialization
│   ├── agent.py              # Core Agent class
│   ├── client.py             # LLM client implementations
│   ├── providers.py          # Provider configurations
│   └── utils.py              # Utility functions
├── tests/                    # Test suite
│   ├── __init__.py
│   ├── conftest.py           # Test configuration
│   ├── test_groq_integration.py
│   └── .env.test             # Test environment variables
├── examples/                 # Example scripts
├── .env.example              # Example environment variables
├── .gitignore
├── pyproject.toml            # Project metadata and dependencies
└── README.md                 # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to all LLM providers for their amazing APIs
- Inspired by various open-source AI agent frameworks
- Built with ❤️ by the community
