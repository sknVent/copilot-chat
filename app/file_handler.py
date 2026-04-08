"""File reading and processing logic for the Copilot Chat application."""

import base64
import os
from typing import Dict, Any


SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}
SUPPORTED_EXCEL_EXTENSIONS = {".xlsx", ".xls"}
SUPPORTED_TEXT_EXTENSIONS = {".txt"}
SUPPORTED_CODE_EXTENSIONS = {".py"}

ALL_SUPPORTED_EXTENSIONS = (
    SUPPORTED_IMAGE_EXTENSIONS
    | SUPPORTED_EXCEL_EXTENSIONS
    | SUPPORTED_TEXT_EXTENSIONS
    | SUPPORTED_CODE_EXTENSIONS
)

FILE_FILTER = (
    "Supported Files (*.png *.jpg *.jpeg *.gif *.bmp *.webp *.xlsx *.xls *.py *.txt);;"
    "Images (*.png *.jpg *.jpeg *.gif *.bmp *.webp);;"
    "Excel Files (*.xlsx *.xls);;"
    "Python Files (*.py);;"
    "Text Files (*.txt);;"
    "All Files (*)"
)


class FileProcessingError(Exception):
    """Raised when a file cannot be processed."""
    pass


def process_file(file_path: str) -> Dict[str, Any]:
    """
    Process a file and return its content in the appropriate format.

    Returns a dict with keys:
        - type: 'image', 'excel', 'python', or 'text'
        - name: filename
        - content: processed content (varies by type)
        - display: human-readable display text for the UI
    """
    if not os.path.exists(file_path):
        raise FileProcessingError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    name = os.path.basename(file_path)

    if ext in SUPPORTED_IMAGE_EXTENSIONS:
        return _process_image(file_path, name, ext)
    elif ext in SUPPORTED_EXCEL_EXTENSIONS:
        return _process_excel(file_path, name)
    elif ext in SUPPORTED_CODE_EXTENSIONS:
        return _process_python(file_path, name)
    elif ext in SUPPORTED_TEXT_EXTENSIONS:
        return _process_text(file_path, name)
    else:
        raise FileProcessingError(f"Unsupported file type: {ext}")


def _process_image(file_path: str, name: str, ext: str) -> Dict[str, Any]:
    """Process an image file into base64 for vision API."""
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode("utf-8")

        mime_map = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".bmp": "image/bmp",
            ".webp": "image/webp",
        }
        mime_type = mime_map.get(ext, "image/png")

        return {
            "type": "image",
            "name": name,
            "path": file_path,
            "mime_type": mime_type,
            "content": b64,
            "display": f"[Image: {name}]",
        }
    except OSError as e:
        raise FileProcessingError(f"Could not read image file: {e}") from e


def _process_excel(file_path: str, name: str) -> Dict[str, Any]:
    """Process an Excel file into a text/table representation."""
    try:
        import openpyxl
        wb = openpyxl.load_workbook(file_path, data_only=True)
        parts = []

        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            rows = list(ws.iter_rows(values_only=True))
            if not rows:
                continue

            parts.append(f"## Sheet: {sheet_name}\n")

            col_widths = []
            for row in rows:
                for i, cell in enumerate(row):
                    val = str(cell) if cell is not None else ""
                    while len(col_widths) <= i:
                        col_widths.append(0)
                    col_widths[i] = max(col_widths[i], len(val))

            for row_idx, row in enumerate(rows):
                cells = [
                    str(cell if cell is not None else "").ljust(col_widths[i] if i < len(col_widths) else 0)
                    for i, cell in enumerate(row)
                ]
                row_str = " | ".join(cells)
                parts.append(row_str)
                if row_idx == 0:
                    parts.append("-" * len(row_str))

        text_content = f"Excel file: {name}\n\n" + "\n".join(parts)

        return {
            "type": "excel",
            "name": name,
            "content": text_content,
            "display": f"[Excel: {name}]",
        }
    except ImportError:
        return _process_excel_pandas(file_path, name)
    except Exception as e:
        raise FileProcessingError(f"Could not read Excel file: {e}") from e


def _process_excel_pandas(file_path: str, name: str) -> Dict[str, Any]:
    """Fallback: process Excel using pandas."""
    try:
        import pandas as pd
        sheets = pd.read_excel(file_path, sheet_name=None)
        parts = []
        for sheet_name, df in sheets.items():
            parts.append(f"## Sheet: {sheet_name}\n")
            parts.append(df.to_string(index=False))
            parts.append("")
        text_content = f"Excel file: {name}\n\n" + "\n".join(parts)
        return {
            "type": "excel",
            "name": name,
            "content": text_content,
            "display": f"[Excel: {name}]",
        }
    except Exception as e:
        raise FileProcessingError(f"Could not read Excel file: {e}") from e


def _process_python(file_path: str, name: str) -> Dict[str, Any]:
    """Process a Python file as a code block."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            code = f.read()
        text_content = f"Python file: {name}\n\n```python\n{code}\n```"
        return {
            "type": "python",
            "name": name,
            "content": text_content,
            "display": f"[Python: {name}]",
        }
    except OSError as e:
        raise FileProcessingError(f"Could not read Python file: {e}") from e


def _process_text(file_path: str, name: str) -> Dict[str, Any]:
    """Process a plain text file."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
        text_content = f"Text file: {name}\n\n{text}"
        return {
            "type": "text",
            "name": name,
            "content": text_content,
            "display": f"[Text: {name}]",
        }
    except OSError as e:
        raise FileProcessingError(f"Could not read text file: {e}") from e


def build_api_content(text: str, files: list) -> object:
    """
    Build the content field for an API message, combining text and file attachments.
    Returns a string for text-only, or a list for multimodal content.
    """
    if not files:
        return text

    content_parts = []

    # Add image parts first (as vision content)
    image_files = [f for f in files if f["type"] == "image"]
    other_files = [f for f in files if f["type"] != "image"]

    # Add text with non-image file contents embedded
    full_text = text
    for file_info in other_files:
        full_text = f"{file_info['content']}\n\n---\n\n{full_text}"

    if image_files:
        # Multimodal content
        if full_text.strip():
            content_parts.append({"type": "text", "text": full_text})
        for img in image_files:
            content_parts.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{img['mime_type']};base64,{img['content']}"
                },
            })
        return content_parts
    else:
        return full_text
