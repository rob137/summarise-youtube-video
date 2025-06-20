# YouTube Transcript Summarizer

A command-line tool that extracts YouTube video transcripts and generates AI-powered summaries using Google's Gemini API.

## Features

- Extracts transcripts from YouTube videos using yt-dlp
- Cleans up transcripts with AI (Gemini 2.0 Flash for cleaning, Gemini 2.5 Pro for summaries)
- Generates brief, medium, and detailed summaries
- Outputs in Org mode format with timestamped links
- Cost tracking for API usage
- Intelligent chunking to handle long videos
- Retry logic with exponential backoff for reliability
- Progress indicators with timing display
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

The script takes only one argument - the YouTube URL. Output files are automatically saved to `~/transcripts/` and the API key must be set as an environment variable.

## Output

The tool generates:
- **Brief Summary**: One sentence key takeaway
- **Medium Summary**: One paragraph overview
- **Detailed Summary**: Comprehensive analysis
- **Timestamped Transcript**: Clickable links to video sections
- **Cost Summary**: API usage tracking

Files are saved to `~/transcripts/` by default in Org mode format.

### Example Output

Here's what the output looks like when run on the first ever YouTube video "Me at the zoo":

```bash
./summarise-video https://www.youtube.com/watch?v=jNQXAC9IVRw
```

> **🔸 BRIEF SUMMARY:**
> The speaker, standing in front of the elephants at the zoo, observes that the cool thing about them is their very long trunks.
> 
> **🔸 MEDIUM SUMMARY:**
> The speaker begins by establishing his location at the zoo, specifically in front of the elephant enclosure. He shares a single, simple observation: the "cool thing" about the elephants is their "really long trunks." He then abruptly concludes his commentary, stating that this observation is "pretty much all there is to say," highlighting the brief and unadorned nature of his report.
> 
> **Cost Summary:**
> - Cleaning: 141 input + 38 output tokens
> - Summary: 171 input + 237 output tokens
> - Total: 312 input + 275 output tokens
> - Estimated cost: $0.0031 USD
> 
> Output saved to: `/Users/robertkirby/transcripts/youtube-transcript-Me-at-the-zoo.org`

The full output file includes detailed analysis and timestamped transcript with clickable YouTube links.

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
