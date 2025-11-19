from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QPushButton, QLineEdit, QLabel, QFrame, QFileDialog, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal

class ATMKeypad(QWidget):
    transaction_signal = pyqtSignal(str, str) 

    def __init__(self):
        super().__init__()
        self.pin_buffer = ""
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        self.setObjectName("ATMPanel")
        
        header = QLabel("🏛️ ATM NGÂN HÀNG")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #00e5ff; margin-bottom: 10px;")
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)

        # --- KHE CẮM THẺ (SỬA ĐỔI) ---
        card_frame = QFrame()
        card_frame.setStyleSheet("background-color: #252525; border-radius: 8px; padding: 10px;")
        card_layout = QVBoxLayout(card_frame)
        
        lbl_card = QLabel("💳 KHE CẮM THẺ:")
        lbl_card.setStyleSheet("color: #aaa; font-size: 12px; font-weight: bold;")
        
        # Layout hàng ngang cho Input và Nút file
        input_layout = QHBoxLayout()
        
        self.pan_input = QLineEdit() # Để trống ban đầu
        self.pan_input.setObjectName("CardInput")
        self.pan_input.setPlaceholderText("Nhập tay hoặc chọn file...")
        
        btn_file = QPushButton("📂 Quẹt Thẻ")
        btn_file.setCursor(Qt.PointingHandCursor)
        btn_file.setStyleSheet("background-color: #009688; color: white; padding: 5px; border-radius: 4px; font-weight: bold;")
        btn_file.clicked.connect(self.select_card_file)
        
        input_layout.addWidget(self.pan_input)
        input_layout.addWidget(btn_file)
        
        card_layout.addWidget(lbl_card)
        card_layout.addLayout(input_layout)
        main_layout.addWidget(card_frame)
        # -----------------------------

        main_layout.addSpacing(20)

        # MÀN HÌNH LCD
        screen_frame = QFrame()
        screen_frame.setStyleSheet("background-color: #333; border-radius: 12px; padding: 5px;")
        screen_layout = QVBoxLayout(screen_frame)
        
        self.pin_display = QLineEdit()
        self.pin_display.setObjectName("DisplayScreen")
        self.pin_display.setEchoMode(QLineEdit.Password) 
        self.pin_display.setReadOnly(True)
        self.pin_display.setAlignment(Qt.AlignCenter)
        self.pin_display.setPlaceholderText("----")
        
        screen_layout.addWidget(self.pin_display)
        main_layout.addWidget(screen_frame)

        main_layout.addSpacing(20)

        # BÀN PHÍM
        keypad_grid = QGridLayout()
        keypad_grid.setSpacing(15)

        keys = [
            ('1', 0, 0), ('2', 0, 1), ('3', 0, 2),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2),
            ('7', 2, 0), ('8', 2, 1), ('9', 2, 2),
            ('XÓA', 3, 0), ('0', 3, 1), ('RÚT', 3, 2)
        ]

        for key, r, c in keys:
            btn = QPushButton(key)
            btn.setProperty("class", "KeypadBtn")
            
            if key == 'XÓA':
                btn.setObjectName("BtnClear")
                btn.setText("❌")
                btn.clicked.connect(self.clear_pin)
            elif key == 'RÚT':
                btn.setObjectName("BtnEnter")
                btn.setText("✅")
                btn.clicked.connect(self.submit_transaction)
            else:
                btn.clicked.connect(lambda _, k=key: self.add_digit(k))
            
            keypad_grid.addWidget(btn, r, c)

        main_layout.addLayout(keypad_grid)
        main_layout.addStretch()
        self.setLayout(main_layout)

    def add_digit(self, digit):
        if len(self.pin_buffer) < 6:
            self.pin_buffer += digit
            self.pin_display.setText(self.pin_buffer)

    def clear_pin(self):
        self.pin_buffer = ""
        self.pin_display.clear()

    def submit_transaction(self):
        pan = self.pan_input.text()
        pin = self.pin_buffer
        self.transaction_signal.emit(pin, pan)

    def select_card_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Chọn File Thẻ (Mô phỏng Quẹt)", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_name:
            try:
                with open(file_name, 'r') as f:
                    # Đọc dòng đầu tiên làm số thẻ
                    card_number = f.readline().strip()
                    self.pan_input.setText(card_number)
            except Exception as e:
                self.pan_input.setText("Lỗi đọc thẻ")