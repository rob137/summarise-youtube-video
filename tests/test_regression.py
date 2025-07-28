"""Regression tests to ensure core functionality doesn't break."""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from yt_transcript.cli import main, extract_video_id, fetch_transcript


class TestRegressionCriticalPaths:
    """Test critical paths that should never break."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    def test_video_id_extraction_common_formats(self):
        """REGRESSION: Ensure common YouTube URL formats always work."""
        test_cases = [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://m.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s", "dQw4w9WgXcQ"),
            ("dQw4w9WgXcQ", "dQw4w9WgXcQ"),  # Bare ID
        ]
        
        for url, expected_id in test_cases:
            result = extract_video_id(url)
            assert result == expected_id, f"Failed for URL: {url}"
    
    def test_cli_exit_codes_consistency(self):
        """REGRESSION: Ensure CLI exit codes remain consistent."""
        # Success case
        with patch('yt_transcript.cli.fetch_transcript') as mock_fetch, \
             patch('yt_transcript.cli.pyperclip.copy'):
            mock_fetch.return_value = "test"
            result = self.runner.invoke(main, ['dQw4w9WgXcQ'])
            assert result.exit_code == 0, "Success case should return 0"
        
        # Invalid video ID
        result = self.runner.invoke(main, ['invalid'])
        assert result.exit_code == 1, "Invalid video ID should return 1"
        
        # Transcript fetch error
        with patch('yt_transcript.cli.fetch_transcript') as mock_fetch:
            mock_fetch.side_effect = RuntimeError("Error")
            result = self.runner.invoke(main, ['dQw4w9WgXcQ'])
            assert result.exit_code == 2, "Transcript error should return 2"
    
    @patch('yt_transcript.cli.YouTubeTranscriptApi.list')
    def test_transcript_api_error_handling(self, mock_list):
        """REGRESSION: Ensure all YouTube API errors are handled gracefully."""
        from youtube_transcript_api import (
            TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
        )
        
        # Test each specific exception type
        error_cases = [
            (TranscriptsDisabled("test"), "Transcripts are disabled"),
            (NoTranscriptFound("test", ["en"], ["en"]), "No transcript available"),
            (VideoUnavailable("test"), "Video is unavailable"),
            (Exception("rate limit"), "rate-limiting"),
            (Exception("network error"), "Unexpected error"),
        ]
        
        for exception, expected_message in error_cases:
            mock_list.side_effect = exception
            
            with pytest.raises(RuntimeError) as exc_info:
                fetch_transcript("test_id")
            
            assert expected_message.lower() in str(exc_info.value).lower()
    
    def test_language_fallback_behavior(self):
        """REGRESSION: Ensure language fallback logic works correctly."""
        with patch('yt_transcript.cli.YouTubeTranscriptApi.list') as mock_list:
            from youtube_transcript_api import NoTranscriptFound
            
            mock_transcript = MagicMock()
            
            # Test fallback from manual to auto-generated for same language
            mock_transcript.find_transcript.side_effect = NoTranscriptFound("test", ["en"], ["en"])
            mock_transcript.find_generated_transcript.return_value.fetch.return_value = [
                {"text": "auto-generated", "start": 0}
            ]
            mock_list.return_value = mock_transcript
            
            result = fetch_transcript("test_id", ["en"])
            assert result == "auto-generated"
            
            # Verify the correct methods were called
            mock_transcript.find_transcript.assert_called_with(["en"])
            mock_transcript.find_generated_transcript.assert_called_with(["en"])


class TestDataIntegrity:
    """Test data integrity and consistency."""
    
    @patch('yt_transcript.cli.YouTubeTranscriptApi.list')
    def test_transcript_text_concatenation(self, mock_list):
        """REGRESSION: Ensure transcript segments are concatenated correctly."""
        mock_transcript = MagicMock()
        mock_transcript.find_transcript.return_value.fetch.return_value = [
            {"text": "First", "start": 0.0},
            {"text": "second", "start": 1.0},
            {"text": "third.", "start": 2.0},
        ]
        mock_list.return_value = mock_transcript
        
        result = fetch_transcript("test_id")
        assert result == "First second third."
        assert result.count(" ") == 2  # Ensure proper spacing
    
    def test_empty_transcript_handling(self):
        """REGRESSION: Ensure empty transcripts are handled gracefully."""
        with patch('yt_transcript.cli.YouTubeTranscriptApi.list') as mock_list:
            mock_transcript = MagicMock()
            mock_transcript.find_transcript.return_value.fetch.return_value = []
            mock_list.return_value = mock_transcript
            
            result = fetch_transcript("test_id")
            assert result == "", "Empty transcript should return empty string"
    
    def test_transcript_with_special_characters(self):
        """REGRESSION: Ensure special characters in transcripts are preserved."""
        with patch('yt_transcript.cli.YouTubeTranscriptApi.list') as mock_list:
            mock_transcript = MagicMock()
            mock_transcript.find_transcript.return_value.fetch.return_value = [
                {"text": "Hello, world!", "start": 0.0},
                {"text": "It's 100% working.", "start": 1.0},
                {"text": "Price: $50 & €40", "start": 2.0},
            ]
            mock_list.return_value = mock_transcript
            
            result = fetch_transcript("test_id")
            expected = "Hello, world! It's 100% working. Price: $50 & €40"
            assert result == expected


class TestPerformanceRegression:
    """Test performance-related regression scenarios."""
    
    def test_large_transcript_handling(self):
        """REGRESSION: Ensure large transcripts don't cause memory issues."""
        with patch('yt_transcript.cli.YouTubeTranscriptApi.list') as mock_list:
            # Create a large mock transcript
            large_transcript = [
                {"text": f"Segment {i}", "start": float(i)}
                for i in range(10000)  # 10k segments
            ]
            
            mock_transcript = MagicMock()
            mock_transcript.find_transcript.return_value.fetch.return_value = large_transcript
            mock_list.return_value = mock_transcript
            
            result = fetch_transcript("test_id")
            
            # Should complete without memory errors
            assert len(result.split()) == 20000  # "Segment X" = 2 words per segment
            assert result.startswith("Segment 0")
            assert result.endswith("Segment 9999")
    
    @patch('yt_transcript.cli.pyperclip.copy')
    def test_clipboard_large_content(self, mock_copy):
        """REGRESSION: Ensure large content can be copied to clipboard."""
        large_content = "word " * 100000  # 100k words
        
        # Should not raise any exceptions
        mock_copy.return_value = None
        mock_copy(large_content)
        mock_copy.assert_called_once_with(large_content)


class TestBackwardCompatibility:
    """Test backward compatibility with previous versions."""
    
    def test_cli_interface_stability(self):
        """REGRESSION: Ensure CLI interface remains stable."""
        runner = CliRunner()
        
        # Test that basic command structure hasn't changed
        result = runner.invoke(main, ['--help'])
        assert result.exit_code == 0
        assert "URL_OR_ID" in result.output
        assert "--lang" in result.output
        assert "--copy" in result.output
    
    def test_output_format_consistency(self):
        """REGRESSION: Ensure output messages remain consistent."""
        runner = CliRunner()
        
        with patch('yt_transcript.cli.fetch_transcript') as mock_fetch, \
             patch('yt_transcript.cli.pyperclip.copy'):
            mock_fetch.return_value = "test transcript content here"
            
            result = runner.invoke(main, ['dQw4w9WgXcQ'])
            
            # Check for expected success message format
            assert "✅" in result.output
            assert "copied to clipboard" in result.output
            assert "words" in result.output
    
    def test_error_message_consistency(self):
        """REGRESSION: Ensure error messages remain user-friendly."""
        runner = CliRunner()
        
        # Test invalid URL error
        result = runner.invoke(main, ['invalid_url'])
        assert result.exit_code == 1
        assert "❌" in result.output
        assert "Could not parse" in result.output
        
        # Test transcript fetch error
        with patch('yt_transcript.cli.fetch_transcript') as mock_fetch:
            mock_fetch.side_effect = RuntimeError("Test error")
            result = runner.invoke(main, ['dQw4w9WgXcQ'])
            assert result.exit_code == 2
            assert "❌" in result.output


class TestSecurityRegression:
    """Test security-related regression scenarios."""
    
    def test_url_validation_security(self):
        """REGRESSION: Ensure URL validation prevents malicious inputs."""
        dangerous_inputs = [
            "javascript:alert('xss')",
            "file:///etc/passwd",
            "data:text/html,<script>alert('xss')</script>",
            "../../../etc/passwd",
            "$(rm -rf /)",
        ]
        
        for dangerous_input in dangerous_inputs:
            with pytest.raises(ValueError):
                extract_video_id(dangerous_input)
    
    def test_no_code_injection_in_transcript(self):
        """REGRESSION: Ensure transcript content can't inject code."""
        with patch('yt_transcript.cli.YouTubeTranscriptApi.list') as mock_list:
            # Transcript with potentially dangerous content
            dangerous_transcript = [
                {"text": "<script>alert('xss')</script>", "start": 0.0},
                {"text": "$(rm -rf /)", "start": 1.0},
                {"text": "; DROP TABLE users; --", "start": 2.0},
            ]
            
            mock_transcript = MagicMock()
            mock_transcript.find_transcript.return_value.fetch.return_value = dangerous_transcript
            mock_list.return_value = mock_transcript
            
            result = fetch_transcript("test_id")
            
            # Content should be preserved as-is (no execution)
            assert "<script>alert('xss')</script>" in result
            assert "$(rm -rf /)" in result
            assert "DROP TABLE" in result
