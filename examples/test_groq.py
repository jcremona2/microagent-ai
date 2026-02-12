"""
Test script for Groq API
"""

import asyncio
import os

from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Get API key from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


async def test_groq_connection():
    """Test the Groq API connection"""
    if not GROQ_API_KEY:
        print("❌ Error: GROQ_API_KEY not found in environment variables")
        print("Please add it to your .env file:")
        print("GROQ_API_KEY=your-api-key-here")
        return False

    print("🔍 Testing Groq API connection...")

    try:
        # Initialize the Groq client
        client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")

        # List available models
        print("\n🔍 Available models:")
        models = ["llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768"]
        for i, model in enumerate(models, 1):
            print(f"{i}. {model}")

        # Try each model until one works
        for model in models:
            try:
                print(f"\n🔍 Trying model: {model}")
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {
                            "role": "user",
                            "content": "Just say 'Groq test successful with {model}' if you can read this.",
                        },
                    ],
                    max_tokens=30,
                    temperature=0.1,
                )
                result = response.choices[0].message.content
                print(f"✅ Success with {model}!")
                return True, result

            except Exception as e:
                print(f"❌ Error with {model}: {str(e)[:200]}...")
                continue

        raise Exception(
            "All models failed. Please check the Groq documentation for available models."
        )

        result = response.choices[0].message.content
        print("✅ Groq API connection successful!")
        print(f"Response: {result}")
        return True

    except Exception as e:
        print("❌ Error connecting to Groq API:")
        print(str(e))
        print("\nTroubleshooting:")
        print("1. Check your GROQ_API_KEY in the .env file")
        print("2. Make sure you have internet connectivity")
        print("3. Verify your Groq account has available credits")
        return False


if __name__ == "__main__":
    asyncio.run(test_groq_connection())
