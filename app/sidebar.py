"""Sidebar with conversation history, new chat button, and settings."""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget,
    QListWidgetItem, QSizePolicy,
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont

from app.conversation import ConversationStore, Conversation
from app.styles import SIDEBAR_STYLESHEET


class Sidebar(QWidget):
    """Dark sidebar with app title, new chat button, conversation history, and settings."""

    new_chat_requested = pyqtSignal()
    conversation_selected = pyqtSignal(str)  # conversation_id
    settings_requested = pyqtSignal()

    def __init__(self, store: ConversationStore, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setStyleSheet(SIDEBAR_STYLESHEET)
        self.setFixedWidth(260)
        self._store = store
        self._build_ui()
        self.refresh_conversations()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 20, 12, 16)
        layout.setSpacing(12)

        # App logo / title
        logo_row = QWidget()
        logo_layout = QVBoxLayout(logo_row)
        logo_layout.setContentsMargins(4, 0, 0, 0)
        logo_layout.setSpacing(2)

        title_label = QLabel("🤖  Copilot Chat")
        title_label.setObjectName("appTitle")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))

        subtitle_label = QLabel("Powered by GitHub Copilot")
        subtitle_label.setObjectName("appSubtitle")

        logo_layout.addWidget(title_label)
        logo_layout.addWidget(subtitle_label)
        layout.addWidget(logo_row)

        # New Chat button
        self.new_chat_btn = QPushButton("✏️  New Chat")
        self.new_chat_btn.setObjectName("newChatButton")
        self.new_chat_btn.setCursor(Qt.PointingHandCursor)
        self.new_chat_btn.clicked.connect(self.new_chat_requested.emit)
        layout.addWidget(self.new_chat_btn)

        # History label
        history_label = QLabel("RECENT CHATS")
        history_label.setObjectName("historyLabel")
        layout.addWidget(history_label)

        # Conversation list
        self.conv_list = QListWidget()
        self.conv_list.setObjectName("conversationList")
        self.conv_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.conv_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.conv_list.setFocusPolicy(Qt.NoFocus)
        self.conv_list.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.conv_list)

        # Settings button at the bottom
        self.settings_btn = QPushButton("⚙️  Settings")
        self.settings_btn.setObjectName("settingsButton")
        self.settings_btn.setCursor(Qt.PointingHandCursor)
        self.settings_btn.clicked.connect(self.settings_requested.emit)
        layout.addWidget(self.settings_btn)

    def refresh_conversations(self):
        """Reload the conversation list from the store."""
        self.conv_list.clear()
        for conv in self._store.get_all():
            item = QListWidgetItem(conv.title)
            item.setData(Qt.UserRole, conv.conversation_id)
            item.setSizeHint(QSize(0, 42))
            self.conv_list.addItem(item)

    def select_conversation(self, conversation_id: str):
        """Highlight the given conversation in the list."""
        for i in range(self.conv_list.count()):
            item = self.conv_list.item(i)
            if item.data(Qt.UserRole) == conversation_id:
                self.conv_list.setCurrentItem(item)
                return
        self.conv_list.clearSelection()

    def deselect_all(self):
        """Clear the current selection."""
        self.conv_list.clearSelection()

    def _on_item_clicked(self, item: QListWidgetItem):
        conv_id = item.data(Qt.UserRole)
        if conv_id:
            self.conversation_selected.emit(conv_id)
