#!/usr/bin/env python3
"""
Example usage of the microagent framework.

This script demonstrates how to create and use the microagent framework
with a simple calculator tool.
"""
import os
from typing import Optional

from microagent import Agent, OpenAIModel, tool

# Define some tools
@tool
def calculator(expression: str) -> float:
    """Evaluate a mathematical expression.
    
    Args:
        expression: A mathematical expression to evaluate (e.g., "2 + 2 * 3")
        
    Returns:
        The result of the evaluation as a float
    """
    return float(eval(expression))

@tool
def get_weather(city: str, country: Optional[str] = None) -> str:
    """Get the current weather for a city.
    
    Args:
        city: The city to get weather for
        country: Optional country name
        
    Returns:
        A weather description
    """
    location = f"{city}, {country}" if country else city
    return f"The weather in {location} is sunny and 25°C"

def main():
    # Get OpenAI API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        return
    
    # Create an LLM instance
    llm = OpenAIModel(
        api_key=api_key,
        model="gpt-3.5-turbo",
        temperature=0.7,
    )
    
    # Create an agent with our tools
    agent = Agent(
        llm=llm,
        tools=[calculator, get_weather],
        debug=True  # Enable debug logging
    )
    
    # Example conversation
    queries = [
        "What is 2 + 2 * 3?",
        "What's the weather like in Paris?",
        "What about in Tokyo, Japan?",
        "Now calculate 15% of 80"
    ]
    
    for query in queries:
        print(f"\nYou: {query}")
        try:
            response = agent.run(query)
            print(f"Agent: {response}")
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
