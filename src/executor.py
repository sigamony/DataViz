import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

def execute_chart_code(code, df):
    """
    Executes the given Python code to generate a chart.
    
    Args:
        code (str): The Python code to execute.
        df (pd.DataFrame): The dataframe to work with.
        
    Returns:
        dict: A dictionary containing success status, image (base64) or error message.
    """
    # Create a buffer to save the image
    img_buf = io.BytesIO()
    
    # Context for execution
    # We pass 'plt' locally so the code can usage it.
    # We also inject a 'savefig' wrapper if strictly needed, but standard plt usage is fine
    # if we save the current figure after execution.
    local_env = {
        'df': df,
        'pd': pd,
        'plt': plt
    }
    
    try:
        # Switch to non-interactive backend to avoid GUI windows popping up
        plt.switch_backend('Agg')
        plt.clf() # Clear any existing plots
        
        # Execute the code
        exec(code, {}, local_env)
        
        # Save the current figure to the buffer
        # We assume the code created a plot on the current figure.
        if plt.get_fignums():
             plt.savefig(img_buf, format='png', bbox_inches='tight')
             img_buf.seek(0)
             img_base64 = base64.b64encode(img_buf.read()).decode('utf-8')
             plt.close('all') # Cleanup
             return {
                 "success": True,
                 "image": img_base64
             }
        else:
            return {
                "success": False,
                "error": "No plot was generated. Ensure code calls plt.plot() or similar."
            }
            
    except Exception as e:
        plt.close('all')
        return {
            "success": False,
            "error": f"Execution error: {str(e)}"
        }
