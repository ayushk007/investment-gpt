# NSE Stock Analysis - Investment GPT

A comprehensive multi-agent AI system for fundamental and technical analysis of NSE (National Stock Exchange of India) stocks with intelligent buy/hold/sell recommendations.

## 🎯 Features

### Multi-Agent Architecture
- **Stock Scraper Agent**: Real-time and historical stock data collection from NSE via Yahoo Finance
- **News Scraper Agent**: Latest market news and sentiment analysis
- **Technical Analysis Agent**: Advanced technical indicators (RSI, MACD, Bollinger Bands, Moving Averages)
- **Fundamental Analysis Agent**: Valuation metrics (P/E, P/B ratios, growth potential)
- **CEO Agent**: Orchestrates all agents and generates comprehensive investment recommendations

### Analysis Capabilities
- **Technical Analysis**
  - RSI (Relative Strength Index)
  - MACD (Moving Average Convergence Divergence)
  - Bollinger Bands
  - Simple & Exponential Moving Averages
  - Support & Resistance Levels
  - Volatility Analysis
  - Volume Trends

- **Fundamental Analysis**
  - P/E Ratio (Price-to-Earnings) Valuation
  - P/B Ratio (Price-to-Book) Analysis
  - Dividend Yield
  - Market Capitalization
  - Growth Potential Assessment
  - Valuation Assessment

- **Market Sentiment**
  - Latest news aggregation
  - Sentiment analysis (positive/neutral/negative)
  - News impact assessment

### Recommendation System
**Two Analysis Modes:**

**Basic Mode (Rule-based)**
- Intelligent scoring algorithm combining technical and fundamental metrics
- Recommendations: STRONG BUY, BUY, HOLD, SELL, STRONG SELL
- Confidence scoring (0-100)
- Risk assessment
- Investment horizon suggestions

**Advanced Mode (LLM-powered with Gemini 2.5 Flash)**
- AI-powered comprehensive analysis
- Short-term (1 month) and long-term (1 year) recommendations
- Detailed reasoning and explainability
- Price target ranges
- News article citations and impact analysis
- Geopolitical and industry context
- Risk assessment with specific factors
- Learned market knowledge integration

### User Interface
- Intuitive Streamlit-based web interface
- Interactive charts (Plotly)
- Real-time data visualization
- Ticker symbol input
- Export functionality (JSON, CSV)

## 📋 Project Structure

```
investment-gpt/
├── app.py                      # Main Streamlit application
├── config.py                   # Configuration and constants
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── setup.sh                   # Setup script
├── run.sh                     # Run script
│
├── agents/                    # AI Agents
│   ├── __init__.py
│   ├── stock_scraper.py       # Stock data collection agent
│   ├── news_scraper.py        # News and sentiment agent
│   ├── analysis.py            # Technical & fundamental analysis
│   └── ceo_agent.py           # Orchestration and reporting
│
├── utils/                     # Utilities
│   ├── __init__.py
│   ├── data_processor.py      # Data processing functions
│   └── api_clients.py         # API client utilities
│
└── data/                      # Data storage (generated)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)
- macOS, Linux, or Windows

### Installation

0. **Install [uv](https://docs.astral.sh/uv/)** (one-time)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

1. **Clone or navigate to the project directory**
```bash
cd /Users/ayush/Documents/my_projects/investment-gpt
```

2. **Run the setup script (wraps `uv sync`)**
```bash
bash setup.sh
```

This will:
- Install all dependencies defined in `pyproject.toml`
- Create/refresh the managed `.venv`
- Create an `.env` file if needed

3. **Start the application**
```bash
bash run.sh
```

The app will open at `http://localhost:8502`

## 📊 Usage

1. **Enter Stock Ticker**: Type the NSE ticker symbol (e.g., RELIANCE, TCS, INFY, HDFC)
2. **Select Analysis Mode**:
   - **Basic**: Fast rule-based analysis (no API key required)
   - **Advanced**: AI-powered analysis with Gemini (requires GOOGLE_API_KEY)
3. **Run Analysis**: Click the "Run Analysis" button
4. **View Results**: 
   - Get AI recommendation (Buy/Hold/Sell)
   - For Advanced mode: See 1-month and 1-year outlooks
   - View technical and fundamental metrics
   - Analyze price charts and volume
   - Read detailed analysis report with reasoning
5. **Export Data**: Download report as JSON or historical data as CSV

## 🛠 Dependency Management (uv)

This project is managed with [uv](https://docs.astral.sh/uv/), which reads dependencies from `pyproject.toml` and maintains an isolated `.venv` for you.

- **Install/refresh dependencies**
  ```bash
  uv sync           # installs everything declared in pyproject.toml
  uv sync --frozen  # installs exactly what's recorded in uv.lock (once generated)
  ```

- **Run ad-hoc commands inside the managed environment**
  ```bash
  uv run streamlit run app.py -- --server.port=8502
  uv run python -m pytest
  ```

- **Add packages**
  ```bash
  uv add <package-name>
  # or for dev-only dependencies
  uv add --dev <package-name>
  ```

- **Regenerate lock file** (optional but recommended for deployments)
  ```bash
  uv lock
  ```

`requirements.txt` is kept for reference, but `pyproject.toml` + `uv` is the source of truth going forward.

### Supported NSE Stocks
- RELIANCE (Reliance Industries)
- TCS (Tata Consultancy Services)
- INFY (Infosys)
- HDFC (HDFC Bank)
- ICICI (ICICI Bank)
- LT (Larsen & Toubro)
- BAJAJ (Bajaj Auto)
- MARUTI (Maruti Suzuki)
- WIPRO (Wipro)
- And many more NSE-listed stocks

## 🔧 Configuration

### API Keys

**For Advanced Mode (Required):**
```env
# Get your free API key from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your_google_api_key_here
```

**For Enhanced Features (Optional):**
```env
FINNHUB_API_KEY=your_key_here
NEWSAPI_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

**Note:** Basic mode works without any API keys. Advanced mode requires a Google Gemini API key.

### Technical Parameters
Edit `config.py` to customize:
- RSI Period and Thresholds
- MACD Parameters
- SMA Periods
- Bollinger Bands Settings
- Fundamental Ratio Thresholds

## 📦 Dependencies

### Core Libraries
- **streamlit**: Web UI framework
- **pandas**: Data manipulation
- **numpy**: Numerical computation
- **plotly**: Interactive charts
- **yfinance**: Stock data API
- **beautifulsoup4**: Web scraping
- **feedparser**: RSS feed parsing
- **ta**: Technical analysis indicators
- **scikit-learn**: Machine learning utilities
- **google-generativeai**: Gemini AI for advanced analysis

See `requirements.txt` for complete list and versions.

## 🤖 Agent Details

### Stock Scraper Agent
- Fetches historical price data (50-200 days)
- Retrieves current price, volume, and market metrics
- Provides 52-week high/low data
- Calculates intraday data (optional)

### News Scraper Agent
- Aggregates latest market news
- Analyzes sentiment (positive/neutral/negative)
- Filters relevant articles
- Tracks news impact on stocks

### Analysis Agent
- Calculates 20+ technical indicators
- Evaluates fundamental ratios
- Determines price trends
- Identifies support/resistance levels

### CEO Agent
**Basic Mode:**
- Coordinates all agents
- Synthesizes findings
- Generates scores (0-100)
- Creates actionable recommendations
- Produces detailed investment reports

**Advanced Mode (LLM-powered):**
- Uses Gemini 2.0 Flash for expert analysis
- Provides dual time-horizon recommendations (1-month and 1-year)
- Generates detailed reasoning with specific data citations
- Quotes news articles and explains their impact
- Incorporates geopolitical and industry context
- Provides price targets and stop-loss recommendations
- Explains assumptions and external knowledge used

## 📈 Analysis Scoring

The system uses a composite scoring algorithm:
- **80-100**: STRONG BUY - Excellent buying opportunity
- **60-79**: BUY - Positive signals for accumulation
- **40-59**: HOLD - Mixed signals, monitor closely
- **20-39**: SELL - Negative indicators, consider caution
- **0-19**: STRONG SELL - Strong sell signals, reduce holdings

## ⚠️ Disclaimer

**This application is for informational and educational purposes only.** 

- Not financial advice
- No liability for investment losses
- Always conduct personal research
- Consult qualified financial advisors
- Past performance ≠ Future results
- Stock markets are inherently risky
- This tool has limitations and may contain errors

## 🔐 Privacy & Security

- All processing is local (no data sent to external servers by default)
- API keys stored in local `.env` file only
- No tracking or analytics
- Your data is private to your machine

## 🎓 Educational Notes

This project demonstrates:
- Multi-agent AI system architecture
- Financial data analysis
- Technical indicator calculation
- Web scraping and data aggregation
- Streamlit UI development
- Python software engineering best practices

## 🤝 Contributing

Contributions are welcome! Areas for enhancement:
- Additional technical indicators
- Machine learning models
- Real-time data updates
- Portfolio analysis
- Backtesting framework
- Mobile app version

## 📞 Support

For issues or questions:
1. Check `config.py` for parameter customization
2. Ensure all dependencies are installed: `pip install -r requirements.txt`
3. Verify internet connection for data fetching
4. Check API rate limits if using external APIs

## 📄 License

See LICENSE file for details.

## 🙏 Acknowledgments

- Yahoo Finance for stock data
- Financial theory and technical analysis concepts
- Streamlit community
- Python data science ecosystem

---

**Happy analyzing! 📊** Make informed investment decisions with data-driven insights.
