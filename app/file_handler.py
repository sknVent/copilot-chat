"""
File reading and processing logic for images, Excel, Python, and text files.
"""
import base64
import os
from typing import Dict, Any, Optional


# Supported file types
SUPPORTED_IMAGES = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}
SUPPORTED_EXCEL = {".xlsx", ".xls"}
SUPPORTED_CODE = {".py"}
SUPPORTED_TEXT = {".txt", ".md", ".csv", ".json", ".xml", ".html", ".css", ".js"}

ALL_SUPPORTED = SUPPORTED_IMAGES | SUPPORTED_EXCEL | SUPPORTED_CODE | SUPPORTED_TEXT

FILE_FILTER = (
    "Supported Files (*.png *.jpg *.jpeg *.gif *.bmp *.webp "
    "*.xlsx *.xls *.py *.txt *.md *.csv *.json *.xml);;"
    "Images (*.png *.jpg *.jpeg *.gif *.bmp *.webp);;"
    "Excel Files (*.xlsx *.xls);;"
    "Python Files (*.py);;"
    "Text Files (*.txt *.md *.csv *.json *.xml *.html *.css *.js);;"
    "All Files (*)"
)

# MIME type mapping
MIME_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".bmp": "image/bmp",
    ".webp": "image/webp",
}

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB limit


class FileProcessingError(Exception):
    """Raised when a file cannot be processed."""
    pass


def process_file(file_path: str) -> Dict[str, Any]:
    """
    Process a file and return a dict with its content ready for the API.

    Returns a dict with keys:
        - name: filename
        - type: 'image', 'excel', 'python', 'text'
        - display_name: human-readable name
        - inline_text: text content for non-image files (included in message)
        - data: base64 encoded data (for images)
        - mime_type: MIME type (for images)
        - size: file size in bytes
        - preview: short preview text for display
    """
    if not os.path.exists(file_path):
        raise FileProcessingError(f"File not found: {file_path}")

    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        raise FileProcessingError(
            f"File too large: {file_size / 1024 / 1024:.1f} MB (max 20 MB)"
        )

    ext = os.path.splitext(file_path)[1].lower()
    filename = os.path.basename(file_path)

    if ext in SUPPORTED_IMAGES:
        return _process_image(file_path, filename, ext, file_size)
    elif ext in SUPPORTED_EXCEL:
        return _process_excel(file_path, filename, file_size)
    elif ext in SUPPORTED_CODE:
        return _process_python(file_path, filename, file_size)
    elif ext in SUPPORTED_TEXT:
        return _process_text(file_path, filename, file_size)
    else:
        raise FileProcessingError(f"Unsupported file type: {ext}")


def _process_image(
    file_path: str, filename: str, ext: str, file_size: int
) -> Dict[str, Any]:
    """Process an image file - encode as base64."""
    with open(file_path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")

    mime_type = MIME_TYPES.get(ext, "image/png")

    return {
        "name": filename,
        "type": "image",
        "display_name": filename,
        "inline_text": "",
        "data": data,
        "mime_type": mime_type,
        "size": file_size,
        "preview": f"🖼️ {filename}",
        "file_path": file_path,
    }


def _process_excel(file_path: str, filename: str, file_size: int) -> Dict[str, Any]:
    """Process an Excel file - convert to text table."""
    try:
        import openpyxl

        wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
        text_parts = [f"**Excel File: {filename}**\n"]

        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            text_parts.append(f"\n### Sheet: {sheet_name}\n")

            rows = []
            for row in ws.iter_rows(values_only=True):
                # Skip completely empty rows
                if any(cell is not None for cell in row):
                    rows.append(row)

            if not rows:
                text_parts.append("*(empty sheet)*\n")
                continue

            # Limit to first 100 rows for large files
            if len(rows) > 100:
                rows = rows[:100]
                truncated = True
            else:
                truncated = False

            # Build markdown table
            if rows:
                # Determine max columns
                max_cols = max(len(r) for r in rows)

                # Header row
                header = rows[0]
                header_cells = [str(c) if c is not None else "" for c in header]
                header_cells += [""] * (max_cols - len(header_cells))

                text_parts.append("| " + " | ".join(header_cells) + " |\n")
                text_parts.append("| " + " | ".join(["---"] * max_cols) + " |\n")

                # Data rows
                for row in rows[1:]:
                    cells = [str(c) if c is not None else "" for c in row]
                    cells += [""] * (max_cols - len(cells))
                    text_parts.append("| " + " | ".join(cells) + " |\n")

                if truncated:
                    text_parts.append(
                        "\n*(showing first 100 rows, file has more data)*\n"
                    )

        wb.close()
        inline_text = "".join(text_parts)
        preview_lines = inline_text.split("\n")[:3]
        preview = "\n".join(preview_lines)

        return {
            "name": filename,
            "type": "excel",
            "display_name": filename,
            "inline_text": inline_text,
            "data": "",
            "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "size": file_size,
            "preview": f"📊 {filename}",
            "file_path": file_path,
        }
    except ImportError:
        raise FileProcessingError(
            "openpyxl is required to open Excel files. Install with: pip install openpyxl"
        )
    except Exception as e:
        raise FileProcessingError(f"Could not read Excel file: {e}")


def _process_python(file_path: str, filename: str, file_size: int) -> Dict[str, Any]:
    """Process a Python file - include as code block."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        # Limit content size
        if len(content) > 50000:
            content = content[:50000] + "\n\n... (file truncated at 50,000 characters)"

        inline_text = f"**Python File: {filename}**\n\n```python\n{content}\n```"
        preview = content[:100].replace("\n", " ")

        return {
            "name": filename,
            "type": "python",
            "display_name": filename,
            "inline_text": inline_text,
            "data": "",
            "mime_type": "text/x-python",
            "size": file_size,
            "preview": f"🐍 {filename}",
            "file_path": file_path,
        }
    except Exception as e:
        raise FileProcessingError(f"Could not read Python file: {e}")


def _process_text(file_path: str, filename: str, file_size: int) -> Dict[str, Any]:
    """Process a text file - include content directly."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        # Limit content size
        if len(content) > 50000:
            content = content[:50000] + "\n\n... (file truncated at 50,000 characters)"

        ext = os.path.splitext(file_path)[1].lower()
        lang_map = {
            ".md": "markdown",
            ".json": "json",
            ".xml": "xml",
            ".html": "html",
            ".css": "css",
            ".js": "javascript",
            ".csv": "",
            ".txt": "",
        }
        lang = lang_map.get(ext, "")

        if lang:
            inline_text = (
                f"**File: {filename}**\n\n```{lang}\n{content}\n```"
            )
        else:
            inline_text = f"**File: {filename}**\n\n{content}"

        return {
            "name": filename,
            "type": "text",
            "display_name": filename,
            "inline_text": inline_text,
            "data": "",
            "mime_type": "text/plain",
            "size": file_size,
            "preview": f"📄 {filename}",
            "file_path": file_path,
        }
    except Exception as e:
        raise FileProcessingError(f"Could not read text file: {e}")


def get_file_icon(file_type: str) -> str:
    """Return an emoji icon for a file type."""
    icons = {
        "image": "🖼️",
        "excel": "📊",
        "python": "🐍",
        "text": "📄",
    }
    return icons.get(file_type, "📎")


def format_file_size(size_bytes: int) -> str:
    """Format file size as human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / 1024 / 1024:.1f} MB"


def get_image_thumbnail(file_path: str, max_size: int = 64) -> Optional[bytes]:
    """
    Generate a thumbnail for an image file.
    Returns bytes of the thumbnail in PNG format, or None on error.
    """
    try:
        from PIL import Image
        import io

        img = Image.open(file_path)
        img.thumbnail((max_size, max_size), Image.LANCZOS)

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except Exception:
        return None
