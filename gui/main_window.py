import os
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter, QMessageBox
from PyQt5.QtCore import Qt

from gui.components.atm_keypad import ATMKeypad
from gui.components.server_logger import ServerLogger
from gui.components.visualizer import AvalancheVisualizer
from core.iso9564 import ISO9564_Processor
from core.key_scheduler import KeyScheduler
from core.des_logic import DES_Logic
from utils.converters import bin_to_hex

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Đồ án ATTT - Mô phỏng Bảo mật ATM (DES White-box)")
        self.resize(1200, 750)

        self.des = DES_Logic()
        self.secret_key_hex = "133457799BBCDFF1" 
        self.subkeys = [] # Chưa sinh khóa vội
        self.current_cipher = None # Lưu tạm bản mã để chờ giải mã
        self.current_pan = None    # Lưu tạm PAN

        self.setup_ui()
        self.load_styles()

    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        self.atm_panel = ATMKeypad()
        self.atm_panel.transaction_signal.connect(self.handle_transaction)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        self.logger = ServerLogger()
        # KẾT NỐI NÚT BẤM TỪ SERVER PANEL
        self.logger.generate_key_signal.connect(self.handle_keygen)
        self.logger.decrypt_signal.connect(self.handle_decryption)

        self.visualizer = AvalancheVisualizer()
        self.visualizer.run_test_signal.connect(self.handle_avalanche_test)

        right_layout.addWidget(self.logger, stretch=4)
        right_layout.addWidget(self.visualizer, stretch=1)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.atm_panel)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 800])
        
        main_layout.addWidget(splitter)

        # LOG TRẠNG THÁI CHỜ
        self.logger.log("Hệ thống đang ở trạng thái chờ (IDLE).", "THÔNG TIN")
        self.logger.log("Vui lòng bấm 'KHỞI TẠO & SINH KHÓA' để bắt đầu.", "LỖI")

    def load_styles(self):
        try:
            style_path = os.path.join(os.path.dirname(__file__), "styles.qss")
            with open(style_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except: pass

    # --- XỬ LÝ SINH KHÓA THỦ CÔNG ---
    def handle_keygen(self):
        self.logger.clear_log()
        self.logger.log("🛠️ ADMIN ĐÃ YÊU CẦU KHỞI TẠO HỆ THỐNG...", "XỬ LÝ")
        self.logger.log(f"🔑 NẠP KHÓA CHÍNH (MASTER KEY): {self.secret_key_hex}", "MÃ HÓA")
        
        self.subkeys = KeyScheduler.generate_subkeys(self.secret_key_hex)
        
        for i, k in enumerate(self.subkeys):
            self.logger.log(f"   > Sinh khóa con K{i+1:02d}: {bin_to_hex(k)}", "THÔNG TIN")
        
        self.logger.log("✅ HỆ THỐNG SẴN SÀNG GIAO DỊCH.", "KẾT QUẢ")

    # --- BƯỚC 1: ATM GỬI GIAO DỊCH ---
    def handle_transaction(self, pin, pan):
        if not self.subkeys:
            QMessageBox.warning(self, "Lỗi", "Hệ thống chưa có khóa! Vui lòng bấm nút Khởi tạo bên Server trước.")
            return

        if not pan:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập số thẻ hoặc chọn file.")
            return

        if len(pin) < 4:
            QMessageBox.warning(self, "Lỗi", "Mã PIN quá ngắn.")
            return
        
        self.logger.clear_log()
        self.logger.log(f"📡 [ATM] GỬI YÊU CẦU GIAO DỊCH...", "THÔNG TIN")
        self.logger.log(f"   PAN: {pan}", "THÔNG TIN")

        # CHUẨN HÓA ISO & MÃ HÓA
        try:
            input_block_hex = ISO9564_Processor.create_input_block(pin, pan)
            self.logger.log(f"🔄 [ATM] ĐÓNG GÓI ISO 9564 (PIN + PAN): {input_block_hex}", "XỬ LÝ")
            
            self.logger.log(f"🔒 [ATM] MÃ HÓA DES (16 Vòng)...", "MÃ HÓA")
            cipher_hex, trace_logs = self.des.run_des_block(input_block_hex, self.subkeys)
            
            # In log chi tiết 16 vòng
            for log_line in trace_logs:
                 # Làm gọn log hiển thị
                log_vi = log_line.replace("R", "V").replace("K:", "Key:").replace("INIT IP", "KHỞI TẠO")
                self.logger.log(f"   {log_vi}", "THÔNG TIN")

            self.logger.log(f"📦 [MẠNG] GÓI TIN MÃ HÓA ĐƯỢC GỬI ĐI: {cipher_hex}", "KẾT QUẢ")
            
            # LƯU TRẠNG THÁI ĐỂ CHỜ GIẢI MÃ
            self.current_cipher = cipher_hex
            self.current_pan = pan
            self.current_input_block = input_block_hex # Lưu để đối chiếu
            
            self.logger.log("⏳ [SERVER] ĐÃ NHẬN GÓI TIN. CHỜ XÁC THỰC...", "LỖI")
            self.logger.enable_decrypt_button(True) # Bật nút giải mã sáng lên

        except Exception as e:
            self.logger.log(f"Lỗi: {str(e)}", "LỖI")

    # --- BƯỚC 2: SERVER GIẢI MÃ (KHI BẤM NÚT) ---
    def handle_decryption(self):
        if not self.current_cipher:
            return

        self.logger.log(f"🔓 [SERVER] ĐANG GIẢI MÃ & KIỂM TRA...", "XỬ LÝ")
        
        decrypted_hex, _ = self.des.run_des_block(self.current_cipher, self.subkeys, is_decrypt=True)
        extracted_pin = ISO9564_Processor.extract_pin(decrypted_hex, self.current_pan)
        
        self.logger.log(f"   Khối giải mã được: {decrypted_hex}", "THÔNG TIN")
        
        if decrypted_hex == self.current_input_block:
            self.logger.log(f"✅ XÁC THỰC THÀNH CÔNG! PIN: {extracted_pin}", "KẾT QUẢ")
            QMessageBox.information(self, "Thành Công", f"Giao dịch chấp thuận!\nPIN trích xuất: {extracted_pin}")
            self.atm_panel.clear_pin()
        else:
            self.logger.log("❌ SAI KHÓA HOẶC DỮ LIỆU BỊ SỬA ĐỔI!", "LỖI")
            QMessageBox.critical(self, "Thất Bại", "Xác thực thất bại!")
        
        # Reset trạng thái
        self.logger.enable_decrypt_button(False)
        self.current_cipher = None

    # --- AVALANCHE TEST ---
    def handle_avalanche_test(self, pin1, pin2):
        if not self.subkeys:
            QMessageBox.warning(self, "Lỗi", "Cần sinh khóa trước khi test.")
            return

        # Lấy PIN từ input người dùng nhập
        pan = "4987123456789012" # PAN giả lập cho test
        
        self.logger.clear_log()
        self.logger.log(f"--- 🧪 SO SÁNH HIỆU ỨNG TUYẾT LỞ ---", "MÃ HÓA")
        self.logger.log(f"Input A: {pin1} | Input B: {pin2}", "THÔNG TIN")

        block1 = ISO9564_Processor.create_input_block(pin1, pan)
        block2 = ISO9564_Processor.create_input_block(pin2, pan)
        
        cipher1, _ = self.des.run_des_block(block1, self.subkeys)
        cipher2, _ = self.des.run_des_block(block2, self.subkeys)
        
        from utils.converters import hex_to_bin
        bin1, bin2 = hex_to_bin(cipher1), hex_to_bin(cipher2)
        diff = sum(1 for a, b in zip(bin1, bin2) if a != b)
        percent = (diff / 64) * 100
        
        self.logger.log(f"Cipher A: {cipher1}", "THÔNG TIN")
        self.logger.log(f"Cipher B: {cipher2}", "THÔNG TIN")
        self.logger.log(f"Khác biệt: {diff} bits ({percent:.2f}%)", "KẾT QUẢ")
        
        self.visualizer.update_progress(percent)