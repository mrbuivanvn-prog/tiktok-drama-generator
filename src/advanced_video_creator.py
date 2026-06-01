"""
Advanced video creator module for TikTok Drama Generator.
Creates video slideshows with images, text overlays, and background music.
"""
import os
import random
from pathlib import Path
from typing import Optional, List
import logging
from loguru import logger

from .utils import VideoIdea
from .image_fetcher import ImageFetcher
from .summarizer import summarize_headline

# MoviePy v2 imports as specified
from moviepy import ImageClip, TextClip, ColorClip, CompositeVideoClip, AudioFileClip
from moviepy.video.fx import FadeIn, FadeOut, Resize


class AdvancedVideoCreator:
    """Creates advanced videos with images, text, and music."""
    
    def __init__(self, config):
        self.config = config
        self.output_dir = Path("data/videos")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.video_config = config.get('video_creation', {})
        self.duration = self.video_config.get('duration_seconds', 5)
        self.resolution = self.video_config.get('resolution', (1080, 1920))
        self.fps = self.video_config.get('fps', 24)
        
        self.enable_background_music = self.video_config.get('enable_background_music', False)
        self.background_music_path = self.video_config.get('background_music_path', '')
        
        self.image_fetcher = ImageFetcher(config)
        
        logger.info(f"AdvancedVideoCreator initialized: {self.resolution}, {self.duration}s")
    
    def create_video_from_idea(self, idea: VideoIdea, output_filename: str = None) -> str:
        if output_filename is None:
            safe_text = "".join(c if c.isalnum() else "_" for c in idea.idea[:30])
            timestamp = idea.timestamp.replace(":", "-").replace(" ", "_")
            output_filename = f"video_{safe_text}_{timestamp}"
        
        output_path = self.output_dir / f"{output_filename}.mp4"
        
        try:
            image_path = self.image_fetcher.fetch_image_for_topic(idea.source_trend)
            
            if image_path and Path(image_path).exists():
                logger.info(f"Using image: {image_path}")
                video_clip = ImageClip(image_path)
                img_w, img_h = video_clip.size
                target_w, target_h = self.resolution
                if img_w != target_w or img_h != target_h:
                    scale = max(target_w / img_w, target_h / img_h)
                    new_size = (int(img_w * scale), int(img_h * scale))
                    video_clip = video_clip.with_effects([Resize(new_size)])
                    x_center = video_clip.w // 2
                    y_center = video_clip.h // 2
                    x1 = x_center - target_w // 2
                    y1 = y_center - target_h // 2
                    video_clip = video_clip.crop(x1=x1, y1=y1, width=target_w, height=target_h)
                video_clip = video_clip.with_duration(self.duration)
            else:
                logger.warning("No image available, using solid background")
                video_clip = ColorClip(size=self.resolution, color=(26, 26, 46)).with_duration(self.duration)
            
            headline = idea.idea
            if hasattr(idea, 'source_trend') and idea.source_trend:
                script = summarize_headline(headline)
            else:
                script = headline
            
            headline_text = self._wrap_text(headline, 38)
            headline_clip = TextClip(
                font=None,
                text=headline_text,
                font_size=50,
                color='#FFE400',
                method='caption',
                size=(self.resolution[0] - 40, 320)
            ).with_duration(self.duration * 0.4).with_position(('center', 120))
            
            script_text = self._wrap_text(script, 38)
            script_clip = TextClip(
                font=None,
                text=script_text,
                font_size=34,
                color='#FFFFFF',
                method='caption',
                size=(self.resolution[0] - 40, 700)
            ).with_duration(self.duration * 0.6).with_position(('center', 520)).with_start(self.duration * 0.4)
            
            header_bar = ColorClip(size=(self.resolution[0], 380), color=(0, 0, 0)).with_duration(self.duration * 0.4).with_opacity(0.6).with_position(('center', 60))
            footer_bar = ColorClip(size=(self.resolution[0], 720), color=(0, 0, 0)).with_duration(self.duration * 0.6).with_opacity(0.7).with_position(('center', 460)).with_start(self.duration * 0.4)
            
            final = CompositeVideoClip([video_clip, header_bar, headline_clip, footer_bar, script_clip])
            
            audio = None
            if self.enable_background_music and self.background_music_path and os.path.exists(self.background_music_path):
                try:
                    audio = AudioFileClip(self.background_music_path).subclipped(0, self.duration)
                    audio = audio.volumex(0.3)
                    audio = audio.with_effects([FadeIn(0.5), FadeOut(0.5)])
                    final = final.with_audio(audio)
                except Exception as e:
                    logger.warning(f"Could not add audio: {e}")
            
            final.write_videofile(
                str(output_path),
                fps=self.fps,
                codec='libx264',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
            
            final.close()
            video_clip.close()
            if audio:
                audio.close()
            
            logger.info(f"Video created: {output_path}")
            return str(output_path)
        
        except Exception as e:
            logger.error(f"Error creating video: {e}")
            raise
    
    def create_slideshow_from_trends(self, trends: list, prefix: str = "daily") -> list:
        results = []
        for i, trend in enumerate(trends[:5], 1):
            try:
                script = summarize_headline(trend.topic if hasattr(trend, 'topic') else str(trend))
                idea = VideoIdea(
                    idea=trend.topic if hasattr(trend, 'topic') else str(trend),
                    source_trend=trend,
                    template_used='script_summary'
                )
                path = self.create_video_from_idea(idea, f"{prefix}_slide_{i}")
                results.append(path)
            except Exception as e:
                logger.error(f"Failed slide {i}: {e}")
                continue
        
        return results
    
    def _wrap_text(self, text: str, max_chars: int) -> str:
        """Wrap text to fit within max characters per line."""
        words = text.split()
        lines = []
        current_line = []
        current_len = 0
        
        for word in words:
            if current_len + len(word) + 1 <= max_chars:
                current_line.append(word)
                current_len += len(word) + 1
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_len = len(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return '\n'.join(lines)


def create_news_videos(trends: list, config: dict) -> list:
    """Convenience function to create news summary videos."""
    creator = AdvancedVideoCreator(config)
    return creator.create_slideshow_from_trends(trends, prefix="news")