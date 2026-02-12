# MicroAgent - Ai

A lightweight framework for building and testing AI agents with support for multiple LLM providers.

## Features

- 🚀 Multi-provider support (OpenAI, Groq, OpenRouter, and more)
- 🔧 Easy configuration via environment variables
- 🧪 Comprehensive test suite
- 📦 Well-documented and type-annotated code
- 🔄 Async/await support
- 🧠 Built-in memory and context management

## Installation

```bash
# Clone the repository
git clone git@github.com:jcremona2/microagent.git
cd microagent

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -e .[dev]

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

## Configuration

Copy `.env.example` to `.env` and update with your API keys:

```env
# Required API Keys
OPENAI_API_KEY=your-openai-key
GROQ_API_KEY=your-groq-key
OPENROUTER_API_KEY=your-openrouter-key

# Optional: Default model settings
DEFAULT_MODEL=openai/gpt-4
DEFAULT_TEMPERATURE=0.7
DEFAULT_MAX_TOKENS=1000

# Optional: Test configuration (for running tests)
TEST_MODEL=openai/gpt-3.5-turbo
TEST_MAX_TOKENS=100
```

## Quick Start

```python
from microagent import Agent, LLMClient
from microagent.providers import ProviderType

# Initialize a client with your preferred provider
client = LLMClient(
    provider=ProviderType.GROQ,
    model="llama3-70b-8192"
)

# Create an agent with the client
agent = Agent(
    llm_client=client,
    system_prompt="You are a helpful assistant."
)

# Run the agent
response = await agent.run("Hello, how are you?")
print(response)
```

## Testing

Run the test suite:

```bash
# Install test dependencies
pip install -e ".[test]"

# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_groq_integration.py -v

# Run with coverage report
pytest --cov=microagent tests/
```

### Test Configuration

Create a `.env.test` file in the `tests` directory to configure test-specific settings:

```env
# tests/.env.test
GROQ_API_KEY=your-test-key
TEST_MODEL=llama3-70b-8192
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
