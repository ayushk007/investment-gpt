"""
Configuration and constants for the Stock Analysis App
"""

# Debug Configuration
DEBUG_MODE = True  # Set to False for production
DEBUG_VERBOSE = True  # Verbose debug output
DEBUG_LOG_FILE = "debug.log"  # Log file path
LOG_LEVEL = "DEBUG"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# API Configuration
FINNHUB_API_KEY = "YOUR_FINNHUB_API_KEY"  # Get from https://finnhub.io/
NEWSAPI_KEY = "YOUR_NEWSAPI_KEY"  # Get from https://newsapi.org/
ANTHROPIC_API_KEY = None  # Will be set from environment
GOOGLE_API_KEY = "AIzaSyDNYu46YybHHPZGTAVXeXx64lJUgxJwAjM"  # Will be set from environment for Gemini

# NSE Stock Market Configuration
NSE_BASE_URL = "https://www.nseindia.com"
NSE_MARKET_OPEN_TIME = "09:15"
NSE_MARKET_CLOSE_TIME = "15:30"

# Technical Analysis Parameters
RSI_PERIOD = 14
MACD_FAST_PERIOD = 12
MACD_SLOW_PERIOD = 26
MACD_SIGNAL_PERIOD = 9
SMA_PERIODS = [20, 50, 200]
BOLLINGER_BANDS_PERIOD = 20

# Fundamental Analysis Thresholds
PE_RATIO_THRESHOLD_LOW = 15
PE_RATIO_THRESHOLD_HIGH = 25
PB_RATIO_THRESHOLD = 3
DEBT_TO_EQUITY_THRESHOLD = 1.5
ROE_THRESHOLD = 15
ROA_THRESHOLD = 5

# Data Collection
DAYS_OF_HISTORICAL_DATA = 200
NEWS_ARTICLES_LIMIT = 20

# UI Configuration
APP_TITLE = "NSE Stock Analysis - Fundamental & Technical Analyzer"
APP_ICON = "📈"

# Recommendation Thresholds
STRONG_BUY_SCORE = 80
BUY_SCORE = 60
HOLD_SCORE = 40
SELL_SCORE = 20
STRONG_SELL_SCORE = 0
