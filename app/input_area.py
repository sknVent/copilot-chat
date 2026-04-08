"""Input text area with send/attach buttons."""

import os
from typing import List

from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QTextEdit,
    QLabel, QFileDialog, QSizePolicy, QScrollArea,
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QKeyEvent, QFont

from app.file_handler import process_file, FILE_FILTER, FileProcessingError
from app.styles import INPUT_AREA_STYLESHEET


class MessageInput(QTextEdit):
    """A text edit that sends on Enter and adds newlines on Shift+Enter."""

    send_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Message Copilot... (Enter to send, Shift+Enter for new line)")
        self.setAcceptRichText(False)
        self.setMinimumHeight(44)
        self.setMaximumHeight(160)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.document().contentsChanged.connect(self._adjust_height)

    def _adjust_height(self):
        doc_height = int(self.document().size().height()) + 16
        new_height = max(44, min(doc_height, 160))
        self.setFixedHeight(new_height)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if event.modifiers() & Qt.ShiftModifier:
                super().keyPressEvent(event)
            else:
                self.send_requested.emit()
        else:
            super().keyPressEvent(event)


class InputArea(QWidget):
    """Bottom input area with text input, attach, and send buttons."""

    send_message = pyqtSignal(str, list)  # (text, files)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("inputContainer")
        self.setStyleSheet(INPUT_AREA_STYLESHEET)
        self._attached_files: List[dict] = []
        self._build_ui()

    def _build_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(16, 12, 16, 16)
        outer_layout.setSpacing(8)

        # Attached files row (hidden when empty)
        self.files_row = QWidget()
        files_layout = QHBoxLayout(self.files_row)
        files_layout.setContentsMargins(0, 0, 0, 0)
        files_layout.setSpacing(6)
        self.files_layout = files_layout
        self.files_row.hide()
        outer_layout.addWidget(self.files_row)

        # Input box container
        input_box = QWidget()
        input_box.setObjectName("inputBox")
        box_layout = QVBoxLayout(input_box)
        box_layout.setContentsMargins(8, 8, 8, 8)
        box_layout.setSpacing(8)

        # Text area
        self.text_input = MessageInput()
        self.text_input.setObjectName("messageInput")
        self.text_input.send_requested.connect(self._on_send)
        box_layout.addWidget(self.text_input)

        # Buttons row
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(4, 0, 4, 0)
        btn_row.setSpacing(8)

        self.attach_btn = QPushButton("📎")
        self.attach_btn.setObjectName("attachButton")
        self.attach_btn.setToolTip("Attach file (images, Excel, Python, text)")
        self.attach_btn.setFixedSize(QSize(36, 32))
        self.attach_btn.clicked.connect(self._attach_file)

        char_hint = QLabel("Enter to send • Shift+Enter for new line")
        char_hint.setStyleSheet("color: #9ca3af; font-size: 11px;")

        self.send_btn = QPushButton("Send")
        self.send_btn.setObjectName("sendButton")
        self.send_btn.setFixedSize(QSize(72, 32))
        self.send_btn.clicked.connect(self._on_send)

        btn_row.addWidget(self.attach_btn)
        btn_row.addWidget(char_hint)
        btn_row.addStretch()
        btn_row.addWidget(self.send_btn)
        box_layout.addLayout(btn_row)

        outer_layout.addWidget(input_box)

    def _attach_file(self):
        """Open file dialog and attach selected files."""
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Attach Files",
            os.path.expanduser("~"),
            FILE_FILTER,
        )
        for path in paths:
            self._add_attachment(path)

    def _add_attachment(self, path: str):
        """Process and add a file attachment."""
        try:
            file_info = process_file(path)
            self._attached_files.append(file_info)
            self._update_files_display()
        except FileProcessingError as e:
            # Show inline error
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "File Error", str(e))

    def _update_files_display(self):
        """Rebuild the attached files display row."""
        # Clear existing file labels (keep only the last label which is the stretch)
        while self.files_layout.count() > 0:
            item = self.files_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        for i, file_info in enumerate(self._attached_files):
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(4)

            label = QLabel(file_info["display"])
            label.setObjectName("attachedFile")

            idx = i
            remove_btn = QPushButton("✕")
            remove_btn.setFlat(True)
            remove_btn.setFixedSize(QSize(16, 16))
            remove_btn.setStyleSheet("color: #92400E; border: none; font-size: 10px;")
            remove_btn.clicked.connect(lambda checked, i=idx: self._remove_attachment(i))

            layout.addWidget(label)
            layout.addWidget(remove_btn)
            self.files_layout.addWidget(container)

        self.files_layout.addStretch()
        self.files_row.setVisible(len(self._attached_files) > 0)

    def _remove_attachment(self, index: int):
        """Remove an attachment by index."""
        if 0 <= index < len(self._attached_files):
            self._attached_files.pop(index)
            self._update_files_display()

    def _on_send(self):
        """Emit send_message signal with text and attached files."""
        text = self.text_input.toPlainText().strip()
        if not text and not self._attached_files:
            return

        files = list(self._attached_files)
        self._attached_files.clear()
        self._update_files_display()
        self.text_input.clear()

        self.send_message.emit(text, files)

    def set_enabled(self, enabled: bool):
        """Enable or disable the input area."""
        self.text_input.setEnabled(enabled)
        self.send_btn.setEnabled(enabled)
        self.attach_btn.setEnabled(enabled)
        if enabled:
            self.text_input.setFocus()

    def focus_input(self):
        """Focus the text input."""
        self.text_input.setFocus()
