# Daily Drama TikTok Video Generator

A project to automatically generate TikTok video ideas based on daily trending dramas and hot topics.

## Features
- Fetch trending topics from various sources (Twitter, Google Trends, Reddit, web scraping)
- Generate video script ideas based on trends using customizable templates
- Output daily content ideas for TikTok videos
- Extensible architecture for adding new sources and generation methods
- Logging and data persistence

## Project Structure
```
tiktok-drama-generator/
├── src/
│   ├── __init__.py
│   ├── fetcher.py        # Fetch trending topics from various sources
│   ├── generator.py      # Generate video ideas from trends
│   ├── utils.py          # Utility functions
│   └── main.py           # Main entry point
├── config/
│   └── settings.json     # Configuration file
├── data/
│   ├── trends/           # Store fetched trends (JSON)
│   └── ideas/            # Store generated video ideas (JSON and TXT)
├── logs/
│   └── app.log           # Application logs
├── requirements.txt      # Python dependencies
└── README.md
```

## Installation
1. Clone the repository
2. Create a virtual environment: `python3 -m venv venv`
3. Activate the virtual environment: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Configure API keys in `config/settings.json` (if using real APIs)
6. Run the generator: `python -m src.main`

## Configuration
Edit `config/settings.json` to enable/disable sources and adjust parameters:

### Sources
- **google_trends**: Requires pytrends library (install via requirements)
- **reddit**: Requires praw library (install via requirements)
- **twitter**: Requires tweepy library (install via requirements)
- **web_scraping**: No additional dependencies, uses requests and BeautifulSoup

### Generation
- Customize video idea templates in the `templates` array
- Set language (`vi` for Vietnamese, `en` for English)
- Set maximum video duration in seconds

### Output
- Choose whether to save raw trends and generated ideas
- Select output format (json or txt)

## Usage
The script is designed to run daily (via cron or similar scheduler) to:
1. Fetch trending drama topics from configured sources
2. Generate video script ideas based on those trends
3. Save the ideas to the data directory for video creation

### Example Daily Run
```
$ python -m src.main
2026-05-29 16:53:32 | INFO     | __main__:main:36 - ==================================================
2026-05-29 16:53:32 | INFO     | __main__:main:37 - TikTok Drama Generator Starting
2026-05-29 16:53:32 | INFO     | __main__:main:38 - ==================================================
2026-05-29 16:53:32 | INFO     | src.generator:main:129 - Starting TikTok Drama Generator
2026-05-29 16:53:32 | INFO     | src.generator:main:132 - Fetching trending topics...
2026-05-29 16:53:32 | INFO     | src.fetcher:fetch_all_trends:308 - Total unique trends fetched: 0
2026-05-29 16:53:32 | WARNING  | src.generator:main:136 - No trends fetched. Using fallback topics.
2026-05-29 16:53:32 | INFO     | src.generator:main:151 - Generating video ideas...
2026-05-29 16:53:32 | INFO     | src.generator:generate_ideas:89 - Generated 5 video ideas from 5 trends

=== Daily Summary for 2026-05-29 ===
Fetched 5 trending topics
Generated 5 video ideas

Top Video Ideas:
1. 3 điều sorprendente về Drama hot hôm nay mà ít người biết
2: Tại sao Xu hướng TikTok Việt Nam lại hot trên mạng?
3: 3 điều sorprendente về Giai trí 24h mà ít người biết
...
2026-05-29 16:53:32 | INFO     | src.generator:main:167 - Daily generation complete
2026-05-29 16:53:32 | INFO     | __main__:main:42 - Application completed successfully
```

## Extending the Project

### Adding New Trend Sources
1. Create a new class in `fetcher.py` that inherits from `TrendFetcher`
2. Implement the `fetch()` method to return a list of `TrendItem` objects
3. Add the new source to the `create_fetcher` factory function
4. Add configuration for the new source in `settings.json`

### Customizing Video Idea Generation
1. Modify the templates in `config/settings.json` under `generation.templates`
2. Or modify the `IdeaGenerator` class in `generator.py` for more complex logic

### Actual Video Creation
To extend this to actually create videos, you could:
1. Integrate with video editing libraries like moviepy
2. Use text-to-speech services for narration
3. Fetch relevant stock footage or images
4. Combine elements into final video files

## Notes
- The current implementation uses placeholder/fallback data sources since real API keys are not configured
- To use real data sources, obtain API keys and set the corresponding `enabled` flags to `true` in `settings.json`
- Web scraping should be done responsibly and in accordance with website terms of service
- For production use, consider adding error handling, rate limiting, and more sophisticated trend analysis

## Requirements
- Python 3.7+
- Dependencies listed in requirements.txt
- API keys for external services (optional, for real data)

## License
MIT