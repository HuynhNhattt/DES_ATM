from data.permutations import IP, FP, E_TABLE, P_BOX
from data.s_boxes import S_BOXES
from utils.converters import hex_to_bin, bin_to_hex, permute, xor_bits, int_to_bin

class DES_Logic:
    def _f_function(self, right_half, subkey):
        """Hàm F: Mở rộng -> XOR Key -> S-Box -> P-Box"""
        # 1. Mở rộng 32 bit lên 48 bit
        expanded_r = permute(right_half, E_TABLE)

        # 2. XOR với khóa con
        xored = xor_bits(expanded_r, subkey)

        # 3. Thay thế qua 8 S-Boxes
        s_box_output = ""
        for i in range(8):
            chunk = xored[i*6 : (i+1)*6]
            row = int(chunk[0] + chunk[5], 2)
            col = int(chunk[1:5], 2)
            val = S_BOXES[i][row][col]
            s_box_output += int_to_bin(val, 4)

        # 4. Hoán vị P
        return permute(s_box_output, P_BOX)

    def run_des_block(self, data_hex, subkeys, is_decrypt=False):
        """
        Thực hiện mã hóa/giải mã và TRẢ VỀ LOG CHI TIẾT (Trace)
        Output: (cipher_hex, trace_logs)
        """
        trace_logs = [] # Danh sách lưu trạng thái từng vòng
        
        data_bin = hex_to_bin(data_hex)
        if len(data_bin) != 64:
            raise ValueError("Input data must be 64-bit hex string")

        # 1. Hoán vị khởi tạo (IP)
        ip_data = permute(data_bin, IP)
        l, r = ip_data[:32], ip_data[32:]

        # Log trạng thái ban đầu
        trace_logs.append(f"INIT IP: L0={bin_to_hex(l)} | R0={bin_to_hex(r)}")

        # Xác định thứ tự khóa (Mã hóa: Xuôi, Giải mã: Ngược)
        keys = subkeys[::-1] if is_decrypt else subkeys

        # 2. Mạng Feistel 16 vòng
        for i in range(16):
            l_prev, r_prev = l, r
            
            # L(i) = R(i-1)
            l = r_prev
            
            # R(i) = L(i-1) XOR F(R(i-1), K(i))
            f_out = self._f_function(r_prev, keys[i])
            r = xor_bits(l_prev, f_out)

            # Ghi log chi tiết cho mỗi vòng (chỉ ghi khi Mã hóa để đỡ rối)
            if not is_decrypt:
                round_key = bin_to_hex(keys[i])
                trace_logs.append(f"R{i+1:02d} | K: {round_key} | L: {bin_to_hex(l)} | R: {bin_to_hex(r)}")

        # 3. Swap cuối cùng (R16, L16)
        final_pair = r + l 

        # 4. Hoán vị kết thúc (FP)
        cipher_bin = permute(final_pair, FP)
        cipher_hex = bin_to_hex(cipher_bin)
        
        return cipher_hex, trace_logs