# YouTube Transcript Summarizer - AGENT.md

## Build/Test/Lint Commands
- **Run main script**: `./summarise-video <youtube_url>`
- **Install dependencies**: `pip install -r requirements.txt` or `make install`
- **Check syntax**: `python3 -m py_compile summarise-video`
- **Format code**: `black summarise-video` or `make format`
- **Lint code**: `ruff check summarise-video` or `make lint`
- **Type check**: `mypy summarise-video` or `make typecheck`
- **If dependencies are missing**, run `make install` to fetch them
- **Aggregate**: `make check` runs formatting, linting, type checking and syntax
  compilation
- **No formal tests**: No test suite exists; functionality tested via execution
- **Environment**: Requires `GEMINI_API_KEY` in `.env` or environment

## Architecture & Codebase
- **Single file application**: `summarise-video` (Python 3 executable)
- **Core class**: `YouTubeTranscriptSummarizer` handles all functionality
- **External dependencies**: yt-dlp (YouTube transcript extraction), requests (HTTP), Gemini AI API
- **Output directory**: Creates `~/transcripts/` for .org files
- **Config**: Environment variables via `.env` file

## Code Style & Conventions
- **Type hints**: Extensive use throughout (`typing` module)
- **Assertions**: Heavy use for input validation and defensive programming
- **Error handling**: Try/catch with sys.exit(1) on failures
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **String formatting**: f-strings preferred
- **Constants**: ALL_CAPS for class-level constants
- **Docstrings**: Triple-quoted strings for function documentation
- **Security**: Proper handling of API keys, no hardcoded secrets
