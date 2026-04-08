"""
Settings dialog for configuring the GitHub Copilot token.
"""
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QSizePolicy,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

from app.styles import SETTINGS_DIALOG_STYLE
from app.conversation import Settings


class ConnectionTestWorker(QThread):
    """Worker thread for testing the API connection."""

    result_ready = pyqtSignal(bool, str)

    def __init__(self, token: str, parent=None):
        super().__init__(parent)
        self.token = token

    def run(self):
        from app.api_client import test_connection
        success, message = test_connection(self.token)
        self.result_ready.emit(success, message)


class SettingsDialog(QDialog):
    """
    Settings dialog for managing the GitHub Copilot Classic token.
    """

    settings_saved = pyqtSignal()

    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self._test_worker: ConnectionTestWorker = None

        self.setWindowTitle("Settings")
        self.setMinimumWidth(520)
        self.setModal(True)
        self.setStyleSheet(SETTINGS_DIALOG_STYLE)

        self._build_ui()
        self._load_settings()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(0)

        # Title
        title = QLabel("⚙️  Settings")
        title.setObjectName("dialog_title")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        layout.addWidget(title)
        layout.addSpacing(24)

        # Token section header
        token_header = QLabel("GITHUB COPILOT TOKEN")
        token_header.setObjectName("section_header")
        layout.addWidget(token_header)
        layout.addSpacing(8)

        # Token description
        desc = QLabel(
            "Enter your GitHub Copilot Classic token to authenticate with the API.\n"
            "You can get this token from your GitHub account settings."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #7a6a5a; font-size: 13px;")
        layout.addWidget(desc)
        layout.addSpacing(12)

        # Token input
        self.token_input = QLineEdit()
        self.token_input.setObjectName("token_input")
        self.token_input.setEchoMode(QLineEdit.Password)
        self.token_input.setPlaceholderText("ghu_xxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        self.token_input.setMinimumHeight(42)
        layout.addWidget(self.token_input)
        layout.addSpacing(8)

        # Show/hide token toggle
        show_row = QHBoxLayout()
        self.show_token_btn = QPushButton("👁  Show token")
        self.show_token_btn.setObjectName("secondary_btn")
        self.show_token_btn.setCheckable(True)
        self.show_token_btn.setFixedHeight(36)
        self.show_token_btn.clicked.connect(self._toggle_token_visibility)
        show_row.addWidget(self.show_token_btn)
        show_row.addStretch()
        layout.addLayout(show_row)
        layout.addSpacing(16)

        # Test connection button
        test_row = QHBoxLayout()
        self.test_btn = QPushButton("🔌  Test Connection")
        self.test_btn.setObjectName("test_btn")
        self.test_btn.setFixedHeight(38)
        self.test_btn.clicked.connect(self._test_connection)
        test_row.addWidget(self.test_btn)
        test_row.addStretch()
        layout.addLayout(test_row)
        layout.addSpacing(8)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setObjectName("status_info")
        self.status_label.setWordWrap(True)
        self.status_label.hide()
        layout.addWidget(self.status_label)

        # Spacer
        layout.addSpacing(24)

        # Separator line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #e8e0d8; border: none; max-height: 1px;")
        layout.addWidget(line)
        layout.addSpacing(20)

        # How to get token section
        help_header = QLabel("HOW TO GET YOUR TOKEN")
        help_header.setObjectName("section_header")
        layout.addWidget(help_header)
        layout.addSpacing(8)

        help_text = QLabel(
            "1. Go to github.com → Settings → Developer settings\n"
            "2. Select 'Personal access tokens' → 'Tokens (classic)'\n"
            "3. Click 'Generate new token (classic)'\n"
            "4. Give it a name and select the 'copilot' scope\n"
            "5. Copy the generated token and paste it above"
        )
        help_text.setStyleSheet("color: #7a6a5a; font-size: 13px; line-height: 1.6;")
        help_text.setWordWrap(True)
        layout.addWidget(help_text)

        layout.addSpacing(28)

        # Buttons row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondary_btn")
        cancel_btn.setFixedHeight(42)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        btn_row.addStretch()

        save_btn = QPushButton("Save Settings")
        save_btn.setObjectName("primary_btn")
        save_btn.setFixedHeight(42)
        save_btn.setMinimumWidth(140)
        save_btn.clicked.connect(self._save_settings)
        btn_row.addWidget(save_btn)

        layout.addLayout(btn_row)

    def _load_settings(self):
        """Load current settings into the form."""
        token = self.settings.copilot_token
        if token:
            self.token_input.setText(token)

    def _toggle_token_visibility(self, checked: bool):
        """Toggle between showing and hiding the token."""
        if checked:
            self.token_input.setEchoMode(QLineEdit.Normal)
            self.show_token_btn.setText("🙈  Hide token")
        else:
            self.token_input.setEchoMode(QLineEdit.Password)
            self.show_token_btn.setText("👁  Show token")

    def _test_connection(self):
        """Test the Copilot API connection."""
        token = self.token_input.text().strip()
        if not token:
            self._show_status("Please enter a token first.", "error")
            return

        self.test_btn.setEnabled(False)
        self.test_btn.setText("Testing...")
        self._show_status("Testing connection to GitHub Copilot API...", "info")

        self._test_worker = ConnectionTestWorker(token, self)
        self._test_worker.result_ready.connect(self._on_test_result)
        self._test_worker.start()

    def _on_test_result(self, success: bool, message: str):
        """Handle connection test result."""
        self.test_btn.setEnabled(True)
        self.test_btn.setText("🔌  Test Connection")

        if success:
            self._show_status(message, "success")
        else:
            self._show_status(message, "error")

    def _show_status(self, message: str, status_type: str = "info"):
        """Show a status message below the test button."""
        self.status_label.setText(message)
        self.status_label.show()

        type_map = {
            "success": "status_ok",
            "error": "status_error",
            "info": "status_info",
        }
        obj_name = type_map.get(status_type, "status_info")
        self.status_label.setObjectName(obj_name)
        # Re-apply style to pick up new object name
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

    def _save_settings(self):
        """Save settings and close dialog."""
        token = self.token_input.text().strip()
        self.settings.copilot_token = token
        self.settings_saved.emit()
        self.accept()
