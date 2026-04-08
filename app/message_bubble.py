"""Individual message bubble widget."""

import re
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QTextBrowser,
    QPushButton, QSizePolicy, QApplication,
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QImage

try:
    import markdown
    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False

try:
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name, guess_lexer, TextLexer
    from pygments.formatters import HtmlFormatter
    HAS_PYGMENTS = True
except ImportError:
    HAS_PYGMENTS = False

from app.styles import USER_BUBBLE_STYLESHEET, ASSISTANT_BUBBLE_STYLESHEET


def _apply_syntax_highlighting(code: str, lang: str = "") -> str:
    """Apply Pygments syntax highlighting to a code block."""
    if not HAS_PYGMENTS:
        return f"<pre><code>{code}</code></pre>"
    try:
        if lang:
            lexer = get_lexer_by_name(lang, stripall=True)
        else:
            lexer = guess_lexer(code)
    except Exception:
        lexer = TextLexer()
    formatter = HtmlFormatter(
        style="friendly",
        cssclass="highlight",
        noclasses=True,
        prestyles=(
            "background: #f8f8f8; border: 1px solid #e5e7eb; border-radius: 6px; "
            "padding: 12px; overflow-x: auto; font-size: 13px; font-family: monospace;"
        ),
    )
    return highlight(code, lexer, formatter)


def _render_markdown(text: str) -> str:
    """Convert markdown text to HTML with syntax highlighting for code blocks."""
    if not HAS_MARKDOWN:
        # Basic escaping and newline-to-br conversion
        escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return f"<p>{escaped.replace(chr(10), '<br>')}</p>"

    # Pre-process code blocks for syntax highlighting before markdown rendering
    code_blocks = {}
    block_counter = [0]

    def replace_code_block(match):
        lang = match.group(1).strip() if match.group(1) else ""
        code = match.group(2)
        placeholder = f"CODEBLOCK{block_counter[0]}PLACEHOLDER"
        code_blocks[placeholder] = _apply_syntax_highlighting(code, lang)
        block_counter[0] += 1
        return placeholder

    processed = re.sub(r"```(\w*)\n?(.*?)```", replace_code_block, text, flags=re.DOTALL)

    # Convert markdown to HTML
    md = markdown.Markdown(extensions=["fenced_code", "tables", "nl2br"])
    html = md.convert(processed)

    # Re-inject highlighted code blocks
    for placeholder, highlighted in code_blocks.items():
        html = html.replace(f"<p>{placeholder}</p>", highlighted)
        html = html.replace(placeholder, highlighted)

    return html


class UserMessageBubble(QWidget):
    """A right-aligned user message bubble."""

    def __init__(self, text: str, files: list = None, parent=None):
        super().__init__(parent)
        self.setStyleSheet(USER_BUBBLE_STYLESHEET)
        self._build_ui(text, files or [])

    def _build_ui(self, text: str, files: list):
        outer = QHBoxLayout(self)
        outer.setContentsMargins(80, 8, 16, 8)
        outer.setSpacing(0)
        outer.addStretch()

        bubble = QWidget()
        bubble.setObjectName("userBubble")

        inner = QVBoxLayout(bubble)
        inner.setContentsMargins(16, 12, 16, 12)
        inner.setSpacing(6)

        # Show file indicators above text
        for file_info in files:
            file_label = QLabel(file_info.get("display", ""))
            file_label.setStyleSheet(
                "background-color: rgba(255,255,255,0.2); color: white; "
                "border-radius: 4px; padding: 2px 6px; font-size: 12px;"
            )
            inner.addWidget(file_label)

            # Show image thumbnail if it's an image
            if file_info.get("type") == "image" and file_info.get("content"):
                try:
                    import base64
                    img_data = base64.b64decode(file_info["content"])
                    qimage = QImage.fromData(img_data)
                    if not qimage.isNull():
                        pixmap = QPixmap.fromImage(qimage).scaled(
                            200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation
                        )
                        img_label = QLabel()
                        img_label.setPixmap(pixmap)
                        img_label.setStyleSheet("background: transparent;")
                        inner.addWidget(img_label)
                except Exception:
                    pass

        if text.strip():
            label = QLabel(text)
            label.setObjectName("userText")
            label.setWordWrap(True)
            label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            inner.addWidget(label)

        outer.addWidget(bubble)


class AssistantMessageBubble(QWidget):
    """A left-aligned assistant message bubble with markdown rendering."""

    copy_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(ASSISTANT_BUBBLE_STYLESHEET)
        self._full_text = ""
        self._build_ui()

    def _build_ui(self):
        outer = QHBoxLayout(self)
        outer.setContentsMargins(16, 8, 80, 8)
        outer.setSpacing(0)

        self.bubble = QWidget()
        self.bubble.setObjectName("assistantBubble")

        inner = QVBoxLayout(self.bubble)
        inner.setContentsMargins(16, 12, 16, 12)
        inner.setSpacing(8)

        self.text_browser = QTextBrowser()
        self.text_browser.setObjectName("assistantText")
        self.text_browser.setOpenExternalLinks(True)
        self.text_browser.setReadOnly(True)
        self.text_browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.text_browser.document().setDefaultStyleSheet(
            "body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; "
            "font-size: 14px; color: #1a1a2e; line-height: 1.6; }"
            "code { background: #f3f4f6; padding: 2px 4px; border-radius: 3px; "
            "font-family: 'Courier New', monospace; font-size: 13px; }"
            "pre { background: #f8f8f8; border: 1px solid #e5e7eb; border-radius: 6px; "
            "padding: 12px; overflow-x: auto; }"
            "blockquote { border-left: 3px solid #D97706; padding-left: 12px; "
            "color: #6b7280; margin: 8px 0; }"
            "table { border-collapse: collapse; width: 100%; }"
            "th, td { border: 1px solid #e5e7eb; padding: 6px 10px; text-align: left; }"
            "th { background: #f9fafb; font-weight: 600; }"
        )
        # Start with placeholder
        self.text_browser.setPlainText("")
        inner.addWidget(self.text_browser)

        # Copy button
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 0, 0, 0)
        btn_row.addStretch()
        self.copy_btn = QPushButton("📋 Copy")
        self.copy_btn.setObjectName("copyButton")
        self.copy_btn.clicked.connect(self._copy_text)
        btn_row.addWidget(self.copy_btn)
        inner.addLayout(btn_row)

        outer.addWidget(self.bubble)
        outer.addStretch()

    def _copy_text(self):
        QApplication.clipboard().setText(self._full_text)
        self.copy_btn.setText("✅ Copied!")
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(2000, lambda: self.copy_btn.setText("📋 Copy"))

    def append_text(self, chunk: str):
        """Append a streaming chunk to the message."""
        self._full_text += chunk
        self._render()

    def set_text(self, text: str):
        """Set the full text of the message."""
        self._full_text = text
        self._render()

    def _render(self):
        """Render the current text as HTML with markdown."""
        html = _render_markdown(self._full_text)
        self.text_browser.setHtml(html)
        # Adjust height to content
        doc_height = int(self.text_browser.document().size().height())
        self.text_browser.setFixedHeight(max(doc_height + 16, 40))

    def get_text(self) -> str:
        return self._full_text


class ErrorMessageBubble(QWidget):
    """A centered error message bubble."""

    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)

        label = QLabel(f"⚠️  {text}")
        label.setWordWrap(True)
        label.setStyleSheet(
            "background-color: #fee2e2; color: #991b1b; border: 1px solid #fecaca; "
            "border-radius: 8px; padding: 10px 16px; font-size: 13px;"
        )
        layout.addWidget(label)
