"""
Example usage of MicroAgent with a weather tool.
"""
import asyncio
from microagent import Agent, tool
from microagent.llm import OpenAIModel
from microagent.memory import InMemoryMemory

# Define some tools for our agent
@tool
def get_weather(location: str, unit: str = 'celsius') -> str:
    """Get the current weather in a given location.
    
    Args:
        location: The city and state, e.g., "San Francisco, CA"
        unit: The unit of temperature (celsius or fahrenheit)
    """
    # In a real application, this would call a weather API
    # For this example, we'll return a mock response
    return f"The weather in {location} is 22°{unit[0].upper()}, sunny with a light breeze."

@tool
def get_forecast(location: str, days: int = 1) -> str:
    """Get the weather forecast for a location.
    
    Args:
        location: The city and state, e.g., "New York, NY"
        days: Number of days to forecast (1-7)
    """
    return f"""{days}-day forecast for {location}:
    - Day 1: Sunny, 22°C
    - Day 2: Partly cloudy, 20°C
    - Day 3: Light rain, 18°C
    """

async def main():
    # Initialize the LLM with your API key
    llm = OpenAIModel(
        api_key="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",
        model="gpt-3.5-turbo"
    )
    
    # Create an agent with our tools and memory
    agent = Agent(
        llm=llm,
        tools=[get_weather, get_forecast],
        memory=InMemoryMemory(),
        debug=True  # Enable debug output
    )
    
    # Example conversation
    queries = [
        "What's the weather like in Tokyo?",
        "What about the forecast for the next 3 days?",
        "Convert the temperature to fahrenheit"
    ]
    
    for query in queries:
        print(f"\nUser: {query}")
        response = await agent.run(query)
        print(f"Agent: {response}")
    
    # Show the conversation history
    print("\n--- Conversation History ---")
    for msg in agent.memory.get_messages():
        print(f"{msg['role'].capitalize()}: {msg['content']}")
    
    # Show the execution trace
    print("\n--- Execution Trace ---")
    trace = agent.explain()
    for i, step in enumerate(trace['steps'], 1):
        print(f"{i}. {step['type']}:")
        print(f"   {step.get('data', {})}")

if __name__ == "__main__":
    asyncio.run(main())
