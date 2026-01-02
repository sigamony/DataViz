"""
Demo Data Module - Provides sample datasets for demonstration purposes.
This module creates realistic business datasets for sales, marketing, and finance.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

DEMO_DIR = "data/demo_datasets"

def ensure_demo_dir():
    """Ensure demo datasets directory exists."""
    os.makedirs(DEMO_DIR, exist_ok=True)

def generate_sales_data():
    """Generate realistic sales dataset."""
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='D')
    
    products = ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Headphones']
    regions = ['North', 'South', 'East', 'West']
    
    data = []
    for date in dates:
        for _ in range(np.random.randint(3, 8)):
            data.append({
                'Date': date.strftime('%Y-%m-%d'),
                'Product': np.random.choice(products),
                'Region': np.random.choice(regions),
                'Quantity': np.random.randint(1, 20),
                'Unit_Price': np.random.randint(20, 1500),
                'Discount': np.random.choice([0, 5, 10, 15, 20]),
            })
    
    df = pd.DataFrame(data)
    df['Total_Sales'] = df['Quantity'] * df['Unit_Price'] * (1 - df['Discount']/100)
    return df

def generate_marketing_data():
    """Generate realistic marketing campaign dataset."""
    np.random.seed(43)
    
    campaigns = ['Email_Campaign', 'Social_Media', 'Google_Ads', 'Content_Marketing', 'Influencer']
    channels = ['Facebook', 'Instagram', 'LinkedIn', 'Twitter', 'Email', 'Google']
    
    data = []
    for i in range(500):
        impressions = np.random.randint(1000, 100000)
        clicks = int(impressions * np.random.uniform(0.01, 0.05))
        conversions = int(clicks * np.random.uniform(0.02, 0.15))
        
        data.append({
            'Campaign_ID': f'CMP_{i+1:04d}',
            'Campaign_Type': np.random.choice(campaigns),
            'Channel': np.random.choice(channels),
            'Budget': np.random.randint(500, 10000),
            'Impressions': impressions,
            'Clicks': clicks,
            'Conversions': conversions,
            'Cost_Per_Click': round(np.random.uniform(0.5, 5.0), 2),
            'Date': (datetime(2024, 1, 1) + timedelta(days=np.random.randint(0, 365))).strftime('%Y-%m-%d')
        })
    
    df = pd.DataFrame(data)
    df['CTR'] = (df['Clicks'] / df['Impressions'] * 100).round(2)
    df['Conversion_Rate'] = (df['Conversions'] / df['Clicks'] * 100).round(2)
    df['ROI'] = ((df['Conversions'] * 50 - df['Budget']) / df['Budget'] * 100).round(2)
    return df

def generate_finance_data():
    """Generate realistic financial dataset."""
    np.random.seed(44)
    
    months = pd.date_range(start='2020-01-01', end='2024-12-31', freq='M')
    departments = ['Sales', 'Marketing', 'Operations', 'IT', 'HR', 'Finance']
    
    data = []
    for month in months:
        for dept in departments:
            revenue = np.random.randint(50000, 500000)
            expenses = int(revenue * np.random.uniform(0.6, 0.9))
            
            data.append({
                'Month': month.strftime('%Y-%m'),
                'Department': dept,
                'Revenue': revenue,
                'Expenses': expenses,
                'Profit': revenue - expenses,
                'Employee_Count': np.random.randint(10, 100),
                'Budget_Utilization': round(np.random.uniform(70, 105), 1)
            })
    
    return pd.DataFrame(data)

def get_demo_datasets():
    """
    Returns metadata about available demo datasets.
    
    Returns:
        list: List of dictionaries containing demo dataset information
    """
    return [
        {
            'id': 'demo_sales',
            'name': 'E-Commerce Sales Data',
            'description': 'Daily sales transactions across products and regions (2023-2024)',
            'category': 'Sales',
            'rows': '~4000',
            'columns': ['Date', 'Product', 'Region', 'Quantity', 'Unit_Price', 'Discount', 'Total_Sales'],
            'use_cases': ['Revenue analysis', 'Product performance', 'Regional trends']
        },
        {
            'id': 'demo_marketing',
            'name': 'Marketing Campaign Analytics',
            'description': 'Multi-channel marketing campaign performance metrics',
            'category': 'Marketing',
            'rows': '500',
            'columns': ['Campaign_ID', 'Campaign_Type', 'Channel', 'Budget', 'Impressions', 'Clicks', 'Conversions', 'CTR', 'ROI'],
            'use_cases': ['Campaign ROI', 'Channel comparison', 'Conversion optimization']
        },
        {
            'id': 'demo_finance',
            'name': 'Financial Performance Dashboard',
            'description': 'Monthly financial metrics by department (2020-2024)',
            'category': 'Finance',
            'rows': '360',
            'columns': ['Month', 'Department', 'Revenue', 'Expenses', 'Profit', 'Employee_Count', 'Budget_Utilization'],
            'use_cases': ['Profit trends', 'Department comparison', 'Budget analysis']
        }
    ]

def initialize_demo_datasets():
    """
    Generate and save all demo datasets to disk.
    Should be called on application startup.
    """
    ensure_demo_dir()
    
    datasets = {
        'demo_sales.csv': generate_sales_data(),
        'demo_marketing.csv': generate_marketing_data(),
        'demo_finance.csv': generate_finance_data()
    }
    
    for filename, df in datasets.items():
        filepath = os.path.join(DEMO_DIR, filename)
        df.to_csv(filepath, index=False)
        print(f"✓ Generated: {filename} ({len(df)} rows)")
    
    return True

def get_demo_dataset_path(demo_id: str) -> str:
    """
    Get the file path for a demo dataset.
    
    Args:
        demo_id: ID of the demo dataset (e.g., 'demo_sales')
    
    Returns:
        str: Full path to the demo dataset file
    """
    filename = f"{demo_id}.csv"
    return os.path.join(DEMO_DIR, filename)
