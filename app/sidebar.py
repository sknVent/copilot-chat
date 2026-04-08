"""
Sidebar widget with conversation history, new chat button, and settings.
"""
from typing import List, Optional

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QSizePolicy,
    QFrame,
    QMenu,
    QAction,
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QIcon

from app.styles import COLORS, SIDEBAR_STYLE
from app.conversation import Conversation, ConversationStore


class Sidebar(QWidget):
    """
    Dark sidebar with:
    - App logo/title
    - New Chat button
    - Scrollable conversation history
    - Settings button at the bottom
    """

    new_chat_clicked = pyqtSignal()
    conversation_selected = pyqtSignal(str)  # emits conversation ID
    conversation_deleted = pyqtSignal(str)   # emits conversation ID
    settings_clicked = pyqtSignal()

    def __init__(self, store: ConversationStore, parent=None):
        super().__init__(parent)
        self.store = store
        self.setObjectName("sidebar")
        self.setStyleSheet(SIDEBAR_STYLE)
        self.setFixedWidth(260)
        self.setMinimumWidth(220)
        self.setMaximumWidth(300)

        self._build_ui()
        self.refresh_conversations()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(0)

        # App logo/title row
        logo_row = QHBoxLayout()
        logo_row.setSpacing(8)

        logo_label = QLabel("✦")
        logo_label.setStyleSheet(
            f"color: {COLORS['accent']}; font-size: 22px; font-weight: bold;"
        )
        logo_row.addWidget(logo_label)

        title_col = QVBoxLayout()
        title_col.setSpacing(0)
        app_title = QLabel("Copilot Chat")
        app_title.setObjectName("app_title")
        app_title.setStyleSheet(
            f"color: {COLORS['sidebar_text']}; font-size: 16px; font-weight: bold;"
        )
        title_col.addWidget(app_title)
        app_sub = QLabel("OpenAI Models")
        app_sub.setObjectName("app_subtitle")
        app_sub.setStyleSheet(
            f"color: {COLORS['sidebar_text_dim']}; font-size: 10px;"
        )
        title_col.addWidget(app_sub)
        logo_row.addLayout(title_col)
        logo_row.addStretch()
        layout.addLayout(logo_row)

        layout.addSpacing(16)

        # New Chat button
        self.new_chat_btn = QPushButton("+ New Chat")
        self.new_chat_btn.setObjectName("new_chat_btn")
        self.new_chat_btn.setCursor(Qt.PointingHandCursor)
        self.new_chat_btn.clicked.connect(self.new_chat_clicked)
        layout.addWidget(self.new_chat_btn)

        layout.addSpacing(20)

        # Conversations section label
        history_label = QLabel("RECENT CHATS")
        history_label.setObjectName("section_label")
        history_label.setStyleSheet(
            f"color: {COLORS['sidebar_text_dim']}; font-size: 10px; "
            "font-weight: 600; letter-spacing: 1px; padding: 0 8px;"
        )
        layout.addWidget(history_label)

        layout.addSpacing(4)

        # Conversation list
        self.conv_list = QListWidget()
        self.conv_list.setObjectName("conversation_list")
        self.conv_list.setStyleSheet(
            f"""
            QListWidget {{
                background-color: transparent;
                border: none;
                padding: 0;
                outline: none;
            }}
            QListWidget::item {{
                color: {COLORS["sidebar_text"]};
                padding: 8px 12px;
                border-radius: 6px;
                margin: 1px 0;
                font-size: 13px;
            }}
            QListWidget::item:hover {{
                background-color: {COLORS["sidebar_hover"]};
            }}
            QListWidget::item:selected {{
                background-color: {COLORS["sidebar_active"]};
                color: {COLORS["sidebar_text"]};
            }}
            """
        )
        self.conv_list.setSpacing(1)
        self.conv_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.conv_list.itemClicked.connect(self._on_item_clicked)
        self.conv_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.conv_list.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.conv_list)

        layout.addStretch(0)
        layout.addSpacing(12)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #2a2a40; border: none; max-height: 1px;")
        layout.addWidget(sep)

        layout.addSpacing(8)

        # Settings button
        self.settings_btn = QPushButton("⚙  Settings")
        self.settings_btn.setObjectName("settings_btn")
        self.settings_btn.setCursor(Qt.PointingHandCursor)
        self.settings_btn.clicked.connect(self.settings_clicked)
        layout.addWidget(self.settings_btn)

    def refresh_conversations(self):
        """Reload the conversation list from the store."""
        self.conv_list.clear()
        for conv in self.store.conversations:
            item = QListWidgetItem(conv.title)
            item.setData(Qt.UserRole, conv.id)
            item.setToolTip(conv.title)
            self.conv_list.addItem(item)

    def select_conversation(self, conv_id: str):
        """Highlight a conversation in the list."""
        for i in range(self.conv_list.count()):
            item = self.conv_list.item(i)
            if item.data(Qt.UserRole) == conv_id:
                self.conv_list.setCurrentItem(item)
                return
        self.conv_list.clearSelection()

    def deselect_all(self):
        """Remove selection from all items."""
        self.conv_list.clearSelection()

    def _on_item_clicked(self, item: QListWidgetItem):
        conv_id = item.data(Qt.UserRole)
        if conv_id:
            self.conversation_selected.emit(conv_id)

    def _show_context_menu(self, pos):
        """Show right-click context menu for conversation items."""
        item = self.conv_list.itemAt(pos)
        if not item:
            return

        conv_id = item.data(Qt.UserRole)
        menu = QMenu(self)
        menu.setStyleSheet(
            f"""
            QMenu {{
                background-color: {COLORS['sidebar_bg']};
                color: {COLORS['sidebar_text']};
                border: 1px solid #3a3a50;
                border-radius: 6px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 6px 16px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: {COLORS['sidebar_hover']};
            }}
            """
        )

        delete_action = QAction("🗑  Delete", self)
        delete_action.triggered.connect(lambda: self.conversation_deleted.emit(conv_id))
        menu.addAction(delete_action)

        menu.exec_(self.conv_list.mapToGlobal(pos))
