from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView

class ChartWidget(QWidget):
    def __init__(self, symbol="USDJPY"):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.web_view = QWebEngineView()
        
        # We pass the symbol as a URL parameter to the React app
        url = f"http://localhost:5173/?symbol={symbol}"
        self.web_view.setUrl(QUrl(url))     

        layout.addWidget(self.web_view)