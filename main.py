#!/usr/bin/env python3
"""
main.py
MeMyselfAI - macOS Desktop Application
Entry point for the application
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from ui.main_window import MainWindow


def main():
    """Main application entry point"""
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("MeMyselfAI")
    app.setOrganizationName("MeMyselfAI")
    
    # Set macOS-specific attributes
    if sys.platform == "darwin":
        app.setAttribute(Qt.ApplicationAttribute.AA_DontShowIconsInMenus, False)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
