"""
Stock Value Scraper Agent
Collects latest and historical stock market price data from NSE
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging
import config

# Configure logging based on config
log_level = logging.DEBUG if config.DEBUG_MODE else logging.INFO
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)

if config.DEBUG_MODE:
    logger.debug("StockScraperAgent initialized in DEBUG mode")


class StockScraperAgent:
    """Agent responsible for scraping stock price data"""
    
    def __init__(self):
        self.data = None
        self.ticker = None
    
    @staticmethod
    def _normalize_yfinance_data(data: pd.DataFrame, ticker_symbol: str) -> pd.DataFrame:
        if isinstance(data.columns, pd.MultiIndex):
            ticker_levels = [
                level
                for level in range(data.columns.nlevels)
                if ticker_symbol in data.columns.get_level_values(level)
            ]
            
            if ticker_levels:
                data = data.xs(ticker_symbol, axis=1, level=ticker_levels[0])
            else:
                data = data.droplevel(-1, axis=1)
        
        return data
        
    def fetch_stock_data(self, ticker_symbol: str, period: str = "200d") -> dict:
        """
        Fetch historical stock data for NSE stocks
        
        Args:
            ticker_symbol: NSE ticker symbol (e.g., 'RELIANCE.NS')
            period: Historical data period (default 200 days)
            
        Returns:
            Dictionary containing stock data and metadata
        """
        try:
            if config.DEBUG_MODE:
                logger.debug(f"fetch_stock_data called with ticker={ticker_symbol}, period={period}")
            
            # Ensure ticker has .NS suffix for NSE
            if not ticker_symbol.endswith('.NS'):
                ticker_symbol = f"{ticker_symbol}.NS"
                if config.DEBUG_MODE:
                    logger.debug(f"Formatted ticker to: {ticker_symbol}")
            
            self.ticker = ticker_symbol
            
            # Fetch historical data
            stock_data = yf.download(ticker_symbol, period=period, progress=False)
            stock_data = self._normalize_yfinance_data(stock_data, ticker_symbol)
            
            if stock_data.empty:
                logger.error(f"No data found for {ticker_symbol}")
                return {
                    "success": False,
                    "error": f"No data found for {ticker_symbol}",
                    "ticker": ticker_symbol
                }
            
            # Fetch current info
            ticker_obj = yf.Ticker(ticker_symbol)
            info = ticker_obj.info
            
            # Get latest price
            latest_price = stock_data['Close'].iloc[-1]
            previous_close = stock_data['Close'].iloc[-2] if len(stock_data) > 1 else latest_price
            
            price_change = latest_price - previous_close
            price_change_percent = (price_change / previous_close * 100) if previous_close != 0 else 0
            
            # Calculate volume data
            avg_volume = stock_data['Volume'].tail(20).mean()
            
            result = {
                "success": True,
                "ticker": ticker_symbol,
                "company_name": info.get('longName', ticker_symbol),
                "latest_price": float(latest_price),
                "previous_close": float(previous_close),
                "price_change": float(price_change),
                "price_change_percent": float(price_change_percent),
                "market_cap": info.get('marketCap', 'N/A'),
                "pe_ratio": info.get('trailingPE', 'N/A'),
                "pb_ratio": info.get('priceToBook', 'N/A'),
                "dividend_yield": info.get('dividendYield', 0),
                "52_week_high": info.get('fiftyTwoWeekHigh', 'N/A'),
                "52_week_low": info.get('fiftyTwoWeekLow', 'N/A'),
                "avg_volume": float(avg_volume),
                "historical_data": stock_data.copy(),
                "data_points": len(stock_data),
                "timestamp": datetime.now().isoformat()
            }
            
            self.data = result
            logger.info(f"Successfully fetched data for {ticker_symbol}")
            return result
            
        except Exception as e:
            logger.error(f"Error fetching stock data: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "ticker": ticker_symbol
            }
    
    def get_intraday_data(self, ticker_symbol: str) -> dict:
        """
        Fetch intraday data for NSE stocks
        """
        try:
            if not ticker_symbol.endswith('.NS'):
                ticker_symbol = f"{ticker_symbol}.NS"
            
            # Fetch 1 day of data with 5-minute intervals
            intraday_data = yf.download(ticker_symbol, period="1d", interval="5m", progress=False)
            intraday_data = self._normalize_yfinance_data(intraday_data, ticker_symbol)
            
            return {
                "success": True,
                "ticker": ticker_symbol,
                "intraday_data": intraday_data,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching intraday data: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "ticker": ticker_symbol
            }
    
    def get_summary(self) -> dict:
        """Return summary of scraped data"""
        if not self.data:
            return {"status": "No data scraped yet"}
        
        return {
            "status": "Data successfully scraped",
            "ticker": self.data["ticker"],
            "company_name": self.data.get("company_name", "N/A"),
            "latest_price": self.data["latest_price"],
            "price_change_percent": self.data["price_change_percent"],
            "data_points": self.data["data_points"],
            "timestamp": self.data["timestamp"]
        }
