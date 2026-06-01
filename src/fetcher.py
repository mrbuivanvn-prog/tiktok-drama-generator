"""
Trend fetching module for TikTok Drama Generator
"""
import requests
from bs4 import BeautifulSoup
import time
import random
from typing import List, Dict, Any
from .utils import logger, TrendItem, save_data, load_data
import json
import os


class TrendFetcher:
    """Base class for trend fetchers."""
    
    def __init__(self, config):
        self.config = config
        self.source_name = self.__class__.__name__.replace('Fetcher', '').lower()
    
    def fetch(self) -> List[TrendItem]:
        """Fetch trending topics. To be implemented by subclasses."""
        raise NotImplementedError
    
    def _create_trend_item(self, topic: str, score: int = 0, metadata: Dict = None) -> TrendItem:
        """Create a TrendItem instance."""
        return TrendItem(
            topic=topic.strip(),
            source=self.source_name,
            score=score,
            metadata=metadata or {}
        )


class GoogleTrendsFetcher(TrendFetcher):
    """Fetch trends from Google Trends."""
    
    def __init__(self, config):
        super().__init__(config)
        settings = config.get('sources', {}).get('google_trends', {})
        self.enabled = settings.get('enabled', False)
        self.keywords = settings.get('keywords', [])
        self.geo = settings.get('geo', 'VN')
        self.timeframe = settings.get('timeframe', 'now 1-d')
    
    def fetch(self) -> List[TrendItem]:
        if not self.enabled or not self.keywords:
            return []
        
        try:
            # Note: In a real implementation, you would use pytrends
            # For now, we'll simulate with a placeholder
            logger.info(f"Fetching Google Trends for keywords: {self.keywords}")
            
            # Placeholder implementation
            trends = []
            for keyword in self.keywords[:3]:  # Limit to avoid overuse
                # Simulate some trending variations
                variations = [
                    f"{keyword} hot",
                    f"{keyword} mới nhất",
                    f"xu hướng {keyword}",
                    f"{keyword} tiktok"
                ]
                for variation in variations:
                    item = self._create_trend_item(
                        topic=variation,
                        score=random.randint(50, 100),
                        metadata={'keyword': keyword, 'source': 'google_trends'}
                    )
                    trends.append(item)
            
            logger.info(f"Fetched {len(trends)} trends from Google Trends")
            return trends
            
        except Exception as e:
            logger.error(f"Error fetching Google Trends: {e}")
            return []


class RedditFetcher(TrendFetcher):
    """Fetch trends from Reddit."""
    
    def __init__(self, config):
        super().__init__(config)
        settings = config.get('sources', {}).get('reddit', {})
        self.enabled = settings.get('enabled', False)
        self.subreddits = settings.get('subreddits', [])
        self.limit = settings.get('limit', 25)
    
    def fetch(self) -> List[TrendItem]:
        if not self.enabled or not self.subreddits:
            return []
        
        try:
            logger.info(f"Fetching Reddit trends from subreddits: {self.subreddits}")
            
            # Placeholder implementation
            trends = []
            for subreddit in self.subreddits:
                # Simulate fetching posts
                sample_posts = [
                    f"Hot drama in {subreddit}",
                    f"Trending topic: {subreddit} update",
                    f"What's popular in {subreddit} today",
                    f"Discussion: {subreddit} viral content"
                ]
                for post in sample_posts[:2]:  # Limit samples
                    item = self._create_trend_item(
                        topic=post,
                        score=random.randint(30, 80),
                        metadata={'subreddit': subreddit, 'source': 'reddit'}
                    )
                    trends.append(item)
            
            logger.info(f"Fetched {len(trends)} trends from Reddit")
            return trends
            
        except Exception as e:
            logger.error(f"Error fetching Reddit trends: {e}")
            return []


class TwitterFetcher(TrendFetcher):
    """Fetch trends from Twitter/X."""
    
    def __init__(self, config):
        super().__init__(config)
        settings = config.get('sources', {}).get('twitter', {})
        self.enabled = settings.get('enabled', False)
        self.keywords = settings.get('keywords', [])
        self.lang = settings.get('lang', 'vi')
        self.count = settings.get('count', 50)
    
    def fetch(self) -> List[TrendItem]:
        if not self.enabled or not self.keywords:
            return []
        
        try:
            logger.info(f"Fetching Twitter trends for keywords: {self.keywords}")
            
            # Placeholder implementation
            trends = []
            for keyword in self.keywords:
                # Simulate tweets
                sample_tweets = [
                    f"Everyone talking about {keyword}",
                    f"{keyword} is trending now",
                    f"Breaking: {keyword} update",
                    f"Why is {keyword} everywhere?",
                    f"My thoughts on {keyword}"
                ]
                for tweet in sample_tweets[:2]:
                    item = self._create_trend_item(
                        topic=tweet,
                        score=random.randint(40, 90),
                        metadata={'keyword': keyword, 'source': 'twitter'}
                    )
                    trends.append(item)
            
            logger.info(f"Fetched {len(trends)} trends from Twitter")
            return trends
            
        except Exception as e:
            logger.error(f"Error fetching Twitter trends: {e}")
            return []


class WebScrapingFetcher(TrendFetcher):
    """Fetch trends from web scraping news sites."""
    
    def __init__(self, config):
        super().__init__(config)
        settings = config.get('sources', {}).get('web_scraping', {})
        self.enabled = settings.get('enabled', False)
        self.sites = settings.get('sites', [])
    
    def fetch(self) -> List[TrendItem]:
        if not self.enabled or not self.sites:
            return []
        
        try:
            logger.info(f"Fetching trends from {len(self.sites)} websites via scraping")
            
            trends = []
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            for site in self.sites:
                try:
                    site_name = site.get('name', 'Unknown')
                    url = site.get('url', '')
                    section = site.get('section', '')
                    
                    if not url:
                        continue
                    
                    full_url = url
                    if section and not url.endswith('/'):
                        full_url += '/' + section
                    elif section:
                        full_url += section
                    
                    logger.debug(f"Scraping {site_name} from {full_url}")
                    
                    response = requests.get(full_url, headers=headers, timeout=10)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    headlines = []
                    selectors = [
                        'h1', 'h2', 'h3',
                        '.title', '.headline', '.post-title',
                        'article h2', 'article h3',
                        '[class*="title"]', '[class*="headline"]'
                    ]
                    
                    for selector in selectors:
                        elements = soup.select(selector)
                        for elem in elements[:5]:
                            text = elem.get_text(strip=True)
                            if text and len(text) > 10 and len(text) < 200:
                                headlines.append(text)
                    
                    headlines = list(dict.fromkeys(headlines))[:10]
                    
                    drama_keywords = [
                        'drama', 'hot', 'trend', 'viral', 'tiktok', 'giai tri', 'sao', 'phim', 'nhac', 'video',
                        'chung ket', 'tuyen sinh', 'thi cu', 'dien vien', 'ca si', 'streamer', 'mang xa hoi',
                        'bien dong', 'gay tranh cai', 'netizen', 'clip', 'hallmark', 'thinh hanh', 'xuat hien',
                    ]
                    for headline in headlines:
                        lower = headline.lower()
                        if any(keyword in lower for keyword in drama_keywords) or len(headline) >= 12:
                            item = self._create_trend_item(
                                topic=headline,
                                score=random.randint(60, 95),
                                metadata={
                                    'site': site_name,
                                    'url': full_url,
                                    'source': 'web_scraping'
                                }
                            )
                            trends.append(item)
                
                except Exception as e:
                    logger.error(f"Error scraping {site.get('name', 'unknown site')}: {e}")
                    continue
                
                time.sleep(random.uniform(1, 3))
            
            logger.info(f"Fetched {len(trends)} trends from web scraping")
            return trends
            
        except Exception as e:
            logger.error(f"Error in web scraping fetcher: {e}")
            return []


class FacebookFetcher(TrendFetcher):
    """Fetch trends from Facebook."""
    
    def __init__(self, config):
        super().__init__(config)
        settings = config.get('sources', {}).get('facebook', {})
        self.enabled = settings.get('enabled', False)
        self.pages = settings.get('pages', [])
        self.access_token = settings.get('access_token', '')
    
    def fetch(self) -> List[TrendItem]:
        if not self.enabled:
            return []
        
        try:
            logger.info(f"Fetching Facebook trends from {len(self.pages)} pages")
            
            trends = []
            
            if self.access_token and self.pages:
                for page in self.pages:
                    try:
                        page_id = page.get('id', '')
                        page_name = page.get('name', page_id)
                        
                        url = f"https://graph.facebook.com/v18.0/{page_id}/posts"
                        params = {
                            'access_token': self.access_token,
                            'fields': 'message,created_time,likes.summary(true)',
                            'limit': 10
                        }
                        
                        response = requests.get(url, params=params, timeout=10)
                        response.raise_for_status()
                        data = response.json()
                        
                        posts = data.get('data', [])
                        for post in posts:
                            message = post.get('message', '')
                            if message and len(message) > 10:
                                likes = post.get('likes', {}).get('summary', {}).get('total_count', 0)
                                score = min(100, int(likes / 10) + 50)
                                
                                item = self._create_trend_item(
                                    topic=message[:200],
                                    score=score,
                                    metadata={
                                        'page': page_name,
                                        'likes': likes,
                                        'source': 'facebook'
                                    }
                                )
                                trends.append(item)
                        
                        time.sleep(1)
                    
                    except Exception as e:
                        logger.error(f"Error fetching from Facebook page {page.get('name', page_id)}: {e}")
                        continue
            else:
                logger.warning("Facebook fetcher enabled but no access_token or pages configured")
                logger.info("Add access_token and pages to config/settings.json under 'facebook' section")
            
            logger.info(f"Fetched {len(trends)} trends from Facebook")
            return trends
            
        except Exception as e:
            logger.error(f"Error in Facebook fetcher: {e}")
            return []


def create_fetcher(fetcher_type: str, config: Dict) -> TrendFetcher:
    """Factory function to create fetcher instances."""
    fetchers = {
        'google_trends': GoogleTrendsFetcher,
        'reddit': RedditFetcher,
        'twitter': TwitterFetcher,
        'facebook': FacebookFetcher,
        'web_scraping': WebScrapingFetcher
    }
    
    fetcher_class = fetchers.get(fetcher_type)
    if not fetcher_class:
        raise ValueError(f"Unknown fetcher type: {fetcher_type}")
    
    return fetcher_class(config)


def fetch_all_trends(config: Dict) -> List[TrendItem]:
    """Fetch trends from all enabled sources."""
    all_trends = []
    sources = config.get('sources', {})
    
    fetcher_types = ['google_trends', 'reddit', 'twitter', 'facebook', 'web_scraping']
    
    for fetcher_type in fetcher_types:
        fetcher_config = sources.get(fetcher_type, {})
        if fetcher_config.get('enabled', False):
            try:
                fetcher = create_fetcher(fetcher_type, config)
                trends = fetcher.fetch()
                all_trends.extend(trends)
                logger.info(f"Fetched {len(trends)} trends from {fetcher_type}")
            except Exception as e:
                logger.error(f"Error creating or using {fetcher_type} fetcher: {e}")
    
    # Remove duplicates based on topic similarity
    unique_trends = []
    seen_topics = set()
    
    for trend in all_trends:
        # Simple deduplication based on lowercase topic
        topic_key = trend.topic.lower().strip()
        if topic_key not in seen_topics and len(topic_key) > 5:
            seen_topics.add(topic_key)
            unique_trends.append(trend)
    
    logger.info(f"Total unique trends fetched: {len(unique_trends)}")
    return unique_trends