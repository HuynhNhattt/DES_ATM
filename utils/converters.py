def hex_to_bin(hex_str):
    """Chuyển chuỗi Hex sang chuỗi Nhị phân (Binary String)"""
    # Tính độ dài bit cần thiết (1 ký tự hex = 4 bit)
    num_bits = len(hex_str) * 4
    # Chuyển sang int hệ 16, sau đó sang bin, cắt bỏ '0b' và padding số 0
    return bin(int(hex_str, 16))[2:].zfill(num_bits)

def bin_to_hex(bin_str):
    """Chuyển chuỗi Nhị phân sang chuỗi Hex (Viết hoa)"""
    # Chuyển sang int hệ 2, sau đó sang hex, cắt bỏ '0x', viết hoa
    hex_str = hex(int(bin_str, 2))[2:].upper()
    # Đảm bảo độ dài chẵn (padding 0 nếu cần)
    if len(hex_str) % 2 != 0:
        hex_str = '0' + hex_str
    return hex_str

def permute(input_bits, table):
    """Thực hiện hoán vị các bit dựa trên bảng tra (Table)"""
    # Lưu ý: Bảng DES thường đánh số từ 1, Python index từ 0
    output_bits = ""
    for position in table:
        output_bits += input_bits[position - 1]
    return output_bits

def xor_bits(bits1, bits2):
    """Thực hiện phép XOR giữa 2 chuỗi bit có cùng độ dài"""
    return ''.join('1' if b1 != b2 else '0' for b1, b2 in zip(bits1, bits2))

def int_to_bin(number, width):
    """Chuyển số nguyên sang chuỗi nhị phân với độ dài cố định"""
    return format(number, f'0{width}b')

def text_to_hex(text):
    """Chuyển văn bản ASCII sang Hex (Dùng cho debug nếu cần)"""
    return text.encode('utf-8').hex().upper()