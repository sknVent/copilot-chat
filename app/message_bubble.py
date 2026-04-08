"""
Individual message bubble widget for displaying chat messages.
"""
import re
from typing import List, Dict, Any

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
    QSizePolicy,
    QApplication,
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QImage, QColor

from app.styles import COLORS


def simple_markdown_to_html(text: str) -> str:
    """
    Convert basic markdown to HTML for display in QLabel.
    Handles: bold, italic, inline code, code blocks, lists, headers.
    """
    # Escape HTML special chars first (except we'll re-add intentional tags)
    # We process block by block

    lines = text.split("\n")
    html_parts = []
    in_code_block = False
    code_lang = ""
    code_lines = []
    in_list = False

    i = 0
    while i < len(lines):
        line = lines[i]

        # Code block start/end
        if line.startswith("```"):
            if in_code_block:
                # End code block
                code_content = "\n".join(code_lines)
                code_content = _escape_html(code_content)
                # Replace spaces with non-breaking for indentation
                code_content = code_content.replace("  ", "&nbsp;&nbsp;")
                html_parts.append(
                    f'<pre style="background-color:{COLORS["code_bg"]};'
                    f'color:{COLORS["code_text"]};'
                    f'border-radius:8px;padding:12px;margin:8px 0;'
                    f'font-family:\'Consolas\',\'Courier New\',monospace;'
                    f'font-size:13px;overflow:auto;">'
                    f"<code>{code_content}</code></pre>"
                )
                in_code_block = False
                code_lang = ""
                code_lines = []
            else:
                # Start code block
                in_code_block = True
                code_lang = line[3:].strip()
                code_lines = []
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        # Close list if we have one and this line isn't a list item
        is_list_item = line.startswith("- ") or line.startswith("* ") or re.match(r"^\d+\. ", line)
        if in_list and not is_list_item and line.strip():
            html_parts.append("</ul>")
            in_list = False

        # Headers
        if line.startswith("### "):
            text_content = _inline_markdown(_escape_html(line[4:]))
            html_parts.append(
                f'<p style="font-size:15px;font-weight:bold;margin:12px 0 4px 0;">'
                f"{text_content}</p>"
            )
        elif line.startswith("## "):
            text_content = _inline_markdown(_escape_html(line[3:]))
            html_parts.append(
                f'<p style="font-size:17px;font-weight:bold;margin:14px 0 6px 0;">'
                f"{text_content}</p>"
            )
        elif line.startswith("# "):
            text_content = _inline_markdown(_escape_html(line[2:]))
            html_parts.append(
                f'<p style="font-size:19px;font-weight:bold;margin:16px 0 8px 0;">'
                f"{text_content}</p>"
            )
        # Horizontal rule
        elif line.strip() in ("---", "***", "___"):
            html_parts.append(
                '<hr style="border:none;border-top:1px solid #e0d8cf;margin:12px 0;">'
            )
        # Unordered list
        elif line.startswith("- ") or line.startswith("* "):
            if not in_list:
                html_parts.append('<ul style="margin:4px 0;padding-left:20px;">')
                in_list = True
            item = _inline_markdown(_escape_html(line[2:]))
            html_parts.append(f"<li>{item}</li>")
        # Ordered list
        elif re.match(r"^\d+\. ", line):
            if not in_list:
                html_parts.append('<ol style="margin:4px 0;padding-left:20px;">')
                in_list = True
            item_text = re.sub(r"^\d+\. ", "", line)
            item = _inline_markdown(_escape_html(item_text))
            html_parts.append(f"<li>{item}</li>")
        # Empty line
        elif line.strip() == "":
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            html_parts.append("<br>")
        # Regular paragraph
        else:
            text_content = _inline_markdown(_escape_html(line))
            html_parts.append(f"<p style='margin:2px 0;'>{text_content}</p>")

        i += 1

    # Close any open list
    if in_list:
        html_parts.append("</ul>")

    # Close any open code block
    if in_code_block and code_lines:
        code_content = _escape_html("\n".join(code_lines))
        code_content = code_content.replace("  ", "&nbsp;&nbsp;")
        html_parts.append(
            f'<pre style="background-color:{COLORS["code_bg"]};'
            f'color:{COLORS["code_text"]};'
            f'border-radius:8px;padding:12px;margin:8px 0;'
            f'font-family:\'Consolas\',\'Courier New\',monospace;'
            f'font-size:13px;">'
            f"<code>{code_content}</code></pre>"
        )

    return "".join(html_parts)


def _escape_html(text: str) -> str:
    """Escape HTML special characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _inline_markdown(text: str) -> str:
    """Convert inline markdown (bold, italic, inline code) to HTML."""
    # Inline code - must come before bold/italic
    text = re.sub(
        r"`([^`]+)`",
        lambda m: (
            f'<code style="background-color:{COLORS["code_bg"]};'
            f'color:{COLORS["code_text"]};'
            f'border-radius:4px;padding:1px 5px;'
            f'font-family:Consolas,monospace;font-size:93%;">'
            f"{m.group(1)}</code>"
        ),
        text,
    )
    # Bold italic
    text = re.sub(r"\*\*\*(.+?)\*\*\*", r"<b><i>\1</i></b>", text)
    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    # Italic
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    # Strikethrough
    text = re.sub(r"~~(.+?)~~", r"<s>\1</s>", text)
    return text


class MessageBubble(QWidget):
    """
    A chat message bubble widget.
    Displays a user or assistant message with appropriate styling.
    """

    copy_requested = pyqtSignal(str)

    def __init__(
        self,
        role: str,
        content: str,
        files: List[Dict[str, Any]] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.role = role
        self.content = content
        self.files = files or []

        self._build_ui()

    def _build_ui(self):
        outer = QHBoxLayout(self)
        outer.setContentsMargins(16, 4, 16, 4)
        outer.setSpacing(0)

        if self.role == "user":
            self._build_user_bubble(outer)
        else:
            self._build_assistant_bubble(outer)

    def _build_user_bubble(self, outer: QHBoxLayout):
        """Build right-aligned user bubble."""
        outer.addStretch(1)

        container = QVBoxLayout()
        container.setSpacing(4)
        container.setContentsMargins(0, 0, 0, 0)

        # File attachments shown above the message
        if self.files:
            for f in self.files:
                tag = self._make_file_tag(f)
                file_row = QHBoxLayout()
                file_row.addStretch()
                file_row.addWidget(tag)
                container.addLayout(file_row)

        # Bubble frame
        bubble = QFrame()
        bubble.setObjectName("user_bubble")
        bubble.setStyleSheet(
            f"QFrame#user_bubble {{"
            f"  background-color: {COLORS['user_bubble']};"
            f"  border-radius: 18px;"
            f"  border-bottom-right-radius: 4px;"
            f"}}"
        )

        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(14, 10, 14, 10)
        bubble_layout.setSpacing(0)

        label = QLabel()
        label.setTextFormat(Qt.PlainText)
        label.setText(self.content)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        label.setStyleSheet(
            f"color: {COLORS['user_bubble_text']}; font-size: 14px; line-height: 1.5;"
        )
        label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        bubble_layout.addWidget(label)

        bubble.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Minimum)
        bubble.setMaximumWidth(600)

        container.addWidget(bubble)
        outer.addLayout(container)

    def _build_assistant_bubble(self, outer: QHBoxLayout):
        """Build left-aligned assistant bubble."""
        # Avatar
        avatar = QLabel("✦")
        avatar.setFixedSize(32, 32)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet(
            f"background-color: {COLORS['accent']};"
            f"color: {COLORS['button_primary_text']};"
            f"border-radius: 16px;"
            f"font-size: 16px;"
            f"font-weight: bold;"
        )
        outer.addWidget(avatar, 0, Qt.AlignTop)
        outer.addSpacing(8)

        container = QVBoxLayout()
        container.setSpacing(4)
        container.setContentsMargins(0, 0, 0, 0)

        # Bubble frame
        bubble = QFrame()
        bubble.setObjectName("assistant_bubble")
        bubble.setStyleSheet(
            f"QFrame#assistant_bubble {{"
            f"  background-color: {COLORS['assistant_bubble']};"
            f"  border-radius: 18px;"
            f"  border-bottom-left-radius: 4px;"
            f"  border: 1px solid #e8e0d8;"
            f"}}"
        )

        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(14, 10, 14, 10)
        bubble_layout.setSpacing(0)

        self._content_label = QLabel()
        self._content_label.setTextFormat(Qt.RichText)
        self._content_label.setOpenExternalLinks(True)
        self._content_label.setWordWrap(True)
        self._content_label.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse
        )
        self._content_label.setStyleSheet(
            f"color: {COLORS['assistant_bubble_text']}; font-size: 14px; line-height: 1.5;"
        )
        self._content_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self._update_content()
        bubble_layout.addWidget(self._content_label)

        bubble.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        bubble.setMaximumWidth(700)

        container.addWidget(bubble)

        # Copy button below bubble
        btn_row = QHBoxLayout()
        copy_btn = QPushButton("⧉ Copy")
        copy_btn.setStyleSheet(
            "QPushButton {"
            "  background: transparent;"
            "  color: #9e9087;"
            "  border: none;"
            "  font-size: 12px;"
            "  padding: 2px 6px;"
            "  border-radius: 4px;"
            "}"
            "QPushButton:hover {"
            "  background-color: #ede8e3;"
            "  color: #5c4a3a;"
            "}"
        )
        copy_btn.setCursor(Qt.PointingHandCursor)
        copy_btn.clicked.connect(lambda: self.copy_requested.emit(self.content))
        btn_row.addWidget(copy_btn)
        btn_row.addStretch()
        container.addLayout(btn_row)

        outer.addLayout(container)
        outer.addStretch(1)

    def _update_content(self):
        """Update the content label with markdown-rendered HTML."""
        if self.content:
            html = simple_markdown_to_html(self.content)
            self._content_label.setText(html)
        else:
            self._content_label.setText(
                '<span style="color: #9e9087; font-style: italic;">▋</span>'
            )

    def update_content(self, new_content: str):
        """Update the message content (used for streaming)."""
        self.content = new_content
        if hasattr(self, "_content_label"):
            self._update_content()

    def _make_file_tag(self, file_info: Dict[str, Any]) -> QFrame:
        """Create a small file indicator tag widget."""
        tag = QFrame()
        tag.setStyleSheet(
            "QFrame {"
            f"  background-color: {COLORS['tag_bg']};"
            "  border-radius: 8px;"
            "  border: 1px solid #d8d0c8;"
            "}"
        )
        tag_layout = QHBoxLayout(tag)
        tag_layout.setContentsMargins(8, 4, 8, 4)
        tag_layout.setSpacing(4)

        # File icon
        icon = QLabel(file_info.get("preview", "📎"))
        icon.setStyleSheet(f"color: {COLORS['tag_text']}; font-size: 12px; border: none;")
        tag_layout.addWidget(icon)

        return tag
