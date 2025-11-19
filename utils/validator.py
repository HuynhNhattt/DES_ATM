class Validator:
    @staticmethod
    def validate_pin(pin):
        """
        Kiểm tra mã PIN:
        - Phải là số
        - Độ dài từ 4 đến 6 ký tự
        """
        if not pin or not isinstance(pin, str):
            return False
        return pin.isdigit() and (4 <= len(pin) <= 6)

    @staticmethod
    def validate_pan(pan):
        """
        Kiểm tra số thẻ (PAN):
        - Loại bỏ khoảng trắng
        - Phải là số
        - Độ dài tiêu chuẩn từ 13 đến 19 ký tự
        """
        if not pan or not isinstance(pan, str):
            return False
        
        clean_pan = pan.replace(" ", "")
        return clean_pan.isdigit() and (13 <= len(clean_pan) <= 19)