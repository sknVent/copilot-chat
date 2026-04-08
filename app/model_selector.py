"""
Model selector dropdown widget - restricted to OpenAI models via Copilot.
"""
from PyQt5.QtWidgets import QComboBox, QSizePolicy
from PyQt5.QtCore import pyqtSignal

from app.styles import MODEL_SELECTOR_STYLE

OPENAI_MODELS = [
    ("gpt-4o", "GPT-4o (Default)"),
    ("gpt-4o-mini", "GPT-4o Mini"),
    ("gpt-4-turbo", "GPT-4 Turbo"),
    ("gpt-4", "GPT-4"),
    ("gpt-3.5-turbo", "GPT-3.5 Turbo"),
    ("o1-preview", "o1-preview"),
    ("o1-mini", "o1-mini"),
    ("o3-mini", "o3-mini"),
]


class ModelSelector(QComboBox):
    """
    ComboBox pre-populated with OpenAI models available through Copilot.
    """

    model_changed = pyqtSignal(str)

    def __init__(self, parent=None, initial_model: str = "gpt-4o"):
        super().__init__(parent)
        self.setObjectName("model_selector")
        self.setStyleSheet(MODEL_SELECTOR_STYLE)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setMinimumWidth(180)

        self._populate()
        self.set_model(initial_model)
        self.currentIndexChanged.connect(self._on_model_changed)

    def _populate(self):
        """Populate the dropdown with OpenAI models."""
        self.blockSignals(True)
        for model_id, display_name in OPENAI_MODELS:
            self.addItem(display_name, model_id)
        self.blockSignals(False)

    def _on_model_changed(self, index: int):
        model_id = self.itemData(index)
        if model_id:
            self.model_changed.emit(model_id)

    def get_model(self) -> str:
        """Return the currently selected model ID."""
        return self.currentData() or "gpt-4o"

    def set_model(self, model_id: str):
        """Set the selected model by ID."""
        for i in range(self.count()):
            if self.itemData(i) == model_id:
                self.setCurrentIndex(i)
                return
        # Default to gpt-4o if not found
        self.setCurrentIndex(0)
