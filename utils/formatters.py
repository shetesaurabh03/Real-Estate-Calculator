"""Formatting utilities for currency, percentages, and numbers"""

import pandas as pd

def format_currency(value, decimals=2):
    """Format a number as currency"""
    if value is None or pd.isna(value):
        return "$0.00"
    return f"${value:,.{decimals}f}"

def format_percentage(value, decimals=2):
    """Format a number as percentage"""
    if value is None or pd.isna(value):
        return "0.00%"
    return f"{value:.{decimals}f}%"

def format_number(value, decimals=0):
    """Format a number with commas"""
    if value is None or pd.isna(value):
        return "0"
    return f"{value:,.{decimals}f}"




