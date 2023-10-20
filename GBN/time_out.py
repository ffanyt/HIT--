import socket
import threading
from time import sleep


class TimeOut(threading.Thread):
    def __init__(self, ack_map: dict, send_package, idx, new_id: int, send_socket: socket, target_addr, target_port, stop_flag, time_out_list):
        super().__init__()
        self.ack_map = ack_map
        self.send_package = send_package
        self.new_id = new_id
        self.send_socket = send_socket
        self.target_addr = target_addr
        self.target_port = target_port
        self.idx = idx
        self.stop_flag = stop_flag
        self.time_out_list = time_out_list

    def run(self):
        try:
            if self.stop_flag:
                return
            sleep(1)
        except Exception as e:
            print(e)
        if self.stop_flag:
            return
        if self.ack_map.get(self.new_id) or self.ack_map.get(self.new_id) is None:
            return
        if not self.ack_map[self.new_id]:
            try:
                # 判断这个分组是否已经被接收
                if self.ack_map[self.new_id] is None or self.ack_map[self.new_id]:
                    return
                print(f"分组{self.idx}超时，重新发送，，该分组序号为： {self.new_id}，数据为： {self.send_package}，此时的ack_map为： {self.ack_map}")
                self.send_socket.sendto(self.send_package, (self.target_addr, self.target_port))
            except Exception as e:
                print("超时重传失败，失败原因：", e)
            time_out_new = TimeOut(self.ack_map, self.send_package, self.idx, self.new_id, self.send_socket, self.target_addr, self.target_port, self.time_out_list)
            time_out_new.start()
            self.time_out_list.append(time_out_new)
            return
        print("timeout类出现异常")

    def set_stop(self):
        self.stop_flag = True
