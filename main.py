from PyQt6.QtWidgets import QApplication, QMessageBox
import sys
import os
from gui import ExtraClassApp

def create_directories():
    """Create necessary directories"""
    directories = ["exports", "data"]
    
    for dir_name in directories:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

def main():
    # Create necessary directories
    create_directories()
    
    app = QApplication(sys.argv)
    app.setApplicationName("Extra Class Counter")
    app.setApplicationVersion("1.0.0")
    app.setStyle('Fusion')
    
    try:
        window = ExtraClassApp()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to start application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()