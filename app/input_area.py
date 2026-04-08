"""
Input area with text input, send button, and file attachment button.
"""
import os
from typing import List, Dict, Any

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QFrame,
    QLabel,
    QFileDialog,
    QSizePolicy,
    QScrollArea,
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QKeyEvent, QFont, QPixmap, QImage

from app.styles import COLORS, INPUT_AREA_STYLE, FILE_TAG_STYLE
from app.file_handler import (
    FILE_FILTER,
    process_file,
    get_file_icon,
    format_file_size,
    FileProcessingError,
    get_image_thumbnail,
)


class FileTag(QFrame):
    """A small widget showing an attached file with a remove button."""

    remove_clicked = pyqtSignal(int)  # emits index

    def __init__(self, file_info: Dict[str, Any], index: int, parent=None):
        super().__init__(parent)
        self.index = index
        self.file_info = file_info
        self.setObjectName("file_tag")
        self.setStyleSheet(
            "QFrame#file_tag {"
            f"  background-color: {COLORS['tag_bg']};"
            "  border-radius: 8px;"
            "  border: 1px solid #d8d0c8;"
            "}"
        )
        self.setFixedHeight(36)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 4, 4)
        layout.setSpacing(4)

        # Image thumbnail or icon
        if file_info.get("type") == "image" and file_info.get("file_path"):
            thumb = get_image_thumbnail(file_info["file_path"], max_size=28)
            if thumb:
                img = QImage.fromData(thumb)
                pix = QPixmap.fromImage(img).scaled(
                    24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                icon_label = QLabel()
                icon_label.setPixmap(pix)
                icon_label.setFixedSize(24, 24)
                layout.addWidget(icon_label)
            else:
                icon_label = QLabel("🖼️")
                icon_label.setStyleSheet(
                    f"color: {COLORS['tag_text']}; font-size: 14px; border: none;"
                )
                layout.addWidget(icon_label)
        else:
            icon = get_file_icon(file_info.get("type", "text"))
            icon_label = QLabel(icon)
            icon_label.setStyleSheet(
                f"color: {COLORS['tag_text']}; font-size: 14px; border: none;"
            )
            layout.addWidget(icon_label)

        # Filename
        name = file_info.get("name", "file")
        size = format_file_size(file_info.get("size", 0))
        text_label = QLabel(f"{name} ({size})")
        text_label.setStyleSheet(
            f"color: {COLORS['tag_text']}; font-size: 12px; border: none;"
        )
        text_label.setMaximumWidth(200)
        layout.addWidget(text_label)

        # Remove button
        remove_btn = QPushButton("✕")
        remove_btn.setObjectName("file_tag_remove")
        remove_btn.setStyleSheet(
            "QPushButton {"
            "  background: transparent;"
            "  color: #9e9087;"
            "  border: none;"
            "  font-size: 12px;"
            "  padding: 2px 4px;"
            "  border-radius: 4px;"
            "}"
            "QPushButton:hover {"
            "  background-color: #d8d0c8;"
            "  color: #5c4a3a;"
            "}"
        )
        remove_btn.setFixedSize(20, 20)
        remove_btn.clicked.connect(lambda: self.remove_clicked.emit(self.index))
        layout.addWidget(remove_btn)


class MessageInput(QTextEdit):
    """
    Multi-line text input that sends on Enter and adds newlines on Shift+Enter.
    """

    send_triggered = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("message_input")
        self.setPlaceholderText("Message Copilot...")
        self.setMinimumHeight(44)
        self.setMaximumHeight(160)
        self.setLineWrapMode(QTextEdit.WidgetWidth)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.document().contentsChanged.connect(self._adjust_height)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if event.modifiers() & Qt.ShiftModifier:
                # Shift+Enter = newline
                super().keyPressEvent(event)
            else:
                # Enter = send
                self.send_triggered.emit()
        else:
            super().keyPressEvent(event)

    def _adjust_height(self):
        """Dynamically adjust height based on content."""
        doc_height = int(self.document().size().height())
        margin = self.contentsMargins().top() + self.contentsMargins().bottom()
        new_height = max(44, min(doc_height + margin + 8, 160))
        self.setFixedHeight(new_height)


class InputArea(QWidget):
    """
    The bottom input area including text input, send button, and file attachment.
    """

    message_sent = pyqtSignal(str, list)  # text, list of file_info dicts
    error_occurred = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("input_area")
        self.setStyleSheet(INPUT_AREA_STYLE)
        self._attached_files: List[Dict[str, Any]] = []
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 8, 16, 12)
        outer.setSpacing(6)

        # File tags area (shown when files are attached)
        self.files_area = QWidget()
        self.files_area.hide()
        files_layout = QHBoxLayout(self.files_area)
        files_layout.setContentsMargins(0, 0, 0, 0)
        files_layout.setSpacing(6)
        self.files_layout = files_layout
        files_layout.addStretch()
        outer.addWidget(self.files_area)

        # Input frame (contains text + buttons)
        input_frame = QFrame()
        input_frame.setObjectName("input_frame")
        input_frame.setStyleSheet(
            "QFrame#input_frame {"
            f"  background-color: {COLORS['input_bg']};"
            f"  border: 2px solid {COLORS['input_border']};"
            "  border-radius: 12px;"
            "}"
        )

        frame_layout = QVBoxLayout(input_frame)
        frame_layout.setContentsMargins(8, 4, 8, 4)
        frame_layout.setSpacing(0)

        # Text input row
        text_row = QHBoxLayout()
        text_row.setSpacing(4)
        text_row.setContentsMargins(0, 0, 0, 0)

        # Attach button
        self.attach_btn = QPushButton("📎")
        self.attach_btn.setObjectName("attach_btn")
        self.attach_btn.setToolTip("Attach file (images, Excel, Python, text)")
        self.attach_btn.setFixedSize(36, 36)
        self.attach_btn.setCursor(Qt.PointingHandCursor)
        self.attach_btn.clicked.connect(self._attach_file)
        text_row.addWidget(self.attach_btn, 0, Qt.AlignBottom)

        # Text input
        self.text_input = MessageInput()
        self.text_input.send_triggered.connect(self._send_message)
        text_row.addWidget(self.text_input)

        # Send button
        self.send_btn = QPushButton("↑")
        self.send_btn.setObjectName("send_btn")
        self.send_btn.setToolTip("Send message (Enter)")
        self.send_btn.setFixedSize(40, 40)
        self.send_btn.setCursor(Qt.PointingHandCursor)
        self.send_btn.clicked.connect(self._send_message)
        text_row.addWidget(self.send_btn, 0, Qt.AlignBottom)

        frame_layout.addLayout(text_row)
        outer.addWidget(input_frame)

        # Footer hint
        hint = QLabel("Enter to send · Shift+Enter for new line")
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet("color: #b0a898; font-size: 11px;")
        outer.addWidget(hint)

    def _send_message(self):
        """Send the current message with any attached files."""
        text = self.text_input.toPlainText().strip()
        if not text and not self._attached_files:
            return

        files = list(self._attached_files)
        self.message_sent.emit(text, files)

        # Clear input
        self.text_input.clear()
        self._clear_files()

    def _attach_file(self):
        """Open file dialog to attach a file."""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Attach Files",
            "",
            FILE_FILTER,
        )

        for path in file_paths:
            if not path:
                continue
            try:
                file_info = process_file(path)
                self._add_file(file_info)
            except FileProcessingError as e:
                self.error_occurred.emit(str(e))

    def _add_file(self, file_info: Dict[str, Any]):
        """Add a file to the attachment list."""
        index = len(self._attached_files)
        self._attached_files.append(file_info)

        tag = FileTag(file_info, index, self)
        tag.remove_clicked.connect(self._remove_file)

        # Insert before the stretch
        insert_pos = self.files_layout.count() - 1
        self.files_layout.insertWidget(insert_pos, tag)

        self.files_area.show()

    def _remove_file(self, index: int):
        """Remove a file from the attachment list."""
        if 0 <= index < len(self._attached_files):
            self._attached_files.pop(index)

        # Rebuild the file tags UI
        self._rebuild_file_tags()

        if not self._attached_files:
            self.files_area.hide()

    def _rebuild_file_tags(self):
        """Rebuild all file tags after removing one."""
        # Remove all tag widgets (except the stretch at the end)
        while self.files_layout.count() > 1:
            item = self.files_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Re-add all remaining files
        for i, file_info in enumerate(self._attached_files):
            tag = FileTag(file_info, i, self)
            tag.remove_clicked.connect(self._remove_file)
            self.files_layout.insertWidget(i, tag)

    def _clear_files(self):
        """Clear all attached files."""
        self._attached_files.clear()
        self._rebuild_file_tags()
        self.files_area.hide()

    def set_enabled(self, enabled: bool):
        """Enable or disable the input area."""
        self.text_input.setEnabled(enabled)
        self.send_btn.setEnabled(enabled)
        self.attach_btn.setEnabled(enabled)

    def focus_input(self):
        """Set focus to the text input."""
        self.text_input.setFocus()
