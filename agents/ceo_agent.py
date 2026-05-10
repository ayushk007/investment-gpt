"""
CEO Agent
Coordinates all other agents and generates comprehensive analysis report
"""

import json
import math
from datetime import datetime
import logging
from typing import Dict, Any, Literal
import os
import config
from pydantic import BaseModel, Field

# Configure logging based on config
log_level = logging.DEBUG if config.DEBUG_MODE else logging.INFO
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
    from google.generativeai.types import GenerationConfig
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Google Generative AI not available. Install with: pip install google-generativeai")


# Pydantic models for structured LLM output
class RecommendationDetail(BaseModel):
    """Structured recommendation for a time horizon"""
    action: Literal["STRONG BUY", "BUY", "HOLD", "SELL", "STRONG SELL"] = Field(
        description="Investment action recommendation"
    )
    confidence_score: int = Field(
        description="Confidence score from 0-100 indicating how confident you are in this recommendation"
    )
    rationale: str = Field(
        description="Detailed rationale explaining the recommendation with specific data points from the provided analysis"
    )


class PriceTargets(BaseModel):
    """Price target ranges"""
    one_month_low: float = Field(description="Lower bound of 1-month price target")
    one_month_high: float = Field(description="Upper bound of 1-month price target")
    one_year_low: float = Field(description="Lower bound of 1-year price target")
    one_year_high: float = Field(description="Upper bound of 1-year price target")
    stop_loss: float = Field(description="Recommended stop-loss price")


class RiskAssessment(BaseModel):
    """Risk assessment details"""
    level: Literal["Low", "Moderate", "High", "Very High"] = Field(
        description="Overall risk level"
    )
    key_risks: list[str] = Field(
        description="List of key risk factors"
    )
    volatility_assessment: str = Field(
        description="Assessment of stock volatility"
    )


class KeyFactorsAnalysis(BaseModel):
    """Analysis of key factors"""
    technical_summary: str = Field(
        description="Summary of technical indicators and their implications"
    )
    fundamental_summary: str = Field(
        description="Summary of fundamental metrics and valuation"
    )
    sentiment_summary: str = Field(
        description="Summary of market sentiment from news analysis"
    )
    catalysts: list[str] = Field(
        description="Key catalysts that could move the stock"
    )


class StockAnalysisResponse(BaseModel):
    """Complete structured response from LLM analysis"""
    executive_summary: str = Field(
        description="Brief executive summary of the analysis (2-3 sentences)"
    )
    short_term_recommendation: RecommendationDetail = Field(
        description="1-month investment recommendation"
    )
    long_term_recommendation: RecommendationDetail = Field(
        description="1-year investment recommendation"
    )
    price_targets: PriceTargets = Field(
        description="Price target ranges for different time horizons"
    )
    risk_assessment: RiskAssessment = Field(
        description="Risk assessment and key concerns"
    )
    key_factors: KeyFactorsAnalysis = Field(
        description="Analysis of key technical, fundamental, and sentiment factors"
    )
    investment_thesis: str = Field(
        description="Comprehensive investment thesis explaining the overall recommendation"
    )

if config.DEBUG_MODE:
    logger.debug("CEOAgent initialized in DEBUG mode")


def _safe_float(value):
    try:
        if value is None:
            return None
        number = float(value)
        if math.isnan(number) or math.isinf(number):
            return None
        return number
    except (TypeError, ValueError):
        return None


def _format_number(value, decimals=2, prefix="", suffix=""):
    number = _safe_float(value)
    if number is None:
        return "N/A"
    return f"{prefix}{number:.{decimals}f}{suffix}"


def _format_percent(value, decimals=2):
    number = _safe_float(value)
    if number is None:
        return "N/A"
    return f"{number:.{decimals}%}"


class CEOAgent:
    """Orchestrates all agents and generates final analysis report"""
    
    def __init__(self, use_llm=False):
        self.final_report = None
        self.use_llm = use_llm
        self.llm_model = None
        
        # Initialize Gemini if LLM mode is enabled
        if self.use_llm and GEMINI_AVAILABLE:
            api_key = os.getenv('GOOGLE_API_KEY') or config.GOOGLE_API_KEY
            if api_key:
                genai.configure(api_key=api_key)
                self.llm_model = genai.GenerativeModel('gemini-2.5-flash')
                logger.info("Gemini LLM initialized for advanced analysis")
            else:
                logger.warning("GOOGLE_API_KEY not found. Falling back to basic mode.")
                self.use_llm = False
        elif self.use_llm and not GEMINI_AVAILABLE:
            logger.warning("Gemini not available. Falling back to basic mode.")
            self.use_llm = False
        self.recommendation = None
    
    def orchestrate_analysis(self, 
                            stock_scraper_data: Dict,
                            news_data: Dict,
                            technical_analysis: Dict,
                            fundamental_analysis: Dict,
                            combined_score: int) -> Dict:
        """
        Orchestrate all agent data and generate comprehensive report
        
        Args:
            stock_scraper_data: Data from stock scraper agent
            news_data: Data from news scraper agent
            technical_analysis: Data from technical analysis
            fundamental_analysis: Data from fundamental analysis
            combined_score: Combined analysis score (0-100)
            
        Returns:
            Comprehensive analysis report with recommendation
        """
        try:
            # Use LLM-based analysis if enabled
            if self.use_llm and self.llm_model:
                return self._llm_based_analysis(
                    stock_scraper_data, 
                    news_data, 
                    technical_analysis, 
                    fundamental_analysis
                )
            
            # Otherwise use rule-based analysis
            # Determine recommendation based on score
            recommendation, recommendation_reason = self._get_recommendation(combined_score)
            
            # Generate detailed report
            report = {
                "report_timestamp": datetime.now().isoformat(),
                "ticker": stock_scraper_data.get("ticker", "N/A"),
                "company_name": stock_scraper_data.get("company_name", "N/A"),
                
                # Stock Information
                "stock_summary": {
                    "current_price": stock_scraper_data.get("latest_price", "N/A"),
                    "price_change": stock_scraper_data.get("price_change", "N/A"),
                    "price_change_percent": stock_scraper_data.get("price_change_percent", "N/A"),
                    "52_week_high": stock_scraper_data.get("52_week_high", "N/A"),
                    "52_week_low": stock_scraper_data.get("52_week_low", "N/A"),
                    "market_cap": stock_scraper_data.get("market_cap", "N/A"),
                    "pe_ratio": stock_scraper_data.get("pe_ratio", "N/A"),
                },
                
                # Technical Analysis Summary
                "technical_analysis": {
                    "current_price": technical_analysis.get("current_price", "N/A"),
                    "trend": technical_analysis.get("price_trend", "N/A"),
                    "rsi": technical_analysis.get("rsi", "N/A"),
                    "rsi_signal": technical_analysis.get("rsi_signal", "N/A"),
                    "support_level": technical_analysis.get("support_level", "N/A"),
                    "resistance_level": technical_analysis.get("resistance_level", "N/A"),
                    "moving_averages": {
                        "sma_20": technical_analysis.get("sma_20", "N/A"),
                        "sma_50": technical_analysis.get("sma_50", "N/A"),
                        "sma_200": technical_analysis.get("sma_200", "N/A"),
                    },
                    "volatility": technical_analysis.get("volatility", "N/A"),
                    "volume_trend": technical_analysis.get("volume_trend", "N/A"),
                },
                
                # Fundamental Analysis Summary
                "fundamental_analysis": {
                    "pe_ratio": fundamental_analysis.get("pe_ratio", "N/A"),
                    "pe_signal": fundamental_analysis.get("pe_signal", "N/A"),
                    "pb_ratio": fundamental_analysis.get("pb_ratio", "N/A"),
                    "pb_signal": fundamental_analysis.get("pb_signal", "N/A"),
                    "dividend_yield": fundamental_analysis.get("dividend_yield", "N/A"),
                    "valuation": fundamental_analysis.get("valuation_assessment", "N/A"),
                    "growth_potential": fundamental_analysis.get("growth_potential", "N/A"),
                },
                
                # News Sentiment
                "news_analysis": {
                    "articles_analyzed": news_data.get("articles_count", 0),
                    "sentiment_distribution": news_data.get("sentiment_distribution", {}),
                    "articles": news_data.get("articles", []),
                },
                
                # Recommendation
                "recommendation": {
                    "action": recommendation,
                    "confidence_score": combined_score,
                    "reason": recommendation_reason,
                    "risk_level": self._assess_risk_level(technical_analysis, fundamental_analysis),
                    "investment_horizon": self._suggest_investment_horizon(technical_analysis, fundamental_analysis),
                },
                
                # Detailed Analysis
                "detailed_analysis": self._generate_detailed_analysis(
                    stock_scraper_data,
                    technical_analysis,
                    fundamental_analysis,
                    news_data,
                    combined_score
                ),
                
                # Key Indicators Summary
                "key_indicators": {
                    "bullish_indicators": self._count_bullish_indicators(technical_analysis, fundamental_analysis),
                    "bearish_indicators": self._count_bearish_indicators(technical_analysis, fundamental_analysis),
                    "neutral_indicators": self._count_neutral_indicators(technical_analysis, fundamental_analysis),
                }
            }
            
            self.final_report = report
            self.recommendation = recommendation
            
            logger.info(f"Report generated with recommendation: {recommendation}")
            
            return report
            
        except Exception as e:
            logger.error(f"Error orchestrating analysis: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _llm_based_analysis(self,
                           stock_data: Dict,
                           news_data: Dict,
                           technical: Dict,
                           fundamental: Dict) -> Dict:
        """
        Generate LLM-based comprehensive analysis using Gemini
        
        Args:
            stock_data: Stock scraper data
            news_data: News and sentiment data
            technical: Technical analysis data
            fundamental: Fundamental analysis data
            
        Returns:
            Comprehensive analysis report with LLM-generated recommendations
        """
        try:
            # Prepare comprehensive context for the LLM
            context = self._prepare_llm_context(stock_data, news_data, technical, fundamental)
            
            # Create expert CEO agent prompt for structured JSON output
            prompt = f"""You are an expert stock market analyst and investment advisor with 20+ years of experience in equity research, technical analysis, and fundamental valuation.

Analyze the following stock and provide a comprehensive investment analysis.

**STOCK INFORMATION:**
{context}

**ANALYSIS INSTRUCTIONS:**
1. Provide SHORT-TERM (1-month) and LONG-TERM (1-year) recommendations
2. Each recommendation must include: action (STRONG BUY/BUY/HOLD/SELL/STRONG SELL), confidence score (0-100), and detailed rationale
3. The rationale MUST reference specific data points from the provided information (e.g., "RSI at 61.66 indicates...", "P/E of 24.07 suggests...")
4. Quote specific news headlines when they influence your recommendation
5. Provide realistic price targets based on technical levels and fundamentals
6. Identify key risks and catalysts

Be specific, data-driven, and actionable in your analysis."""

            # Call Gemini API with structured JSON output
            logger.info("Calling Gemini LLM for advanced analysis with structured output...")
            
            # Create a simplified schema dict compatible with old google.generativeai
            schema_dict = {
                "type": "object",
                "properties": {
                    "executive_summary": {"type": "string"},
                    "short_term_recommendation": {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "enum": ["STRONG BUY", "BUY", "HOLD", "SELL", "STRONG SELL"]},
                            "confidence_score": {"type": "integer"},
                            "rationale": {"type": "string"}
                        },
                        "required": ["action", "confidence_score", "rationale"]
                    },
                    "long_term_recommendation": {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "enum": ["STRONG BUY", "BUY", "HOLD", "SELL", "STRONG SELL"]},
                            "confidence_score": {"type": "integer"},
                            "rationale": {"type": "string"}
                        },
                        "required": ["action", "confidence_score", "rationale"]
                    },
                    "price_targets": {
                        "type": "object",
                        "properties": {
                            "one_month_low": {"type": "number"},
                            "one_month_high": {"type": "number"},
                            "one_year_low": {"type": "number"},
                            "one_year_high": {"type": "number"},
                            "stop_loss": {"type": "number"}
                        },
                        "required": ["one_month_low", "one_month_high", "one_year_low", "one_year_high", "stop_loss"]
                    },
                    "risk_assessment": {
                        "type": "object",
                        "properties": {
                            "level": {"type": "string", "enum": ["Low", "Moderate", "High", "Very High"]},
                            "key_risks": {"type": "array", "items": {"type": "string"}},
                            "volatility_assessment": {"type": "string"}
                        },
                        "required": ["level", "key_risks", "volatility_assessment"]
                    },
                    "key_factors": {
                        "type": "object",
                        "properties": {
                            "technical_summary": {"type": "string"},
                            "fundamental_summary": {"type": "string"},
                            "sentiment_summary": {"type": "string"},
                            "catalysts": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["technical_summary", "fundamental_summary", "sentiment_summary", "catalysts"]
                    },
                    "investment_thesis": {"type": "string"}
                },
                "required": ["executive_summary", "short_term_recommendation", "long_term_recommendation", 
                           "price_targets", "risk_assessment", "key_factors", "investment_thesis"]
            }
            
            try:
                response = self.llm_model.generate_content(
                    prompt,
                    generation_config=GenerationConfig(
                        response_mime_type="application/json",
                        response_schema=schema_dict
                    )
                )
            except Exception as api_error:
                logger.error(f"Gemini API call failed: {api_error}")
                if config.DEBUG_MODE:
                    import traceback
                    logger.debug(f"Full traceback: {traceback.format_exc()}")
                raise ValueError(f"Gemini API error: {api_error}")
            
            # Parse the structured JSON response
            try:
                llm_json = json.loads(response.text)
                analysis_result = StockAnalysisResponse(**llm_json)
                logger.info("Successfully parsed structured LLM response")
            except (json.JSONDecodeError, Exception) as parse_error:
                logger.error(f"Failed to parse structured response: {parse_error}")
                logger.debug(f"Raw response: {response.text[:500]}")
                raise ValueError(f"LLM response parsing failed: {parse_error}")
            
            # Build comprehensive report
            report = {
                "report_timestamp": datetime.now().isoformat(),
                "ticker": stock_data.get("ticker", "N/A"),
                "company_name": stock_data.get("company_name", "N/A"),
                "analysis_mode": "Advanced (LLM-based)",
                
                # Stock Information
                "stock_summary": {
                    "current_price": stock_data.get("latest_price", "N/A"),
                    "price_change": stock_data.get("price_change", "N/A"),
                    "price_change_percent": stock_data.get("price_change_percent", "N/A"),
                    "52_week_high": stock_data.get("52_week_high", "N/A"),
                    "52_week_low": stock_data.get("52_week_low", "N/A"),
                    "market_cap": stock_data.get("market_cap", "N/A"),
                    "pe_ratio": stock_data.get("pe_ratio", "N/A"),
                },
                
                # Technical Analysis Summary
                "technical_analysis": {
                    "current_price": technical.get("current_price", "N/A"),
                    "trend": technical.get("price_trend", "N/A"),
                    "rsi": technical.get("rsi", "N/A"),
                    "rsi_signal": technical.get("rsi_signal", "N/A"),
                    "support_level": technical.get("support_level", "N/A"),
                    "resistance_level": technical.get("resistance_level", "N/A"),
                    "moving_averages": {
                        "sma_20": technical.get("sma_20", "N/A"),
                        "sma_50": technical.get("sma_50", "N/A"),
                        "sma_200": technical.get("sma_200", "N/A"),
                    },
                    "volatility": technical.get("volatility", "N/A"),
                    "volume_trend": technical.get("volume_trend", "N/A"),
                },
                
                # Fundamental Analysis Summary
                "fundamental_analysis": {
                    "pe_ratio": fundamental.get("pe_ratio", "N/A"),
                    "pe_signal": fundamental.get("pe_signal", "N/A"),
                    "pb_ratio": fundamental.get("pb_ratio", "N/A"),
                    "pb_signal": fundamental.get("pb_signal", "N/A"),
                    "dividend_yield": fundamental.get("dividend_yield", "N/A"),
                    "valuation": fundamental.get("valuation_assessment", "N/A"),
                    "growth_potential": fundamental.get("growth_potential", "N/A"),
                },
                
                # News Sentiment
                "news_analysis": {
                    "articles_analyzed": news_data.get("articles_count", 0),
                    "sentiment_distribution": news_data.get("sentiment_distribution", {}),
                    "articles": news_data.get("articles", []),
                },
                
                # LLM-based Recommendations (from Pydantic model)
                "recommendation": {
                    "short_term": {
                        "action": analysis_result.short_term_recommendation.action,
                        "confidence": analysis_result.short_term_recommendation.confidence_score,
                        "rationale": analysis_result.short_term_recommendation.rationale,
                    },
                    "long_term": {
                        "action": analysis_result.long_term_recommendation.action,
                        "confidence": analysis_result.long_term_recommendation.confidence_score,
                        "rationale": analysis_result.long_term_recommendation.rationale,
                    },
                    "price_targets": {
                        "one_month_low": f"₹{analysis_result.price_targets.one_month_low:,.2f}",
                        "one_month_high": f"₹{analysis_result.price_targets.one_month_high:,.2f}",
                        "one_year_low": f"₹{analysis_result.price_targets.one_year_low:,.2f}",
                        "one_year_high": f"₹{analysis_result.price_targets.one_year_high:,.2f}",
                        "stop_loss": f"₹{analysis_result.price_targets.stop_loss:,.2f}",
                    },
                    "risk_assessment": {
                        "level": analysis_result.risk_assessment.level,
                        "key_risks": analysis_result.risk_assessment.key_risks,
                        "volatility": analysis_result.risk_assessment.volatility_assessment,
                    },
                },
                
                # Key Factors Analysis
                "key_factors": {
                    "technical_summary": analysis_result.key_factors.technical_summary,
                    "fundamental_summary": analysis_result.key_factors.fundamental_summary,
                    "sentiment_summary": analysis_result.key_factors.sentiment_summary,
                    "catalysts": analysis_result.key_factors.catalysts,
                },
                
                # Key Indicators (for compatibility)
                "key_indicators": {
                    "bullish_indicators": 1 if "BUY" in analysis_result.short_term_recommendation.action else 0,
                    "neutral_indicators": 1 if analysis_result.short_term_recommendation.action == "HOLD" else 0,
                    "bearish_indicators": 1 if "SELL" in analysis_result.short_term_recommendation.action else 0,
                },
                
                # Full LLM Analysis
                "executive_summary": analysis_result.executive_summary,
                "investment_thesis": analysis_result.investment_thesis,
                "detailed_analysis": analysis_result.investment_thesis,
                "llm_raw_response": response.text,
            }
            
            self.final_report = report
            logger.info("LLM-based analysis completed successfully")
            
            return report
            
        except Exception as e:
            logger.error(f"Error in LLM-based analysis: {str(e)}")
            # Fallback to basic analysis
            logger.warning("Falling back to basic rule-based analysis")
            self.use_llm = False
            return self.orchestrate_analysis(stock_data, news_data, technical, fundamental, 50)
    
    def _prepare_llm_context(self, stock_data: Dict, news_data: Dict, 
                            technical: Dict, fundamental: Dict) -> str:
        """Prepare comprehensive context for LLM"""
        
        # Format news articles
        news_context = ""
        articles = news_data.get("articles", [])
        if articles:
            news_context = "**Recent News Articles:**\n"
            for i, article in enumerate(articles[:10], 1):
                news_context += f"\n{i}. [{article.get('sentiment', 'N/A').upper()}] {article.get('title', 'N/A')}\n"
                news_context += f"   Source: {article.get('source', 'N/A')}\n"
                news_context += f"   Published: {article.get('published', 'N/A')}\n"
                news_context += f"   Summary: {article.get('summary', 'N/A')[:200]}\n"
        
        context = f"""
**Company:** {stock_data.get('company_name', 'N/A')} ({stock_data.get('ticker', 'N/A')})

**Current Market Data:**
- Current Price: ₹{_format_number(stock_data.get('latest_price'))}
- Price Change: {_format_number(stock_data.get('price_change_percent'), suffix='%')}
- 52-Week High: ₹{_format_number(stock_data.get('52_week_high'))}
- 52-Week Low: ₹{_format_number(stock_data.get('52_week_low'))}
- Market Cap: {stock_data.get('market_cap', 'N/A')}

**Technical Analysis:**
- Trend: {technical.get('price_trend', 'N/A')}
- RSI (14): {_format_number(technical.get('rsi'))} - {technical.get('rsi_signal', 'N/A')}
- MACD Signal: {_format_number(technical.get('macd_signal'))}
- Support Level: ₹{_format_number(technical.get('support_level'))}
- Resistance Level: ₹{_format_number(technical.get('resistance_level'))}
- SMA 20: ₹{_format_number(technical.get('sma_20'))}
- SMA 50: ₹{_format_number(technical.get('sma_50'))}
- SMA 200: ₹{_format_number(technical.get('sma_200'))}
- Volatility: {_format_percent(technical.get('volatility'))}
- Volume Trend: {technical.get('volume_trend', 'N/A')}

**Fundamental Analysis:**
- P/E Ratio: {fundamental.get('pe_ratio', 'N/A')} ({fundamental.get('pe_signal', 'N/A')})
- P/B Ratio: {fundamental.get('pb_ratio', 'N/A')} ({fundamental.get('pb_signal', 'N/A')})
- Dividend Yield: {fundamental.get('dividend_yield', 'N/A')}
- Valuation: {fundamental.get('valuation_assessment', 'N/A')}
- Growth Potential: {fundamental.get('growth_potential', 'N/A')}

**Market Sentiment:**
- Articles Analyzed: {news_data.get('articles_count', 0)}
- Positive: {news_data.get('sentiment_distribution', {}).get('positive', 0)}
- Neutral: {news_data.get('sentiment_distribution', {}).get('neutral', 0)}
- Negative: {news_data.get('sentiment_distribution', {}).get('negative', 0)}

{news_context}
"""
        return context
    
    def _get_recommendation(self, score: int) -> tuple:
        """
        Generate recommendation based on score
        
        Args:
            score: Analysis score (0-100)
            
        Returns:
            Tuple of (recommendation, reason)
        """
        if score >= 80:
            return "STRONG BUY", f"Score {score}/100 - Strong buy signals across technical and fundamental metrics"
        elif score >= 60:
            return "BUY", f"Score {score}/100 - Positive indicators suggest accumulation opportunities"
        elif score >= 40:
            return "HOLD", f"Score {score}/100 - Mixed signals, suitable for long-term holders"
        elif score >= 20:
            return "SELL", f"Score {score}/100 - Negative indicators suggest caution"
        else:
            return "STRONG SELL", f"Score {score}/100 - Strong sell signals, consider exiting positions"
    
    def _assess_risk_level(self, technical: Dict, fundamental: Dict) -> str:
        """Assess investment risk level"""
        volatility = _safe_float(technical.get("volatility")) or 0
        
        if volatility > 0.3:
            return "High"
        elif volatility > 0.15:
            return "Moderate"
        else:
            return "Low"
    
    def _suggest_investment_horizon(self, technical: Dict, fundamental: Dict) -> str:
        """Suggest investment time horizon"""
        trend = technical.get("price_trend", "Sideways")
        
        if trend == "Uptrend":
            return "Short to Medium Term (1-6 months)"
        elif trend == "Downtrend":
            return "Long Term (1+ years) for value investors"
        else:
            return "Medium to Long Term (6 months - 2 years)"
    
    def _count_bullish_indicators(self, technical: Dict, fundamental: Dict) -> int:
        """Count bullish indicators"""
        count = 0
        
        if technical.get("price_trend") == "Uptrend":
            count += 1
        if technical.get("rsi_signal") == "Oversold - Potential Buy Signal":
            count += 1
        if (_safe_float(technical.get("macd_signal")) or 0) > 0:
            count += 1
        if fundamental.get("pe_signal") == "Undervalued":
            count += 1
        if "Below" in fundamental.get("pb_signal", ""):
            count += 1
            
        return count
    
    def _count_bearish_indicators(self, technical: Dict, fundamental: Dict) -> int:
        """Count bearish indicators"""
        count = 0
        
        if technical.get("price_trend") == "Downtrend":
            count += 1
        if technical.get("rsi_signal") == "Overbought - Potential Sell Signal":
            count += 1
        if (_safe_float(technical.get("macd_signal")) or 0) < 0:
            count += 1
        if fundamental.get("pe_signal") == "Overvalued":
            count += 1
        if "Premium" in fundamental.get("pb_signal", ""):
            count += 1
            
        return count
    
    def _calculate_sentiment_impact(self, news: Dict) -> str:
        """Calculate and describe the sentiment impact on the score"""
        sentiment_dist = news.get('sentiment_distribution', {})
        positive = sentiment_dist.get('positive', 0)
        negative = sentiment_dist.get('negative', 0)
        neutral = sentiment_dist.get('neutral', 0)
        total = positive + negative + neutral
        
        if total == 0:
            return "No sentiment data available"
        
        positive_ratio = positive / total
        negative_ratio = negative / total
        
        impact = 0
        description = ""
        
        # Calculate impact (matching the logic in AnalysisAgent.get_combined_score)
        if positive_ratio > 0.6:
            impact = 15
            description = f"Strongly Positive (+{impact} points) - {positive_ratio:.0%} positive news"
        elif positive_ratio > 0.4:
            impact = 10
            description = f"Positive (+{impact} points) - {positive_ratio:.0%} positive news"
        elif positive_ratio > 0.2:
            impact = 5
            description = f"Moderately Positive (+{impact} points) - {positive_ratio:.0%} positive news"
        
        if negative_ratio > 0.6:
            impact = -15
            description = f"Strongly Negative ({impact} points) - {negative_ratio:.0%} negative news"
        elif negative_ratio > 0.4:
            impact = -10
            description = f"Negative ({impact} points) - {negative_ratio:.0%} negative news"
        elif negative_ratio > 0.2:
            impact = -5
            description = f"Moderately Negative ({impact} points) - {negative_ratio:.0%} negative news"
        
        if not description:
            description = "Neutral (0 points) - Balanced or neutral sentiment"
        
        return description
    
    def _format_news_articles(self, articles: list) -> str:
        """Format news articles for detailed analysis report"""
        if not articles:
            return "No news articles available for analysis."
        
        formatted = []
        for i, article in enumerate(articles[:10], 1):  # Show top 10
            sentiment_emoji = {
                'positive': '✅',
                'neutral': '➖',
                'negative': '❌'
            }.get(article.get('sentiment', 'neutral'), '➖')
            
            formatted.append(f"""
{i}. {article.get('title', 'N/A')} [{sentiment_emoji} {article.get('sentiment', 'N/A').upper()}]
   Source: {article.get('source', 'N/A')}
   Link: {article.get('link', 'N/A')}
   Published: {article.get('published', 'N/A')}
   Analyzed Text: "{article.get('analyzed_text', article.get('summary', 'N/A')[:200])}"
""")
        
        return '\n'.join(formatted)
    
    def _count_neutral_indicators(self, technical: Dict, fundamental: Dict) -> int:
        """Count neutral indicators"""
        count = 0
        
        if technical.get("price_trend") == "Sideways":
            count += 1
        if technical.get("rsi_signal") == "Neutral":
            count += 1
        if fundamental.get("pe_signal") == "Fairly Valued":
            count += 1
        if "Fair" in fundamental.get("pb_signal", "") or "Moderate" in fundamental.get("pb_signal", ""):
            count += 1
            
        return count
    
    def _generate_detailed_analysis(self, 
                                   stock_data: Dict,
                                   technical: Dict,
                                   fundamental: Dict,
                                   news: Dict,
                                   score: int) -> str:
        """Generate detailed written analysis"""
        
        analysis = f"""
COMPREHENSIVE STOCK ANALYSIS REPORT
{'='*60}

EXECUTIVE SUMMARY:
{stock_data.get('company_name', 'Stock')} ({stock_data.get('ticker', 'N/A')}) is currently trading at 
{_format_number(stock_data.get('latest_price'), prefix='₹')} with a {_format_number(stock_data.get('price_change_percent'), suffix='%')} change.

TECHNICAL PERSPECTIVE:
- Current Trend: {technical.get('price_trend', 'N/A')}
- RSI (14): {_format_number(technical.get('rsi'))} - {technical.get('rsi_signal', 'N/A')}
- Support Level: {_format_number(technical.get('support_level'), prefix='₹')}
- Resistance Level: {_format_number(technical.get('resistance_level'), prefix='₹')}
- Volatility (Annualized): {_format_percent(technical.get('volatility'))}
- Volume Trend: {technical.get('volume_trend', 'N/A')}

FUNDAMENTAL PERSPECTIVE:
- P/E Ratio: {fundamental.get('pe_ratio', 'N/A')} ({fundamental.get('pe_signal', 'N/A')})
- P/B Ratio: {fundamental.get('pb_ratio', 'N/A')} ({fundamental.get('pb_signal', 'N/A')})
- Valuation Assessment: {fundamental.get('valuation_assessment', 'N/A')}
- Growth Potential: {fundamental.get('growth_potential', 'N/A')}

MARKET SENTIMENT (Contributing to Final Score):
- Articles Analyzed: {news.get('articles_count', 0)}
- Positive Sentiment: {news.get('sentiment_distribution', {}).get('positive', 0)}
- Neutral Sentiment: {news.get('sentiment_distribution', {}).get('neutral', 0)}
- Negative Sentiment: {news.get('sentiment_distribution', {}).get('negative', 0)}
- Sentiment Impact: {self._calculate_sentiment_impact(news)}

NEWS ARTICLES & SENTIMENT ANALYSIS:
{self._format_news_articles(news.get('articles', []))}

FINAL ANALYSIS SCORE: {score}/100
(Technical Analysis + Fundamental Analysis + News Sentiment)

Note: This analysis is based on technical and fundamental metrics. Always conduct 
your own research and consult with a financial advisor before making investment decisions.
        """
        
        return analysis.strip()
    
    def get_report(self) -> Dict:
        """Return the final report"""
        return self.final_report or {"status": "No report generated yet"}
    
    def export_report(self, format: str = "json") -> str:
        """Export report in specified format"""
        if not self.final_report:
            return "No report available"
        
        if format == "json":
            return json.dumps(self.final_report, indent=2, default=str)
        elif format == "text":
            return self.final_report.get("detailed_analysis", "N/A")
        
        return "Unsupported format"
