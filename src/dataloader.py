import pandas as pd
import io
import os

def load_data(file_path):
    """
    Loads a CSV or Excel file into a pandas DataFrame.
    
    Args:
        file_path (str): Absolute path to the file.
        
    Returns:
        pd.DataFrame: The loaded data.
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        elif file_path.endswith(('.xls', '.xlsx')):
            return pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file format. Please use CSV or Excel.")
    except Exception as e:
        raise Exception(f"Error loading file: {str(e)}")

def generate_profile(df):
    """
    Generates a profile of the dataframe for the LLM.
    
    Args:
        df (pd.DataFrame): The dataframe to profile.
        
    Returns:
        dict: A dictionary containing columns, dtypes, sample rows, and summary stats.
    """
    
    # Convert dtypes to string representation
    dtypes = {col: str(dtype) for col, dtype in df.dtypes.items()}
    
    # Get a small sample (top 5 rows)
    # Convert detailed types (like Timestamp) to string for JSON serialization if needed
    sample_rows = df.head(5).to_dict(orient='records')
    
    import math

    def clean_nan(obj):
        """Recursively replace NaN/Infinity with None for JSON serialization."""
        if isinstance(obj, float):
            if math.isnan(obj) or math.isinf(obj):
                return None
            return obj
        elif isinstance(obj, dict):
            return {k: clean_nan(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [clean_nan(v) for v in obj]
        return obj

    try:
        desc = df.describe(include='all')
        numeric_summary = desc.to_dict() 
    except Exception:
        numeric_summary = {}

    profile = {
        "columns": list(df.columns),
        "dtypes": dtypes,
        "row_count": len(df),
        "sample_rows": sample_rows,
        "numeric_summary": numeric_summary
    }
    
    return clean_nan(profile)
