#!/usr/bin/env python3
"""
Copilot Chat - A PyQt5 chat application with Claude-inspired UI
powered by GitHub Copilot API using OpenAI models.
"""
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from app.main_window import MainWindow


def main():
    # Enable high-DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("Copilot Chat")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("CopilotChat")

    # Set default font
    font = QFont("Segoe UI", 10)
    font.setStyleHint(QFont.SansSerif)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
