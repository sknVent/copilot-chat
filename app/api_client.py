"""
GitHub Copilot API client with streaming support using QThread.
"""
import json
import requests
from typing import List, Dict, Any, Optional, Tuple

from PyQt5.QtCore import QThread, pyqtSignal


COPILOT_API_URL = "https://api.githubcopilot.com/chat/completions"

API_HEADERS = {
    "Content-Type": "application/json",
    "Editor-Version": "vscode/1.85.0",
    "Editor-Plugin-Version": "copilot-chat/0.12.0",
    "Openai-Intent": "conversation-panel",
    "Accept": "text/event-stream",
}


class ApiWorker(QThread):
    """
    Worker thread for making streaming API calls to GitHub Copilot.
    Emits tokens as they arrive so the UI can update in real-time.
    """

    # Emitted with each token/chunk of text
    token_received = pyqtSignal(str)
    # Emitted when the stream is complete
    finished = pyqtSignal()
    # Emitted on error
    error = pyqtSignal(str)

    def __init__(
        self,
        token: str,
        model: str,
        messages: List[Dict[str, Any]],
        parent=None,
    ):
        super().__init__(parent)
        self.token = token
        self.model = model
        self.messages = messages
        self._abort = False

    def abort(self):
        """Request the worker to stop."""
        self._abort = True

    def run(self):
        """Execute the API request in a background thread."""
        try:
            headers = {
                **API_HEADERS,
                "Authorization": f"Bearer {self.token}",
            }

            payload = {
                "model": self.model,
                "messages": self.messages,
                "stream": True,
                "temperature": 0.7,
                "max_tokens": 4096,
            }

            with requests.post(
                COPILOT_API_URL,
                headers=headers,
                json=payload,
                stream=True,
                timeout=60,
            ) as response:
                if response.status_code == 401:
                    self.error.emit(
                        "Authentication failed. Please check your Copilot token in Settings."
                    )
                    return
                elif response.status_code == 403:
                    self.error.emit(
                        "Access forbidden. Your Copilot token may not have the required permissions."
                    )
                    return
                elif response.status_code == 429:
                    self.error.emit(
                        "Rate limit exceeded. Please wait a moment before sending another message."
                    )
                    return
                elif response.status_code != 200:
                    try:
                        error_data = response.json()
                        msg = error_data.get("error", {}).get(
                            "message", f"API error: {response.status_code}"
                        )
                    except Exception:
                        msg = f"API error: {response.status_code} {response.reason}"
                    self.error.emit(msg)
                    return

                # Stream the response
                for line in response.iter_lines():
                    if self._abort:
                        break

                    if not line:
                        continue

                    # Lines are formatted as "data: {...}" or "data: [DONE]"
                    if isinstance(line, bytes):
                        line = line.decode("utf-8")

                    if not line.startswith("data: "):
                        continue

                    data_str = line[6:]  # Strip "data: " prefix

                    if data_str.strip() == "[DONE]":
                        break

                    try:
                        data = json.loads(data_str)
                        choices = data.get("choices", [])
                        if not choices:
                            continue

                        delta = choices[0].get("delta", {})
                        content = delta.get("content", "")

                        if content:
                            self.token_received.emit(content)

                    except json.JSONDecodeError:
                        continue

            self.finished.emit()

        except requests.exceptions.ConnectionError:
            self.error.emit(
                "Connection error. Please check your internet connection."
            )
        except requests.exceptions.Timeout:
            self.error.emit(
                "Request timed out. The server took too long to respond."
            )
        except requests.exceptions.RequestException as e:
            self.error.emit(f"Network error: {str(e)}")
        except Exception as e:
            self.error.emit(f"Unexpected error: {str(e)}")


def test_connection(token: str) -> Tuple[bool, str]:
    """
    Test the Copilot API connection with a simple request.
    Returns (success, message).
    """
    try:
        headers = {
            **API_HEADERS,
            "Authorization": f"Bearer {token}",
        }

        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": "Say 'ok' in one word."}],
            "stream": False,
            "max_tokens": 10,
        }

        response = requests.post(
            COPILOT_API_URL,
            headers=headers,
            json=payload,
            timeout=15,
        )

        if response.status_code == 200:
            return True, "✓ Connection successful! Token is valid."
        elif response.status_code == 401:
            return False, "✗ Invalid token. Please check your Copilot Classic token."
        elif response.status_code == 403:
            return False, "✗ Access forbidden. Token may lack required permissions."
        else:
            return False, f"✗ API returned status {response.status_code}: {response.reason}"

    except requests.exceptions.ConnectionError:
        return False, "✗ Connection failed. Please check your internet connection."
    except requests.exceptions.Timeout:
        return False, "✗ Request timed out."
    except Exception as e:
        return False, f"✗ Error: {str(e)}"
