from src.dataloader import load_data, generate_profile
import os

def test_profiler():
    # Use absolute path for robustness
    file_path = os.path.abspath("data/sales.csv")
    print(f"Testing with file: {file_path}")
    
    try:
        # Load
        df = load_data(file_path)
        print("✅ Data loaded successfully.")
        print(f"Shape: {df.shape}")
        
        # Profile
        profile = generate_profile(df)
        print("✅ Profile generated successfully.")
        
        # Display bits of the profile to verify
        print("\n--- Profile Output ---")
        print(f"Columns: {profile['columns']}")
        print(f"Row Count: {profile['row_count']}")
        print(f"Dtypes: {profile['dtypes']}")
        print("Sample Rows (First 1):")
        print(profile['sample_rows'][0])
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_profiler()
