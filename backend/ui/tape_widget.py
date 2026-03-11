from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QHeaderView

class TapeWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.ts_table = QTableWidget(0, 3)
        self.ts_table.setHorizontalHeaderLabels(["Time", "Price", "Size"])
        self.ts_table.verticalHeader().setVisible(False)
        self.ts_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.ts_table)