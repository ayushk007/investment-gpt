"""
Latest Market News Scraper Agent
Collects latest news and long-term plans for stocks
"""

import requests
import feedparser
from datetime import datetime, timedelta
import logging
from typing import List, Dict
import config

# Configure logging based on config
log_level = logging.DEBUG if config.DEBUG_MODE else logging.INFO
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)

if config.DEBUG_MODE:
    logger.debug("NewsScraperAgent initialized in DEBUG mode")


class NewsScraperAgent:
    """Agent responsible for scraping news and announcements"""
    
    def __init__(self):
        self.news_data = []
        self.ticker = None
    
    def fetch_news(self, company_name: str, ticker: str = None, days: int = 30) -> dict:
        """
        Fetch latest news about the company
        
        Args:
            company_name: Name of the company
            ticker: Stock ticker symbol
            days: Number of days to look back
            
        Returns:
            Dictionary containing news articles
        """
        try:
            news_articles = []
            
            # Search for news from multiple sources
            search_queries = [
                f"{company_name} stock",
                f"{company_name} earnings",
                f"{company_name} news",
            ]
            
            if ticker:
                search_queries.append(ticker)
            
            # Try using feedparser for RSS feeds (common for financial news)
            news_sources = [
                f"https://feeds.bloomberg.com/markets/news.rss",
                f"https://feeds.reuters.com/finance/Markets",
            ]
            
            for source in news_sources:
                try:
                    feed = feedparser.parse(source)
                    for entry in feed.entries[:5]:
                        if any(q.lower() in entry.get('title', '').lower() 
                               or q.lower() in entry.get('summary', '').lower() 
                               for q in search_queries):
                            
                            article = {
                                "title": entry.get('title', 'N/A'),
                                "summary": entry.get('summary', 'N/A')[:500],
                                "source": source,
                                "published": entry.get('published', 'N/A'),
                                "link": entry.get('link', 'N/A')
                            }
                            news_articles.append(article)
                except Exception as e:
                    logger.warning(f"Error fetching from {source}: {str(e)}")
                    continue
            
            # Simulate fetching from a financial API (in production, use actual API)
            # This is a placeholder for real API integration
            sample_news = self._get_sample_news(company_name, ticker)
            news_articles.extend(sample_news)
            
            # Remove duplicates
            seen = set()
            unique_articles = []
            for article in news_articles:
                title_key = article.get('title', '').lower()
                if title_key not in seen:
                    seen.add(title_key)
                    unique_articles.append(article)
            
            # Analyze sentiment for each article
            analyzed_articles = []
            for article in unique_articles[:20]:
                text_to_analyze = f"{article.get('title', '')} {article.get('summary', '')}"
                sentiment = self.analyze_sentiment(text_to_analyze)
                article['sentiment'] = sentiment
                article['analyzed_text'] = text_to_analyze[:300]  # Store snippet of analyzed text
                analyzed_articles.append(article)
            
            self.news_data = analyzed_articles
            self.ticker = ticker
            
            # Calculate sentiment distribution
            sentiment_counts = {
                'positive': sum(1 for a in analyzed_articles if a['sentiment'] == 'positive'),
                'neutral': sum(1 for a in analyzed_articles if a['sentiment'] == 'neutral'),
                'negative': sum(1 for a in analyzed_articles if a['sentiment'] == 'negative')
            }
            
            return {
                "success": True,
                "ticker": ticker,
                "company_name": company_name,
                "articles_count": len(analyzed_articles),
                "articles": analyzed_articles,
                "sentiment_distribution": sentiment_counts,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching news: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "ticker": ticker
            }
    
    def _get_sample_news(self, company_name: str, ticker: str = None) -> List[Dict]:
        """Generate sample news for demonstration"""
        sample_articles = [
            {
                "title": f"{company_name} reports strong Q1 earnings",
                "summary": f"{company_name} exceeded analyst expectations with robust Q1 performance driven by strong demand and operational efficiency.",
                "source": "Financial News",
                "published": (datetime.now() - timedelta(days=1)).isoformat(),
                "link": "#"
            },
            {
                "title": f"{company_name} announces new expansion plans",
                "summary": f"The company announced plans to expand operations across new markets, targeting 30% growth over the next 2 years.",
                "source": "Corporate News",
                "published": (datetime.now() - timedelta(days=3)).isoformat(),
                "link": "#"
            },
            {
                "title": f"{company_name} receives industry award",
                "summary": f"{company_name} was recognized for innovation and excellence in the industry, strengthening its market position.",
                "source": "Industry Updates",
                "published": (datetime.now() - timedelta(days=5)).isoformat(),
                "link": "#"
            }
        ]
        return sample_articles
    
    def analyze_sentiment(self, text: str) -> str:
        """
        Simple sentiment analysis (can be enhanced with ML)
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment label: 'positive', 'neutral', 'negative'
        """
        positive_words = ['strong', 'growth', 'excellent', 'robust', 'award', 'success', 'surge', 'beat', 'profit']
        negative_words = ['decline', 'loss', 'poor', 'weak', 'miss', 'fall', 'risk', 'challenge', 'downgrade']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def get_summary(self) -> dict:
        """Return summary of news data"""
        if not self.news_data:
            return {"status": "No news scraped yet"}
        
        sentiments = [self.analyze_sentiment(article.get('title', '')) for article in self.news_data]
        
        return {
            "status": "News successfully scraped",
            "ticker": self.ticker,
            "articles_count": len(self.news_data),
            "sentiment_distribution": {
                "positive": sentiments.count("positive"),
                "neutral": sentiments.count("neutral"),
                "negative": sentiments.count("negative")
            }
        }
