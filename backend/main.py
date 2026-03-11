import os
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QTableWidget, 
                             QVBoxLayout, QWidget, QHeaderView, QLabel, QDockWidget)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView

# --- MODULAR COMPONENTS ---
from ui.dom_widget import DOMWidget
from ui.tape_widget import TapeWidget
from ui.chart_widget import ChartWidget
from ui.orders_widget import OrdersWidget

os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--log-level=3"

# --- MAIN WINDOW ---

class TradingPlatform(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pro Trading Terminal")
        self.resize(1600, 900)

        # --- 1. CREATE ALL WIDGETS AND DOCKS FIRST ---

        # Chart 1
        self.chart_dock_1 = QDockWidget("USDJPY Chart", self)
        self.chart_widget_1 = ChartWidget(symbol="USDJPY")
        self.chart_dock_1.setWidget(self.chart_widget_1)

        # Chart 2
        self.chart_dock_2 = QDockWidget("EURUSD Chart", self)
        self.chart_widget_2 = ChartWidget(symbol="EURUSD")
        self.chart_dock_2.setWidget(self.chart_widget_2)

        # DOM Ladder
        self.dom_dock = QDockWidget("DOM Ladder", self)
        self.dom_widget = DOMWidget() # (Or whatever your class is named)
        self.dom_dock.setWidget(self.dom_widget)

        # Time & Sales Tape
        self.tape_dock = QDockWidget("Time & Sales", self)
        self.tape_widget = TapeWidget() # (Or whatever your class is named)
        self.tape_dock.setWidget(self.tape_widget)

        # Orders
        self.orders_dock = QDockWidget("Account & Orders", self)
        self.orders_widget = OrdersWidget()
        self.orders_dock.setWidget(self.orders_widget)

        # --- 2. ARRANGE THEM ON THE SCREEN ---

        # Remove the central widget so docks can use 100% of the window
        self.setCentralWidget(None)
        
        # Allow docks to be nested and tabbed
        self.setDockOptions(
            QMainWindow.DockOption.AllowNestedDocks | 
            QMainWindow.DockOption.AllowTabbedDocks
        )

        # 1. Anchor Chart 1 to the left (takes whole window initially)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.chart_dock_1)

        # 2. Split Chart 1 HORIZONTALLY to create the MIDDLE column (DOM)
        self.splitDockWidget(self.chart_dock_1, self.dom_dock, Qt.Orientation.Horizontal)

        # 3. Split the DOM HORIZONTALLY to create the RIGHT column (Tape)
        self.splitDockWidget(self.dom_dock, self.tape_dock, Qt.Orientation.Horizontal)

        # 4. NOW split Chart 1 VERTICALLY. Since Chart 1 is now constrained to the left column,
        # Chart 2 will perfectly tuck directly underneath it without spanning the window!
        self.splitDockWidget(self.chart_dock_1, self.chart_dock_2, Qt.Orientation.Vertical)

        # 5. Split DOM and add orders below
        self.splitDockWidget(self.dom_dock, self.orders_dock, Qt.Orientation.Vertical)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # --- QT STYLE SHEET (QSS) ---
    dark_stylesheet = """
    /* Main Window Background */
    QMainWindow {
        background-color: #121212;
    }

    /* Dock Widget Overall Style */
    QDockWidget {
        color: #ffffff;
        font-weight: bold;
        font-size: 12px;
        titlebar-close-icon: url(close_icon.png); /* You can add custom icons here */
        titlebar-normal-icon: url(float_icon.png);
    }

    /* Dock Widget Title Bar */
    QDockWidget::title {
        background: #1e1e1e;
        padding-left: 10px;
        padding-top: 4px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        border: 1px solid #333333;
    }

    /* The content area inside the Dock Widget */
    QDockWidget > QWidget {
        border: 1px solid #333333;
        background-color: #1e1e1e;
    }

    /* Tabs (When you drag one dock widget on top of another) */
    QTabBar::tab {
        background: #2d2d2d;
        color: #888888;
        padding: 8px 15px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        border: 1px solid #333333;
        border-bottom: none;
    }

    /* Active Tab */
    QTabBar::tab:selected {
        background: #1e1e1e;
        color: #ffffff;
        border-top: 2px solid #4caf50; /* Green accent for the active tab */
    }

    /* Hover State for Tabs */
    QTabBar::tab:hover {
        background: #3d3d3d;
        color: #ffffff;
    }
    """
    
    # Apply the styling globally
    app.setStyleSheet(dark_stylesheet)
    
    window = TradingPlatform()
    window.show()
    sys.exit(app.exec())