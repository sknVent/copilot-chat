"""Claude-inspired QSS stylesheet definitions for the Copilot Chat application."""

# Color palette
COLORS = {
    "sidebar_bg": "#1e1e2e",
    "sidebar_hover": "#2a2a3e",
    "sidebar_selected": "#313145",
    "sidebar_text": "#cdd6f4",
    "sidebar_text_muted": "#7f849c",
    "accent": "#D97706",
    "accent_hover": "#B45309",
    "accent_light": "#FEF3C7",
    "chat_bg": "#FAF9F6",
    "user_bubble": "#D97706",
    "user_bubble_text": "#ffffff",
    "assistant_bubble": "#ffffff",
    "assistant_bubble_text": "#1a1a2e",
    "input_bg": "#ffffff",
    "input_border": "#e5e7eb",
    "input_border_focus": "#D97706",
    "border": "#e5e7eb",
    "text_primary": "#1a1a2e",
    "text_secondary": "#6b7280",
    "error": "#ef4444",
    "success": "#22c55e",
    "code_bg": "#f3f4f6",
    "shadow": "rgba(0, 0, 0, 0.1)",
}

MAIN_STYLESHEET = """
QMainWindow {
    background-color: #FAF9F6;
}

QWidget {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
    font-size: 14px;
}

/* Scrollbar styling */
QScrollBar:vertical {
    background: transparent;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: rgba(0, 0, 0, 0.2);
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(0, 0, 0, 0.3);
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: transparent;
}

QScrollBar:horizontal {
    background: transparent;
    height: 8px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background: rgba(0, 0, 0, 0.2);
    border-radius: 4px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background: rgba(0, 0, 0, 0.3);
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0px;
}
"""

SIDEBAR_STYLESHEET = """
QWidget#sidebar {
    background-color: #1e1e2e;
    border-right: 1px solid #2a2a3e;
}

QLabel#appTitle {
    color: #cdd6f4;
    font-size: 18px;
    font-weight: bold;
    padding: 8px 4px;
}

QLabel#appSubtitle {
    color: #7f849c;
    font-size: 11px;
    padding: 0px 4px;
}

QPushButton#newChatButton {
    background-color: #D97706;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 16px;
    font-size: 14px;
    font-weight: 600;
    text-align: left;
}

QPushButton#newChatButton:hover {
    background-color: #B45309;
}

QPushButton#newChatButton:pressed {
    background-color: #92400E;
}

QLabel#historyLabel {
    color: #7f849c;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
    padding: 4px;
}

QListWidget#conversationList {
    background-color: transparent;
    border: none;
    outline: none;
    padding: 4px 0px;
}

QListWidget#conversationList::item {
    color: #cdd6f4;
    padding: 10px 12px;
    border-radius: 6px;
    margin: 1px 4px;
}

QListWidget#conversationList::item:hover {
    background-color: #2a2a3e;
}

QListWidget#conversationList::item:selected {
    background-color: #313145;
    color: #cdd6f4;
}

QPushButton#settingsButton {
    background-color: transparent;
    color: #7f849c;
    border: 1px solid #2a2a3e;
    border-radius: 8px;
    padding: 10px 16px;
    font-size: 13px;
    text-align: left;
}

QPushButton#settingsButton:hover {
    background-color: #2a2a3e;
    color: #cdd6f4;
    border-color: #313145;
}
"""

CHAT_STYLESHEET = """
QWidget#chatContainer {
    background-color: #FAF9F6;
}

QScrollArea#chatScrollArea {
    background-color: #FAF9F6;
    border: none;
}

QWidget#messagesWidget {
    background-color: #FAF9F6;
}

QLabel#welcomeTitle {
    color: #1a1a2e;
    font-size: 28px;
    font-weight: bold;
}

QLabel#welcomeSubtitle {
    color: #6b7280;
    font-size: 16px;
}
"""

USER_BUBBLE_STYLESHEET = """
QWidget#userBubble {
    background-color: #D97706;
    border-radius: 18px;
    border-bottom-right-radius: 4px;
}

QLabel#userText {
    color: white;
    background-color: transparent;
    font-size: 14px;
    line-height: 1.5;
}
"""

ASSISTANT_BUBBLE_STYLESHEET = """
QWidget#assistantBubble {
    background-color: white;
    border-radius: 18px;
    border-bottom-left-radius: 4px;
    border: 1px solid #e5e7eb;
}

QTextBrowser#assistantText {
    color: #1a1a2e;
    background-color: transparent;
    border: none;
    font-size: 14px;
    line-height: 1.5;
}

QPushButton#copyButton {
    background-color: transparent;
    color: #9ca3af;
    border: 1px solid #e5e7eb;
    border-radius: 4px;
    padding: 3px 8px;
    font-size: 11px;
}

QPushButton#copyButton:hover {
    background-color: #f9fafb;
    color: #6b7280;
}
"""

INPUT_AREA_STYLESHEET = """
QWidget#inputContainer {
    background-color: #FAF9F6;
    border-top: 1px solid #e5e7eb;
}

QWidget#inputBox {
    background-color: white;
    border: 2px solid #e5e7eb;
    border-radius: 12px;
}

QWidget#inputBox:focus-within {
    border-color: #D97706;
}

QTextEdit#messageInput {
    background-color: transparent;
    border: none;
    outline: none;
    color: #1a1a2e;
    font-size: 14px;
    padding: 8px;
}

QPushButton#sendButton {
    background-color: #D97706;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 14px;
    font-weight: 600;
    min-width: 70px;
}

QPushButton#sendButton:hover {
    background-color: #B45309;
}

QPushButton#sendButton:pressed {
    background-color: #92400E;
}

QPushButton#sendButton:disabled {
    background-color: #d1d5db;
    color: #9ca3af;
}

QPushButton#attachButton {
    background-color: transparent;
    color: #9ca3af;
    border: none;
    border-radius: 6px;
    padding: 6px;
    font-size: 18px;
}

QPushButton#attachButton:hover {
    background-color: #f3f4f6;
    color: #6b7280;
}

QLabel#attachedFile {
    background-color: #FEF3C7;
    color: #92400E;
    border: 1px solid #FCD34D;
    border-radius: 6px;
    padding: 3px 8px;
    font-size: 12px;
}
"""

MODEL_SELECTOR_STYLESHEET = """
QWidget#modelSelectorContainer {
    background-color: #FAF9F6;
    border-bottom: 1px solid #e5e7eb;
}

QComboBox#modelSelector {
    background-color: white;
    color: #1a1a2e;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 13px;
    min-width: 200px;
}

QComboBox#modelSelector:hover {
    border-color: #D97706;
}

QComboBox#modelSelector::drop-down {
    border: none;
    padding-right: 8px;
}

QComboBox#modelSelector QAbstractItemView {
    background-color: white;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    selection-background-color: #FEF3C7;
    selection-color: #1a1a2e;
    padding: 4px;
}
"""

SETTINGS_DIALOG_STYLESHEET = """
QDialog {
    background-color: #FAF9F6;
}

QLabel#dialogTitle {
    color: #1a1a2e;
    font-size: 20px;
    font-weight: bold;
}

QLabel#fieldLabel {
    color: #374151;
    font-size: 13px;
    font-weight: 600;
}

QLabel#fieldHint {
    color: #6b7280;
    font-size: 12px;
}

QLineEdit#tokenInput {
    background-color: white;
    color: #1a1a2e;
    border: 2px solid #e5e7eb;
    border-radius: 8px;
    padding: 10px 12px;
    font-size: 14px;
}

QLineEdit#tokenInput:focus {
    border-color: #D97706;
}

QPushButton#saveButton {
    background-color: #D97706;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-size: 14px;
    font-weight: 600;
}

QPushButton#saveButton:hover {
    background-color: #B45309;
}

QPushButton#testButton {
    background-color: white;
    color: #374151;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    padding: 10px 24px;
    font-size: 14px;
}

QPushButton#testButton:hover {
    background-color: #f9fafb;
    border-color: #D97706;
    color: #D97706;
}

QPushButton#cancelButton {
    background-color: transparent;
    color: #6b7280;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 10px 24px;
    font-size: 14px;
}

QPushButton#cancelButton:hover {
    background-color: #f9fafb;
}

QLabel#statusLabel {
    font-size: 13px;
    padding: 6px 12px;
    border-radius: 6px;
}

QLabel#statusLabel[status="success"] {
    background-color: #dcfce7;
    color: #166534;
}

QLabel#statusLabel[status="error"] {
    background-color: #fee2e2;
    color: #991b1b;
}

QLabel#statusLabel[status="testing"] {
    background-color: #dbeafe;
    color: #1e40af;
}
"""
