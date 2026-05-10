"""
Fundamental and Technical Analysis Agent
Performs technical and fundamental analysis on stocks
"""

import pandas as pd
import numpy as np
import math
from datetime import datetime
import logging
from typing import Dict, Tuple
import ta
import config

# Configure logging based on config
log_level = logging.DEBUG if config.DEBUG_MODE else logging.INFO
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)

if config.DEBUG_MODE:
    logger.debug("AnalysisAgent initialized in DEBUG mode")


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


class AnalysisAgent:
    """Agent responsible for fundamental and technical analysis"""
    
    def __init__(self):
        self.technical_analysis = {}
        self.fundamental_analysis = {}
        self.ticker = None
    
    def technical_analysis_report(self, stock_data: pd.DataFrame, ticker: str) -> Dict:
        """
        Perform technical analysis on stock data
        
        Args:
            stock_data: DataFrame with OHLCV data
            ticker: Stock ticker
            
        Returns:
            Dictionary containing technical analysis metrics
        """
        try:
            self.ticker = ticker
            analysis = {}
            
            # Ensure we have enough data
            if len(stock_data) < 50:
                return {"error": "Insufficient data for analysis", "data_points": len(stock_data)}
            
            # Moving Averages
            analysis["sma_20"] = float(stock_data['Close'].tail(20).mean())
            analysis["sma_50"] = float(stock_data['Close'].tail(50).mean())
            analysis["sma_200"] = float(stock_data['Close'].tail(200).mean()) if len(stock_data) >= 200 else None
            
            # EMA
            ema_12 = ta.trend.ema_indicator(stock_data['Close'], window=12).iloc[-1]
            ema_26 = ta.trend.ema_indicator(stock_data['Close'], window=26).iloc[-1]
            analysis["ema_12"] = float(ema_12)
            analysis["ema_26"] = float(ema_26)
            
            # RSI (Relative Strength Index)
            rsi = ta.momentum.rsi(stock_data['Close'], window=14).iloc[-1]
            analysis["rsi"] = float(rsi)
            analysis["rsi_signal"] = self._interpret_rsi(rsi)
            
            # MACD
            macd_indicator = ta.trend.MACD(stock_data['Close'], window_fast=12, window_slow=26, window_sign=9)
            macd_line = macd_indicator.macd()
            macd_signal_line = macd_indicator.macd_signal()
            analysis["macd"] = float(macd_line.iloc[-1]) if not macd_line.empty else 0
            analysis["macd_signal"] = float(macd_line.iloc[-1] - macd_signal_line.iloc[-1]) if not macd_line.empty else 0
            
            # Bollinger Bands
            bb_indicator = ta.volatility.BollingerBands(stock_data['Close'], window=20, window_dev=2)
            bb_upper = bb_indicator.bollinger_hband()
            bb_middle = bb_indicator.bollinger_mavg()
            bb_lower = bb_indicator.bollinger_lband()
            analysis["bb_upper"] = float(bb_upper.iloc[-1]) if not bb_upper.empty else None
            analysis["bb_middle"] = float(bb_middle.iloc[-1]) if not bb_middle.empty else None
            analysis["bb_lower"] = float(bb_lower.iloc[-1]) if not bb_lower.empty else None
            
            # Current price analysis
            current_price = stock_data['Close'].iloc[-1]
            analysis["current_price"] = float(current_price)
            
            # Price trend
            analysis["price_trend"] = self._determine_trend(stock_data['Close'].tail(20).values)
            analysis["support_level"] = float(stock_data['Low'].tail(20).min())
            analysis["resistance_level"] = float(stock_data['High'].tail(20).max())
            
            # Volume analysis
            avg_volume = stock_data['Volume'].tail(20).mean()
            current_volume = stock_data['Volume'].iloc[-1]
            analysis["volume_trend"] = "Above Average" if current_volume > avg_volume else "Below Average"
            
            # Volatility (Standard Deviation)
            returns = stock_data['Close'].pct_change()
            volatility = returns.std() * np.sqrt(252)  # Annualized
            analysis["volatility"] = float(volatility)
            
            self.technical_analysis = analysis
            
            return {
                "success": True,
                "ticker": ticker,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in technical analysis: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "ticker": ticker
            }
    
    def fundamental_analysis_report(self, stock_info: Dict) -> Dict:
        """
        Perform fundamental analysis based on stock info
        
        Args:
            stock_info: Dictionary containing stock fundamental data
            
        Returns:
            Dictionary containing fundamental analysis metrics
        """
        try:
            analysis = {}
            
            # Valuation Metrics
            pe_ratio = _safe_float(stock_info.get('pe_ratio'))
            pb_ratio = _safe_float(stock_info.get('pb_ratio'))
            
            analysis["pe_ratio"] = pe_ratio if pe_ratio is not None else 'N/A'
            analysis["pe_signal"] = self._interpret_pe(pe_ratio) if pe_ratio is not None else 'N/A'
            
            analysis["pb_ratio"] = pb_ratio if pb_ratio is not None else 'N/A'
            analysis["pb_signal"] = self._interpret_pb(pb_ratio) if pb_ratio is not None else 'N/A'
            
            # Profitability
            analysis["dividend_yield"] = stock_info.get('dividend_yield', 0)
            analysis["market_cap"] = stock_info.get('market_cap', 'N/A')
            
            # Generate qualitative assessment
            analysis["valuation_assessment"] = self._assess_valuation(pe_ratio, pb_ratio)
            analysis["growth_potential"] = self._assess_growth(stock_info)
            
            self.fundamental_analysis = analysis
            
            return {
                "success": True,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in fundamental analysis: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _interpret_rsi(self, rsi: float) -> str:
        """Interpret RSI value"""
        if rsi >= 70:
            return "Overbought - Potential Sell Signal"
        elif rsi <= 30:
            return "Oversold - Potential Buy Signal"
        else:
            return "Neutral"
    
    def _interpret_pe(self, pe_ratio: float) -> str:
        """Interpret P/E ratio"""
        if pe_ratio < 15:
            return "Undervalued"
        elif 15 <= pe_ratio <= 25:
            return "Fairly Valued"
        else:
            return "Overvalued"
    
    def _interpret_pb(self, pb_ratio: float) -> str:
        """Interpret P/B ratio"""
        if pb_ratio < 1:
            return "Trading Below Book Value - Potential Value Buy"
        elif 1 <= pb_ratio <= 3:
            return "Fair Valuation"
        else:
            return "Premium Valuation"
    
    def _determine_trend(self, prices: np.ndarray) -> str:
        """Determine price trend from recent prices"""
        if len(prices) < 2:
            return "Insufficient Data"
        
        recent_price = prices[-1]
        previous_price = prices[0]
        
        if recent_price > previous_price * 1.02:
            return "Uptrend"
        elif recent_price < previous_price * 0.98:
            return "Downtrend"
        else:
            return "Sideways"
    
    def _assess_valuation(self, pe: float, pb: float) -> str:
        """Assess overall valuation"""
        pe = _safe_float(pe)
        pb = _safe_float(pb)
        
        if pe is not None and pb is not None:
            if pe < 20 and pb < 2:
                return "Attractive Valuation"
            elif pe > 25 or pb > 3:
                return "Expensive Valuation"
            else:
                return "Moderate Valuation"
        return "Insufficient Data"
    
    def _assess_growth(self, stock_info: Dict) -> str:
        """Assess growth potential"""
        # This is a simplified assessment
        return "Moderate to High Growth Potential"
    
    def get_combined_score(self, technical: Dict, fundamental: Dict, news_sentiment: Dict = None) -> int:
        """
        Calculate combined score for buy/hold/sell recommendation
        
        Args:
            technical: Technical analysis data
            fundamental: Fundamental analysis data
            news_sentiment: News sentiment data (optional)
        
        Returns:
            Score from 0-100
        """
        score = 50  # Start at neutral
        
        # Technical analysis scoring (max +30, min -30)
        if 'rsi' in technical:
            rsi = _safe_float(technical['rsi'])
            if rsi is not None and rsi < 30:
                score += 10
            elif rsi is not None and rsi > 70:
                score -= 10
        
        if 'price_trend' in technical:
            if technical['price_trend'] == "Uptrend":
                score += 15
            elif technical['price_trend'] == "Downtrend":
                score -= 15
        
        if 'macd_signal' in technical:
            macd_signal = _safe_float(technical['macd_signal'])
            if macd_signal is not None and macd_signal > 0:
                score += 5
        
        # Fundamental analysis scoring (max +15, min -10)
        if 'pe_signal' in fundamental:
            signal = fundamental['pe_signal']
            if signal == "Undervalued":
                score += 10
            elif signal == "Overvalued":
                score -= 10
        
        if 'pb_signal' in fundamental:
            signal = str(fundamental['pb_signal'])
            if "Undervalued" in signal or "Below" in signal:
                score += 5
        
        # News sentiment scoring (max +15, min -15)
        if news_sentiment:
            sentiment_dist = news_sentiment.get('sentiment_distribution', {})
            positive = sentiment_dist.get('positive', 0)
            negative = sentiment_dist.get('negative', 0)
            neutral = sentiment_dist.get('neutral', 0)
            total = positive + negative + neutral
            
            if total > 0:
                # Calculate sentiment ratio
                positive_ratio = positive / total
                negative_ratio = negative / total
                
                # Strong positive sentiment
                if positive_ratio > 0.6:
                    score += 15
                elif positive_ratio > 0.4:
                    score += 10
                elif positive_ratio > 0.2:
                    score += 5
                
                # Strong negative sentiment
                if negative_ratio > 0.6:
                    score -= 15
                elif negative_ratio > 0.4:
                    score -= 10
                elif negative_ratio > 0.2:
                    score -= 5
        
        return max(0, min(100, score))
    
    def get_summary(self) -> dict:
        """Return summary of analysis"""
        return {
            "technical_analysis": self.technical_analysis or "Not performed",
            "fundamental_analysis": self.fundamental_analysis or "Not performed"
        }
