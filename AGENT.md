# YouTube Transcript Summarizer Agent Instructions

## Commands
- **Run tool**: `./summarise-video <youtube_url>` or `python3 summarise-video <youtube_url>`
- **With output file**: `./summarise-video <youtube_url> -o output.md`
- **With API key**: `./summarise-video <youtube_url> --api-key YOUR_KEY`
- **Test dependencies**: `yt-dlp --version` and check `GEMINI_API_KEY` env var

## Architecture
- Single Python script (`summarise-video`) with YouTube transcript extraction and AI summarization
- Dependencies: `yt-dlp` for transcript extraction, `requests` for Gemini API calls
- Uses Gemini 1.5 Flash for transcript cleaning and Gemini 2.0 Flash for summarization
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
