"""Tests for the CLI module."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

from yt_transcript.cli import main, extract_video_id, fetch_transcript


class TestVideoIdExtraction:
    """Test video ID extraction from various URL formats."""
    
    def test_extract_video_id_from_watch_url(self):
        """Test extraction from standard YouTube watch URL."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"
    
    def test_extract_video_id_from_youtu_be(self):
        """Test extraction from shortened youtu.be URL."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"
    
    def test_extract_video_id_from_embed(self):
        """Test extraction from embed URL."""
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"
    
    def test_extract_video_id_with_parameters(self):
        """Test extraction from URL with additional parameters."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s&list=PLXyz"
        assert extract_video_id(url) == "dQw4w9WgXcQ"
    
    def test_extract_video_id_bare_id(self):
        """Test extraction from bare video ID."""
        video_id = "dQw4w9WgXcQ"
        assert extract_video_id(video_id) == "dQw4w9WgXcQ"
    
    def test_extract_video_id_invalid_url(self):
        """Test error handling for invalid URLs."""
        with pytest.raises(ValueError, match="Could not parse a YouTube video ID"):
            extract_video_id("https://example.com/video")
    
    def test_extract_video_id_invalid_id(self):
        """Test error handling for invalid video IDs."""
        with pytest.raises(ValueError, match="Could not parse a YouTube video ID"):
            extract_video_id("invalid_id")


class TestTranscriptFetching:
    """Test transcript fetching functionality."""
    
    @patch('yt_transcript.cli.YouTubeTranscriptApi.list')
    def test_fetch_transcript_success(self, mock_list):
        """Test successful transcript fetching."""
        # Mock transcript data
        mock_transcript = MagicMock()
        mock_transcript.find_transcript.return_value.fetch.return_value = [
            {"text": "Hello", "start": 0.0, "duration": 2.0},
            {"text": "world", "start": 2.0, "duration": 2.0}
        ]
        mock_list.return_value = mock_transcript
        
        result = fetch_transcript("dQw4w9WgXcQ", ["en"])
        assert result == "Hello world"
        mock_list.assert_called_once_with("dQw4w9WgXcQ")
    
    @patch('yt_transcript.cli.YouTubeTranscriptApi.list')
    def test_fetch_transcript_fallback_to_auto_generated(self, mock_list):
        """Test fallback to auto-generated captions."""
        from youtube_transcript_api import NoTranscriptFound
        
        mock_transcript = MagicMock()
        # First call (manual transcript) raises exception
        mock_transcript.find_transcript.side_effect = NoTranscriptFound(
            "dQw4w9WgXcQ", ["en"], ["en"]
        )
        # Second call (auto-generated) succeeds
        mock_transcript.find_generated_transcript.return_value.fetch.return_value = [
            {"text": "Auto generated", "start": 0.0, "duration": 2.0}
        ]
        mock_list.return_value = mock_transcript
        
        result = fetch_transcript("dQw4w9WgXcQ", ["en"])
        assert result == "Auto generated"
    
    @patch('yt_transcript.cli.YouTubeTranscriptApi.list')
    def test_fetch_transcript_multiple_languages(self, mock_list):
        """Test language preference order."""
        from youtube_transcript_api import NoTranscriptFound
        
        mock_transcript = MagicMock()
        # Spanish transcript not found, English succeeds
        mock_transcript.find_transcript.side_effect = [
            NoTranscriptFound("dQw4w9WgXcQ", ["es"], ["es"]),
            MagicMock(fetch=lambda: [{"text": "English text", "start": 0.0}])
        ]
        mock_list.return_value = mock_transcript
        
        result = fetch_transcript("dQw4w9WgXcQ", ["es", "en"])
        assert result == "English text"
    
    @patch('yt_transcript.cli.YouTubeTranscriptApi.list')
    def test_fetch_transcript_transcripts_disabled(self, mock_list):
        """Test handling of disabled transcripts."""
        from youtube_transcript_api import TranscriptsDisabled
        
        mock_list.side_effect = TranscriptsDisabled("dQw4w9WgXcQ")
        
        with pytest.raises(RuntimeError, match="Transcripts are disabled"):
            fetch_transcript("dQw4w9WgXcQ")
    
    @patch('yt_transcript.cli.YouTubeTranscriptApi.list')
    def test_fetch_transcript_video_unavailable(self, mock_list):
        """Test handling of unavailable videos."""
        from youtube_transcript_api import VideoUnavailable
        
        mock_list.side_effect = VideoUnavailable("dQw4w9WgXcQ")
        
        with pytest.raises(RuntimeError, match="Video is unavailable"):
            fetch_transcript("dQw4w9WgXcQ")


class TestCLI:
    """Test the CLI interface."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    @patch('yt_transcript.cli.fetch_transcript')
    @patch('yt_transcript.cli.pyperclip.copy')
    def test_cli_success_with_copy(self, mock_copy, mock_fetch):
        """Test successful CLI execution with clipboard copy."""
        mock_fetch.return_value = "Test transcript content"
        
        result = self.runner.invoke(main, ['dQw4w9WgXcQ'])
        
        assert result.exit_code == 0
        assert "✅ Transcript (3 words) copied to clipboard" in result.output
        mock_fetch.assert_called_once_with("dQw4w9WgXcQ", [])
        mock_copy.assert_called_once_with("Test transcript content")
    
    @patch('yt_transcript.cli.fetch_transcript')
    def test_cli_success_no_copy(self, mock_fetch):
        """Test successful CLI execution without clipboard copy."""
        mock_fetch.return_value = "Test transcript content"
        
        result = self.runner.invoke(main, ['dQw4w9WgXcQ', '--no-copy'])
        
        assert result.exit_code == 0
        assert "Test transcript content" in result.output
        mock_fetch.assert_called_once_with("dQw4w9WgXcQ", [])
    
    @patch('yt_transcript.cli.fetch_transcript')
    @patch('yt_transcript.cli.pyperclip.copy')
    def test_cli_with_language_preferences(self, mock_copy, mock_fetch):
        """Test CLI with language preferences."""
        mock_fetch.return_value = "Spanish transcript"
        
        result = self.runner.invoke(main, [
            'dQw4w9WgXcQ', 
            '--lang', 'es', 
            '--lang', 'en'
        ])
        
        assert result.exit_code == 0
        mock_fetch.assert_called_once_with("dQw4w9WgXcQ", ['es', 'en'])
    
    def test_cli_invalid_video_id(self):
        """Test CLI with invalid video ID."""
        result = self.runner.invoke(main, ['invalid_url'])
        
        assert result.exit_code == 1
        assert "❌ Could not parse a YouTube video ID" in result.output
    
    @patch('yt_transcript.cli.fetch_transcript')
    def test_cli_transcript_fetch_error(self, mock_fetch):
        """Test CLI when transcript fetching fails."""
        mock_fetch.side_effect = RuntimeError("No transcript available")
        
        result = self.runner.invoke(main, ['dQw4w9WgXcQ'])
        
        assert result.exit_code == 2
        assert "❌ No transcript available" in result.output
    
    @patch('yt_transcript.cli.fetch_transcript')
    @patch('yt_transcript.cli.pyperclip.copy')
    def test_cli_clipboard_error_fallback(self, mock_copy, mock_fetch):
        """Test CLI fallback when clipboard is not available."""
        from pyperclip import PyperclipException
        
        mock_fetch.return_value = "Test transcript"
        mock_copy.side_effect = PyperclipException("No clipboard")
        
        result = self.runner.invoke(main, ['dQw4w9WgXcQ'])
        
        assert result.exit_code == 0
        assert "⚠️  Could not access the clipboard" in result.output
        assert "Test transcript" in result.output
    
    @patch('yt_transcript.cli.fetch_transcript')
    @patch('yt_transcript.cli.pyperclip.copy')
    def test_cli_full_url(self, mock_copy, mock_fetch):
        """Test CLI with full YouTube URL."""
        mock_fetch.return_value = "URL transcript"
        
        result = self.runner.invoke(main, ['https://www.youtube.com/watch?v=dQw4w9WgXcQ'])
        
        assert result.exit_code == 0
        mock_fetch.assert_called_once_with("dQw4w9WgXcQ", [])


class TestIntegration:
    """Integration tests that test multiple components together."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    @patch('yt_transcript.cli.YouTubeTranscriptApi.list')
    @patch('yt_transcript.cli.pyperclip.copy')
    def test_end_to_end_success(self, mock_copy, mock_list):
        """Test end-to-end successful execution."""
        # Mock successful transcript fetching
        mock_transcript = MagicMock()
        mock_transcript.find_transcript.return_value.fetch.return_value = [
            {"text": "This is a test", "start": 0.0},
            {"text": "transcript", "start": 2.0}
        ]
        mock_list.return_value = mock_transcript
        
        result = self.runner.invoke(main, [
            'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            '--lang', 'en'
        ])
        
        assert result.exit_code == 0
        assert "✅ Transcript (4 words) copied to clipboard" in result.output
        mock_copy.assert_called_once_with("This is a test transcript")
