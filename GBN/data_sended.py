class Data:
    # static常量
    num_of_id_bytes = 2

    def __init__(self, single_package, uid: int):
        if single_package is None:
            self.uid = uid
            self.checksum = None
            self.single_package = None
        else:
            if type(single_package) is not bytes:
                single_package = single_package.encode()
            # 计算校验和
            self.single_package = single_package
            self.checksum = self.cal_checksum()
            self.uid = uid

    def cal_checksum(self):
        checksum = 0
        len_of_single_cal = 8
        # 需要对self.single_package二进制编码后计算校验和
        bin_of_package = bin(int.from_bytes(self.single_package, byteorder="big"))
        len_of_package = len(bin_of_package) - 2
        # 补0
        if len_of_package % len_of_single_cal != 0:
            bin_of_package += "0" * (len_of_single_cal - len_of_package % len_of_single_cal)
        j = 0
        for i in range(2, len_of_package, len_of_single_cal): # 从2开始，因为前两位是0b
            block = int(bin_of_package[i:i + len_of_single_cal], 2) # 将每个块的八位转换为十进制
            checksum += block
            j += 1
            # 若相加结果超过len_of_single_cal位，则将溢出的高位加到低位
            if checksum > 0xff:
                checksum = (checksum & 0xff) + 1
        # 将结果取反，并以无符号整数形式返回
        checksum = ~checksum & 0xff
        return checksum

    def package(self):
        if self.checksum is None or self.single_package is None:
            ack = self.uid.to_bytes(1, "big") + b'0'
            return ack
        # 把校验和从数字形式转换为bytes
        checksum_bytes = self.checksum.to_bytes(1, byteorder="big")
        # print("校验和为：", checksum_bytes)
        id_bytes = self.uid.to_bytes(1, byteorder="big")
        # print("id为：", id_bytes)
        # 将校验和和id拼接到数据后面
        full_data = id_bytes + checksum_bytes + self.single_package + b"0"
        # 将校验和和id拼接到数据后面
        return full_data

    @staticmethod
    def unpackage(full_data):
        if full_data is None: # 如果没有数据
            return None, None, None
        if len(full_data) < 3: # 如果数据长度小于3
            got_id = full_data[0]
            return got_id, None, None
        got_id = full_data[0] # 取到id
        got_checksum = full_data[1] # 取到校验和
        got_data = full_data[2: -1] # 取到数据
        return got_id, got_checksum, got_data

    # 检查数据
    # 这个函数是static的
    @staticmethod
    def check(full_data, len_of_single_cal=8):
        # 取到full_data的校验和
        get_checksum = full_data[1]
        # 取到full_data的数据
        data = full_data[2:-1]
        # print("接收到的数据为：", data)
        # 计算校验和
        checksum = 0
        bin_of_package = bin(int.from_bytes(data, byteorder="big"))
        len_of_package = len(bin_of_package) - 2
        if len_of_package % len_of_single_cal != 0:
            bin_of_package += "0" * (len_of_single_cal - len_of_package % len_of_single_cal)
        for i in range(2, len_of_package, len_of_single_cal):
            block = int(bin_of_package[i:i + len_of_single_cal], 2)
            checksum += block
            # 若相加结果超过len_of_single_cal位，则将溢出的高位加到低位
            if checksum > 0xff:
                checksum = (checksum & 0xff) + 1
        if get_checksum + checksum == 0xff: # 如果校验和正确
            return True
        else: # 如果校验和错误
            print("校验和错误")
            return False
