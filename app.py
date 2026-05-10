"""
Main Streamlit Application - NSE Stock Analysis App
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import logging
import sys
import math

from agents import StockScraperAgent, NewsScraperAgent, AnalysisAgent, CEOAgent
from utils import DataProcessor
import config

# Configure logging for debug mode
if config.DEBUG_MODE:
    log_level = logging.DEBUG
    log_format = '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s'
else:
    log_level = logging.INFO
    log_format = '%(asctime)s - %(levelname)s - %(message)s'

logging.basicConfig(
    level=log_level,
    format=log_format,
    handlers=[
        logging.FileHandler(config.DEBUG_LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)
if config.DEBUG_MODE:
    logger.debug(f"Debug mode enabled. Logging to {config.DEBUG_LOG_FILE}")


def safe_float(value):
    try:
        if value is None:
            return None
        number = float(value)
        if math.isnan(number) or math.isinf(number):
            return None
        return number
    except (TypeError, ValueError):
        return None


def format_number(value, decimals=2, prefix="", suffix=""):
    number = safe_float(value)
    if number is None:
        return "N/A"
    return f"{prefix}{number:.{decimals}f}{suffix}"


def format_percent(value, decimals=2):
    number = safe_float(value)
    if number is None:
        return "N/A"
    return f"{number:.{decimals}%}"

# Streamlit page configuration
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        color: #1f77d2;
    }
    .recommendation-strong-buy {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #28a745;
    }
    .recommendation-buy {
        background-color: #d1ecf1;
        color: #0c5460;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #17a2b8;
    }
    .recommendation-hold {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #ffc107;
    }
    .recommendation-sell {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #dc3545;
    }
    </style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state"""
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'report' not in st.session_state:
        st.session_state.report = None
    if 'stock_data' not in st.session_state:
        st.session_state.stock_data = None
    if 'analysis_mode' not in st.session_state:
        st.session_state.analysis_mode = "Basic"


def create_price_chart(stock_data):
    """Create interactive price chart using Plotly"""
    if stock_data is None or stock_data.empty:
        st.warning("No data available for chart")
        return
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=stock_data.index,
        y=stock_data['Close'],
        mode='lines',
        name='Close Price',
        line=dict(color='#1f77d2', width=2),
        fill='tozeroy',
        fillcolor='rgba(31, 119, 210, 0.1)'
    ))
    
    fig.update_layout(
        title="Stock Price Movement (Historical)",
        xaxis_title="Date",
        yaxis_title="Price (₹)",
        hovermode='x unified',
        height=400,
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def create_volume_chart(stock_data):
    """Create volume chart"""
    if stock_data is None or stock_data.empty:
        return
    
    fig = go.Figure()
    
    colors = ['green' if stock_data['Close'].iloc[i] >= stock_data['Close'].iloc[i-1] 
              else 'red' for i in range(1, len(stock_data))]
    colors.insert(0, 'gray')
    
    fig.add_trace(go.Bar(
        x=stock_data.index,
        y=stock_data['Volume'],
        name='Volume',
        marker_color=colors
    ))
    
    fig.update_layout(
        title="Trading Volume",
        xaxis_title="Date",
        yaxis_title="Volume",
        height=300,
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def create_recommendation_box(recommendation, score):
    """Display recommendation in styled box"""
    color_map = {
        "STRONG BUY": "recommendation-strong-buy",
        "BUY": "recommendation-buy",
        "HOLD": "recommendation-hold",
        "SELL": "recommendation-sell",
        "STRONG SELL": "recommendation-sell"
    }
    
    class_name = color_map.get(recommendation, "recommendation-hold")
    
    st.markdown(f"""
        <div class="{class_name}">
            <h3 style="margin: 0;">📊 Recommendation: <strong>{recommendation}</strong></h3>
            <p style="margin: 0.5rem 0 0 0;">Confidence Score: <strong>{score}/100</strong></p>
        </div>
    """, unsafe_allow_html=True)


def display_key_metrics(report):
    """Display key metrics in columns"""
    stock_summary = report.get('stock_summary', {})
    tech_analysis = report.get('technical_analysis', {})
    fund_analysis = report.get('fundamental_analysis', {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Current Price",
            format_number(stock_summary.get('current_price'), prefix="₹"),
            format_number(stock_summary.get('price_change_percent'), suffix="%")
        )
    
    with col2:
        st.metric(
            "RSI (14)",
            format_number(tech_analysis.get('rsi')),
            tech_analysis.get('rsi_signal', 'N/A')
        )
    
    with col3:
        st.metric(
            "P/E Ratio",
            f"{fund_analysis.get('pe_ratio', 'N/A')}",
            fund_analysis.get('pe_signal', 'N/A')
        )
    
    with col4:
        st.metric(
            "Trend",
            tech_analysis.get('trend', 'N/A'),
            f"Support: {format_number(tech_analysis.get('support_level'), prefix='₹')}"
        )


def display_detailed_analysis(report):
    """Display detailed analysis sections"""
    
    st.subheader("📈 Technical Analysis")
    tech_col1, tech_col2 = st.columns(2)
    
    with tech_col1:
        tech_data = report.get('technical_analysis', {})
        st.write(f"**Price Trend:** {tech_data.get('trend', 'N/A')}")
        st.write(f"**RSI (14):** {format_number(tech_data.get('rsi'))}")
        st.write(f"**SMA 20:** {format_number(tech_data.get('moving_averages', {}).get('sma_20'), prefix='₹')}")
        st.write(f"**SMA 50:** {format_number(tech_data.get('moving_averages', {}).get('sma_50'), prefix='₹')}")
    
    with tech_col2:
        st.write(f"**Support Level:** {format_number(tech_data.get('support_level'), prefix='₹')}")
        st.write(f"**Resistance Level:** {format_number(tech_data.get('resistance_level'), prefix='₹')}")
        st.write(f"**Volatility:** {format_percent(tech_data.get('volatility'))}")
        st.write(f"**Volume Trend:** {tech_data.get('volume_trend', 'N/A')}")
    
    st.subheader("💰 Fundamental Analysis")
    fund_col1, fund_col2 = st.columns(2)
    
    with fund_col1:
        fund_data = report.get('fundamental_analysis', {})
        st.write(f"**P/E Ratio:** {fund_data.get('pe_ratio', 'N/A')} ({fund_data.get('pe_signal', 'N/A')})")
        st.write(f"**P/B Ratio:** {fund_data.get('pb_ratio', 'N/A')} ({fund_data.get('pb_signal', 'N/A')})")
    
    with fund_col2:
        st.write(f"**Valuation:** {fund_data.get('valuation', 'N/A')}")
        st.write(f"**Growth Potential:** {fund_data.get('growth_potential', 'N/A')}")
    
    st.subheader("📰 Market Sentiment (Contributing to Final Score)")
    news_data = report.get('news_analysis', {})
    sentiment = news_data.get('sentiment_distribution', {})
    
    # Calculate sentiment impact
    positive = sentiment.get('positive', 0)
    negative = sentiment.get('negative', 0)
    neutral = sentiment.get('neutral', 0)
    total = positive + negative + neutral
    
    if total > 0:
        positive_ratio = positive / total
        negative_ratio = negative / total
        
        # Determine impact
        if positive_ratio > 0.6:
            impact_text = "📈 Strongly Positive (+15 points)"
            impact_color = "green"
        elif positive_ratio > 0.4:
            impact_text = "📈 Positive (+10 points)"
            impact_color = "green"
        elif positive_ratio > 0.2:
            impact_text = "📈 Moderately Positive (+5 points)"
            impact_color = "green"
        elif negative_ratio > 0.6:
            impact_text = "📉 Strongly Negative (-15 points)"
            impact_color = "red"
        elif negative_ratio > 0.4:
            impact_text = "📉 Negative (-10 points)"
            impact_color = "red"
        elif negative_ratio > 0.2:
            impact_text = "📉 Moderately Negative (-5 points)"
            impact_color = "red"
        else:
            impact_text = "➖ Neutral (0 points)"
            impact_color = "gray"
        
        st.info(f"**Sentiment Impact on Score:** {impact_text}")
    
    sent_col1, sent_col2, sent_col3 = st.columns(3)
    with sent_col1:
        st.metric("Positive", sentiment.get('positive', 0))
    with sent_col2:
        st.metric("Neutral", sentiment.get('neutral', 0))
    with sent_col3:
        st.metric("Negative", sentiment.get('negative', 0))
    
    # Display news articles with sentiment
    articles = news_data.get('articles', [])
    if articles:
        st.write("**Recent News Articles:**")
        for i, article in enumerate(articles[:5], 1):
            sentiment_emoji = {
                'positive': '✅',
                'neutral': '➖',
                'negative': '❌'
            }.get(article.get('sentiment', 'neutral'), '➖')
            
            with st.expander(f"{sentiment_emoji} {article.get('title', 'N/A')} - {article.get('sentiment', 'N/A').upper()}"):
                st.write(f"**Source:** {article.get('source', 'N/A')}")
                st.write(f"**Published:** {article.get('published', 'N/A')}")
                st.write(f"**Summary:** {article.get('summary', 'N/A')}")
                if article.get('link') and article.get('link') != '#':
                    st.write(f"**Link:** [{article.get('link')}]({article.get('link')})")
                st.write(f"**Analyzed Text:** {article.get('analyzed_text', 'N/A')}")
    
    st.subheader("🎯 Key Indicators Summary")
    key_indicators = report.get('key_indicators', {})
    
    ind_col1, ind_col2, ind_col3 = st.columns(3)
    with ind_col1:
        st.metric("Bullish Indicators", key_indicators.get('bullish_indicators', 0))
    with ind_col2:
        st.metric("Neutral Indicators", key_indicators.get('neutral_indicators', 0))
    with ind_col3:
        st.metric("Bearish Indicators", key_indicators.get('bearish_indicators', 0))


def run_analysis(ticker_symbol):
    """Run comprehensive analysis using all agents"""
    
    with st.spinner("🔍 Running Comprehensive Analysis..."):
        try:
            logger.info(f"Starting analysis for ticker: {ticker_symbol}")
            if config.DEBUG_MODE:
                logger.debug(f"Analysis started at: {datetime.now()}")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Stock Data Scraping
            status_text.text("📊 Step 1/4: Fetching stock data...")
            progress_bar.progress(20)
            
            logger.info("Step 1: Initializing StockScraperAgent")
            stock_scraper = StockScraperAgent()
            if config.DEBUG_MODE:
                logger.debug(f"StockScraperAgent created")
            
            logger.info(f"Fetching stock data for {ticker_symbol}")
            stock_data_result = stock_scraper.fetch_stock_data(ticker_symbol, period="200d")
            
            if not stock_data_result.get("success"):
                logger.error(f"Failed to fetch stock data: {stock_data_result.get('error')}")
                st.error(f"❌ Failed to fetch stock data: {stock_data_result.get('error')}")
                return
            
            if config.DEBUG_MODE:
                logger.debug(f"Stock data fetched successfully: {len(stock_data_result)} keys")
            
            stock_data = stock_data_result
            historical_data = stock_data.pop('historical_data')
            
            # Step 2: News Scraping
            status_text.text("📰 Step 2/4: Gathering market news and sentiment...")
            progress_bar.progress(40)
            
            logger.info("Step 2: Initializing NewsScraperAgent")
            news_scraper = NewsScraperAgent()
            if config.DEBUG_MODE:
                logger.debug("NewsScraperAgent created")
            
            logger.info(f"Fetching news for {stock_data.get('company_name', ticker_symbol)}")
            news_result = news_scraper.fetch_news(
                stock_data.get("company_name", ticker_symbol),
                ticker_symbol
            )
            if config.DEBUG_MODE:
                logger.debug(f"News fetched: {news_result.get('articles_count', 0)} articles")
            
            # Step 3: Technical & Fundamental Analysis
            status_text.text("📈 Step 3/4: Performing technical and fundamental analysis...")
            progress_bar.progress(60)
            
            logger.info("Step 3: Initializing AnalysisAgent")
            analysis_agent = AnalysisAgent()
            if config.DEBUG_MODE:
                logger.debug(f"AnalysisAgent created with {len(historical_data)} data points")
            
            logger.info("Performing technical analysis...")
            technical_result = analysis_agent.technical_analysis_report(historical_data, ticker_symbol)
            technical_analysis = technical_result.get("analysis", {})
            if config.DEBUG_MODE:
                logger.debug(f"Technical analysis complete: {len(technical_analysis)} indicators")
            
            logger.info("Performing fundamental analysis...")
            fundamental_result = analysis_agent.fundamental_analysis_report(stock_data)
            fundamental_analysis = fundamental_result.get("analysis", {})
            if config.DEBUG_MODE:
                logger.debug(f"Fundamental analysis complete: {len(fundamental_analysis)} metrics")
            
            # Calculate combined score (including news sentiment)
            logger.info("Calculating combined score...")
            combined_score = analysis_agent.get_combined_score(technical_analysis, fundamental_analysis, news_result)
            logger.info(f"Combined score calculated: {combined_score}/100")
            if config.DEBUG_MODE:
                logger.debug(f"Score breakdown - Technical signals, Fundamental metrics, News sentiment processed")
            
            # Step 4: CEO Agent Orchestration
            status_text.text("🤖 Step 4/4: CEO Agent generating comprehensive report...")
            progress_bar.progress(80)
            
            # Get analysis mode from session state
            use_llm = st.session_state.get('analysis_mode', 'Basic') == 'Advanced'
            
            logger.info(f"Step 4: Initializing CEOAgent for report generation (Mode: {'Advanced' if use_llm else 'Basic'})")
            ceo_agent = CEOAgent(use_llm=use_llm)
            if config.DEBUG_MODE:
                logger.debug(f"CEOAgent created in {'LLM' if use_llm else 'rule-based'} mode")
            
            logger.info("Orchestrating all agent data and generating final report...")
            final_report = ceo_agent.orchestrate_analysis(
                stock_data,
                news_result,
                technical_analysis,
                fundamental_analysis,
                combined_score
            )
            
            if config.DEBUG_MODE:
                logger.debug(f"Final report generated with recommendation: {final_report.get('recommendation', {}).get('action', 'N/A')}")
            
            logger.info(f"Analysis complete. Recommendation: {final_report.get('recommendation', {}).get('action', 'N/A')}")
            
            progress_bar.progress(100)
            status_text.text("✅ Analysis complete!")
            
            if config.DEBUG_MODE:
                logger.debug(f"Analysis completed in {(datetime.now()).isoformat()}")
                logger.debug("Storing results in session state")
            
            # Store in session state
            st.session_state.report = final_report
            st.session_state.stock_data = historical_data
            st.session_state.analysis_complete = True
            
            logger.info(f"Analysis successfully completed for {ticker_symbol}")
            return final_report
            
        except Exception as e:
            logger.error(f"Error during analysis: {str(e)}", exc_info=True)
            if config.DEBUG_MODE:
                logger.debug(f"Full error traceback logged above")
            st.error(f"❌ Error during analysis: {str(e)}")
            return None


def main():
    """Main application function"""
    
    initialize_session_state()
    
    logger.info("=" * 60)
    logger.info("NSE Stock Analysis App Started")
    if config.DEBUG_MODE:
        logger.debug(f"DEBUG MODE ENABLED - Log file: {config.DEBUG_LOG_FILE}")
        logger.debug(f"Python version: {sys.version}")
        logger.debug(f"Streamlit version: {st.__version__}")
    logger.info("=" * 60)
    
    # Header
    st.markdown("""
        <div class="main-header">
        📈 NSE Stock Analysis - Fundamental & Technical Analyzer
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("*Comprehensive analysis powered by multiple AI agents*")
    st.divider()
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Configuration")
        
        st.subheader("Stock Selection")
        ticker_input = st.text_input(
            "Enter NSE Ticker Symbol",
            value="RELIANCE",
            placeholder="e.g., RELIANCE, TCS, INFY, HDFC"
        ).upper()
        
        st.info(
            "💡 Popular NSE stocks: RELIANCE, TCS, INFY, HDFC, ICICI, LT, BAJAJ, MARUTI, WIPRO, ADANIGREEN"
        )
        
        st.divider()
        
        # Analysis Mode Selection
        st.subheader("🤖 Analysis Mode")
        analysis_options = ["Basic", "Advanced"]
        default_index = analysis_options.index(st.session_state.analysis_mode) if st.session_state.analysis_mode in analysis_options else 0
        analysis_mode = st.radio(
            "Select Analysis Mode:",
            options=analysis_options,
            index=default_index,
            help="""
            **Basic**: Rule-based scoring using technical and fundamental indicators
            
            **Advanced**: LLM-powered analysis using Gemini AI for comprehensive recommendations with 1-month and 1-year outlooks
            """
        )
        st.session_state.analysis_mode = analysis_mode
        
        if analysis_mode == "Advanced":
            st.info("🧠 **Advanced Mode**: Uses Gemini 2.0 Flash for expert stock analysis with detailed reasoning and explainability")
        else:
            st.info("📊 **Basic Mode**: Fast rule-based analysis using technical and fundamental metrics")
        
        st.divider()
        
        # Analysis button
        if st.button("🚀 Run Analysis", use_container_width=True):
            if ticker_input:
                st.session_state.analysis_complete = False
                st.session_state.report = None
                st.session_state.analysis_mode = analysis_mode
                run_analysis(ticker_input)
            else:
                st.error("Please enter a ticker symbol")
    
    # Main content
    if st.session_state.analysis_complete and st.session_state.report:
        report = st.session_state.report
        
        # Success message
        st.success("✅ Analysis completed successfully!")
        st.divider()
        
        # Display recommendation
        recommendation = report.get('recommendation', {})
        
        # Check if this is LLM-based analysis (has short_term and long_term)
        if 'short_term' in recommendation and 'long_term' in recommendation:
            # Advanced LLM-based recommendation display
            st.markdown("### 🎯 AI-Powered Investment Recommendations")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📅 Short-term (1 Month)")
                short_term = recommendation.get('short_term', {})
                create_recommendation_box(
                    short_term.get('action', 'HOLD'),
                    short_term.get('confidence', 50)
                )
                if short_term.get('rationale'):
                    st.write(f"**Rationale:** {short_term.get('rationale')}")
            
            with col2:
                st.markdown("#### 📈 Long-term (1 Year)")
                long_term = recommendation.get('long_term', {})
                create_recommendation_box(
                    long_term.get('action', 'HOLD'),
                    long_term.get('confidence', 50)
                )
                if long_term.get('rationale'):
                    st.write(f"**Rationale:** {long_term.get('rationale')}")
            
            # Price targets
            price_targets = recommendation.get('price_targets', {})
            if price_targets:
                st.markdown("#### 🎯 Price Targets")
                target_col1, target_col2, target_col3 = st.columns(3)
                with target_col1:
                    st.metric("1-Month Range", 
                             f"{price_targets.get('one_month_low', 'N/A')} - {price_targets.get('one_month_high', 'N/A')}")
                with target_col2:
                    st.metric("1-Year Range", 
                             f"{price_targets.get('one_year_low', 'N/A')} - {price_targets.get('one_year_high', 'N/A')}")
                with target_col3:
                    st.metric("Stop Loss", price_targets.get('stop_loss', 'N/A'))
            
            # Executive Summary
            if report.get('executive_summary'):
                st.markdown("#### 📝 Executive Summary")
                st.info(report.get('executive_summary'))
            
            # Risk Assessment (structured)
            risk_assessment = recommendation.get('risk_assessment', {})
            if isinstance(risk_assessment, dict) and risk_assessment:
                st.markdown("#### ⚠️ Risk Assessment")
                risk_col1, risk_col2 = st.columns([1, 2])
                with risk_col1:
                    risk_level = risk_assessment.get('level', 'Moderate')
                    risk_color = {"Low": "🟢", "Moderate": "🟡", "High": "🟠", "Very High": "🔴"}.get(risk_level, "⚪")
                    st.metric("Risk Level", f"{risk_color} {risk_level}")
                with risk_col2:
                    st.write(f"**Volatility:** {risk_assessment.get('volatility', 'N/A')}")
                
                key_risks = risk_assessment.get('key_risks', [])
                if key_risks:
                    st.write("**Key Risks:**")
                    for risk in key_risks:
                        st.write(f"- {risk}")
            
            # Key Factors Analysis
            key_factors = report.get('key_factors', {})
            if key_factors:
                st.markdown("#### 🔍 Key Factors Analysis")
                with st.expander("Technical Analysis", expanded=False):
                    st.write(key_factors.get('technical_summary', 'N/A'))
                with st.expander("Fundamental Analysis", expanded=False):
                    st.write(key_factors.get('fundamental_summary', 'N/A'))
                with st.expander("Market Sentiment", expanded=False):
                    st.write(key_factors.get('sentiment_summary', 'N/A'))
                
                catalysts = key_factors.get('catalysts', [])
                if catalysts:
                    with st.expander("Key Catalysts", expanded=False):
                        for catalyst in catalysts:
                            st.write(f"• {catalyst}")
        else:
            # Basic rule-based recommendation display
            create_recommendation_box(
                recommendation.get('action', 'N/A'),
                recommendation.get('confidence_score', 0)
            )
        
        st.subheader(f"📊 {report.get('company_name', 'Stock')} Analysis Report")
        
        # Key metrics
        display_key_metrics(report)
        
        st.divider()
        
        # Charts
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.subheader("Price Movement")
            if st.session_state.stock_data is not None:
                create_price_chart(st.session_state.stock_data)
        
        with col2:
            st.subheader("Trading Volume")
            if st.session_state.stock_data is not None:
                create_volume_chart(st.session_state.stock_data)
        
        st.divider()
        
        # Detailed analysis
        display_detailed_analysis(report)
        
        # Risk and investment horizon (for basic mode)
        if 'risk_level' in recommendation or 'investment_horizon' in recommendation:
            st.subheader("⚠️ Risk Assessment & Investment Horizon")
            risk_col1, risk_col2 = st.columns(2)
            
            with risk_col1:
                st.write(f"**Risk Level:** {recommendation.get('risk_level', 'N/A')}")
            
            with risk_col2:
                st.write(f"**Investment Horizon:** {recommendation.get('investment_horizon', 'N/A')}")
        
        # Detailed analysis text
        st.subheader("📋 Detailed Analysis Summary")
        
        # Check if LLM analysis (will have investment_thesis)
        if report.get('analysis_mode') == 'Advanced (LLM-based)':
            investment_thesis = report.get('investment_thesis', '')
            if investment_thesis:
                st.markdown("#### 💡 Investment Thesis")
                st.markdown(investment_thesis)
        else:
            # Basic mode - show rule-based analysis
            analysis_text = report.get('detailed_analysis', 'N/A')
            st.text(analysis_text)
            
            # Risk assessment for basic mode
            if 'risk_level' in recommendation:
                st.subheader("⚠️ Risk Assessment")
                st.info(f"Risk Level: {recommendation.get('risk_level', 'N/A')}")
        
        # Export options
        st.divider()
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Download Report (JSON)", use_container_width=True):
                import json
                json_str = json.dumps(report, indent=2, default=str)
                st.download_button(
                    label="Download JSON",
                    data=json_str,
                    file_name=f"{report.get('ticker', 'stock')}_report.json",
                    mime="application/json"
                )
        
        with col2:
            if st.button("📊 Export Data (CSV)", use_container_width=True):
                if st.session_state.stock_data is not None:
                    csv = st.session_state.stock_data.to_csv()
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"{report.get('ticker', 'stock')}_data.csv",
                        mime="text/csv"
                    )
        
        st.divider()
        
        # Disclaimer
        st.warning(
            """
            **⚠️ Disclaimer:** This analysis is for informational purposes only and should not be considered as 
            financial advice. Always conduct your own research and consult with a qualified financial advisor 
            before making investment decisions. Past performance does not guarantee future results.
            """
        )
    
    else:
        # Welcome message
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("👋 Welcome to NSE Stock Analyzer")
            st.write("""
                This application provides comprehensive fundamental and technical analysis of NSE stocks 
                using multiple AI agents working together:
                
                **🤖 Agent Architecture:**
                - **Stock Scraper Agent**: Fetches real-time and historical stock data
                - **News Scraper Agent**: Gathers latest market news and sentiment
                - **Analysis Agent**: Performs technical and fundamental analysis
                - **CEO Agent**: Orchestrates all agents and generates final recommendation
                
                **📊 Analysis Modes:**
                - **Basic Mode**: Fast rule-based scoring using technical and fundamental indicators
                - **Advanced Mode**: AI-powered analysis using Gemini 2.0 Flash with:
                  - Short-term (1 month) and long-term (1 year) recommendations
                  - Detailed reasoning and explainability
                  - Price targets and risk assessment
                  - News article citations and geopolitical context
                
                **📈 Analysis Includes:**
                - Technical indicators (RSI, MACD, Bollinger Bands, Moving Averages)
                - Fundamental metrics (P/E, P/B, Valuation, Growth Potential)
                - Market sentiment analysis from news articles
                - Buy/Hold/Sell recommendations with confidence scores
                
                **🚀 Get Started:**
                1. Enter a NSE ticker symbol in the sidebar
                2. Choose Basic or Advanced analysis mode
                3. Click "Run Analysis"
                4. View comprehensive analysis and recommendations
            """)
        
        with col2:
            st.info("""
                **Featured Stocks:**
                - RELIANCE
                - TCS
                - INFY
                - HDFC
                - ICICI
            """)


if __name__ == "__main__":
    main()
