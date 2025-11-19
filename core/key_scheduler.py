from data.key_tables import PC1, PC2, SHIFT_SCHEDULE
from utils.converters import hex_to_bin, permute

class KeyScheduler:
    @staticmethod
    def generate_subkeys(main_key_hex):
        """Sinh 16 khóa con 48-bit từ khóa chính 64-bit"""
        # Chuyển khóa hex sang nhị phân 64-bit
        bin_key = hex_to_bin(main_key_hex)
        if len(bin_key) != 64:
            bin_key = bin_key.zfill(64)[:64]

        # Hoán vị PC-1 (64 -> 56 bits)
        permuted_key = permute(bin_key, PC1)

        # Chia đôi thành C (28 bits) và D (28 bits)
        c = permuted_key[:28]
        d = permuted_key[28:]

        subkeys = []
        
        # Lặp 16 vòng để tạo 16 khóa con
        for shift in SHIFT_SCHEDULE:
            # Dịch vòng trái (Left Circular Shift)
            c = c[shift:] + c[:shift]
            d = d[shift:] + d[:shift]

            # Ghép C và D, sau đó qua hoán vị PC-2 (56 -> 48 bits)
            cd_merged = c + d
            subkey = permute(cd_merged, PC2)
            subkeys.append(subkey)

        return subkeys