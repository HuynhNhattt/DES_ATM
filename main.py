
import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow

# Thiết lập chế độ High DPI cho màn hình sắc nét
def setup_high_dpi():
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

if __name__ == "__main__":
    # Setup DPI
    from PyQt5.QtCore import Qt
    setup_high_dpi()
    
    app = QApplication(sys.argv)
    
    # Tên ứng dụng
    app.setApplicationName("DES ATM Security Demo")
    
    # Khởi chạy cửa sổ chính
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())