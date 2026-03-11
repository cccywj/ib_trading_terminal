from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QHeaderView, QAbstractItemView, QPushButton, QSpinBox, QLabel)
from PySide6.QtCore import Qt

class DOMWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumWidth(460)
        
        # Main vertical layout for the whole DOM dock
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # --- 1. STATE: Track the active order size ---
        self.current_size = 1

        # --- 2. CONTROL BAR: Order Size Selector ---
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(5, 5, 5, 5)
        
        control_layout.addWidget(QLabel("Size:"))

        # Custom text input (QSpinBox is perfect for numbers)
        self.size_input = QSpinBox()
        self.size_input.setRange(1, 1000000) # Min 1, Max 1 Million
        self.size_input.setValue(self.current_size)
        self.size_input.setFixedWidth(80)
        self.size_input.valueChanged.connect(self.on_input_changed)
        control_layout.addWidget(self.size_input)

        # Quick Preset Buttons
        self.size_buttons = {}
        presets = [1, 10, 100, 500, 1000]
        
        for size in presets:
            btn = QPushButton(str(size))
            btn.setCheckable(True) # Makes it act like a toggle button
            btn.setFixedWidth(40)
            # Use a lambda to pass the specific size of this button to the function
            btn.clicked.connect(lambda checked, s=size: self.set_preset_size(s))
            control_layout.addWidget(btn)
            self.size_buttons[size] = btn

        # Highlight the default button on startup
        self.size_buttons[1].setChecked(True)
        
        # Add a stretch to the right so the buttons stay aligned to the left
        control_layout.addStretch()

        # Add the control bar to the top of the main layout
        layout.addLayout(control_layout)

        # --- 3. THE DOM LADDER TABLE ---
        self.table = QTableWidget(40, 8) 
        headers = ["Price", "OB", "BID", "ASK", "OS", "VPS", "VPB", "VPD"]
        self.table.setHorizontalHeaderLabels(headers)

        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.setAlternatingRowColors(True)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch) 
        
        fixed_width = 55
        for col in range(1, 8):
            self.table.setColumnWidth(col, fixed_width)

        layout.addWidget(self.table)

    # --- 4. LOGIC: Syncing Buttons and the Text Box ---
    def set_preset_size(self, size):
        self.current_size = size
        
        # Update text box quietly (block signals so it doesn't trigger on_input_changed)
        self.size_input.blockSignals(True)
        self.size_input.setValue(size)
        self.size_input.blockSignals(False)
        
        # Visually check the clicked button and uncheck the rest
        for s, btn in self.size_buttons.items():
            btn.setChecked(s == size)

    def on_input_changed(self, value):
        self.current_size = value
        
        # If user types a number, check if it matches a preset. If not, uncheck all buttons.
        for s, btn in self.size_buttons.items():
            btn.setChecked(s == value)