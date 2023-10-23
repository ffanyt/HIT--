import socket
import threading
import data_sended


class RevAck(threading.Thread):
    def __init__(self, socket1: socket, ackMap: dict, stop_flag: bool, len_of_data: int):
        super().__init__()
        self.socket1 = socket1
        self.socket1.settimeout(3)
        self.ackMap = ackMap
        self.stop_flag = stop_flag
        self.len_of_data = len_of_data
        self.count = 0
        # self.packet_size = packet_size

    def run(self):
        # if self.stop_flag:
        #     return
        end_flag = False  # end_flag是防止ackMap为空时，线程提前结束，因为发送前ackMap为空。
        # 而当接收socket收到数据时，意味着客户端已经开始发数据了，可以让end_flag为True，通过ackMap为空来判断是否结束。
        recv_size = 2
        while True:
            # print("接收线程正在进行")
            if self.stop_flag:
                # print("接收线程结束")
                return
            # if len(self.ackMap) == 0 and end_flag:
            #     break
            data = None
            if end_flag and len(self.ackMap) == 0:
                # print("接收线程结束")
                break
            # 以固定长度接收数据
            # data, addr = self.socket1.recvfrom(self.packet_size)
            # 创建对象，接收固定长度的数据包
            try:
                data, addr = self.socket1.recvfrom(recv_size)
            except Exception as e:
                pass
                # print("ACK接收完成，异常为：", e)
                # print(e)
            ack = data_sended.Data.unpackage(data)
            ack_id = ack[0]
            if ack_id is not None:
                end_flag = True
            # print(f"接收到ACK序号为： {ack}，接收后的ackMap为： {self.ackMap}")
            if self.ackMap.get(ack_id) is not None:
                if self.ackMap[ack_id] is False:
                    self.ackMap[ack_id] = True
                    self.count += 1
                    print(f"接收到ACK序号为： {ack_id}，接收后的ackMap为： {self.ackMap}")
                else:
                    print(f"接收到ACK序号为： {ack_id}，但是该分组已经被接收过了，此时的ackMap为： {self.ackMap}")
            else:
                if ack_id is not None:
                    print(f"接收到ACK序号为： {ack_id}，但是此时的ackMap为： {self.ackMap}，不需要这个接收序号，丢弃")
            if len(self.ackMap) == 0 and end_flag and self.count == self.len_of_data:
                print("接收线程结束")
                return

    def set_stop(self):
        # print("设置接收线程结束标志")
        self.stop_flag = True
