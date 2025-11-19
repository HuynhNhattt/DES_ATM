from utils.converters import hex_to_bin, bin_to_hex, xor_bits

class ISO9564_Processor:
    @staticmethod
    def create_input_block(pin, pan):
        """Tạo PIN Block Format 0 (PIN XOR PAN) để mã hóa"""
        # 1. Định dạng PIN Block: 0 + Len(PIN) + PIN + Padding(F)
        pin_len = len(pin)
        pin_block = f"0{pin_len}{pin}".ljust(16, 'F')
        
        # 2. Định dạng PAN Block: 0000 + 12 số của PAN (bỏ check digit)
        # Lấy 12 số tính từ bên trái của số cuối cùng
        clean_pan = pan.replace(" ", "")
        pan_part = clean_pan[-13:-1] if len(clean_pan) >= 13 else clean_pan.zfill(12)
        pan_block = f"0000{pan_part}"

        # 3. Thực hiện XOR giữa PIN Block và PAN Block
        bin_pin = hex_to_bin(pin_block)
        bin_pan = hex_to_bin(pan_block)
        
        xor_result = xor_bits(bin_pin, bin_pan)
        
        return bin_to_hex(xor_result)

    @staticmethod
    def extract_pin(decrypted_hex, pan):
        """Tách PIN gốc từ dữ liệu sau giải mã (Dùng cho Server xác thực)"""
        # Tái tạo lại PAN Block
        clean_pan = pan.replace(" ", "")
        pan_part = clean_pan[-13:-1] if len(clean_pan) >= 13 else clean_pan.zfill(12)
        pan_block = f"0000{pan_part}"
        
        # XOR ngược lại: Decrypted XOR PAN Block -> PIN Block
        bin_decrypted = hex_to_bin(decrypted_hex)
        bin_pan = hex_to_bin(pan_block)
        
        bin_pin_block = xor_bits(bin_decrypted, bin_pan)
        pin_block_hex = bin_to_hex(bin_pin_block)
        
        # Parse PIN từ PIN Block (Format: 0LPPPP...)
        try:
            pin_len = int(pin_block_hex[1])
            extracted_pin = pin_block_hex[2:2+pin_len]
            return extracted_pin
        except:
            return None