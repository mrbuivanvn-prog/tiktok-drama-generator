"""
Image fetcher module for TikTok Drama Generator.
Fetches images to illustrate news/trends.
"""
import os
import random
import requests
from pathlib import Path
from typing import Optional
import logging

from .utils import logger

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False


class ImageFetcher:
    """Fetches images for video content."""
    
    def __init__(self, config):
        self.config = config
        self.cache_dir = Path("data/assets/images")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def fetch_image_for_topic(self, trend, max_size=(1080, 1920)) -> Optional[str]:
        """
        Fetch or select an image for a trend topic.
        Returns path to image file or None.
        """
        if not trend or not hasattr(trend, 'metadata'):
            return self._get_fallback_image()
        
        metadata = trend.metadata or {}
        url = metadata.get('url', '')
        source = metadata.get('source', '')
        
        # Try to get image from the article/source page
        image_path = None
        
        if source == 'web_scraping' and url:
            image_path = self._scrape_image_from_url(url)
        
        if not image_path:
            image_path = self._get_fallback_image()
        
        return image_path
    
    def _scrape_image_from_url(self, url: str) -> Optional[str]:
        """Try to extract a main image from the article page."""
        if not HAS_BS4:
            return None
        
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, 'html.parser')
            
            # Try Open Graph image
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                img_url = og_image['content']
                return self._download_image(img_url, 'og')
            
            # Try Twitter image
            twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
            if twitter_image and twitter_image.get('content'):
                img_url = twitter_image['content']
                return self._download_image(img_url, 'twitter')
            
            # Try first large image in article
            article = soup.find('article') or soup.find('div', class_='content') or soup
            imgs = article.find_all('img')
            for img in imgs:
                src = img.get('src') or img.get('data-src')
                if src and self._is_valid_image(src):
                    return self._download_image(src, 'article')
            
            return None
            
        except Exception as e:
            logger.debug(f"Could not scrape image from {url}: {e}")
            return None
    
    def _is_valid_image(self, url: str) -> bool:
        """Check if URL looks like an image."""
        url = url.lower()
        return any(ext in url for ext in ['.jpg', '.jpeg', '.png', '.webp'])
    
    def _download_image(self, url: str, prefix: str) -> Optional[str]:
        """Download an image and cache it."""
        try:
            if url.startswith('//'):
                url = 'https:' + url
            elif url.startswith('/'):
                from urllib.parse import urlparse
                base = self.config.get('sources', {}).get('web_scraping', {}).get('sites', [{}])[0].get('url', '')
                if base:
                    url = base.rstrip('/') + url
            
            resp = requests.get(url, headers=self.headers, timeout=15)
            resp.raise_for_status()
            
            fmt = 'png'
            if '.jpg' in url.lower() or '.jpeg' in url.lower():
                fmt = 'jpg'
            elif '.webp' in url.lower():
                fmt = 'webp'
            
            cache_path = self.cache_dir / f"{prefix}_{hash(url) % 100000}.{fmt}"
            with open(cache_path, 'wb') as f:
                f.write(resp.content)
            
            logger.debug(f"Downloaded image: {cache_path}")
            return str(cache_path)
            
        except Exception as e:
            logger.debug(f"Failed to download image {url}: {e}")
            return None
    
    def _get_fallback_image(self) -> Optional[str]:
        """Get a fallback gradient or pattern image."""
        try:
            from PIL import Image, ImageDraw
            cache_path = self.cache_dir / "fallback_bg.png"
            
            if not cache_path.exists():
                img = Image.new('RGB', (1080, 1920), (26, 26, 46))
                draw = ImageDraw.Draw(img)
                for y in range(1920):
                    r = int(26 + (y / 1920) * 20)
                    g = int(26 + (y / 1920) * 10)
                    b = int(46 + (y / 1920) * 30)
                    draw.line([(0, y), (1080, y)], fill=(r, g, b))
                img.save(cache_path, 'PNG')
            
            return str(cache_path)
        except Exception as e:
            logger.debug(f"Could not create fallback image: {e}")
            return None
    
    def cleanup_old_images(self, keep=50):
        """Clean up old cached images."""
        if not self.cache_dir.exists():
            return
        
        images = sorted(self.cache_dir.glob('*.png') + self.cache_dir.glob('*.jpg') + self.cache_dir.glob('*.webp'),
                       key=lambda p: p.stat().st_mtime, reverse=True)
        for img in images[keep:]:
            try:
                img.unlink()
            except Exception:
                pass
