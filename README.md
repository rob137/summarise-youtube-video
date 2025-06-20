# YouTube Transcript Summarizer

A command-line tool that extracts YouTube video transcripts and generates AI-powered summaries using Google's Gemini API.

## Features

- Extracts transcripts from YouTube videos using yt-dlp
- Cleans up transcripts with AI (Gemini 2.5 Pro)
- Generates brief, medium, and detailed summaries
- Outputs in Org mode format with timestamped links
- Cost tracking for API usage
- Works offline for basic transcript extraction

## Installation

### Prerequisites

- Python 3.7 or higher
- Gemini API key (optional, for AI features)

### Quick Setup

1. Clone this repository:
```bash
git clone git@github.com:rob137/summarise-youtube-video.git
cd summarise-youtube-video
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Make the script executable:
```bash
chmod +x summarise-video
```

4. Set up your API key (optional):
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

## Usage

### Basic usage:
```bash
./summarise-video https://www.youtube.com/watch?v=VIDEO_ID
```

### With custom output file:
```bash
./summarise-video https://www.youtube.com/watch?v=VIDEO_ID -o my-summary.org
```

### With API key (if not set in environment):
```bash
./summarise-video https://www.youtube.com/watch?v=VIDEO_ID --api-key YOUR_KEY
```

## Output

The tool generates:
- **Brief Summary**: One sentence key takeaway
- **Medium Summary**: One paragraph overview
- **Detailed Summary**: Comprehensive analysis
- **Timestamped Transcript**: Clickable links to video sections
- **Cost Summary**: API usage tracking

Files are saved to `~/transcripts/` by default in Org mode format.

## API Key Setup

Get a free Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey).

Set it as an environment variable:
```bash
export GEMINI_API_KEY="your-api-key-here"
```

Or add it to your `.env` file:
```
GEMINI_API_KEY=your-api-key-here
```

## Dependencies

- **yt-dlp**: Video transcript extraction
- **requests**: API communication
- **Python 3.7+**: Runtime environment

## License

MIT License - see LICENSE file for details.
