"""
Conversation data model and local storage.
"""
import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any


# Store conversations in user's home config directory
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".copilot_chat")
CONVERSATIONS_FILE = os.path.join(CONFIG_DIR, "conversations.json")
SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.json")


def ensure_config_dir():
    """Create config directory if it doesn't exist."""
    os.makedirs(CONFIG_DIR, exist_ok=True)


class Message:
    """Represents a single chat message."""

    def __init__(
        self,
        role: str,
        content: str,
        files: Optional[List[Dict[str, Any]]] = None,
        timestamp: Optional[str] = None,
    ):
        self.role = role  # "user" or "assistant"
        self.content = content
        self.files = files or []
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "files": self.files,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        return cls(
            role=data["role"],
            content=data["content"],
            files=data.get("files", []),
            timestamp=data.get("timestamp"),
        )

    def to_api_message(self) -> Dict[str, Any]:
        """Convert to format expected by Copilot API."""
        if self.files:
            # Build content with file attachments
            content_parts = []

            # Add text content if present
            if self.content:
                content_parts.append({"type": "text", "text": self.content})

            # Add file content
            for f in self.files:
                file_type = f.get("type", "text")
                if file_type == "image":
                    content_parts.append(
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{f['mime_type']};base64,{f['data']}"
                            },
                        }
                    )
                else:
                    # Text-based file - include inline as text
                    content_parts.append(
                        {
                            "type": "text",
                            "text": f.get("inline_text", ""),
                        }
                    )

            return {"role": self.role, "content": content_parts}
        else:
            return {"role": self.role, "content": self.content}


class Conversation:
    """Represents a single conversation thread."""

    def __init__(
        self,
        id: Optional[str] = None,
        title: str = "New Chat",
        messages: Optional[List[Message]] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        model: str = "gpt-4o",
    ):
        self.id = id or str(uuid.uuid4())
        self.title = title
        self.messages: List[Message] = messages or []
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or datetime.now().isoformat()
        self.model = model

    def add_message(self, message: Message):
        self.messages.append(message)
        self.updated_at = datetime.now().isoformat()
        # Auto-generate title from first user message
        if len(self.messages) == 1 and message.role == "user":
            text = message.content.strip()
            self.title = text[:50] + ("..." if len(text) > 50 else "")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "messages": [m.to_dict() for m in self.messages],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "model": self.model,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Conversation":
        messages = [Message.from_dict(m) for m in data.get("messages", [])]
        return cls(
            id=data.get("id"),
            title=data.get("title", "New Chat"),
            messages=messages,
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            model=data.get("model", "gpt-4o"),
        )

    def get_api_messages(self) -> List[Dict[str, Any]]:
        """Get messages in API format."""
        return [m.to_api_message() for m in self.messages]


class ConversationStore:
    """Manages loading and saving conversations."""

    def __init__(self):
        ensure_config_dir()
        self.conversations: List[Conversation] = []
        self.load()

    def load(self):
        """Load conversations from disk."""
        if os.path.exists(CONVERSATIONS_FILE):
            try:
                with open(CONVERSATIONS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.conversations = [Conversation.from_dict(c) for c in data]
                # Sort by most recently updated
                self.conversations.sort(key=lambda c: c.updated_at, reverse=True)
            except (json.JSONDecodeError, KeyError, Exception):
                self.conversations = []

    def save(self):
        """Save conversations to disk."""
        ensure_config_dir()
        try:
            data = [c.to_dict() for c in self.conversations]
            with open(CONVERSATIONS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def add_conversation(self, conversation: Conversation):
        """Add a new conversation to the store."""
        self.conversations.insert(0, conversation)
        self.save()

    def update_conversation(self, conversation: Conversation):
        """Update an existing conversation."""
        for i, c in enumerate(self.conversations):
            if c.id == conversation.id:
                self.conversations[i] = conversation
                # Re-sort
                self.conversations.sort(key=lambda x: x.updated_at, reverse=True)
                self.save()
                return
        # Not found - add it
        self.add_conversation(conversation)

    def delete_conversation(self, conversation_id: str):
        """Delete a conversation."""
        self.conversations = [c for c in self.conversations if c.id != conversation_id]
        self.save()

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID."""
        for c in self.conversations:
            if c.id == conversation_id:
                return c
        return None


class Settings:
    """Application settings with persistence."""

    def __init__(self):
        ensure_config_dir()
        self._data: Dict[str, Any] = {}
        self.load()

    def load(self):
        """Load settings from disk."""
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except Exception:
                self._data = {}

    def save(self):
        """Save settings to disk."""
        ensure_config_dir()
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
        except Exception:
            pass

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any):
        self._data[key] = value
        self.save()

    @property
    def copilot_token(self) -> str:
        return self._data.get("copilot_token", "")

    @copilot_token.setter
    def copilot_token(self, value: str):
        self._data["copilot_token"] = value
        self.save()

    @property
    def default_model(self) -> str:
        return self._data.get("default_model", "gpt-4o")

    @default_model.setter
    def default_model(self, value: str):
        self._data["default_model"] = value
        self.save()
