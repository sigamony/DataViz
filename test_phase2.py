from src.dataloader import load_data
from src.executor import execute_chart_code
import os
import base64

def test_execution():
    file_path = os.path.abspath("data/sales.csv")
    print(f"Loading {file_path}...")
    df = load_data(file_path)
    
    # 1. Test Valid Code
    print("\n--- Testing Valid Code ---")
    valid_code = """
import matplotlib.pyplot as plt
# Sum sales by region
grouped = df.groupby('region')['sales'].sum()
grouped.plot(kind='bar', color='skyblue')
plt.title('Total Sales by Region')
plt.xlabel('Region')
plt.ylabel('Sales')
"""
    result = execute_chart_code(valid_code, df)
    
    if result['success']:
        print("✅ Chart generated successfully.")
        # Save to disk to verify visually
        with open("output_test_valid.png", "wb") as f:
            f.write(base64.b64decode(result['image']))
        print(f"✅ Saved to output_test_valid.png (Base64 length: {len(result['image'])})")
    else:
        print(f"❌ Failed: {result.get('error')}")

    # 2. Test Invalid Code (Runtime Error)
    print("\n--- Testing Invalid Code (Runtime Error) ---")
    invalid_code = """
# Typo in column name
df['non_existent_column'].plot()
"""
    result = execute_chart_code(invalid_code, df)
    if not result['success']:
        print(f"✅ Correctly caught error: {result['error']}")
    else:
        print("❌ Unexpected success for invalid code.")

    # 3. Test No Plot Generated
    print("\n--- Testing No Plot Code ---")
    no_plot_code = """
x = 1 + 1
print(x)
"""
    result = execute_chart_code(no_plot_code, df)
    if not result['success'] and "No plot" in result['error']:
        print(f"✅ Correctly identified no plot: {result['error']}")
    else:
        print(f"❌ Unexpected behavior: {result}")

if __name__ == "__main__":
    test_execution()
