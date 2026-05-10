# Advanced LLM-Based Analysis Mode Guide

## Overview

The Investment GPT application now supports two analysis modes:

### **Basic Mode** (Default)
- Fast rule-based scoring using technical and fundamental indicators
- No API key required
- Provides single Buy/Hold/Sell recommendation with confidence score

### **Advanced Mode** (NEW)
- AI-powered analysis using Google Gemini 2.5 Flash
- Requires Google API key
- Provides dual time-horizon recommendations (1-month and 1-year)
- Detailed reasoning, explainability, and price targets

## Setup for Advanced Mode

### 1. Get Google Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

### 2. Configure Environment

Add your API key to the `.env` file:

```bash
GOOGLE_API_KEY=your_actual_api_key_here
```

### 3. Install Dependencies

All Gemini dependencies are already declared in `pyproject.toml`. Simply run:

```bash
uv sync
```

This ensures `google-generativeai>=0.3.0` (and everything else) is available inside the managed `.venv`.

## Using Advanced Mode

### In the UI

1. Open the application
2. In the sidebar, find **"🤖 Analysis Mode"**
3. Select **"Advanced"** radio button
4. Enter your stock ticker (e.g., RELIANCE)
5. Click **"🚀 Run Analysis"**

### What You Get

**Short-term Recommendation (1 Month):**
- Action: BUY / HOLD / SELL
- Confidence Score: 0-100
- Detailed rationale with specific data points

**Long-term Recommendation (1 Year):**
- Action: BUY / HOLD / SELL
- Confidence Score: 0-100
- Detailed rationale with specific data points

**Additional Insights:**
- Price target ranges (1-month and 1-year)
- Risk assessment with specific factors
- News article citations and impact analysis
- Technical indicator explanations
- Fundamental metric analysis
- Geopolitical and industry context
- Stop-loss recommendations

## How It Works

### Data Collection
The system collects:
- Historical stock data (200 days)
- Technical indicators (RSI, MACD, Moving Averages, etc.)
- Fundamental metrics (P/E, P/B ratios, etc.)
- Recent news articles with sentiment analysis

### LLM Processing
All data is sent to Gemini 2.5 Flash with a comprehensive prompt that:
- Positions the AI as an expert stock analyst with 20+ years experience
- Requests dual time-horizon analysis
- Demands specific citations and reasoning
- Requires explainability for all recommendations
- Asks for price targets and risk assessment

### Output Generation
The LLM generates:
- Structured recommendations
- Detailed analysis report
- Specific data point references
- News article citations
- Risk factors and considerations

## Comparison: Basic vs Advanced

| Feature | Basic Mode | Advanced Mode |
|---------|-----------|---------------|
| **Speed** | Fast (2-5 seconds) | Moderate (10-20 seconds) |
| **API Key** | Not required | Google API key required |
| **Cost** | Free | Free tier available, then pay-per-use |
| **Recommendations** | Single (Buy/Hold/Sell) | Dual (1-month + 1-year) |
| **Reasoning** | Rule-based summary | Detailed AI-generated analysis |
| **Price Targets** | No | Yes (ranges for both horizons) |
| **News Citations** | Sentiment only | Specific article quotes |
| **Context** | Technical + Fundamental | + Geopolitical + Industry |
| **Explainability** | Basic | Comprehensive |

## Example Output (Advanced Mode)

```
🎯 AI-Powered Investment Recommendations

📅 Short-term (1 Month)
Action: BUY
Confidence: 75/100
Rationale: Strong technical momentum with RSI at 45 (neutral to bullish), 
MACD showing positive crossover, and price above 20-day SMA. Recent positive 
news about Q1 earnings beat supports short-term upside.

📈 Long-term (1 Year)
Action: HOLD
Confidence: 65/100
Rationale: While fundamentals are solid (P/E of 22 vs industry average of 25), 
the stock has run up significantly. Recommend holding current positions and 
accumulating on dips below ₹2,400.

🎯 Price Targets
1-Month Range: ₹2,550 - ₹2,750
1-Year Range: ₹2,800 - ₹3,200

⚠️ Risk Assessment
Moderate risk. Key factors: Global commodity price volatility, regulatory 
changes in the sector, and macroeconomic headwinds. Stop-loss recommended 
at ₹2,350.
```

## Troubleshooting

### "GOOGLE_API_KEY not found"
- Ensure `.env` file exists in project root
- Check that the key is correctly formatted: `GOOGLE_API_KEY=your_key_here`
- Restart the application after adding the key

### "Falling back to basic mode"
- Check your API key is valid
- Verify internet connection
- Check Google AI Studio for API quota/limits
- Re-run `uv sync` to ensure the latest dependencies (including `google-generativeai`) are installed

### Slow Response
- Advanced mode takes 10-20 seconds due to LLM processing
- This is normal - the AI is analyzing comprehensive data
- Basic mode is faster if you need quick results

## Best Practices

1. **Use Basic Mode for:**
   - Quick screening of multiple stocks
   - When you don't need detailed reasoning
   - Testing the application

2. **Use Advanced Mode for:**
   - Detailed investment decisions
   - Understanding the "why" behind recommendations
   - Getting multiple time-horizon perspectives
   - Analyzing complex market situations

3. **API Key Management:**
   - Never commit `.env` file to version control
   - Keep your API key secure
   - Monitor your API usage in Google AI Studio
   - Use free tier wisely (rate limits apply)

## Technical Details

### Model Used
- **Gemini 2.5 Flash** (`gemini-2.5-flash`)
- Fast, efficient, and cost-effective
- Excellent for structured analysis tasks

### Prompt Engineering
The system uses a carefully crafted prompt that:
- Sets expert persona (20+ years stock analyst)
- Provides comprehensive context (technical, fundamental, news)
- Requests structured output format
- Demands specific citations and reasoning
- Requires dual time-horizon analysis

### Fallback Mechanism
If Advanced mode fails:
- Automatically falls back to Basic mode
- Logs the error for debugging
- User is notified of the fallback
- Analysis still completes successfully

## Future Enhancements

Potential improvements:
- Custom time horizons (user-defined)
- Portfolio-level analysis
- Comparative analysis (multiple stocks)
- Backtesting recommendations
- Fine-tuned models for Indian markets
- Integration with more data sources

## Support

For issues with Advanced mode:
1. Check logs in debug mode (`DEBUG_MODE = True` in `config.py`)
2. Verify API key and internet connection
3. Try Basic mode to isolate the issue
4. Check Google AI Studio for API status

---

**Note:** Advanced mode uses AI and may occasionally produce unexpected results. Always verify recommendations with your own research and consult financial advisors for investment decisions.
