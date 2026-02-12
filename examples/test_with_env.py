"""
Test script that loads API key from .env file
"""
from dotenv import load_dotenv
import os
from openai import OpenAI

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API key from environment variables
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in .env file")
        print("Please create a .env file with your API key:")
        print("OPENAI_API_KEY=your-api-key-here")
        return
    
    print("🔍 Testing OpenAI API connection...")
    
    try:
        # Initialize the client
        client = OpenAI(api_key=api_key)
        
        # Make a test API call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Just say 'API test successful' if you can read this."}
            ],
            max_tokens=20
        )
        
        print("✅ Success! API is working correctly.")
        print("Response:", response.choices[0].message.content)
        
    except Exception as e:
        print("❌ Error testing API:")
        print(str(e))
        print("\nTroubleshooting:")
        print("1. Make sure your API key is valid")
        print("2. Check your internet connection")
        print("3. Verify the .env file is in the correct location")
        print("4. Ensure the OPENAI_API_KEY is properly set in the .env file")

if __name__ == "__main__":
    main()
