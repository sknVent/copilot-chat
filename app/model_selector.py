"""Model dropdown selector widget."""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QComboBox, QLabel
from PyQt5.QtCore import pyqtSignal

from app.api_client import OPENAI_MODELS, DEFAULT_MODEL
from app.styles import MODEL_SELECTOR_STYLESHEET


class ModelSelector(QWidget):
    """Dropdown widget for selecting the OpenAI model."""

    model_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("modelSelectorContainer")
        self.setStyleSheet(MODEL_SELECTOR_STYLESHEET)
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)

        label = QLabel("Model:")
        label.setStyleSheet("color: #6b7280; font-size: 13px;")

        self.combo = QComboBox()
        self.combo.setObjectName("modelSelector")
        for model in OPENAI_MODELS:
            self.combo.addItem(model)

        idx = self.combo.findText(DEFAULT_MODEL)
        if idx >= 0:
            self.combo.setCurrentIndex(idx)

        self.combo.currentTextChanged.connect(self.model_changed.emit)

        layout.addWidget(label)
        layout.addWidget(self.combo)
        layout.addStretch()

    def get_model(self) -> str:
        """Return the currently selected model name."""
        return self.combo.currentText()

    def set_model(self, model: str):
        """Set the selected model by name."""
        idx = self.combo.findText(model)
        if idx >= 0:
            self.combo.setCurrentIndex(idx)
