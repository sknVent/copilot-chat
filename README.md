# Copilot Chat

A beautiful PyQt5 desktop chat application with a **Claude-inspired UI**, powered by the **GitHub Copilot API** using **OpenAI models** exclusively. Supports file uploads (images, Excel, Python, and text files) with real-time streaming responses.

---

## Features

- **Claude-inspired UI** — Warm cream/beige chat area, dark sidebar, rounded message bubbles
- **GitHub Copilot Classic Token** — Secure settings dialog with persistent storage and connection testing
- **OpenAI Models Only** — GPT-4o, GPT-4o-mini, GPT-4-turbo, GPT-4, GPT-3.5-turbo, o1-preview, o1-mini, o3-mini
- **File Uploads** — Images (base64 vision), Excel (parsed to markdown table), Python (.py), Text (.txt, .md, .json, etc.)
- **Streaming Responses** — Real-time token-by-token display
- **Conversation History** — Sidebar with past chats, new chat, delete conversations
- **Markdown Rendering** — Bold, italic, inline code, code blocks, lists, headers
- **Copy Messages** — One-click copy of assistant responses
- **Threaded API Calls** — UI stays responsive using QThread

---

## Project Structure

```
copilot-chat/
├── README.md
├── requirements.txt
├── main.py
├── .gitignore
└── app/
    ├── __init__.py
    ├── main_window.py        # Main window (sidebar + chat)
    ├── chat_widget.py        # Scrollable message display area
    ├── message_bubble.py     # Chat bubble widgets + markdown rendering
    ├── sidebar.py            # Dark sidebar with conversation list
    ├── input_area.py         # Multi-line input + send/attach buttons
    ├── settings_dialog.py    # Token configuration dialog
    ├── model_selector.py     # OpenAI model dropdown
    ├── file_handler.py       # File processing (image, Excel, Python, text)
    ├── api_client.py         # Copilot API streaming client (QThread)
    ├── conversation.py       # Conversation data model and local storage
    └── styles.py             # QSS stylesheet definitions
```

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip

### Steps

1. **Clone the repository:**

   ```bash
   git clone https://github.com/sknVent/copilot-chat.git
   cd copilot-chat
   ```

2. **Create a virtual environment (recommended):**

   ```bash
   python -m venv venv

   # On Windows:
   venv\Scripts\activate

   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**

   ```bash
   python main.py
   ```

---

## Getting Your GitHub Copilot Classic Token

1. Go to [github.com](https://github.com) and sign in
2. Click your avatar → **Settings** → **Developer settings**
3. Select **Personal access tokens** → **Tokens (classic)**
4. Click **Generate new token (classic)**
5. Give it a name (e.g., "Copilot Chat App")
6. Select the `copilot` scope
7. Click **Generate token** and copy the token (starts with `ghu_`)

> **Note:** You need an active GitHub Copilot subscription for the token to work.

---

## Usage

### First Run

When you first launch the app, a welcome dialog will appear asking you to configure your Copilot token. Click **Open Settings** and enter your token.

### Configuring the Token

1. Click **Settings** at the bottom of the sidebar
2. Enter your Copilot Classic token in the password field
3. Click **Test Connection** to verify it works
4. Click **Save Settings**

### Sending Messages

- Type your message in the input box at the bottom
- Press **Enter** to send, or **Shift+Enter** for a new line
- Click the **↑** button to send

### Attaching Files

1. Click the **paperclip** (📎) button next to the input field
2. Select a supported file:
   - **Images**: `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.webp` — sent as base64 for vision models
   - **Excel**: `.xlsx`, `.xls` — parsed and included as a markdown table
   - **Python**: `.py` — included as a code block
   - **Text**: `.txt`, `.md`, `.json`, `.xml`, etc. — included as text content
3. Multiple files can be attached to a single message
4. Remove attachments by clicking the **✕** on the file tag

### Switching Models

Use the **Model** dropdown in the top right to switch between:

| Model | Description |
|-------|-------------|
| `gpt-4o` | Latest, most capable (default) |
| `gpt-4o-mini` | Faster, cheaper GPT-4o |
| `gpt-4-turbo` | GPT-4 Turbo with 128k context |
| `gpt-4` | Original GPT-4 |
| `gpt-3.5-turbo` | Fast and economical |
| `o1-preview` | Advanced reasoning |
| `o1-mini` | Smaller reasoning model |
| `o3-mini` | Latest mini reasoning model |

### Conversation Management

- Click **+ New Chat** to start a fresh conversation
- Click any conversation in the sidebar to switch to it
- Right-click a conversation and select **Delete** to remove it

### Copying Responses

Click the **⧉ Copy** button below any assistant message to copy it to your clipboard.

---

## Configuration Storage

The app stores configuration in your home directory:

- **Settings** (token, default model): `~/.copilot_chat/settings.json`
- **Conversations**: `~/.copilot_chat/conversations.json`

> These files are excluded from git via `.gitignore` to keep your token safe.

---

## API Details

The app uses the GitHub Copilot API endpoint:

```
POST https://api.githubcopilot.com/chat/completions
```

With headers:
```
Authorization: Bearer <token>
Content-Type: application/json
Editor-Version: vscode/1.85.0
Editor-Plugin-Version: copilot-chat/0.12.0
Openai-Intent: conversation-panel
```

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| PyQt5 | >=5.15.0 | GUI framework |
| requests | >=2.28.0 | HTTP client for API calls |
| openpyxl | >=3.1.0 | Excel file reading |
| pandas | >=2.0.0 | Data manipulation (optional Excel support) |
| Pillow | >=10.0.0 | Image thumbnail generation |
| markdown | >=3.4.0 | Markdown parsing |
| Pygments | >=2.15.0 | Syntax highlighting |

---

## Troubleshooting

**"Authentication failed" error:**
- Verify your token starts with `ghu_`
- Ensure you have an active GitHub Copilot subscription
- Check that the token has the `copilot` scope

**App won't start:**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that Python 3.8+ is installed: `python --version`

**Excel files not loading:**
- Ensure `openpyxl` is installed: `pip install openpyxl`

**Images not sending:**
- Only vision-capable models (like `gpt-4o`) support image attachments
- Ensure the image file is not corrupted

---

## License

MIT License — see [LICENSE](LICENSE) for details.
