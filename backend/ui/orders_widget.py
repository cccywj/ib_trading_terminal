from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
                             QTableWidget, QHeaderView, QLabel, QAbstractItemView)
from PySide6.QtCore import Qt

class OrdersWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setMaximumHeight(200)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # --- 1. Top Bar: Account PnL ---
        pnl_layout = QHBoxLayout()
        pnl_layout.setContentsMargins(10, 5, 10, 5)
        
        self.pnl_label = QLabel("Daily PnL: $0.00")
        self.pnl_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #a0a0a0;")
        pnl_layout.addWidget(self.pnl_label)
        pnl_layout.addStretch()
        
        layout.addLayout(pnl_layout)

        # --- 2. Tabbed Data Tables ---
        self.tabs = QTabWidget()
        
        # Tab A: Positions
        self.positions_table = self.create_data_table(["Symbol", "Pos", "Avg Price", "Last", "Unrealized"])
        self.tabs.addTab(self.positions_table, "Positions")

        # Tab B: Open Orders
        self.orders_table = self.create_data_table(["Symbol", "Side", "Qty", "Type", "Price"])
        self.tabs.addTab(self.orders_table, "Working Orders")

        layout.addWidget(self.tabs)

    def create_data_table(self, headers):
        # Create an empty table that auto-stretches to fill the panel
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setAlternatingRowColors(True)
        
        # Make columns stretch evenly
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        return table