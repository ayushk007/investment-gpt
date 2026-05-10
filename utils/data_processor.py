"""
Data processing utilities
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataProcessor:
    """Utility class for data processing"""
    
    @staticmethod
    def clean_stock_data(data: pd.DataFrame) -> pd.DataFrame:
        """
        Clean stock data
        
        Args:
            data: Raw stock data DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        data = data.copy()
        
        # Remove rows with NaN values
        data = data.dropna()
        
        # Remove duplicates
        data = data[~data.index.duplicated(keep='first')]
        
        # Sort by date
        data = data.sort_index()
        
        return data
    
    @staticmethod
    def calculate_returns(data: pd.DataFrame, periods: List[int] = [1, 5, 20, 60]) -> pd.DataFrame:
        """
        Calculate returns for specified periods
        
        Args:
            data: Stock data DataFrame with 'Close' column
            periods: List of periods for return calculation
            
        Returns:
            DataFrame with calculated returns
        """
        returns = pd.DataFrame(index=data.index)
        
        for period in periods:
            returns[f'return_{period}d'] = data['Close'].pct_change(period) * 100
        
        return returns
    
    @staticmethod
    def normalize_data(data: pd.Series) -> pd.Series:
        """
        Normalize data to 0-100 scale
        
        Args:
            data: Data series to normalize
            
        Returns:
            Normalized series
        """
        min_val = data.min()
        max_val = data.max()
        
        if max_val == min_val:
            return pd.Series([50] * len(data), index=data.index)
        
        return ((data - min_val) / (max_val - min_val)) * 100
    
    @staticmethod
    def aggregate_data(data: Dict) -> Dict:
        """
        Aggregate multiple data sources
        
        Args:
            data: Dictionary of data from different sources
            
        Returns:
            Aggregated data dictionary
        """
        aggregated = {
            "sources": len(data),
            "timestamps": [v.get("timestamp") for v in data.values() if v.get("timestamp")],
            "data": data
        }
        
        return aggregated
    
    @staticmethod
    def format_currency(value: float, currency: str = "INR") -> str:
        """Format value as currency"""
        if currency == "INR":
            return f"₹{value:,.2f}"
        elif currency == "USD":
            return f"${value:,.2f}"
        else:
            return f"{value:,.2f}"
    
    @staticmethod
    def format_percentage(value: float) -> str:
        """Format value as percentage"""
        sign = "+" if value >= 0 else ""
        return f"{sign}{value:.2f}%"
    
    @staticmethod
    def create_summary_stats(data: pd.DataFrame) -> Dict:
        """
        Create summary statistics from stock data
        
        Args:
            data: Stock data DataFrame
            
        Returns:
            Dictionary of summary statistics
        """
        return {
            "mean": data['Close'].mean(),
            "median": data['Close'].median(),
            "std": data['Close'].std(),
            "min": data['Close'].min(),
            "max": data['Close'].max(),
            "range": data['Close'].max() - data['Close'].min(),
            "total_volume": data['Volume'].sum(),
            "avg_volume": data['Volume'].mean()
        }
