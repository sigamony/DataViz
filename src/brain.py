import json
from src.llm_client import call_llm
from typing import List, Dict, Optional

def format_conversation_context(messages: List[Dict]) -> str:
    """
    Format conversation history for LLM context.
    
    Args:
        messages: List of message dictionaries with role and content
        
    Returns:
        Formatted string of conversation history
    """
    if not messages:
        return ""
    
    context = "\n\nPrevious Conversation:\n"
    for msg in messages:
        role = "User" if msg['role'] == 'user' else "Assistant"
        context += f"{role}: {msg['content']}\n"
    
    return context

def detect_intent(profile, user_query, conversation_history: Optional[List[Dict]] = None, provider="gemini", model="gemini-2.5-flash-lite"):
    """
    Analyzes the user query and dataset profile to determine intent.
    Now includes conversation history for context.
    """
    
    # Add conversation context if available
    context = format_conversation_context(conversation_history) if conversation_history else ""
    
    system_prompt = f"""
You are a smart data analyst assistant. 
Your job is to analyze a User Query in the context of a Dataset Profile and determine the user's intent.

Dataset Profile:
{json.dumps(profile, default=str)}
{context}

User Query:
"{user_query}"

Task:
Determine if the user wants to visualize data from this dataset.
1. **Is Related**: Does the query refer to the data columns available? Or is it a generic greeting/unrelated question like "How are you?" or "Write me a poem"?
2. **Is Visualization**: Does the user imply seeing a chart, plot, diagram, or trend?
3. **Needs Clarification**: Is the query too vague to produce ANY meaningful chart (e.g. "Show me data" without saying what)? 
   - Note: If the query is "Show me trends" and there are date/numeric columns, you should try your best (Needs Clarification = False). Only return True if it is impossible to infer a reasonable default.
   - Consider previous conversation context when determining if clarification is needed.

Output strictly valid JSON in the following format:
{{
    "is_related": boolean,
    "is_visualization": boolean,
    "needs_clarification": boolean,
    "clarification_message": "string (only if needs_clarification is true, else null)",
    "rationale": "short explanation"
}}
"""
    try:
        # We generally use the selected model for consistency, 
        # but if we wanted speed we could force a lighter model here.
        # For now, respect user choice.
        response_text = call_llm(system_prompt, provider=provider, model=model)
        # Clean up code blocks if the LLM wraps JSON in markdown
        cleaned_text = response_text.strip().replace("```json", "").replace("```", "")
        return json.loads(cleaned_text)
    except Exception as e:
        # Fallback in case of parsing error
        return {
            "is_related": True, 
            "is_visualization": True,
            "needs_clarification": False,
            "rationale": f"Parsing failed: {str(e)}" 
        }

def generate_code_prompt(profile, user_query, conversation_history: Optional[List[Dict]] = None):
    """Generate code prompt with conversation context."""
    context = format_conversation_context(conversation_history) if conversation_history else ""
    
    return f"""
You are a Python Data Visualization Expert.
You have access to a pandas DataFrame named `df`.

Dataset Metadata:
{json.dumps(profile, default=str)}
{context}

User Request:
"{user_query}"

Goal:
Write Python code to create the most appropriate visualization for the user's request.
Consider the conversation history to understand context and references (e.g., "make it horizontal" refers to previous chart).

Rules:
1. **Use ONLY pandas and matplotlib.pyplot**.
2. **Assume `df` is already loaded.** Do NOT load the file again.
3. **Handle Data Types**: Check the dtypes in metadata. If a column is object/string but represents a date, convert it using `pd.to_datetime`. If it's numeric strings, convert using `pd.to_numeric`.
4. **Best Effort**: If the user is vague (e.g. "show trends"), pick the most logical columns (e.g. a date column and a numeric column) and plot them.
5. **No Explanations**: Output ONLY the executable Python code.
6. **One Plot**: Create exactly one figure.
7. **Formatting**: Title the chart, label axes, and use a nice style (e.g. `plt.style.use('ggplot')` or similar if available, or just standard).
8. **Final Step**: The code MUST end with a plotting command that renders to the current figure (like `plt.plot`, `df.plot`, etc). DO NOT use `plt.show()` as this is a headless environment, just creating the plot is enough.

Code Format:
```python
# Code here
```
"""

def generate_visualization(profile, user_query, conversation_history: Optional[List[Dict]] = None, intent_data=None, provider="gemini", model="gemini-2.5-flash-lite"):
    """
    Orchestrates the brain logic: Intent -> Code Gen.
    Now supports conversation history for context-aware responses.
    """
    
    # 1. Detect Intent
    if not intent_data:
        intent_data = detect_intent(profile, user_query, conversation_history, provider=provider, model=model)
        
    if not intent_data.get("is_related", False):
        return {
            "status": "skipped",
            "message": "I can only help with visualizing or understanding this dataset. Please ask a question about the data."
        }
    
    # Check if visualization is requested
    if not intent_data.get("is_visualization", False):
        # Handle general Q&A about data with conversation context
        context = format_conversation_context(conversation_history) if conversation_history else ""
        qa_prompt = f"""
You are a Data Analyst.
Dataset Profile: {json.dumps(profile, default=str)}
{context}
User Question: "{user_query}"
Answer the user's question based on the metadata and conversation history. Keep it concise.
"""
        try:
            answer = call_llm(qa_prompt, provider=provider, model=model)
            return {
                "status": "success",
                "message": answer,
                "type": "text_response" 
            }
        except Exception as e:
             return {
                "status": "error",
                "message": f"Failed to answer question: {str(e)}"
            }
        
    if intent_data.get("needs_clarification", False):
        return {
            "status": "skipped", 
            "message": intent_data.get("clarification_message", "Could you contain more details?")
        }

    # 2. Generate Code (Only if visualization is needed)
    prompt = generate_code_prompt(profile, user_query, conversation_history)
    try:
        raw_response = call_llm(prompt, provider=provider, model=model)
        # Extract code from markdown blocks
        code = raw_response
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0].strip()
        elif "```" in code:
            code = code.split("```")[1].split("```")[0].strip()
            
        return {
            "status": "success",
            "code": code,
            "message": "Code generated.",
            "type": "chart_response"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Code generation failed: {str(e)}"
        }
