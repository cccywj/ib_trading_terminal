from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import QUrl, QTimer
from PySide6.QtWebEngineWidgets import QWebEngineView

class ChartWidget(QWidget):
    # Notice we changed 'symbol' to 'symbols' here
    def __init__(self, symbols="EURUSD,EURUSD", timeframes="10s,1D"):
        super().__init__()
        self.setMinimumHeight(400) 
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.web_view = QWebEngineView()
        self.web_view.setStyleSheet("background-color: #121212;")
        layout.addWidget(self.web_view)

        # Pass multiple symbols in the query string
        self.url = f"http://localhost:5173/?symbols={symbols}&timeframes={timeframes}"
        
        # Give the Qt layout engine 500ms to settle before spinning up Chromium
        QTimer.singleShot(500, self.load_chart)

    def load_chart(self):
        self.web_view.setUrl(QUrl(self.url))

    def update_url(self, symbols, timeframes):
        """Reloads the charts with new parameters."""
        self.url = f"http://localhost:5173/?symbols={symbols}&timeframes={timeframes}"
        self.web_view.setUrl(QUrl(self.url))