# YouTube Transcript Summarizer Agent Instructions

## Commands
- **Run tool**: `./summarise-video <youtube_url>` or `python3 summarise-video <youtube_url>`
- **Test dependencies**: `yt-dlp --version` and check `GEMINI_API_KEY` env var

Note: Script only accepts a single YouTube URL argument. Output files are automatically saved to `~/transcripts/` directory. API key must be set via `GEMINI_API_KEY` environment variable.

## Architecture
- Single Python script (`summarise-video`) with YouTube transcript extraction and AI summarization
- Dependencies: `yt-dlp` for transcript extraction, `requests` for Gemini API calls
- Uses Gemini 2.5 Pro for both transcript cleaning and summarization
- Configurable 300s API timeout with retry logic and exponential backoff
- Intelligent chunking (20k words max per chunk) to avoid token limits
- Graceful handling of MAX_TOKENS responses with warnings
- Outputs structured markdown with brief/medium/detailed summaries plus timestamped transcript

## Code Style
- Python 3 with type hints (`typing` module)
- Class-based architecture with `YouTubeTranscriptSummarizer` main class
- Error handling with try/catch blocks and graceful fallbacks
- Environment variables for API keys (`.env` file supported)
- Camelcase for class names, snake_case for methods/variables
- Comprehensive docstrings for all methods
- 4-space indentation, max 100 characters per line where possible
- Use f-strings for string formatting
- Extensive assertions for input validation and bug catching
