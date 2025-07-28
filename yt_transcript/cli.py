import re
import sys
from typing import List, Optional

import click
import pyperclip
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)

YT_ID_RE = re.compile(
    r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
)  # catches youtu.be/, embed/, watch?v=, etc


def extract_video_id(url_or_id: str) -> str:
    """
    Accepts a full YouTube URL or a bare 11-char video ID.
    Raises ValueError if not recognisable.
    """
    if len(url_or_id) == 11 and re.match(r"^[0-9A-Za-z_-]+$", url_or_id):
        return url_or_id
    m = YT_ID_RE.search(url_or_id)
    if m:
        return m.group(1)
    raise ValueError(f"Could not parse a YouTube video ID from '{url_or_id}'")


def fetch_transcript(video_id: str, preferred_langs: Optional[List[str]] = None) -> str:
    """
    Returns plain-text transcript.  Tries languages in order.
    Falls back to auto-generated captions.
    """
    preferred_langs = preferred_langs or ["en"]
    try:
        transcript_list = YouTubeTranscriptApi.list(video_id)

        # Choose best track: first matching manual caption, else auto-generated.
        for lang in preferred_langs:
            try:
                return " ".join(
                    [t["text"] for t in transcript_list.find_transcript([lang]).fetch()]
                )
            except NoTranscriptFound:
                # try auto-generated in that language
                try:
                    return " ".join(
                        [
                            t["text"]
                            for t in transcript_list.find_generated_transcript([lang]).fetch()
                        ]
                    )
                except NoTranscriptFound:
                    continue  # keep looping
        # Still no match – default to first available
        return " ".join([item["text"] for item in transcript_list.find_transcript([]).fetch()])

    except TranscriptsDisabled:
        raise RuntimeError("Transcripts are disabled for this video.")
    except NoTranscriptFound:
        raise RuntimeError("No transcript available in the requested languages.")
    except Exception as e:
        if "rate" in str(e).lower():
            raise RuntimeError("YouTube is rate-limiting us.  Try again later.")
        raise RuntimeError(f"Unexpected error: {e}")
    except VideoUnavailable:
        raise RuntimeError("Video is unavailable or private.")


@click.command()
@click.argument("url_or_id")
@click.option(
    "-l",
    "--lang",
    multiple=True,
    help="Preferred language code(s), e.g. --lang en --lang es.  Order matters.",
)
@click.option(
    "--copy/--no-copy",
    default=True,
    help="Copy to clipboard (default) or just print.",
)
def main(url_or_id: str, lang: List[str], copy: bool):
    """
    Extract YouTube transcript and copy it to the clipboard.

    URL_OR_ID can be a full YouTube URL or a plain 11-character video ID.
    """
    try:
        video_id = extract_video_id(url_or_id)
    except ValueError as e:
        click.echo(f"❌ {e}", err=True)
        sys.exit(1)

    try:
        text = fetch_transcript(video_id, list(lang))
    except RuntimeError as e:
        click.echo(f"❌ {e}", err=True)
        sys.exit(2)

    if copy:
        try:
            pyperclip.copy(text)
            click.echo(f"✅ Transcript ({len(text.split())} words) copied to clipboard.")
        except pyperclip.PyperclipException:
            click.echo("⚠️  Could not access the clipboard; printing instead:\n")
            click.echo(text)
    else:
        click.echo(text)


if __name__ == "__main__":
    main()
