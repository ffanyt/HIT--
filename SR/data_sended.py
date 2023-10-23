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
            if uid == 66:
                print(f"初始化序号为：{uid}，数据长度为：{len(single_package)},数据为：{single_package}")
            self.single_package = single_package
            self.checksum = self.cal_checksum()
            self.uid = uid
        # self.num_of_id_bytes = num_of_id_bytes

    # def __int__(self, uid: int):
    #     self.uid = uid

    def cal_checksum(self):
        checksum = 0
        len_of_single_cal = 8
        # 需要对self.single_package二进制编码后计算校验和
        bin_of_package = bin(int.from_bytes(self.single_package, byteorder="big"))
        # 在数据结尾加上结束标志帧
        # print("type(bin_of_package):", type(bin_of_package))
        len_of_package = len(bin_of_package) - 2
        # print("输入的数据长度为：", len_of_package)
        # print("以二进制形式打印temp：", bin_of_package)
        # 补0
        if len_of_package % len_of_single_cal != 0:
            bin_of_package += "0" * (len_of_single_cal - len_of_package % len_of_single_cal)
            # print("补0后的数据长度为：", len(bin_of_package))
            # print("补0后的数据为：", bin_of_package)
        j = 0
        # 以十六位为块计算校验和
        for i in range(2, len_of_package, len_of_single_cal):
            # print("第", j, "块的二进制为：", bin_of_package[i:i + len_of_single_cal])
            # 将每个块的十六位转换为十进制
            block = int(bin_of_package[i:i + len_of_single_cal], 2)
            # print("第", j, "块的十进制为：", block)
            # 将每个块的十六位相加
            checksum += block
            # print("第", j, "块的十进制相加结果为：", checksum)
            j += 1
            # 若相加结果超过len_of_single_cal位，则将溢出的高位加到低位
            if checksum > 0xff:
                checksum = (checksum & 0xff) + 1
        # 将十六位的结果取反，并以无符号整数形式返回
        # print("校验和为：", checksum)
        # print("校验和后：", ~checksum)
        checksum = ~checksum & 0xff
        # print("取反后的无符号校验和为：", checksum)
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
        # print(f"发送数据序号为： {self.uid}，序号长度为： {len(id_bytes)}，校验和长度为： {len(checksum_bytes)}，数据长度为： {len(self.single_package)}，发送的数据长度为： {len(full_data)}")
        # print("发送的数据为：", full_data)
        # 将校验和和id拼接到数据后面
        return full_data

    @staticmethod
    def unpackage(full_data):
        if full_data is None:
            return None, None, None
        if len(full_data) < 3:
            got_id = full_data[0]
            return got_id, None, None
        got_id = full_data[0]
        # got_id = int.from_bytes(got_id, byteorder="big")
        got_checksum = full_data[1]
        got_data = full_data[2: -1]
        # got_data = got_data.decode()
        return got_id, got_checksum, got_data

    # 检查数据
    # 这个函数是static的
    @staticmethod
    def check(full_data, len_of_single_cal=8):
        # 取到full_data的校验和
        get_checksum = full_data[1]
        # print("接收到的校验和为：", get_checksum)
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
            # print("第", j, "块的二进制为：", bin_of_package[i:i + len_of_single_cal])
            # 将每个块的十六位转换为十进制
            block = int(bin_of_package[i:i + len_of_single_cal], 2)
            # print("第", j, "块的十进制为：", block)
            # 将每个块的十六位相加
            checksum += block
            # print("第", j, "块的十进制相加结果为：", checksum)
            # j += 1
            # 若相加结果超过len_of_single_cal位，则将溢出的高位加到低位
            if checksum > 0xff:
                checksum = (checksum & 0xff) + 1
        # 将十六位的结果取反，并以无符号整数形式返回
        # print("校验和为：", checksum)
        # get_checksum = int(get_checksum.decode())
        if get_checksum + checksum == 0xff:
            return True
        else:
            get_checksum = full_data[1]
            data = full_data[2:-1]
            checksum = 0
            bin_of_package = bin(int.from_bytes(data, byteorder="big"))
            len_of_package = len(bin_of_package) - 2
            print("校验和错误")
            print("get_checksum: ", get_checksum)
            print("data: ", data)
            print("bin_of_package: ", bin_of_package)
            print("len_of_package: ", len_of_package)
            if len_of_package % len_of_single_cal != 0:
                print(f"需要补{len_of_single_cal - len_of_package % len_of_single_cal}个0，因为len_of_package % len_of_single_cal = {len_of_package % len_of_single_cal}")
                bin_of_package += "0" * (len_of_single_cal - len_of_package % len_of_single_cal)
            # print("校验和错误, get_checksum: ", get_checksum, "checksum: ", checksum)
            # print(f"校验和错误, get_checksum: {get_checksum}, checksum: {checksum}\ndata：{data}\nbin_of_package: {bin_of_package}\nlen_of_package: {len_of_package}\nlen_of_single_cal: {len_of_single_cal}")
            j = 1
            for i in range(2, len_of_package, len_of_single_cal):
                # print("第", j, "块的二进制为：", bin_of_package[i:i + len_of_single_cal])
                # 将每个块的十六位转换为十进制
                print("第", j, "块的二进制为：", bin_of_package[i:i + len_of_single_cal])
                block = int(bin_of_package[i:i + len_of_single_cal], 2)
                print("第", j, "块的十进制为：", block)
                # print("第", j, "块的十进制为：", block)
                # 将每个块的十六位相加
                checksum += block
                print("第", j, "块的十进制相加结果为：", checksum)
                # print("第", j, "块的十进制相加结果为：", checksum)
                j += 1
                # 若相加结果超过len_of_single_cal位，则将溢出的高位加到低位
                if checksum > 0xff:
                    print("溢出了")
                    checksum = (checksum & 0xff) + 1
            print("校验和为：", checksum)
            return False
