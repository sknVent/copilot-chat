"""GitHub Copilot API client with streaming support."""

import json
from typing import Generator, Optional, List

import requests
from PyQt5.QtCore import QThread, pyqtSignal


COPILOT_API_URL = "https://api.githubcopilot.com/chat/completions"

DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "Editor-Version": "vscode/1.85.0",
    "Editor-Plugin-Version": "copilot-chat/0.12.0",
    "Openai-Intent": "conversation-panel",
}

OPENAI_MODELS = [
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4-turbo",
    "gpt-4",
    "gpt-3.5-turbo",
    "o1-preview",
    "o1-mini",
    "o3-mini",
]

DEFAULT_MODEL = "gpt-4o"


class APIError(Exception):
    """Raised when the API returns an error response."""
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


def build_headers(token: str) -> dict:
    """Build request headers with the given token."""
    headers = dict(DEFAULT_HEADERS)
    headers["Authorization"] = f"Bearer {token}"
    return headers


def stream_chat_completion(
    token: str,
    messages: List[dict],
    model: str = DEFAULT_MODEL,
) -> Generator[str, None, None]:
    """
    Stream a chat completion from the Copilot API.
    Yields text chunks as they arrive via SSE.
    """
    headers = build_headers(token)
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
    }

    try:
        response = requests.post(
            COPILOT_API_URL,
            headers=headers,
            json=payload,
            stream=True,
            timeout=60,
        )
    except requests.exceptions.ConnectionError as e:
        raise APIError(f"Connection error: {e}") from e
    except requests.exceptions.Timeout as e:
        raise APIError("Request timed out. Please try again.") from e
    except requests.exceptions.RequestException as e:
        raise APIError(f"Request failed: {e}") from e

    if response.status_code == 401:
        raise APIError(
            "Authentication failed. Please check your Copilot token in Settings.",
            status_code=401,
        )
    elif response.status_code == 403:
        raise APIError(
            "Access forbidden. Your token may not have Copilot access.",
            status_code=403,
        )
    elif response.status_code == 429:
        raise APIError(
            "Rate limit exceeded. Please wait a moment before sending another message.",
            status_code=429,
        )
    elif response.status_code >= 500:
        raise APIError(
            f"Server error ({response.status_code}). Please try again later.",
            status_code=response.status_code,
        )
    elif response.status_code != 200:
        try:
            error_data = response.json()
            error_msg = error_data.get("error", {}).get("message", response.text)
        except (ValueError, KeyError):
            error_msg = response.text
        raise APIError(f"API error ({response.status_code}): {error_msg}", status_code=response.status_code)

    # Parse SSE stream
    for line in response.iter_lines():
        if not line:
            continue
        if isinstance(line, bytes):
            line = line.decode("utf-8")
        if not line.startswith("data: "):
            continue
        data_str = line[6:]
        if data_str.strip() == "[DONE]":
            break
        try:
            data = json.loads(data_str)
            choices = data.get("choices", [])
            if not choices:
                continue
            delta = choices[0].get("delta", {})
            content = delta.get("content")
            if content:
                yield content
        except (json.JSONDecodeError, KeyError, IndexError):
            continue


def test_connection(token: str) -> bool:
    """
    Test if the token is valid by sending a minimal request.
    Returns True if successful, raises APIError otherwise.
    """
    messages = [{"role": "user", "content": "Hi"}]
    # Consume just enough to confirm it works
    for _ in stream_chat_completion(token, messages, model="gpt-4o-mini"):
        return True
    return True


class StreamWorker(QThread):
    """QThread worker for streaming API calls without blocking the UI."""

    chunk_received = pyqtSignal(str)
    finished = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, token: str, messages: List[dict], model: str = DEFAULT_MODEL):
        super().__init__()
        self.token = token
        self.messages = messages
        self.model = model
        self._cancelled = False

    def cancel(self):
        """Request cancellation of the stream."""
        self._cancelled = True

    def run(self):
        """Run the API call in a background thread."""
        try:
            for chunk in stream_chat_completion(self.token, self.messages, self.model):
                if self._cancelled:
                    break
                self.chunk_received.emit(chunk)
            if not self._cancelled:
                self.finished.emit()
        except APIError as e:
            self.error_occurred.emit(str(e))
        except Exception as e:
            self.error_occurred.emit(f"Unexpected error: {e}")
