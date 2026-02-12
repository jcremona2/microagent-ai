"""
Integration tests for Groq API client using mocks
"""

from unittest.mock import MagicMock, patch, AsyncMock

import pytest
from groq import APIConnectionError, APIStatusError, Groq

# Test configuration
TEST_PROMPT = "What is the capital of France?"


# Define a mock response class
class MockCompletion:
    def __init__(self, content):
        class Choice:
            def __init__(self, content):
                class Message:
                    def __init__(self, content):
                        self.content = content
                        self.role = "assistant"

                self.message = Message(content)
                self.finish_reason = "stop"

        self.choices = [Choice(content)]
        self.usage = {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}


class TestMockedGroqIntegration:
    """Test suite for Groq API integration with mocks"""

    @pytest.fixture(autouse=True)
    def setup_mocks(self, test_config):
        """Setup test fixtures with mocks"""
        self.config = test_config

        self.mock_client = MagicMock()

        # Create a mock for the completions
        self.mock_completions = MagicMock()
        self.mock_client.chat.completions = self.mock_completions

        # Patch the Groq class to return our mock client
        self.patcher = patch(
            "tests.test_groq_integration.Groq", return_value=self.mock_client
        )
        self.mock_groq = self.patcher.start()

        yield

        # Clean up
        self.patcher.stop()

    def test_mocked_connection(self):
        """Test basic API connection with mock"""
        # When
        client = Groq(api_key="test_key")

        # Then
        self.mock_groq.assert_called_once_with(api_key="test_key")

    def test_connection_error(self):
        """Test handling of connection errors"""
        # Given
        self.mock_completions.create.side_effect = APIConnectionError(
            message="Connection failed", request=MagicMock()
        )

        # When/Then
        with pytest.raises(APIConnectionError) as excinfo:
            client = Groq(api_key="test_key")
            client.chat.completions.create(
                model="test-model",
                messages=[{"role": "user", "content": TEST_PROMPT}],
            )

        assert "Connection failed" in str(excinfo.value)

    def test_api_error(self):
        """Test handling of API errors"""
        # Given
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": {"message": "Invalid request"}}

        # Configure the mock to raise an API error
        self.mock_completions.create.side_effect = APIStatusError(
            message="Invalid request",
            response=mock_response,
            body={"error": {"message": "Invalid request"}},
        )

        # When/Then
        with pytest.raises(APIStatusError) as excinfo:
            client = Groq(api_key="test_key")
            client.chat.completions.create(
                model="test-model",
                messages=[{"role": "user", "content": TEST_PROMPT}],
            )

        assert "Invalid request" in str(excinfo.value)
        assert excinfo.value.status_code == 400
