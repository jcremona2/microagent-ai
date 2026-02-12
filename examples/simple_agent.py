"""
Simple example demonstrating basic usage of MicroAgent.
"""
import asyncio
from microagent import Agent, tool
from microagent.llm import OpenAIModel
from microagent.memory import InMemoryMemory

# Define a simple calculator tool
@tool
def calculate(expression: str) -> float:
    """Evaluate a mathematical expression.
    
    Args:
        expression: A mathematical expression to evaluate, e.g., "2 + 2" or "10 * (5 - 3)"
        
    Returns:
        The result of the calculation
    """
    # WARNING: Using eval can be dangerous with untrusted input
    # In a production environment, use a proper expression evaluator
    try:
        return float(eval(expression))  # Simple evaluator for demonstration
    except Exception as e:
        raise ValueError(f"Could not evaluate expression: {e}")

async def main():
    # Initialize the LLM with your API key
    llm = OpenAIModel(
        api_key="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",
        model="gpt-3.5-turbo"
    )
    
    # Create an agent with our calculator tool
    agent = Agent(
        llm=llm,
        tools=[calculate],
        memory=InMemoryMemory(),
        debug=True  # Enable debug output
    )
    
    # Example calculations
    queries = [
        "What is 2 + 2?",
        "Multiply that by 5",
        "Now add 10 to the result"
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
