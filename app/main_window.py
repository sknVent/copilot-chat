"""Main window with sidebar + chat area layout."""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QSplitter, QMessageBox,
)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QFont

from app.conversation import Conversation, ConversationStore
from app.sidebar import Sidebar
from app.chat_widget import ChatWidget
from app.input_area import InputArea
from app.model_selector import ModelSelector
from app.settings_dialog import SettingsDialog
from app.api_client import StreamWorker, DEFAULT_MODEL
from app.file_handler import build_api_content
from app.styles import MAIN_STYLESHEET


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Copilot Chat")
        self.setMinimumSize(900, 600)
        self.resize(1200, 800)
        self.setStyleSheet(MAIN_STYLESHEET)

        self._store = ConversationStore()
        self._current_conversation: Conversation = None
        self._stream_worker: StreamWorker = None
        self._token = SettingsDialog.load_saved_token()
        self._current_model = DEFAULT_MODEL

        self._build_ui()
        self._check_token_on_startup()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar(self._store)
        self.sidebar.new_chat_requested.connect(self._new_chat)
        self.sidebar.conversation_selected.connect(self._load_conversation)
        self.sidebar.settings_requested.connect(self._open_settings)

        # Chat area (right side)
        chat_area = QWidget()
        chat_area.setStyleSheet("background-color: #FAF9F6;")
        chat_layout = QVBoxLayout(chat_area)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)

        # Model selector at top
        self.model_selector = ModelSelector()
        self.model_selector.model_changed.connect(self._on_model_changed)
        chat_layout.addWidget(self.model_selector)

        # Chat messages area
        self.chat_widget = ChatWidget()
        chat_layout.addWidget(self.chat_widget, 1)

        # Input area at bottom
        self.input_area = InputArea()
        self.input_area.send_message.connect(self._send_message)
        chat_layout.addWidget(self.input_area)

        root_layout.addWidget(self.sidebar)
        root_layout.addWidget(chat_area, 1)

    def _check_token_on_startup(self):
        """Show settings dialog if no token is configured."""
        if not self._token:
            self._show_welcome_setup()

    def _show_welcome_setup(self):
        """Show setup prompt for first-time users."""
        msg = QMessageBox(self)
        msg.setWindowTitle("Welcome to Copilot Chat")
        msg.setText(
            "<b>Welcome to Copilot Chat!</b><br><br>"
            "To get started, you'll need to configure your GitHub Copilot Classic token.<br><br>"
            "Click <b>Open Settings</b> to enter your token."
        )
        msg.setStandardButtons(QMessageBox.Open | QMessageBox.Cancel)
        msg.button(QMessageBox.Open).setText("Open Settings")
        result = msg.exec_()
        if result == QMessageBox.Open:
            self._open_settings()

    def _open_settings(self):
        """Open the settings dialog."""
        dialog = SettingsDialog(self)
        dialog.token_saved.connect(self._on_token_saved)
        dialog.exec_()

    def _on_token_saved(self, token: str):
        """Handle token being saved from settings dialog."""
        self._token = token

    def _on_model_changed(self, model: str):
        """Update the current model."""
        self._current_model = model

    def _new_chat(self):
        """Start a new conversation."""
        if self._stream_worker and self._stream_worker.isRunning():
            self._stream_worker.cancel()

        self._current_conversation = None
        self.chat_widget.clear()
        self.input_area.set_enabled(True)
        self.sidebar.deselect_all()
        self.input_area.focus_input()

    def _load_conversation(self, conversation_id: str):
        """Load a saved conversation."""
        if self._stream_worker and self._stream_worker.isRunning():
            self._stream_worker.cancel()

        conv = self._store.get_by_id(conversation_id)
        if conv is None:
            return

        self._current_conversation = conv
        self.chat_widget.load_conversation(conv.messages)
        self.sidebar.select_conversation(conversation_id)
        self.input_area.set_enabled(True)
        self.input_area.focus_input()

    def _send_message(self, text: str, files: list):
        """Handle sending a message."""
        if not self._token:
            self._show_welcome_setup()
            return

        if self._stream_worker and self._stream_worker.isRunning():
            return  # Don't allow sending while streaming

        # Ensure we have a conversation
        if self._current_conversation is None:
            self._current_conversation = Conversation()
            self._store.add(self._current_conversation)

        # Build API content (text + files)
        api_content = build_api_content(text, files)

        # Add to conversation
        self._current_conversation.add_message("user", api_content)
        self._store.update(self._current_conversation)

        # Display user message in UI
        display_text = text
        self.chat_widget.add_user_message(display_text, files)

        # Update sidebar
        self.sidebar.refresh_conversations()
        self.sidebar.select_conversation(self._current_conversation.conversation_id)

        # Disable input while streaming
        self.input_area.set_enabled(False)

        # Start assistant bubble
        self._current_assistant_bubble = self.chat_widget.start_assistant_message()

        # Start streaming
        self._stream_worker = StreamWorker(
            token=self._token,
            messages=self._current_conversation.get_api_messages(),
            model=self._current_model,
        )
        self._stream_worker.chunk_received.connect(self._on_chunk)
        self._stream_worker.finished.connect(self._on_stream_finished)
        self._stream_worker.error_occurred.connect(self._on_stream_error)
        self._stream_worker.start()

    def _on_chunk(self, chunk: str):
        """Handle an incoming chunk from the stream."""
        if self._current_assistant_bubble:
            self._current_assistant_bubble.append_text(chunk)
            self.chat_widget._scroll_to_bottom()

    def _on_stream_finished(self):
        """Handle stream completion."""
        if self._current_assistant_bubble and self._current_conversation:
            full_text = self._current_assistant_bubble.get_text()
            self._current_conversation.add_message("assistant", full_text)
            self._store.update(self._current_conversation)
            self.sidebar.refresh_conversations()

        self._current_assistant_bubble = None
        self.input_area.set_enabled(True)
        self.input_area.focus_input()

    def _on_stream_error(self, error: str):
        """Handle stream error."""
        if self._current_assistant_bubble:
            self._current_assistant_bubble.setParent(None)
            self._current_assistant_bubble = None

        self.chat_widget.add_error_message(error)
        self.input_area.set_enabled(True)
        self.input_area.focus_input()

    def closeEvent(self, event):
        """Handle window close."""
        if self._stream_worker and self._stream_worker.isRunning():
            self._stream_worker.cancel()
            self._stream_worker.wait(2000)
        self._store.save()
        super().closeEvent(event)
