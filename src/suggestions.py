"""
Visualization Suggestions Module - Generates smart chart recommendations.
Analyzes data profile to suggest relevant visualizations.
"""

from typing import List, Dict
import random


def analyze_column_types(profile: Dict) -> Dict:
    """
    Analyze columns to categorize them by type.
    
    Args:
        profile: Dataset profile with columns and dtypes
        
    Returns:
        Dict with categorized columns
    """
    numeric_cols = []
    categorical_cols = []
    date_cols = []
    
    columns = profile.get('columns', [])
    dtypes = profile.get('dtypes', {})
    
    for col in columns:
        dtype = dtypes.get(col, 'object')
        
        if 'int' in str(dtype).lower() or 'float' in str(dtype).lower():
            numeric_cols.append(col)
        elif 'date' in str(dtype).lower() or 'time' in str(dtype).lower():
            date_cols.append(col)
        elif 'date' in col.lower() or 'time' in col.lower():
            date_cols.append(col)
        else:
            categorical_cols.append(col)
    
    return {
        'numeric': numeric_cols,
        'categorical': categorical_cols,
        'date': date_cols
    }


def generate_suggestions(profile: Dict) -> List[Dict]:
    """
    Generate 3 precise visualization suggestions based on data profile.
    Creates exact queries that will generate specific chart types.
    
    Args:
        profile: Dataset profile containing columns, dtypes, row_count
        
    Returns:
        List of 3 suggestion dictionaries with precise queries
    """
    col_types = analyze_column_types(profile)
    suggestions = []
    
    numeric = col_types['numeric']
    categorical = col_types['categorical']
    date = col_types['date']
    
    # Strategy 1: Time series line chart (most precise for trends)
    if date and numeric:
        date_col = date[0]
        num_col = numeric[0]
        suggestions.append({
            'query': f"Create a line chart showing {num_col} over {date_col}",
            'description': f"Time series trend of {num_col}",
            'icon': '📈',
            'type': 'trend'
        })
    
    # Strategy 2: Bar chart for categorical comparison
    if categorical and numeric and len(suggestions) < 3:
        cat_col = categorical[0]
        num_col = numeric[0]
        suggestions.append({
            'query': f"Create a bar chart of {num_col} grouped by {cat_col}",
            'description': f"Compare {num_col} across {cat_col}",
            'icon': '📊',
            'type': 'comparison'
        })
    
    # Strategy 3: Histogram for distribution
    if numeric and len(suggestions) < 3:
        num_col = numeric[0]
        suggestions.append({
            'query': f"Create a histogram of {num_col} distribution",
            'description': f"Distribution analysis of {num_col}",
            'icon': '📊',
            'type': 'distribution'
        })
    
    # Strategy 4: Scatter plot for correlation
    if len(numeric) >= 2 and len(suggestions) < 3:
        suggestions.append({
            'query': f"Create a scatter plot of {numeric[0]} vs {numeric[1]}",
            'description': f"Correlation between {numeric[0]} and {numeric[1]}",
            'icon': '🔗',
            'type': 'correlation'
        })
    
    # Strategy 5: Horizontal bar for top N ranking
    if categorical and numeric and len(suggestions) < 3:
        cat_col = categorical[0]
        num_col = numeric[0]
        suggestions.append({
            'query': f"Create a horizontal bar chart showing top 10 {cat_col} by {num_col}",
            'description': f"Top 10 {cat_col} ranked by {num_col}",
            'icon': '🏆',
            'type': 'ranking'
        })
    
    # Strategy 6: Pie chart for categorical breakdown
    if categorical and len(suggestions) < 3:
        cat_col = categorical[0]
        suggestions.append({
            'query': f"Create a pie chart showing the distribution of {cat_col}",
            'description': f"Percentage breakdown of {cat_col}",
            'icon': '🥧',
            'type': 'breakdown'
        })
    
    # Strategy 7: Box plot for statistical distribution
    if numeric and len(suggestions) < 3:
        num_col = numeric[0]
        suggestions.append({
            'query': f"Create a box plot of {num_col} to show statistical distribution",
            'description': f"Statistical summary of {num_col}",
            'icon': '📦',
            'type': 'boxplot'
        })
    
    # Strategy 8: Grouped bar chart for multi-category comparison
    if len(categorical) >= 2 and numeric and len(suggestions) < 3:
        suggestions.append({
            'query': f"Create a grouped bar chart of {numeric[0]} by {categorical[0]} and {categorical[1]}",
            'description': f"Multi-category comparison",
            'icon': '📊',
            'type': 'grouped'
        })
    
    # Strategy 9: Stacked area chart for time series composition
    if date and len(numeric) >= 2 and len(suggestions) < 3:
        date_col = date[0]
        suggestions.append({
            'query': f"Create a stacked area chart of {numeric[0]} and {numeric[1]} over {date_col}",
            'description': f"Composition over time",
            'icon': '📈',
            'type': 'stacked'
        })
    
    # Strategy 10: Heatmap for correlation matrix
    if len(numeric) >= 3 and len(suggestions) < 3:
        suggestions.append({
            'query': f"Create a heatmap showing correlation between all numeric columns",
            'description': "Correlation matrix visualization",
            'icon': '🔥',
            'type': 'heatmap'
        })
    
    # Fallback: Simple visualization request
    if len(suggestions) < 3:
        all_cols = profile.get('columns', [])
        if len(all_cols) >= 2:
            suggestions.append({
                'query': f"Create a chart visualizing {all_cols[0]} and {all_cols[1]}",
                'description': "Basic data visualization",
                'icon': '📊',
                'type': 'basic'
            })
    
    # Final fallback
    while len(suggestions) < 3:
        if numeric:
            suggestions.append({
                'query': f"Create a line plot of {numeric[0]}",
                'description': f"Simple plot of {numeric[0]}",
                'icon': '📈',
                'type': 'simple'
            })
        else:
            suggestions.append({
                'query': "Show me the first few rows of data",
                'description': "Data preview",
                'icon': '👁️',
                'type': 'preview'
            })
    
    return suggestions[:3]


def get_suggestion_examples() -> List[Dict]:
    """
    Get example suggestions for demo purposes.
    
    Returns:
        List of example suggestions
    """
    return [
        {
            'query': "Show sales trends over time",
            'description': "Time series analysis",
            'icon': '📈',
            'type': 'trend'
        },
        {
            'query': "Compare revenue by region",
            'description': "Regional comparison",
            'icon': '📊',
            'type': 'comparison'
        },
        {
            'query': "Show top 10 products by sales",
            'description': "Top performers",
            'icon': '🏆',
            'type': 'ranking'
        }
    ]
