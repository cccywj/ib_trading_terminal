from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QMouseEvent

class CustomTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(35) # Define exactly how thick you want the top bar
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 0, 0, 0)
        self.layout.setSpacing(0)

        # 1. Window Title
        self.title_label = QLabel("Pro Trading Terminal")
        self.title_label.setStyleSheet("color: #a0a0a0; font-family: 'Trebuchet MS'; font-weight: bold;")
        self.layout.addWidget(self.title_label)
        self.layout.addStretch()

        # 2. Window Control Buttons
        self.btn_min = self.create_button("—", self.parent.showMinimized)
        self.btn_max = self.create_button("□", self.toggle_maximize)
        self.btn_close = self.create_button("✕", self.parent.close, is_close=True)

        self.layout.addWidget(self.btn_min)
        self.layout.addWidget(self.btn_max)
        self.layout.addWidget(self.btn_close)

        # Style the background of the title bar
        self.setStyleSheet("background-color: #1e1e1e;")

        # Variables for window dragging
        self.start_pos = None

    def create_button(self, text, function, is_close=False):
        btn = QPushButton(text)
        btn.setFixedSize(45, 35)
        btn.clicked.connect(function)
        
        # QSS (Qt CSS) for button styling and hover effects
        hover_color = "#e81123" if is_close else "#333333"
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: #a0a0a0;
                border: none;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
                color: white;
            }}
        """)
        return btn

    def toggle_maximize(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()

    # --- Mouse Events to allow dragging the frameless window ---
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_pos = event.globalPosition().toPoint() - self.parent.frameGeometry().topLeft()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.start_pos is not None and event.buttons() == Qt.MouseButton.LeftButton:
            self.parent.move(event.globalPosition().toPoint() - self.start_pos)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.start_pos = None