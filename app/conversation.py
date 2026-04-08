"""Conversation data model and storage for the Copilot Chat application."""

import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional


class Message:
    """Represents a single chat message."""

    def __init__(self, role: str, content, timestamp: Optional[datetime] = None):
        self.role = role  # "user" or "assistant"
        self.content = content  # str or list (for multimodal)
        self.timestamp = timestamp or datetime.now()

    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        timestamp = datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat()))
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=timestamp,
        )

    def to_api_dict(self) -> dict:
        """Convert to API-compatible format (role + content only)."""
        return {"role": self.role, "content": self.content}


class Conversation:
    """Represents a single conversation with a list of messages."""

    def __init__(self, title: str = "New Chat", conversation_id: Optional[str] = None):
        self.conversation_id = conversation_id or str(uuid.uuid4())
        self.title = title
        self.messages: List[Message] = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def add_message(self, role: str, content) -> Message:
        msg = Message(role=role, content=content)
        self.messages.append(msg)
        self.updated_at = datetime.now()
        # Auto-title based on first user message
        if len(self.messages) == 1 and role == "user":
            text = content if isinstance(content, str) else str(content)
            self.title = text[:50] + ("..." if len(text) > 50 else "")
        return msg

    def get_api_messages(self) -> List[dict]:
        """Get messages in API-compatible format."""
        return [msg.to_api_dict() for msg in self.messages]

    def to_dict(self) -> dict:
        return {
            "conversation_id": self.conversation_id,
            "title": self.title,
            "messages": [msg.to_dict() for msg in self.messages],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Conversation":
        conv = cls(
            title=data.get("title", "Chat"),
            conversation_id=data.get("conversation_id"),
        )
        conv.messages = [Message.from_dict(m) for m in data.get("messages", [])]
        conv.created_at = datetime.fromisoformat(data.get("created_at", datetime.now().isoformat()))
        conv.updated_at = datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat()))
        return conv


class ConversationStore:
    """Manages persistence of conversations to disk."""

    def __init__(self):
        self.storage_dir = os.path.join(os.path.expanduser("~"), ".copilot-chat")
        self.storage_file = os.path.join(self.storage_dir, "conversations.json")
        os.makedirs(self.storage_dir, exist_ok=True)
        self._conversations: List[Conversation] = []
        self._load()

    def _load(self):
        """Load conversations from disk."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._conversations = [Conversation.from_dict(c) for c in data]
            except (json.JSONDecodeError, KeyError, ValueError):
                self._conversations = []

    def save(self):
        """Save conversations to disk."""
        try:
            data = [c.to_dict() for c in self._conversations]
            with open(self.storage_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except OSError:
            pass

    def get_all(self) -> List[Conversation]:
        """Return all conversations, most recent first."""
        return sorted(self._conversations, key=lambda c: c.updated_at, reverse=True)

    def add(self, conversation: Conversation):
        """Add a new conversation."""
        self._conversations.append(conversation)
        self.save()

    def update(self, conversation: Conversation):
        """Update an existing conversation."""
        self.save()

    def delete(self, conversation_id: str):
        """Delete a conversation by ID."""
        self._conversations = [c for c in self._conversations if c.conversation_id != conversation_id]
        self.save()

    def get_by_id(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by its ID."""
        for conv in self._conversations:
            if conv.conversation_id == conversation_id:
                return conv
        return None
