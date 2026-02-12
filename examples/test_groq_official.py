"""
Test script for Groq API using the official Groq client
"""
import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

def test_groq_connection():
    """Test the Groq API connection using the official client"""
    if not GROQ_API_KEY:
        print("❌ Error: GROQ_API_KEY not found in environment variables")
        print("Please add it to your .env file:")
        print("GROQ_API_KEY=your-api-key-here")
        return False
    
    print("🔍 Testing Groq API connection with official client...")
    
    try:
        # Initialize the Groq client
        client = Groq(api_key=GROQ_API_KEY)
        
        # List available models to test
        models_to_try = [
            "openai/gpt-oss-120b",  # From user's example
            "llama3-70b-8192",
            "mixtral-8x7b-32768"
        ]
        
        successful_model = None
        
        for model in models_to_try:
            try:
                print(f"\n🔍 Testing model: {model}")
                # Test with streaming
                print("Testing streaming response...")
                completion = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "user",
                            "content": "Tell me a short joke about artificial intelligence in one sentence."
                        }
                    ],
                    temperature=0.7,
                    max_tokens=100,
                    top_p=1,
                    stream=True,
                    stop=None
                )
                
                print("✅ Streaming response received:")
                for chunk in completion:
                    content = chunk.choices[0].delta.content or ""
                    print(content, end="", flush=True)
                print("\n")
                
                successful_model = model
                break
                
            except Exception as e:
                print(f"❌ Error with model {model}: {str(e)[:200]}")
                continue
        
        if not successful_model:
            raise Exception("All models failed. Please check the Groq documentation for available models.")
            
        # Use the successful model for the non-streaming test
        model = successful_model
        
        print("\n✅ Streaming response received:")
        for chunk in completion:
            content = chunk.choices[0].delta.content or ""
            print(content, end="", flush=True)
        
        # Test with non-streaming using the working model
        print(f"\n🔍 Testing non-streaming response with model: {model}")
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": "What is the capital of France?"
                }
            ],
            temperature=0.7,
            max_tokens=50,
            top_p=1,
            stream=False
        )
        
        print("\n✅ Non-streaming response:")
        print(completion.choices[0].message.content)
        
        return True
        
    except Exception as e:
        print("\n❌ Error connecting to Groq API:")
        print(str(e))
        print("\nTroubleshooting:")
        print("1. Check your GROQ_API_KEY in the .env file")
        print("2. Make sure you have internet connectivity")
        print("3. Verify your Groq account has available credits")
        print("4. Check the Groq status page: https://status.groq.com/")
        return False

if __name__ == "__main__":
    test_groq_connection()
