"""
Main application window combining sidebar, chat area, and input.
"""
from typing import Optional, List, Dict, Any

from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QMessageBox,
    QSplitter,
    QFrame,
    QApplication,
)
from PyQt5.QtCore import Qt, QTimer, pyqtSlot
from PyQt5.QtGui import QFont, QClipboard

from app.styles import MAIN_STYLE, COLORS, HEADER_STYLE
from app.conversation import Conversation, ConversationStore, Message, Settings
from app.sidebar import Sidebar
from app.chat_widget import ChatWidget
from app.input_area import InputArea
from app.model_selector import ModelSelector
from app.settings_dialog import SettingsDialog
from app.api_client import ApiWorker


class MainWindow(QMainWindow):
    """
    Main application window with:
    - Left: dark sidebar (conversations, settings)
    - Right: chat header, message area, input area
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Copilot Chat")
        self.setMinimumSize(900, 600)
        self.resize(1200, 800)

        self.settings = Settings()
        self.store = ConversationStore()
        self.current_conversation: Optional[Conversation] = None
        self._api_worker: Optional[ApiWorker] = None

        self.setStyleSheet(MAIN_STYLE)
        self._build_ui()

        # If no token configured, show settings on startup
        if not self.settings.copilot_token:
            QTimer.singleShot(400, self._prompt_for_token)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar(self.store, self)
        self.sidebar.new_chat_clicked.connect(self._new_chat)
        self.sidebar.conversation_selected.connect(self._load_conversation)
        self.sidebar.conversation_deleted.connect(self._delete_conversation)
        self.sidebar.settings_clicked.connect(self._open_settings)
        main_layout.addWidget(self.sidebar)

        # Right pane (header + chat + input)
        right_pane = QWidget()
        right_pane.setStyleSheet(f"background-color: {COLORS['chat_bg']};")
        right_layout = QVBoxLayout(right_pane)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Chat header
        self._header = self._build_header()
        right_layout.addWidget(self._header)

        # Chat widget (scrollable messages)
        self.chat_widget = ChatWidget(self)
        self.chat_widget.copy_requested.connect(self._copy_to_clipboard)
        right_layout.addWidget(self.chat_widget, 1)

        # Input area
        self.input_area = InputArea(self)
        self.input_area.message_sent.connect(self._handle_send)
        self.input_area.error_occurred.connect(self._show_error)
        right_layout.addWidget(self.input_area)

        main_layout.addWidget(right_pane, 1)

    def _build_header(self) -> QWidget:
        """Build the top header bar with title and model selector."""
        header = QWidget()
        header.setObjectName("chat_header")
        header.setFixedHeight(56)
        header.setStyleSheet(
            f"QWidget#chat_header {{"
            f"  background-color: {COLORS['chat_bg']};"
            f"  border-bottom: 1px solid {COLORS['separator']};"
            f"}}"
        )

        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 8, 20, 8)
        layout.setSpacing(12)

        self.chat_title_label = QLabel("New Chat")
        self.chat_title_label.setObjectName("chat_title")
        self.chat_title_label.setStyleSheet(
            "font-size: 15px; font-weight: 600; color: #2d2520;"
        )
        layout.addWidget(self.chat_title_label)

        layout.addStretch()

        model_label = QLabel("Model:")
        model_label.setStyleSheet("color: #9e9087; font-size: 13px;")
        layout.addWidget(model_label)

        self.model_selector = ModelSelector(
            self, initial_model=self.settings.default_model
        )
        self.model_selector.model_changed.connect(self._on_model_changed)
        layout.addWidget(self.model_selector)

        return header

    # -------------------------------------------------------------------------
    # Chat lifecycle
    # -------------------------------------------------------------------------

    def _new_chat(self):
        """Start a new empty conversation."""
        # Stop any ongoing API call
        self._stop_api_worker()

        self.current_conversation = None
        self.chat_widget.clear_messages()
        self.chat_title_label.setText("New Chat")
        self.sidebar.deselect_all()
        self.input_area.set_enabled(True)
        self.input_area.focus_input()

    def _load_conversation(self, conv_id: str):
        """Load and display an existing conversation."""
        self._stop_api_worker()

        conv = self.store.get_conversation(conv_id)
        if not conv:
            return

        self.current_conversation = conv
        self.chat_widget.clear_messages()
        self.chat_title_label.setText(conv.title)

        # Display all messages
        for msg in conv.messages:
            self.chat_widget.add_message(msg.role, msg.content, msg.files)

        # Set model to match conversation
        self.model_selector.set_model(conv.model)
        self.sidebar.select_conversation(conv_id)
        self.input_area.set_enabled(True)
        self.input_area.focus_input()

    def _delete_conversation(self, conv_id: str):
        """Delete a conversation."""
        if self.current_conversation and self.current_conversation.id == conv_id:
            self._new_chat()

        self.store.delete_conversation(conv_id)
        self.sidebar.refresh_conversations()

    # -------------------------------------------------------------------------
    # Sending messages
    # -------------------------------------------------------------------------

    @pyqtSlot(str, list)
    def _handle_send(self, text: str, files: List[Dict[str, Any]]):
        """Handle a new message being sent."""
        if not text.strip() and not files:
            return

        # Check token
        if not self.settings.copilot_token:
            self._show_error(
                "No Copilot token configured. Please go to Settings and add your token."
            )
            self._open_settings()
            return

        # Create conversation if needed
        if self.current_conversation is None:
            self.current_conversation = Conversation(
                model=self.model_selector.get_model()
            )

        # Build user message
        user_msg = Message(role="user", content=text, files=files)
        self.current_conversation.add_message(user_msg)

        # Update title label
        self.chat_title_label.setText(self.current_conversation.title)

        # Display user message
        self.chat_widget.add_message("user", text, files)

        # Disable input while waiting for response
        self.input_area.set_enabled(False)

        # Build API message list
        api_messages = self.current_conversation.get_api_messages()

        # Start assistant bubble for streaming
        self.chat_widget.start_assistant_message()

        # Launch API worker
        model = self.model_selector.get_model()
        self.current_conversation.model = model

        self._api_worker = ApiWorker(
            token=self.settings.copilot_token,
            model=model,
            messages=api_messages,
            parent=self,
        )
        self._api_worker.token_received.connect(self._on_token)
        self._api_worker.finished.connect(self._on_api_finished)
        self._api_worker.error.connect(self._on_api_error)
        self._api_worker.start()

    @pyqtSlot(str)
    def _on_token(self, token: str):
        """Append a streaming token to the assistant message."""
        self.chat_widget.append_to_assistant(token)

    @pyqtSlot()
    def _on_api_finished(self):
        """Handle successful completion of API response."""
        # Get the final content from the current bubble
        if self.chat_widget._current_assistant_bubble:
            content = self.chat_widget._current_assistant_bubble.content
        else:
            content = ""

        self.chat_widget.finish_assistant_message()

        # Save assistant message to conversation
        if self.current_conversation:
            assistant_msg = Message(role="assistant", content=content)
            self.current_conversation.add_message(assistant_msg)
            self.store.update_conversation(self.current_conversation)
            self.sidebar.refresh_conversations()
            self.sidebar.select_conversation(self.current_conversation.id)

        self.input_area.set_enabled(True)
        self.input_area.focus_input()
        self._api_worker = None

    @pyqtSlot(str)
    def _on_api_error(self, error_msg: str):
        """Handle API error."""
        self.chat_widget.finish_assistant_message()

        # Replace the empty assistant bubble with an error message
        if self.chat_widget._message_widgets:
            last = self.chat_widget._message_widgets[-1]
            if last.role == "assistant" and not last.content:
                last.update_content(f"⚠️ **Error:** {error_msg}")

        self.input_area.set_enabled(True)
        self.input_area.focus_input()
        self._api_worker = None

    def _stop_api_worker(self):
        """Stop any running API worker."""
        if self._api_worker and self._api_worker.isRunning():
            self._api_worker.abort()
            self._api_worker.wait(2000)
            self._api_worker = None

    # -------------------------------------------------------------------------
    # Model selection
    # -------------------------------------------------------------------------

    def _on_model_changed(self, model_id: str):
        """Handle model selector change."""
        self.settings.default_model = model_id
        if self.current_conversation:
            self.current_conversation.model = model_id

    # -------------------------------------------------------------------------
    # Settings
    # -------------------------------------------------------------------------

    def _open_settings(self):
        """Open the settings dialog."""
        dialog = SettingsDialog(self.settings, self)
        dialog.settings_saved.connect(self._on_settings_saved)
        dialog.exec_()

    def _on_settings_saved(self):
        """Handle settings being saved."""
        pass  # Nothing special needed; settings are already persisted

    def _prompt_for_token(self):
        """Show a prompt asking user to configure token."""
        msg = QMessageBox(self)
        msg.setWindowTitle("Welcome to Copilot Chat")
        msg.setText(
            "Welcome! To get started, you need to configure your\n"
            "GitHub Copilot Classic token.\n\n"
            "Click 'Open Settings' to add your token."
        )
        msg.setIcon(QMessageBox.Information)
        open_btn = msg.addButton("Open Settings", QMessageBox.AcceptRole)
        msg.addButton("Later", QMessageBox.RejectRole)
        msg.exec_()

        if msg.clickedButton() == open_btn:
            self._open_settings()

    # -------------------------------------------------------------------------
    # Utilities
    # -------------------------------------------------------------------------

    def _copy_to_clipboard(self, text: str):
        """Copy text to clipboard."""
        QApplication.clipboard().setText(text)

    def _show_error(self, message: str):
        """Show an error message dialog."""
        QMessageBox.critical(self, "Error", message)

    def closeEvent(self, event):
        """Clean up on close."""
        self._stop_api_worker()
        event.accept()
