"""Settings / token configuration dialog."""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QSpacerItem, QSizePolicy,
)
from PyQt5.QtCore import Qt, QSettings, QThread, pyqtSignal
from PyQt5.QtGui import QFont

from app.styles import SETTINGS_DIALOG_STYLESHEET


class TestWorker(QThread):
    """Background thread for testing the token."""
    result = pyqtSignal(bool, str)

    def __init__(self, token: str):
        super().__init__()
        self.token = token

    def run(self):
        try:
            from app.api_client import test_connection
            test_connection(self.token)
            self.result.emit(True, "Connection successful! Your token is working.")
        except Exception as e:
            self.result.emit(False, str(e))


class SettingsDialog(QDialog):
    """Dialog for configuring the Copilot Classic token."""

    token_saved = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(520)
        self.setModal(True)
        self.setStyleSheet(SETTINGS_DIALOG_STYLESHEET)
        self._test_worker = None
        self._build_ui()
        self._load_token()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        # Title
        title = QLabel("⚙️  Settings")
        title.setObjectName("dialogTitle")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        layout.addWidget(title)

        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #e5e7eb;")
        layout.addWidget(line)

        # Token section
        token_label = QLabel("GitHub Copilot Classic Token")
        token_label.setObjectName("fieldLabel")
        layout.addWidget(token_label)

        hint = QLabel(
            "Enter your GitHub Copilot Classic token. "
            "You can generate one at: github.com → Settings → Developer settings → "
            "Personal access tokens → Tokens (classic) — with the 'copilot' scope."
        )
        hint.setObjectName("fieldHint")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        self.token_input = QLineEdit()
        self.token_input.setObjectName("tokenInput")
        self.token_input.setEchoMode(QLineEdit.Password)
        self.token_input.setPlaceholderText("ghp_xxxxxxxxxxxxxxxxxxxx")
        layout.addWidget(self.token_input)

        # Show/hide toggle
        self.show_token_btn = QPushButton("Show token")
        self.show_token_btn.setFlat(True)
        self.show_token_btn.setStyleSheet("color: #D97706; border: none; text-align: left; font-size: 12px;")
        self.show_token_btn.clicked.connect(self._toggle_token_visibility)
        layout.addWidget(self.show_token_btn)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setWordWrap(True)
        self.status_label.hide()
        layout.addWidget(self.status_label)

        layout.addItem(QSpacerItem(0, 8, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.test_btn = QPushButton("Test Connection")
        self.test_btn.setObjectName("testButton")
        self.test_btn.clicked.connect(self._test_connection)

        self.save_btn = QPushButton("Save")
        self.save_btn.setObjectName("saveButton")
        self.save_btn.clicked.connect(self._save)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(self.test_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)

    def _load_token(self):
        settings = QSettings()
        token = settings.value("copilot_token", "")
        if token:
            self.token_input.setText(token)

    def _toggle_token_visibility(self):
        if self.token_input.echoMode() == QLineEdit.Password:
            self.token_input.setEchoMode(QLineEdit.Normal)
            self.show_token_btn.setText("Hide token")
        else:
            self.token_input.setEchoMode(QLineEdit.Password)
            self.show_token_btn.setText("Show token")

    def _set_status(self, text: str, status: str):
        """Display a status message. status: 'success', 'error', or 'testing'"""
        self.status_label.setText(text)
        self.status_label.setProperty("status", status)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
        self.status_label.show()

    def _test_connection(self):
        token = self.token_input.text().strip()
        if not token:
            self._set_status("Please enter a token first.", "error")
            return

        self.test_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self._set_status("Testing connection...", "testing")

        self._test_worker = TestWorker(token)
        self._test_worker.result.connect(self._on_test_result)
        self._test_worker.start()

    def _on_test_result(self, success: bool, message: str):
        self.test_btn.setEnabled(True)
        self.save_btn.setEnabled(True)
        if success:
            self._set_status(f"✅  {message}", "success")
        else:
            self._set_status(f"❌  {message}", "error")

    def _save(self):
        token = self.token_input.text().strip()
        settings = QSettings()
        settings.setValue("copilot_token", token)
        self.token_saved.emit(token)
        self.accept()

    def get_token(self) -> str:
        return self.token_input.text().strip()

    @staticmethod
    def load_saved_token() -> str:
        """Load the saved token from QSettings."""
        settings = QSettings()
        return settings.value("copilot_token", "")
