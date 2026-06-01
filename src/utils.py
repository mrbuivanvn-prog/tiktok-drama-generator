"""
Utility functions for the TikTok Drama Generator
"""
import json
import os
import logging
from datetime import datetime
from pathlib import Path
from loguru import logger


def load_config(config_path="config/settings.json"):
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config file: {e}")
        return {}


def ensure_directory(directory_path):
    """Ensure a directory exists, create if it doesn't."""
    Path(directory_path).mkdir(parents=True, exist_ok=True)


def save_data(data, filepath, format='json'):
    """Save data to file in specified format."""
    ensure_directory(os.path.dirname(filepath))
    
    try:
        if format == 'json':
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        elif format == 'txt':
            with open(filepath, 'w', encoding='utf-8') as f:
                if isinstance(data, list):
                    f.write('\n'.join(str(item) for item in data))
                else:
                    f.write(str(data))
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        logger.debug(f"Data saved to {filepath}")
        return True
    except Exception as e:
        logger.error(f"Error saving data to {filepath}: {e}")
        return False


def load_data(filepath, format='json'):
    """Load data from file."""
    try:
        if not os.path.exists(filepath):
            logger.warning(f"File not found: {filepath}")
            return None
            
        if format == 'json':
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        elif format == 'txt':
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read().strip()
        else:
            raise ValueError(f"Unsupported format: {format}")
    except Exception as e:
        logger.error(f"Error loading data from {filepath}: {e}")
        return None


def get_today_string():
    """Get today's date as string in YYYY-MM-DD format."""
    return datetime.now().strftime("%Y-%m-%d")


def get_timestamp():
    """Get current timestamp string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class TrendItem:
    """Represents a trending topic."""
    
    def __init__(self, topic, source, score=0, metadata=None):
        self.topic = topic
        self.source = source
        self.score = score
        self.metadata = metadata or {}
        self.timestamp = get_timestamp()
    
    def to_dict(self):
        return {
            'topic': self.topic,
            'source': self.source,
            'score': self.score,
            'metadata': self.metadata,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data):
        item = cls(
            topic=data['topic'],
            source=data['source'],
            score=data.get('score', 0),
            metadata=data.get('metadata', {})
        )
        item.timestamp = data.get('timestamp', get_timestamp())
        return item


class VideoIdea:
    """Represents a generated video idea."""
    
    def __init__(self, idea, source_trend, template_used=None):
        self.idea = idea
        self.source_trend = source_trend
        self.template_used = template_used
        self.timestamp = get_timestamp()
    
    def to_dict(self):
        return {
            'idea': self.idea,
            'source_trend': self.source_trend.to_dict() if hasattr(self.source_trend, 'to_dict') else self.source_trend,
            'template_used': self.template_used,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data):
        idea = cls(
            idea=data['idea'],
            source_trend=data['source_trend'],
            template_used=data.get('template_used')
        )
        idea.timestamp = data.get('timestamp', get_timestamp())
        return idea