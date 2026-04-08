# 🤖 Copilot Chat

A desktop chat application built with **PyQt5** that mimics the Claude AI interface and connects to the **GitHub Copilot API** using a Copilot Classic token. Supports OpenAI models exclusively, with file upload capabilities for images, Excel spreadsheets, Python files, and text files.

---

## ✨ Features

- **Claude-inspired UI** — Warm cream chat area, dark sidebar, rounded message bubbles, modern fonts
- **GitHub Copilot Classic Token** — Secure token storage with QSettings, persists between sessions
- **OpenAI Models Only** — Dropdown restricted to GPT-4o, GPT-4o-mini, GPT-4-turbo, GPT-4, GPT-3.5-turbo, o1-preview, o1-mini, o3-mini
- **Streaming Responses** — Real-time token-by-token output via SSE
- **File Uploads** — Attach images (with preview), Excel files (parsed to text), `.py` and `.txt` files
- **Conversation History** — Sidebar with past chats, click to restore any conversation
- **Markdown Rendering** — Bold, italic, headers, bullet lists, code blocks with syntax highlighting
- **Copy Messages** — One-click copy button on every assistant response
- **Keyboard Shortcuts** — Enter to send, Shift+Enter for new line
- **Error Handling** — User-friendly messages for API errors, auth failures, and rate limits

---

## 📸 Screenshots

> _Add screenshots here after running the application._

---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/sknVent/copilot-chat.git
cd copilot-chat

# 2. Create and activate a virtual environment
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python main.py
```

---

## 🔑 Getting a GitHub Copilot Classic Token

1. Go to [github.com](https://github.com) and sign in
2. Click your profile picture → **Settings**
3. Scroll down to **Developer settings** → **Personal access tokens** → **Tokens (classic)**
4. Click **Generate new token (classic)**
5. Give it a name (e.g., `copilot-chat-app`)
6. Select the **`copilot`** scope
7. Click **Generate token** and copy the token (starts with `ghp_`)
8. In the app, click **⚙️ Settings** in the sidebar and paste your token

> **Note:** You must have an active GitHub Copilot subscription for the token to work.

---

## 📖 Usage

1. **Launch the app**: `python main.py`
2. **Enter your token**: Click **⚙️ Settings** and paste your Copilot Classic token, then click **Save**
3. **Select a model**: Use the dropdown at the top of the chat area
4. **Start chatting**: Type in the input box and press **Enter** to send
5. **Attach files**: Click the **📎** button to attach images, Excel files, Python files, or text files
6. **New chat**: Click **✏️ New Chat** in the sidebar to start a fresh conversation
7. **Switch conversations**: Click any past chat in the sidebar to restore it

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Enter` | Send message |
| `Shift+Enter` | Insert new line |

---

## 📎 Supported File Types

| Type | Extensions | How it's sent |
|---|---|---|
| **Images** | `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.webp` | Base64-encoded for vision API |
| **Excel** | `.xlsx`, `.xls` | Parsed to text/table representation |
| **Python** | `.py` | Included as a formatted code block |
| **Text** | `.txt` | Included as plain text |

---

## 🤖 Available Models

| Model | Description |
|---|---|
| `gpt-4o` | Most capable multimodal model (default) |
| `gpt-4o-mini` | Fast and cost-efficient |
| `gpt-4-turbo` | GPT-4 Turbo with vision |
| `gpt-4` | GPT-4 standard |
| `gpt-3.5-turbo` | Fast and lightweight |
| `o1-preview` | Advanced reasoning model |
| `o1-mini` | Fast reasoning model |
| `o3-mini` | Latest compact reasoning model |

---

## 📁 Project Structure

```
copilot-chat/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── main.py                   # Application entry point
├── .gitignore                # Python gitignore
└── app/
    ├── __init__.py           # Package init
    ├── main_window.py        # Main window with sidebar + chat area
    ├── chat_widget.py        # Scrollable chat message area
    ├── message_bubble.py     # User/assistant message bubble widgets
    ├── sidebar.py            # Dark sidebar with conversation history
    ├── input_area.py         # Text input with send/attach buttons
    ├── settings_dialog.py    # Token configuration dialog
    ├── model_selector.py     # OpenAI model dropdown
    ├── file_handler.py       # File reading and processing
    ├── api_client.py         # Copilot API client with streaming
    ├── conversation.py       # Conversation data model and storage
    └── styles.py             # Claude-inspired QSS stylesheets
```

---

## 📦 Dependencies

```
PyQt5>=5.15.0       # Desktop GUI framework
requests>=2.28.0    # HTTP client for API calls
openpyxl>=3.1.0     # Excel file reading
pandas>=2.0.0       # Excel fallback parser
Pillow>=10.0.0      # Image processing
markdown>=3.4.0     # Markdown rendering
Pygments>=2.15.0    # Syntax highlighting in code blocks
```

---

## 📄 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2024 Copilot Chat Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
