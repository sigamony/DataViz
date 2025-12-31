from google import genai
import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

# Configure API keys
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
HF_TOKEN = os.environ.get("HF_TOKEN")

def get_gemini_client():
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    return genai.Client(api_key=GEMINI_API_KEY)

def get_hf_client():
    if not HF_TOKEN:
        raise ValueError("HF_TOKEN environment variable not set.")
    # Using featherless-ai as requested in the specific example, or let it default if provider not explicitly needed for the generic client init?
    # The example showed: client = InferenceClient(provider="featherless-ai", api_key=...)
    # We will use that exact setup.
    return InferenceClient(provider="featherless-ai", api_key=HF_TOKEN)

def call_llm(prompt, provider="gemini", model="gemini-2.5-flash-lite"):
    """
    Calls the specified LLM provider.
    
    Args:
        prompt (str): The prompt text.
        provider (str): 'gemini' or 'huggingface'.
        model (str): The model ID to use.
        
    Returns:
        str: The text response from the LLM.
    """
    try:
        if provider == "gemini":
            client = get_gemini_client()
            # If user asks for gemini types, map to valid google genai model names if needed
            response = client.models.generate_content(
                model=model,
                contents=prompt
            )
            return response.text

        elif provider == "huggingface":
            client = get_hf_client()
            # The error indicated 'conversational' task is supported.
            # We use chat_completion which maps to the standard chat API.
            response = client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model=model,
                max_tokens=2048, # Note: param is max_tokens in chat API, max_new_tokens in text_generation
                temperature=0.1
            )
            return response.choices[0].message.content
            
        else:
            raise ValueError(f"Unknown provider: {provider}")

    except Exception as e:
        raise Exception(f"LLM Call failed ({provider}/{model}): {str(e)}")
