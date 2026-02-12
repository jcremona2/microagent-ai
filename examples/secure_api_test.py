"""
Secure API Test for OpenAI
--------------------------
This script demonstrates how to test the OpenAI API securely.
It will prompt for your API key and test the connection.
"""

import os

from openai import OpenAI


def test_openai_connection(api_key: str) -> bool:
    """
    Test the OpenAI API connection with the provided API key.

    Args:
        api_key: Your OpenAI API key

    Returns:
        bool: True if the test was successful, False otherwise
    """
    try:
        # Initialize the client with the provided API key
        client = OpenAI(api_key=api_key)

        # Make a simple API call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": "Just say 'API test successful' if you can read this.",
                },
            ],
            max_tokens=20,
        )

        # Print the response
        print("\n✅ API Test Successful!")
        print("Response:", response.choices[0].message.content)
        return True

    except Exception as e:
        print("\n❌ API Test Failed!")
        print("Error:", str(e))
        return False


def main():
    print("🔒 Secure OpenAI API Test")
    print("=" * 30)

    # Get API key from user input
    api_key = input("\nPlease enter your OpenAI API key: ").strip()

    # Test the connection
    success = test_openai_connection(api_key)

    if success:
        print("\n🎉 Success! Your API key is working correctly.")

        # Show how to use environment variables
        print("\nFor future use, you can set your API key as an environment variable:")
        print("\nIn your terminal:")
        print('  export OPENAI_API_KEY="your-api-key-here"')
        print("\nOr in Python code:")
        print("  import os")
        print('  os.environ["OPENAI_API_KEY"] = "your-api-key-here"')

        print("\nOr use a .env file (recommended):")
        print('  1. Create a file named ".env" in your project root')
        print("  2. Add: OPENAI_API_KEY=your-api-key-here")
        print('  3. Add ".env" to your .gitignore file')
        print("  4. In Python: from dotenv import load_dotenv; load_dotenv()")

    print("\n🔐 Remember to keep your API key secure and never share it publicly!")


if __name__ == "__main__":
    main()
