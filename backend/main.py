import os
import sys

os.environ["QT_API"] = "pyside6"

# 1. Force Qt to use software OpenGL
os.environ["QT_OPENGL"] = "software"

# 2. Clean, stable flags to disable hardware GPU without breaking V8 Proxy
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
    "--disable-gpu "
    "--disable-gpu-compositing "
    "--disable-gpu-rasterization "
    "--log-level=3"
)
import asyncio
import qasync
from PySide6.QtWidgets import (QApplication, QMainWindow, QDockWidget)
from PySide6.QtCore import Qt

# --- MODULAR COMPONENTS ---
from ui.dom_widget import DOMWidget
from ui.tape_widget import TapeWidget
from ui.chart_widget import ChartWidget
from ui.orders_widget import OrdersWidget

# --- NEW SERVICES ---
from core.ib_client import IBBridge
from services.dom_service import DOMService
from ib_async import Forex

from services.chart_service import ChartService
from server.ws_server import ChartWebSocketServer

# --- MAIN WINDOW ---
class TradingPlatform(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pro Trading Terminal")
        self.resize(1600, 900)

        # --- 1. CREATE ALL WIDGETS AND DOCKS FIRST ---

        # Charts
        self.charts_dock = QDockWidget("EURUSD Chart", self)
        self.charts_widget = ChartWidget(symbols="EURUSD,EURUSD", timeframes="10s,1D")
        self.charts_dock.setWidget(self.charts_widget)

        # DOM Ladder
        self.dom_dock = QDockWidget("DOM Ladder", self)
        self.dom_widget = DOMWidget() 
        self.dom_dock.setWidget(self.dom_widget)

        # Time & Sales Tape
        self.tape_dock = QDockWidget("Time & Sales", self)
        self.tape_widget = TapeWidget() 
        self.tape_dock.setWidget(self.tape_widget)

        # Orders
        self.orders_dock = QDockWidget("Account & Orders", self)
        self.orders_widget = OrdersWidget()
        self.orders_dock.setWidget(self.orders_widget)

        # --- 2. ARRANGE THEM ON THE SCREEN ---
        self.setCentralWidget(None)
        
        self.setDockOptions(
            QMainWindow.DockOption.AllowNestedDocks | 
            QMainWindow.DockOption.AllowTabbedDocks
        )

        # Anchor the single Charts dock to the left
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.charts_dock)
        
        # Split horizontally for the DOM
        self.splitDockWidget(self.charts_dock, self.dom_dock, Qt.Orientation.Horizontal)
        
        # Split horizontally again for the Tape
        self.splitDockWidget(self.dom_dock, self.tape_dock, Qt.Orientation.Horizontal)
        
        # Split the DOM vertically to put the Orders underneath
        self.splitDockWidget(self.dom_dock, self.orders_dock, Qt.Orientation.Vertical)

        # Force horizontal proportions (Charts get 50%, DOM 25%, Tape 25%)
        self.resizeDocks([self.charts_dock, self.dom_dock, self.tape_dock], [600, 600, 400], Qt.Orientation.Horizontal)


    def switch_symbol(self, new_symbol: str, timeframes: str = "10s,1D"):
        """Central command to update all widgets at once."""
        print(f"Switching entire terminal to {new_symbol}...")
        
        double_symbol_string = f"{new_symbol},{new_symbol}"
        # 1. Update the Charts
        # This reloads the Chromium instance with the new symbol in the URL
        self.charts_widget.update_url(double_symbol_string, timeframes)
        
        # 2. Update the Dock Title so you know what you're looking at
        self.charts_dock.setWindowTitle(f"{new_symbol} Charts")
        self.dom_dock.setWindowTitle(f"{new_symbol} DOM")

async def start_application(window):
    """Initializes IBKR services while the UI is running."""
    from core.ib_client import IBBridge
    from services.dom_service import DOMService
    from services.chart_service import ChartService
    from server.ws_server import ChartWebSocketServer
    from ib_async import Forex
    
    bridge = IBBridge()
    await bridge.connect()

    # --- 1. INITIALIZE ALL SERVICES FIRST ---
    dom_service = DOMService(bridge)
    chart_service = ChartService(bridge)
    ws_server = ChartWebSocketServer(chart_service)
    
    # Start the WebSocket Server immediately so the charts can connect
    asyncio.create_task(ws_server.start())

    # --- 2. DEFINE THE DYNAMIC SWITCHER ---
    # We need a variable to track the true active symbol
    current_active_symbol = None
    current_dom_subscription = None

    async def update_active_symbol(new_symbol):
        nonlocal current_dom_subscription, current_active_symbol
        
        # 1. Immediately update our state so stray ticks are ignored
        current_active_symbol = new_symbol
        
        # 2. Cancel the old subscription if it exists
        if current_dom_subscription:
            bridge.ib.cancelMktDepth(current_dom_subscription.contract)
        
        new_contract = Forex(new_symbol)
        
        # Reset the DOM Widget's ladder
        window.dom_widget.ladder_initialized = False
        
        def handle_dom_data(contract, asks, bids):
            incoming_symbol = f"{contract.symbol}{contract.currency}"
            if incoming_symbol != current_active_symbol:
                return 

            tick_size = 0.001 if "JPY" in new_symbol else 0.0001
            window.dom_widget.update_dom(asks, bids, tick_size=tick_size)

        current_dom_subscription = await dom_service.subscribe_level2(new_contract, handle_dom_data)
        window.switch_symbol(new_symbol)

    # --- 3. TRIGGER INITIAL LOAD ---
    # Start with EURUSD
    #await update_active_symbol("EURUSD")

    # TEST: Wait 10 seconds and switch to USDJPY
    #await asyncio.sleep(10)
    await update_active_symbol("USDJPY")

    # Keep app alive
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # --- QT ASYNC EVENT LOOP (qasync) ---
    # We replace the standard app.exec() with qasync to allow ib_async to run 
    # without freezing the PySide6 UI.
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    # --- QT STYLE SHEET (QSS) ---
    dark_stylesheet = """
    QMainWindow { background-color: #121212; }
    QDockWidget { color: #ffffff; font-weight: bold; font-size: 12px; }
    QDockWidget::title { background: #1e1e1e; padding-left: 10px; padding-top: 4px; border-top-left-radius: 4px; border-top-right-radius: 4px; border: 1px solid #333333; }
    QDockWidget > QWidget { border: 1px solid #333333; background-color: #1e1e1e; }
    QTabBar::tab { background: #2d2d2d; color: #888888; padding: 8px 15px; border-top-left-radius: 4px; border-top-right-radius: 4px; border: 1px solid #333333; border-bottom: none; }
    QTabBar::tab:selected { background: #1e1e1e; color: #ffffff; border-top: 2px solid #4caf50; }
    QTabBar::tab:hover { background: #3d3d3d; color: #ffffff; }
    """
    
    app.setStyleSheet(dark_stylesheet)
    
    window = TradingPlatform()
    window.show()
    
    # Run the application using the async loop
    with loop:
        loop.run_until_complete(start_application(window))