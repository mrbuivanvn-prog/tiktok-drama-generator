"""
Video idea generation module for TikTok Drama Generator
"""
import random
from typing import List, Dict, Any
from .utils import logger, VideoIdea, save_data, load_data, TrendItem
import json


class IdeaGenerator:
    """Generates video ideas from trending topics."""
    
    def __init__(self, config):
        self.config = config
        self.generation_config = config.get('generation', {})
        self.templates = self.generation_config.get('templates', [
            "Xu hướng {topic} ngày hôm nay - bạn có biết không?",
            "3 điều sorprendente về {topic} mà ít người biết",
            "Tại sao {topic} lại hot trên mạng?",
            "Réaksi cộng đồng wobec {topic}",
            "{topic} - xu hướng đến đỉnh?",
            "Bạn có cùng xu hướng {topic} không?",
            "Phân tích xu hướng {topic} trong 60 giây"
        ])
        self.language = self.generation_config.get('language', 'vi')
        self.max_duration = self.generation_config.get('max_duration_seconds', 60)
    
    def generate_idea(self, trend: TrendItem) -> VideoIdea:
        """Generate a single video idea from a trend."""
        template = random.choice(self.templates)
        idea = template.format(topic=trend.topic)
        
        # Add some variation based on language
        if self.language == 'vi':
            # Already in Vietnamese templates
            pass
        elif self.language == 'en':
            # Convert to English (simplified)
            idea = idea.replace("Xu hướng", "Trend")\
                       .replace("ngày hôm nay", "today")\
                       .replace("bạn có biết không?", "did you know?")\
                       .replace("3 điều sorprendente", "3 surprising facts")\
                       .replace("ít người biết", "few people know")\
                       .replace("Tại sao", "Why")\
                       .replace("lại hot trên mạng", "is trending online")\
                       .replace("Réaksi cộng đồng", "Community reaction")\
                       .replace("về", "about")\
                       .replace("xu hướng đến đỉnh?", "trend peaking?")\
                       .replace("Bạn có cùng", "Are you also")\
                       .replace("không?", "?")\
                       .replace("Phân tích", "Analyze")\
                       .replace("trong 60 giây", "in 60 seconds")
        
        return VideoIdea(
            idea=idea,
            source_trend=trend,
            template_used=template
        )
    
    def generate_ideas(self, trends: List[TrendItem], count: int = None) -> List[VideoIdea]:
        """Generate multiple video ideas from trends."""
        if not trends:
            return []
        
        # Determine how many ideas to generate
        if count is None:
            # Use a reasonable default based on number of trends
            count = min(len(trends), 5)  # Generate up to 5 ideas
        else:
            count = min(count, len(trends))
        
        # Select trends to generate ideas from (weighted by score if available)
        if len(trends) <= count:
            selected_trends = trends
        else:
            # Weighted selection based on score
            weights = [max(1, trend.score) for trend in trends]
            selected_trends = random.choices(trends, weights=weights, k=count)
        
        ideas = []
        for trend in selected_trends:
            try:
                idea = self.generate_idea(trend)
                ideas.append(idea)
                logger.debug(f"Generated idea: '{idea.idea}' from trend: '{trend.topic}'")
            except Exception as e:
                logger.error(f"Error generating idea from trend '{trend.topic}': {e}")
        
        logger.info(f"Generated {len(ideas)} video ideas from {len(trends)} trends")
        return ideas


def save_daily_output(trends: List[TrendItem], ideas: List[VideoIdea], config: Dict):
    """Save daily trends and ideas to files."""
    output_config = config.get('output', {})
    from .utils import get_today_string
    date_str = get_today_string()
    
    # Save trends
    if output_config.get('save_raw_trends', True):
        trends_data = [trend.to_dict() for trend in trends]
        trends_path = f"data/trends/trends_{date_str}.json"
        save_data(trends_data, trends_path, 'json')
    
    # Save ideas
    if output_config.get('save_generated_ideas', True):
        ideas_data = [idea.to_dict() for idea in ideas]
        ideas_path = f"data/ideas/ideas_{date_str}.json"
        save_data(ideas_data, ideas_path, 'json')
        
        # Also save as readable text
        if output_config.get('idea_format', 'json') == 'txt':
            ideas_text_path = f"data/ideas/ideas_{date_str}.txt"
            ideas_text = [idea.idea for idea in ideas]
            save_data(ideas_text, ideas_text_path, 'txt')


def main():
    """Main function to run the trend fetching and idea generation."""
    from .utils import load_config, logger
    from .fetcher import fetch_all_trends
    from .video_creator import create_daily_videos
    
    # Load configuration
    config = load_config()
    if not config:
        logger.error("Failed to load configuration. Exiting.")
        return
    
    logger.info("Starting TikTok Drama Generator")
    
    # Fetch trends
    logger.info("Fetching trending topics...")
    trends = fetch_all_trends(config)
    
    if not trends:
        logger.warning("No trends fetched. Using fallback topics.")
        # Fallback topics
        fallback_topics = [
            "Drama hot hôm nay",
            "Xu hướng TikTok Việt Nam",
            "Giai trí 24h",
            "Sao Việt đang nói gì?",
            "Xu hướng mạng hôm nay"
        ]
        trends = [
            TrendItem(topic=topic, source="fallback", score=70)
            for topic in fallback_topics
        ]
    
    # Generate video ideas
    logger.info("Generating video ideas...")
    generator = IdeaGenerator(config)
    ideas = generator.generate_ideas(trends, count=5)
    
    # Save output
    save_daily_output(trends, ideas, config)
    
    # Create videos if enabled
    video_creation_config = config.get('video_creation', {})
    if video_creation_config.get('enabled', False):
        logger.info("Creating videos from generated ideas...")
        video_paths = create_daily_videos(ideas, config)
        
        # Save video paths
        output_config = config.get('output', {})
        if output_config.get('save_generated_ideas', True):
            from .utils import get_today_string
            date_str = get_today_string()
            video_data = [{'path': path, 'idea': idea.idea} for path, idea in zip(video_paths, ideas)]
            video_path_str = f"data/videos/videos_{date_str}.json"
            save_data(video_data, video_path_str, 'json')
            logger.info(f"Saved video metadata to {video_path_str}")
    
    # Print summary
    from .utils import get_today_string
    print(f"\n=== Daily Summary for {get_today_string()} ===")
    print(f"Fetched {len(trends)} trending topics")
    print(f"Generated {len(ideas)} video ideas")
    if video_creation_config.get('enabled', False):
        print(f"Created {len(video_paths)} videos")
    print("\nTop Video Ideas:")
    for i, idea in enumerate(ideas[:3], 1):
        print(f"{i}. {idea.idea}")
    
    logger.info("Daily generation complete")


if __name__ == "__main__":
    main()