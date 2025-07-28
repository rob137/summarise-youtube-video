# YouTube Transcript Extractor

A command-line tool to extract YouTube video transcripts and copy them to the clipboard.

## Features

- Extract transcripts from YouTube videos using URLs or video IDs
- Support for multiple languages (with fallback to auto-generated captions)
- Copy transcript directly to clipboard or print to stdout
- Clean, robust error handling

## Installation

```bash
pip install -e .
```

This installs the `yt-trans` command globally.

## Usage

### Command Line

```bash
# Extract transcript and copy to clipboard
yt-trans "https://www.youtube.com/watch?v=VIDEO_ID"

# Or use just the video ID
yt-trans VIDEO_ID

# Specify preferred language(s)
yt-trans VIDEO_ID --lang en --lang es

# Print to stdout instead of copying to clipboard
yt-trans VIDEO_ID --no-copy
```

### Direct Script Execution

You can also run the standalone script directly:

```bash
./yt-transcript "https://www.youtube.com/watch?v=VIDEO_ID"
```

## Dependencies

- `click` - CLI framework
- `pyperclip` - Clipboard access
- `youtube-transcript-api` - YouTube transcript extraction

## Project Structure

- `yt_transcript/cli.py` - Main CLI application using Click framework
- `yt-transcript` - Standalone script (alternative entry point)
- `pyproject.toml` - Project configuration and dependencies

## Error Handling

The tool handles various error conditions gracefully:
- Invalid YouTube URLs
- Videos without transcripts
- Rate limiting from YouTube
- Clipboard access issues
- Network connectivity problems

## Development

### Running Tests

The project includes comprehensive tests for regression testing:

```bash
# Install development dependencies
make install-dev

# Run all tests
make test

# Run tests with coverage
make test-coverage

# Run specific test suites
make test-regression
make test-cli
make test-standalone
```

### Test Coverage

The test suite covers:
- URL parsing and video ID extraction
- Transcript fetching with various error conditions
- CLI argument handling and user interactions
- Clipboard functionality
- Language preference handling
- Performance regression scenarios
- Security validations
- Backward compatibility

### Available Make Commands

```bash
make help           # Show all available commands
make install        # Install package in development mode
make install-dev    # Install with test dependencies
make test           # Run test suite
make clean          # Clean build artifacts
make verify         # Verify installation works
```
