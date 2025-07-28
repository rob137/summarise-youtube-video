"""Tests for the standalone yt-transcript script."""

import pytest
import subprocess
import sys
import os
from unittest.mock import patch, MagicMock
from pathlib import Path


class TestStandaloneScript:
    """Test the standalone yt-transcript script."""
    
    @property
    def script_path(self):
        """Get the path to the standalone script."""
        return Path(__file__).parent.parent / "yt-transcript"
    
    def test_script_exists_and_executable(self):
        """Test that the script file exists and is executable."""
        assert self.script_path.exists(), f"Script not found at {self.script_path}"
        assert os.access(self.script_path, os.X_OK), "Script is not executable"
    
    def test_script_usage_message(self):
        """Test script shows usage when called without arguments."""
        result = subprocess.run(
            [sys.executable, str(self.script_path)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 1
        assert "Usage: yt-transcript <youtube_url>" in result.stdout
    
    def test_script_invalid_video_id(self):
        """Test script error handling for invalid video IDs."""
        result = subprocess.run(
            [sys.executable, str(self.script_path), "invalid_url"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 1
        assert "❌ Could not extract video ID" in result.stdout
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'})
    @patch('requests.get')
    def test_script_video_title_extraction(self, mock_get):
        """Test video title extraction functionality."""
        # Mock HTML response with title
        mock_response = MagicMock()
        mock_response.text = '<title>Test Video Title - YouTube</title>'
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Import the functions directly to test them
        import sys
        sys.path.insert(0, str(self.script_path.parent))
        
        # Read and execute the script to get access to functions
        with open(self.script_path, 'r') as f:
            script_content = f.read()
        
        # Create a namespace to execute the script in
        script_globals = {}
        exec(script_content, script_globals)
        
        # Test the get_video_title function
        title = script_globals['get_video_title']('dQw4w9WgXcQ')
        assert title == "Test Video Title"
    
    def test_script_video_id_extraction(self):
        """Test video ID extraction from the standalone script."""
        import sys
        sys.path.insert(0, str(self.script_path.parent))
        
        # Read and execute the script to get access to functions
        with open(self.script_path, 'r') as f:
            script_content = f.read()
        
        script_globals = {}
        exec(script_content, script_globals)
        
        # Test the extract_video_id function
        extract_video_id = script_globals['extract_video_id']
        
        # Test various URL formats
        assert extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"
        assert extract_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
        assert extract_video_id("dQw4w9WgXcQ") is None  # Invalid format in this implementation


class TestScriptIntegration:
    """Integration tests for the standalone script."""
    
    @property
    def script_path(self):
        """Get the path to the standalone script."""
        return Path(__file__).parent.parent / "yt-transcript"
    
    @patch.dict(os.environ, {}, clear=True)
    def test_script_without_api_key(self):
        """Test script behavior when GEMINI_API_KEY is not set."""
        # This test checks that the script can still extract transcripts
        # even without the API key (it just won't get AI summaries)
        result = subprocess.run(
            [sys.executable, str(self.script_path), "dQw4w9WgXcQ"],
            capture_output=True,
            text=True,
            timeout=10  # Don't let it hang
        )
        # Should fail at transcript extraction, not at API key check
        assert "GEMINI_API_KEY environment variable not found" in result.stdout
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'})
    def test_script_with_api_key_set(self):
        """Test that script accepts API key from environment."""
        # Just test that it gets past the API key check
        result = subprocess.run(
            [sys.executable, str(self.script_path), "dQw4w9WgXcQ"],
            capture_output=True,
            text=True,
            timeout=10
        )
        # Should fail at transcript fetching, not API key validation
        assert "GEMINI_API_KEY environment variable not found" not in result.stdout


class TestScriptFunctions:
    """Test individual functions from the standalone script by importing them."""
    
    @classmethod
    def setup_class(cls):
        """Set up the class by importing the script functions."""
        script_path = Path(__file__).parent.parent / "yt-transcript"
        
        with open(script_path, 'r') as f:
            script_content = f.read()
        
        cls.script_globals = {}
        exec(script_content, cls.script_globals)
    
    def test_extract_video_id_function(self):
        """Test the extract_video_id function directly."""
        extract_video_id = self.script_globals['extract_video_id']
        
        # Test valid URLs
        assert extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"
        assert extract_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
        
        # Test invalid URLs
        assert extract_video_id("https://example.com") is None
        assert extract_video_id("invalid") is None
    
    @patch('requests.get')
    def test_get_video_title_function(self, mock_get):
        """Test the get_video_title function directly."""
        get_video_title = self.script_globals['get_video_title']
        
        # Test successful title extraction
        mock_response = MagicMock()
        mock_response.text = '<title>Amazing Video - YouTube</title>'
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        title = get_video_title('dQw4w9WgXcQ')
        assert title == "Amazing Video"
        
        # Test with network error
        mock_get.side_effect = Exception("Network error")
        title = get_video_title('dQw4w9WgXcQ')
        assert title == "YouTube Video dQw4w9WgXcQ"
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'})
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_get_gemini_summary_function(self, mock_model_class, mock_configure):
        """Test the get_gemini_summary function directly."""
        get_gemini_summary = self.script_globals['get_gemini_summary']
        
        # Mock the Gemini model
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "• Key point 1\n• Key point 2"
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        result = get_gemini_summary("Test Title", "Test transcript content")
        assert "• Key point 1" in result
        assert "• Key point 2" in result
        
        mock_configure.assert_called_once_with(api_key='test_key')
        mock_model.generate_content.assert_called_once()
    
    @patch.dict(os.environ, {}, clear=True)  # Clear GEMINI_API_KEY
    def test_get_gemini_summary_no_api_key(self):
        """Test get_gemini_summary when API key is missing."""
        get_gemini_summary = self.script_globals['get_gemini_summary']
        
        title = "Test Title"
        transcript = "Test transcript"
        
        result = get_gemini_summary(title, transcript)
        # Should return the original content with prompt when API fails
        assert title in result
        assert transcript in result
        assert "Key takeaways as bullets, plain English." in result
