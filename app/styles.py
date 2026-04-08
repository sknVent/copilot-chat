"""
QSS Stylesheet definitions for the Claude-inspired theme.
"""

# Color palette
COLORS = {
    "sidebar_bg": "#1e1e2e",
    "sidebar_hover": "#2a2a3e",
    "sidebar_active": "#313148",
    "sidebar_text": "#cdd6f4",
    "sidebar_text_dim": "#6c7086",
    "accent": "#cba6f7",
    "accent_hover": "#d4b3ff",
    "chat_bg": "#faf8f5",
    "chat_bg_alt": "#f5f0eb",
    "user_bubble": "#e8a87c",
    "user_bubble_text": "#2d1b00",
    "assistant_bubble": "#ffffff",
    "assistant_bubble_text": "#1a1a2e",
    "input_bg": "#ffffff",
    "input_border": "#e0d8cf",
    "input_border_focus": "#cba6f7",
    "button_primary": "#cba6f7",
    "button_primary_hover": "#d4b3ff",
    "button_primary_text": "#1e1e2e",
    "send_button": "#cba6f7",
    "send_button_hover": "#d4b3ff",
    "separator": "#e8e0d8",
    "code_bg": "#282c34",
    "code_text": "#abb2bf",
    "tag_bg": "#e8e0d8",
    "tag_text": "#5c4a3a",
    "error_bg": "#fee2e2",
    "error_text": "#991b1b",
    "warning_bg": "#fef3c7",
    "warning_text": "#92400e",
    "success_bg": "#d1fae5",
    "success_text": "#065f46",
}

MAIN_STYLE = f"""
QMainWindow {{
    background-color: {COLORS["chat_bg"]};
}}

QWidget {{
    font-family: "Segoe UI", "SF Pro Display", -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 14px;
}}

QScrollBar:vertical {{
    border: none;
    background: transparent;
    width: 8px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: #c0b8b0;
    border-radius: 4px;
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background: #a09890;
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0;
    background: none;
}}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {{
    background: none;
}}

QScrollBar:horizontal {{
    border: none;
    background: transparent;
    height: 8px;
    margin: 0;
}}

QScrollBar::handle:horizontal {{
    background: #c0b8b0;
    border-radius: 4px;
    min-width: 20px;
}}

QScrollBar::handle:horizontal:hover {{
    background: #a09890;
}}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {{
    width: 0;
    background: none;
}}

QToolTip {{
    background-color: {COLORS["sidebar_bg"]};
    color: {COLORS["sidebar_text"]};
    border: 1px solid {COLORS["sidebar_hover"]};
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
}}
"""

SIDEBAR_STYLE = f"""
QWidget#sidebar {{
    background-color: {COLORS["sidebar_bg"]};
    border-right: 1px solid #2a2a40;
}}

QLabel#app_title {{
    color: {COLORS["sidebar_text"]};
    font-size: 18px;
    font-weight: bold;
    padding: 8px 4px;
}}

QLabel#app_subtitle {{
    color: {COLORS["sidebar_text_dim"]};
    font-size: 11px;
    padding: 0 4px 8px 4px;
}}

QPushButton#new_chat_btn {{
    background-color: {COLORS["accent"]};
    color: {COLORS["button_primary_text"]};
    border: none;
    border-radius: 8px;
    padding: 10px 16px;
    font-size: 13px;
    font-weight: 600;
    text-align: left;
}}

QPushButton#new_chat_btn:hover {{
    background-color: {COLORS["accent_hover"]};
}}

QPushButton#new_chat_btn:pressed {{
    background-color: #b894e0;
}}

QLabel#section_label {{
    color: {COLORS["sidebar_text_dim"]};
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 8px 8px 4px 8px;
}}

QListWidget#conversation_list {{
    background-color: transparent;
    border: none;
    padding: 0;
    outline: none;
}}

QListWidget#conversation_list::item {{
    color: {COLORS["sidebar_text"]};
    padding: 8px 12px;
    border-radius: 6px;
    margin: 1px 4px;
    font-size: 13px;
}}

QListWidget#conversation_list::item:hover {{
    background-color: {COLORS["sidebar_hover"]};
}}

QListWidget#conversation_list::item:selected {{
    background-color: {COLORS["sidebar_active"]};
    color: {COLORS["sidebar_text"]};
}}

QPushButton#settings_btn {{
    background-color: transparent;
    color: {COLORS["sidebar_text_dim"]};
    border: 1px solid #3a3a50;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    text-align: left;
}}

QPushButton#settings_btn:hover {{
    background-color: {COLORS["sidebar_hover"]};
    color: {COLORS["sidebar_text"]};
}}
"""

CHAT_AREA_STYLE = f"""
QWidget#chat_area {{
    background-color: {COLORS["chat_bg"]};
}}

QScrollArea#message_scroll {{
    background-color: {COLORS["chat_bg"]};
    border: none;
}}

QWidget#messages_container {{
    background-color: {COLORS["chat_bg"]};
}}
"""

USER_BUBBLE_STYLE = f"""
QFrame#user_bubble {{
    background-color: {COLORS["user_bubble"]};
    border-radius: 18px;
    border-bottom-right-radius: 4px;
}}

QLabel#user_bubble_text {{
    color: {COLORS["user_bubble_text"]};
    background: transparent;
    padding: 2px;
    font-size: 14px;
    line-height: 1.5;
}}
"""

ASSISTANT_BUBBLE_STYLE = f"""
QFrame#assistant_bubble {{
    background-color: {COLORS["assistant_bubble"]};
    border-radius: 18px;
    border-bottom-left-radius: 4px;
    border: 1px solid #e8e0d8;
}}

QLabel#assistant_bubble_text {{
    color: {COLORS["assistant_bubble_text"]};
    background: transparent;
    padding: 2px;
    font-size: 14px;
    line-height: 1.5;
}}
"""

INPUT_AREA_STYLE = f"""
QWidget#input_area {{
    background-color: {COLORS["chat_bg"]};
    border-top: 1px solid {COLORS["separator"]};
}}

QFrame#input_frame {{
    background-color: {COLORS["input_bg"]};
    border: 2px solid {COLORS["input_border"]};
    border-radius: 12px;
}}

QFrame#input_frame:focus-within {{
    border: 2px solid {COLORS["input_border_focus"]};
}}

QTextEdit#message_input {{
    background-color: transparent;
    border: none;
    color: #2d2520;
    font-size: 14px;
    padding: 4px 8px;
    line-height: 1.5;
}}

QTextEdit#message_input::placeholder {{
    color: #9e9087;
}}

QPushButton#send_btn {{
    background-color: {COLORS["send_button"]};
    color: {COLORS["button_primary_text"]};
    border: none;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 16px;
    font-weight: bold;
    min-width: 40px;
    min-height: 36px;
}}

QPushButton#send_btn:hover {{
    background-color: {COLORS["send_button_hover"]};
}}

QPushButton#send_btn:pressed {{
    background-color: #b894e0;
}}

QPushButton#send_btn:disabled {{
    background-color: #d8d0c8;
    color: #9e9087;
}}

QPushButton#attach_btn {{
    background-color: transparent;
    color: #9e9087;
    border: none;
    border-radius: 6px;
    padding: 6px;
    font-size: 16px;
    min-width: 32px;
    min-height: 32px;
}}

QPushButton#attach_btn:hover {{
    background-color: {COLORS["tag_bg"]};
    color: #5c4a3a;
}}
"""

MODEL_SELECTOR_STYLE = f"""
QComboBox#model_selector {{
    background-color: {COLORS["assistant_bubble"]};
    color: {COLORS["assistant_bubble_text"]};
    border: 1px solid {COLORS["input_border"]};
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 13px;
    min-width: 160px;
}}

QComboBox#model_selector:hover {{
    border-color: {COLORS["input_border_focus"]};
}}

QComboBox#model_selector::drop-down {{
    border: none;
    width: 24px;
}}

QComboBox#model_selector::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #9e9087;
    margin-right: 8px;
}}

QComboBox#model_selector QAbstractItemView {{
    background-color: {COLORS["assistant_bubble"]};
    border: 1px solid {COLORS["input_border"]};
    border-radius: 8px;
    color: {COLORS["assistant_bubble_text"]};
    selection-background-color: {COLORS["tag_bg"]};
    selection-color: {COLORS["assistant_bubble_text"]};
    padding: 4px;
    outline: none;
}}
"""

SETTINGS_DIALOG_STYLE = f"""
QDialog {{
    background-color: {COLORS["chat_bg"]};
}}

QLabel#dialog_title {{
    font-size: 20px;
    font-weight: bold;
    color: #2d2520;
}}

QLabel#section_header {{
    font-size: 13px;
    font-weight: 600;
    color: #5c4a3a;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

QLabel {{
    color: #2d2520;
    font-size: 13px;
}}

QLineEdit {{
    background-color: {COLORS["input_bg"]};
    border: 2px solid {COLORS["input_border"]};
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 14px;
    color: #2d2520;
}}

QLineEdit:focus {{
    border-color: {COLORS["input_border_focus"]};
}}

QPushButton#primary_btn {{
    background-color: {COLORS["accent"]};
    color: {COLORS["button_primary_text"]};
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: 600;
}}

QPushButton#primary_btn:hover {{
    background-color: {COLORS["accent_hover"]};
}}

QPushButton#secondary_btn {{
    background-color: transparent;
    color: #5c4a3a;
    border: 1px solid {COLORS["input_border"]};
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 14px;
}}

QPushButton#secondary_btn:hover {{
    background-color: {COLORS["tag_bg"]};
}}

QPushButton#test_btn {{
    background-color: #e0f0e8;
    color: #2d6a4f;
    border: 1px solid #a8d5b5;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 600;
}}

QPushButton#test_btn:hover {{
    background-color: #c8e8d4;
}}

QLabel#status_ok {{
    color: {COLORS["success_text"]};
    background-color: {COLORS["success_bg"]};
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 13px;
}}

QLabel#status_error {{
    color: {COLORS["error_text"]};
    background-color: {COLORS["error_bg"]};
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 13px;
}}

QLabel#status_info {{
    color: {COLORS["warning_text"]};
    background-color: {COLORS["warning_bg"]};
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 13px;
}}
"""

HEADER_STYLE = f"""
QWidget#chat_header {{
    background-color: {COLORS["chat_bg"]};
    border-bottom: 1px solid {COLORS["separator"]};
}}

QLabel#chat_title {{
    font-size: 15px;
    font-weight: 600;
    color: #2d2520;
}}
"""

FILE_TAG_STYLE = f"""
QFrame#file_tag {{
    background-color: {COLORS["tag_bg"]};
    border-radius: 8px;
    border: 1px solid #d8d0c8;
}}

QLabel#file_tag_text {{
    color: {COLORS["tag_text"]};
    font-size: 12px;
    background: transparent;
}}

QPushButton#file_tag_remove {{
    background: transparent;
    color: #9e9087;
    border: none;
    font-size: 14px;
    font-weight: bold;
    padding: 0;
    min-width: 16px;
    max-width: 16px;
    min-height: 16px;
    max-height: 16px;
}}

QPushButton#file_tag_remove:hover {{
    color: #5c4a3a;
}}
"""
