"""Chat message display/scroll area."""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QLabel, QSizePolicy,
    QSpacerItem,
)
from PyQt5.QtCore import Qt, QTimer

from app.message_bubble import UserMessageBubble, AssistantMessageBubble, ErrorMessageBubble
from app.styles import CHAT_STYLESHEET


class ChatWidget(QWidget):
    """Scrollable area that displays chat message bubbles."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("chatContainer")
        self.setStyleSheet(CHAT_STYLESHEET)
        self._current_assistant_bubble = None
        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("chatScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.messages_widget = QWidget()
        self.messages_widget.setObjectName("messagesWidget")

        self.messages_layout = QVBoxLayout(self.messages_widget)
        self.messages_layout.setContentsMargins(0, 16, 0, 16)
        self.messages_layout.setSpacing(4)
        self.messages_layout.addStretch()

        self.scroll_area.setWidget(self.messages_widget)
        main_layout.addWidget(self.scroll_area)

        self._show_welcome()

    def _show_welcome(self):
        """Show welcome message when chat is empty."""
        welcome = QWidget()
        welcome.setObjectName("welcomeWidget")
        layout = QVBoxLayout(welcome)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(12)

        title = QLabel("👋  Welcome to Copilot Chat")
        title.setObjectName("welcomeTitle")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #1a1a2e; font-size: 24px; font-weight: bold;")

        subtitle = QLabel("Start a conversation using the input below.\nSelect a model and optionally attach files.")
        subtitle.setObjectName("welcomeSubtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #6b7280; font-size: 15px; line-height: 1.6;")

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()

        self._welcome_widget = welcome
        # Insert before the stretch at the end
        self.messages_layout.insertWidget(0, welcome)

    def _remove_welcome(self):
        """Remove the welcome widget once first message is added."""
        if hasattr(self, "_welcome_widget") and self._welcome_widget is not None:
            self._welcome_widget.setParent(None)
            self._welcome_widget = None

    def add_user_message(self, text: str, files: list = None):
        """Add a user message bubble."""
        self._remove_welcome()
        bubble = UserMessageBubble(text=text, files=files or [])
        self._insert_bubble(bubble)
        self._scroll_to_bottom()

    def start_assistant_message(self) -> AssistantMessageBubble:
        """Start a new streaming assistant message. Returns the bubble for appending chunks."""
        self._remove_welcome()
        bubble = AssistantMessageBubble()
        self._current_assistant_bubble = bubble
        self._insert_bubble(bubble)
        self._scroll_to_bottom()
        return bubble

    def add_error_message(self, text: str):
        """Add an error message bubble."""
        bubble = ErrorMessageBubble(text=text)
        self._insert_bubble(bubble)
        self._scroll_to_bottom()

    def _insert_bubble(self, widget: QWidget):
        """Insert a bubble widget before the trailing stretch."""
        count = self.messages_layout.count()
        self.messages_layout.insertWidget(count - 1, widget)

    def _scroll_to_bottom(self):
        """Scroll to the bottom of the chat area."""
        QTimer.singleShot(50, self._do_scroll_to_bottom)

    def _do_scroll_to_bottom(self):
        sb = self.scroll_area.verticalScrollBar()
        sb.setValue(sb.maximum())

    def clear(self):
        """Clear all messages from the chat area."""
        self._current_assistant_bubble = None
        # Remove all widgets except the final stretch
        while self.messages_layout.count() > 1:
            item = self.messages_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        self._welcome_widget = None
        self._show_welcome()

    def load_conversation(self, messages: list):
        """Load a saved conversation's messages."""
        self.clear()
        self._remove_welcome()
        for msg in messages:
            if msg.role == "user":
                content = msg.content
                text = content if isinstance(content, str) else (
                    next((p["text"] for p in content if isinstance(p, dict) and p.get("type") == "text"), "")
                )
                self.add_user_message(text)
            elif msg.role == "assistant":
                content = msg.content if isinstance(msg.content, str) else ""
                bubble = AssistantMessageBubble()
                bubble.set_text(content)
                self._insert_bubble(bubble)
        self._scroll_to_bottom()
