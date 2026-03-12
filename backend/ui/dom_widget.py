from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QAbstractItemView)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont

class DOMWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 1. Setup Table with a generous range (e.g., 500 rows)
        self.row_count = 500
        self.table = QTableWidget(self.row_count, 3) 
        self.table.setHorizontalHeaderLabels(["Bid Size", "Price", "Ask Size"])
        
        # UI Styling: Dark, Clean, No Selection
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table.setStyleSheet("""
            QTableWidget { background-color: #121212; gridline-color: #222222; border: none; }
            QHeaderView::section { background-color: #1e1e1e; color: #888888; border: 1px solid #333333; }
        """)
        
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Pre-initialize all items so we can update .setText() fast
        font = QFont("Consolas", 10)
        for r in range(self.row_count):
            for c in range(3):
                item = QTableWidgetItem("")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setFont(font)
                self.table.setItem(r, c, item)

        layout.addWidget(self.table)
        
        # State
        self.price_to_row = {}
        self.ladder_initialized = False

    def _initialize_ladder(self, base_price, tick_size):
        """Creates the fixed price list once. Higher prices at the top."""
        self.price_to_row.clear()
        
        # Start the top of the ladder ~250 ticks above current price
        top_price = base_price + ( (self.row_count // 2) * tick_size)
        
        for i in range(self.row_count):
            current_p = round(top_price - (i * tick_size), 5)
            self.price_to_row[current_p] = i
            
            # Set the Price column text (Column 1)
            price_item = self.table.item(i, 1)
            price_item.setText(f"{current_p:.5f}")
            price_item.setForeground(QColor("#cccccc"))
            price_item.setBackground(QColor("#181818"))
            
        # Initial scroll to center (only happens once on startup)
        self.table.scrollToItem(self.table.item(self.row_count // 2, 1), 
                                QAbstractItemView.ScrollHint.PositionAtCenter)
        self.ladder_initialized = True

    def update_dom(self, asks, bids, tick_size=0.0001):
        if not asks and not bids: return

        # Dynamically determine decimals: 5 for EURUSD (0.0001), 3 for USDJPY (0.001)
        decimals = 5 if tick_size < 0.001 else 3

        if not self.ladder_initialized:
            best_ask = asks[0].price if asks else (bids[0].price + tick_size)
            best_bid = bids[0].price if bids else (asks[0].price - tick_size)
            mid = round((best_ask + best_bid) / 2.0, decimals)
            
            # Rebuild ladder with the correct precision
            self.price_to_row.clear()
            top_price = mid + ((self.row_count // 2) * tick_size)
            for i in range(self.row_count):
                current_p = round(top_price - (i * tick_size), decimals)
                self.price_to_row[current_p] = i
                
                price_item = self.table.item(i, 1)
                # Format string dynamically based on decimals
                format_str = f"{{:.{decimals}f}}" 
                price_item.setText(format_str.format(current_p))
                price_item.setForeground(QColor("#cccccc"))
                price_item.setBackground(QColor("#181818"))

            self.table.scrollToItem(self.table.item(self.row_count // 2, 1), 
                                    QAbstractItemView.ScrollHint.PositionAtCenter)
            self.ladder_initialized = True

        # 1. Tell Qt to stop painting to the screen
        self.table.setUpdatesEnabled(False)

        # 2. Do all the heavy clearing in the background
        for i in range(self.row_count):
            self.table.item(i, 0).setText("") 
            self.table.item(i, 2).setText("") 
            self.table.item(i, 0).setBackground(QColor("#121212"))
            self.table.item(i, 2).setBackground(QColor("#121212"))

        # 3. Apply Bids
        for b in bids:
            p = round(b.price, decimals)
            if p in self.price_to_row:
                row = self.price_to_row[p]
                self.table.item(row, 0).setText(f"{int(b.size/1000)}k")
                self.table.item(row, 0).setBackground(QColor("#0a320a")) 
                self.table.item(row, 0).setForeground(QColor("#66ff66"))

        # 4. Apply Asks
        for a in asks:
            p = round(a.price, decimals)
            if p in self.price_to_row:
                row = self.price_to_row[p]
                self.table.item(row, 2).setText(f"{int(a.size/1000)}k")
                self.table.item(row, 2).setBackground(QColor("#320a0a")) 
                self.table.item(row, 2).setForeground(QColor("#ff6666"))

        # 5. Tell Qt to paint the final result all at once
        self.table.setUpdatesEnabled(True)