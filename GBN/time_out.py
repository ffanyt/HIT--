import socket
import threading
from time import sleep


class TimeOut(threading.Thread):
    def __init__(self, ack_map: dict, send_packages, idx, new_id: int, send_socket: socket, target_addr, target_port, stop_flag, time_out_list, len_of_package, send_window):
        super().__init__()
        self.ack_map = ack_map
        self.send_packages = send_packages
        self.new_id = new_id
        self.send_socket = send_socket
        self.target_addr = target_addr
        self.target_port = target_port
        self.idx = idx
        self.stop_flag = stop_flag
        self.time_out_list = time_out_list
        self.len_of_package = len_of_package
        self.send_window = send_window

    def run(self):
        try:
            if self.stop_flag:
                return
            sleep(1)
        except Exception as e:
            print(e)
        if self.stop_flag:
            return
        flag = False
        for i in range(self.send_window):
            if self.ack_map.get(self.new_id + i) is None or self.ack_map.get(self.new_id + i):
                continue
            else:
                flag = True
                break
        if not flag:
            return
        # if self.ack_map.get(self.new_id) or self.ack_map.get(self.new_id) is None:
        #     return
        try:
            print("准备超时重传，此时的ack_map为： ", self.ack_map, "，此时的base id为： ", self.new_id, "此时的window为： ", self.send_window)
            # print("type(self.send_packages): ", type(self.send_packages))
            print("len", len(self.send_packages))
            time_out_send_ids = []
            for i in range(self.send_window):
                # print("i: ", i)
                print("self.new_id + i: ", self.new_id + i)
                print(self.ack_map.get(self.new_id + i))
                if self.ack_map.get(self.new_id + i) is None:
                    continue
                if not self.ack_map.get(self.new_id + i):
                    print("超时重传，重传的分组序号为： ", self.new_id + i)
                    send_package = self.send_packages[i]
                    # print("send_package: ", send_package)
                    # 转换为bytes类型
                    # send_package = send_package.encode("utf-8")
                    # print("type(send_package): ", type(send_package))
                    self.send_socket.sendto(send_package, (self.target_addr, self.target_port))
                    time_out_send_ids.append(self.new_id + i)
                    # print(
                    #     f"分组{self.idx}超时，重新发送，，该分组序号为： {self.new_id}，数据为： {self.send_packages}，此时的ack_map为： {self.ack_map}")
            print(f"分组{self.idx}超时，重新发送，，该分组序号为： {time_out_send_ids}，数据为： {self.send_packages}，此时的ack_map为： {self.ack_map}")
        except Exception as e:
            print("超时重传失败，失败原因：", e)
        time_out_new = TimeOut(self.ack_map, self.send_packages, self.idx, self.new_id, self.send_socket,
                               self.target_addr, self.target_port, self.stop_flag, self.time_out_list,
                               self.len_of_package, self.send_window)
        time_out_new.start()
        self.time_out_list.append(time_out_new)
        return

    def set_stop(self):
        self.stop_flag = True
