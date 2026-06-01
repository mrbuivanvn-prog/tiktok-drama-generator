"""
Main entry point for TikTok Drama Generator
"""
import sys
import os
from src.utils import logger
from src.generator import main as run_generator


def setup_logging():
    """Setup logging configuration."""
    from loguru import logger as log
    log.remove()
    log.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    log.add(
        "logs/app.log",
        rotation="10 MB",
        retention="1 week",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG"
    )


def main():
    """Main application entry point."""
    setup_logging()
    logger.info("=" * 50)
    logger.info("TikTok Drama Generator Starting")
    logger.info("=" * 50)
    try:
        run_generator()
        logger.info("Application completed successfully")
    except Exception as e:
        logger.exception(f"Application failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
