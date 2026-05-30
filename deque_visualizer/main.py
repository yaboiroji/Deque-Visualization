import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Consolas", 10))
    app.setApplicationName("Deque")

    app.setStyleSheet("""
        QMainWindow, QWidget {
            background-color: #050A18;
            color: #E0EEFF;
        }
        QPushButton {
            background-color: rgba(15, 30, 60, 180);
            color: #7EB8FF;
            border: 1px solid rgba(60, 120, 220, 0.4);
            border-radius: 8px;
            padding: 6px 10px;
            font-family: Consolas;
            font-size: 11px;
        }
        QPushButton:hover {
            background-color: rgba(30, 70, 140, 200);
            border: 1px solid rgba(80, 160, 255, 0.9);
            color: #FFFFFF;
        }
        QPushButton:pressed {
            background-color: rgba(10, 30, 80, 220);
        }
        QPushButton:checked {
            background-color: rgba(20, 60, 140, 210);
            border: 1px solid #5BB0FF;
            color: #A0D4FF;
        }
        QPushButton:disabled {
            background-color: rgba(10, 20, 40, 120);
            color: rgba(80, 100, 140, 0.5);
            border: 1px solid rgba(40, 60, 100, 0.3);
        }
        QLineEdit {
            background-color: rgba(10, 25, 55, 180);
            color: #C8DEFF;
            border: 1px solid rgba(60, 120, 220, 0.4);
            border-radius: 8px;
            padding: 6px 10px;
            font-family: Consolas;
            font-size: 11px;
        }
        QLineEdit:focus {
            border: 1px solid rgba(80, 160, 255, 0.9);
            background-color: rgba(15, 35, 75, 200);
        }
        QSlider::groove:horizontal {
            height: 4px;
            background: rgba(40, 80, 160, 0.4);
            border-radius: 2px;
        }
        QSlider::handle:horizontal {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #5BB0FF, stop:1 #2266CC);
            border: 1px solid #88CCFF;
            width: 14px;
            height: 14px;
            margin: -5px 0;
            border-radius: 7px;
        }
        QSlider::sub-page:horizontal {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #1A4A9A, stop:1 #3D8EF0);
            border-radius: 2px;
        }
        QStatusBar {
            background-color: rgba(3, 8, 20, 240);
            color: #6A9ACA;
            font-family: Consolas;
            font-size: 12px;
            border-top: 1px solid rgba(40, 80, 160, 0.5);
            padding: 3px 8px;
        }
        QFrame[frameShape="4"] {
            color: rgba(30, 60, 120, 0.5);
            
        QPushButton#peekFront {
            border-color: rgba(255, 220, 50, 0.5);
            color: #FFD700;
        }
        QPushButton#peekFront:hover {
            border-color: #FFD700;
            background-color: rgba(255, 200, 0, 0.15);
        }
        QPushButton#peekFront:pressed {
            background-color: rgba(255, 200, 0, 0.25);
            border-color: #FFE040;
        }
        QPushButton#peekRear {
            border-color: rgba(180, 100, 255, 0.5);
            color: #C87FFF;
        }
        QPushButton#peekRear:hover {
            border-color: #C87FFF;
            background-color: rgba(160, 80, 255, 0.15);
        }
        QPushButton#peekRear:pressed {
            background-color: rgba(160, 80, 255, 0.25);
            border-color: #D090FF;
        }
    """)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()