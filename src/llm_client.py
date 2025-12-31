from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

# Configure the API key
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def get_client():
    """
    Returns the configured GenAI Client.
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    
    # Initialize the client
    client = genai.Client(api_key=GEMINI_API_KEY)
    return client

def call_llm(prompt):
    """
    Calls the Gemini LLM with the given prompt using the new Google GenAI SDK.
    
    Args:
        prompt (str): The prompt text.
        
    Returns:
        str: The text response from the LLM.
    """
    try:
        client = get_client()
        
        # Using gemini-1.5-flash which is a balanced model
        # The new SDK syntax: client.models.generate_content(...)
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )
        
        # If the response structure is complex, we might need to drill down,
        # but usually .text property is available on the result or response part.
        # Based on new SDK, it returns a GenerateContentResponse
        
        return response.text
        
    except Exception as e:
        raise Exception(f"LLM Call failed: {str(e)}")
