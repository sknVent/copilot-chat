"""
Chat message display area - scrollable container for message bubbles.
"""
from typing import List, Dict, Any

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QSizePolicy,
    QApplication,
    QLabel,
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont

from app.message_bubble import MessageBubble
from app.styles import COLORS, CHAT_AREA_STYLE


class ChatWidget(QWidget):
    """
    Scrollable area that shows all messages in the conversation.
    """

    copy_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("chat_area")
        self.setStyleSheet(CHAT_AREA_STYLE)

        self._current_assistant_bubble: MessageBubble = None
        self._message_widgets: List[MessageBubble] = []

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("message_scroll")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)
        self.scroll_area.setStyleSheet(
            f"QScrollArea {{ background-color: {COLORS['chat_bg']}; border: none; }}"
        )

        # Container for messages
        self.container = QWidget()
        self.container.setObjectName("messages_container")
        self.container.setStyleSheet(
            f"QWidget#messages_container {{ background-color: {COLORS['chat_bg']}; }}"
        )

        self.messages_layout = QVBoxLayout(self.container)
        self.messages_layout.setContentsMargins(0, 16, 0, 16)
        self.messages_layout.setSpacing(8)
        self.messages_layout.addStretch()

        self.scroll_area.setWidget(self.container)
        layout.addWidget(self.scroll_area)

        # Show welcome message initially
        self._show_welcome()

    def _show_welcome(self):
        """Show a welcome message in the empty chat."""
        self._welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(self._welcome_widget)
        welcome_layout.setAlignment(Qt.AlignCenter)
        welcome_layout.setContentsMargins(40, 60, 40, 60)
        welcome_layout.setSpacing(12)

        icon_label = QLabel("✦")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(
            f"color: {COLORS['accent']}; font-size: 48px; font-weight: bold;"
        )
        welcome_layout.addWidget(icon_label)

        title = QLabel("How can I help you today?")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            "color: #2d2520; font-size: 22px; font-weight: 600;"
        )
        welcome_layout.addWidget(title)

        subtitle = QLabel(
            "Ask me anything. I'm powered by GitHub Copilot\nwith OpenAI models."
        )
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet(
            "color: #9e9087; font-size: 14px; line-height: 1.6;"
        )
        welcome_layout.addWidget(subtitle)

        # Insert before the stretch at the end
        idx = self.messages_layout.count() - 1
        self.messages_layout.insertWidget(idx, self._welcome_widget)

    def add_message(
        self,
        role: str,
        content: str,
        files: List[Dict[str, Any]] = None,
    ) -> MessageBubble:
        """Add a new message bubble and return it."""
        # Remove welcome widget on first message
        if self._welcome_widget is not None:
            self._welcome_widget.setParent(None)
            self._welcome_widget.deleteLater()
            self._welcome_widget = None

        bubble = MessageBubble(role=role, content=content, files=files or [])
        bubble.copy_requested.connect(self.copy_requested)

        # Insert before the stretch
        idx = self.messages_layout.count() - 1
        self.messages_layout.insertWidget(idx, bubble)
        self._message_widgets.append(bubble)

        if role == "assistant":
            self._current_assistant_bubble = bubble

        # Scroll to bottom after a brief delay to allow layout update
        QTimer.singleShot(50, self._scroll_to_bottom)

        return bubble

    def start_assistant_message(self) -> MessageBubble:
        """Add an empty assistant bubble ready for streaming content."""
        return self.add_message("assistant", "")

    def append_to_assistant(self, token: str):
        """Append a token to the current streaming assistant message."""
        if self._current_assistant_bubble:
            new_content = self._current_assistant_bubble.content + token
            self._current_assistant_bubble.update_content(new_content)
            # Scroll to bottom periodically
            QTimer.singleShot(0, self._scroll_to_bottom)

    def finish_assistant_message(self):
        """Mark the current assistant message as complete."""
        self._current_assistant_bubble = None

    def clear_messages(self):
        """Remove all message bubbles."""
        # Clear all message widgets
        for widget in self._message_widgets:
            widget.setParent(None)
            widget.deleteLater()
        self._message_widgets.clear()
        self._current_assistant_bubble = None

        # Re-show welcome
        self._welcome_widget = None
        self._show_welcome()

    def _scroll_to_bottom(self):
        """Scroll the message area to the bottom."""
        sb = self.scroll_area.verticalScrollBar()
        sb.setValue(sb.maximum())

    def set_welcome_visible(self, visible: bool):
        """Show or hide the welcome widget."""
        if self._welcome_widget:
            self._welcome_widget.setVisible(visible)
