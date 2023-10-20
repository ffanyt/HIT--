import socket
import data_sended
import time_out
import RevACK


class Method:
    send_window = 5
    recv_window = 2
    # 单个分组大小
    packet_size = 32
    # 序号的比特数
    seq_bits = 32

    def send(self, send_socket: socket, data, target_addr: str, target_port: int):
        time_out_list = []
        base_idx = 0
        next_idx = 0
        end_flag = False
        data = data.encode("utf-8")
        print(f"该数据总长度为： {len(data)}")
        # 分割数据
        data = [data[i:i + self.packet_size] for i in range(0, len(data), self.packet_size)]
        num_of_packets = len(data)
        ack_map = {}
        print(f"分组内数据的大小为： {self.packet_size}字节，分为{len(data)}个分组发送")
        stop_flag = False
        if len(data) != 0:
            rev = RevACK.RevAck(send_socket, ack_map, stop_flag)
            rev.start()
        end_end_flag = False
        while next_idx <= num_of_packets or len(ack_map) > 0:
            if len(data) == 0:
                break
            old_base = base_idx
            old_size = len(ack_map)
            # print(f"现在对窗口进行更新，当前窗口起点为： {base_idx}，next_point为： {next_idx}，此时的ack_map为： {ack_map}")
            for i in range(old_size):
                idx = (old_base + i + 1) % 256
                # 检查ack_map是否有idx的键值对
                if ack_map.get(idx) is None:
                    print(f"ack_map中没有{idx}这个键值对，跳过")
                    # break
                if ack_map[idx] is False:
                    break
                base_idx += 1
                # next_idx += 1
                ack_map.pop(idx)
                if end_flag and len(ack_map) == 0 and base_idx == len(data):
                    end_end_flag = True
                    break
            if end_end_flag:
                print("所有的发送数据都被接收完成")
                rev.set_stop()
                # 等待线程结束
                rev.join()
                # print("test")
                break
            ack_num = base_idx + len(ack_map)
            i = 1
            # print(f"即将发送下一个窗口，当前窗口起点为： {base_idx}，next_point为： {next_idx}，此时的ack_map为： {ack_map}")
            while next_idx - base_idx < self.send_window and next_idx < num_of_packets:
                # if rev.is_alive():
                    # print("testtest111")
                    # print(rev.getName())
                if next_idx > num_of_packets:
                    break
                new_id = (ack_num + i) % 256
                i += 1
                send_data = data_sended.Data(data[next_idx], new_id)
                send_package = send_data.package()
                unpacked_data = data_sended.Data.unpackage(send_package)
                send_socket.sendto(send_package, (target_addr, target_port))
                print(f"发送分组{next_idx}，序号为{new_id}，打包前数据为： {data[next_idx]}，但打包后为：{send_package},此时的ack_map为： {ack_map}")
                # if new_id == 66:
                #     print(f"发送分组{next_idx}，序号为{new_id}，发送数据打包前长度为：{len(data[next_idx])}，发送的数据打包后长度为：{len(send_package)}")
                ack_map[new_id] = False
                time_out_new = time_out.TimeOut(ack_map, send_package, next_idx, new_id, send_socket, target_addr, target_port, stop_flag, time_out_list)
                time_out_new.start()
                time_out_list.append(time_out_new)
                next_idx += 1
                end_flag = True
                # 开始计时
        print("发送完成，退出")

        return

    def recv(self, recv_socket: socket, target_addr: str, target_port: int, path: str):
        rec_idx_arr = []
        rec_data_map = {}
        all_data = b""
        base_idx = 1
        # next_idx = 0
        max_idx = base_idx + self.recv_window - 1
        while True:
            # 接收数据
            try:
                recv_package, recv_addr = recv_socket.recvfrom(self.packet_size + 3)
            except Exception as e:
                print("接收完成，退出，退出原因：", e)
                with open(path, "wb") as f:
                    f.write(all_data)
                f.close()
                break
            addr_send = recv_addr[0]
            port_send = recv_addr[1]
            # print(f"接收到的数据为： {recv_package}")
            # 解析数据
            # print(f"接收到的数据长度为： {len(recv_package)}")
            recv_data_unpackage = data_sended.Data.unpackage(recv_package)
            # print(f"接收到的数据解析后为： {recv_data_unpackage}")
            # 检查校验和
            if not data_sended.Data.check(recv_package):
                print("校验和错误")
                continue
            # 分解data
            recv_id, recv_checksum, recv_data = recv_data_unpackage
            # 检查序号，若为期待的序号，则将数据存入字典
            if recv_id < base_idx:

                ack = data_sended.Data(None, recv_id)
                ack = ack.package()
                recv_socket.sendto(ack, (target_addr, target_port))
                print(f"该数据{recv_id}已经被接收，丢弃，base_idx为： {base_idx}，重新发送ack: {ack}")
                continue
            if recv_id > max_idx:
                print(f"该数据{recv_id}之前数据未被接收，丢弃，此时的rev_idx_arr为： {recv_id}，max_idx为： {max_idx}")
                # ack = data_sended.Data(None, recv_id)
                # ack = ack.package()
                # recv_socket.sendto(ack, (target_addr, target_port))
                continue
            # 检查序号是否已经被接收
            if recv_id in rec_idx_arr:
                print(f"该数据{recv_id}已经被接收，丢弃")
                # ack = data_sended.Data(None, recv_id)
                # ack = ack.package()
                # recv_socket.sendto(ack, (target_addr, target_port))
                continue
            # 检查是否为期待的分组
            rec_idx_arr.append(recv_id)
            rec_data_map[recv_id] = recv_data
            # 发送ack
            ack_int = data_sended.Data(None, recv_id)
            ack = ack_int.package()
            recv_socket.sendto(ack, (target_addr, target_port))
            print(f"发送ack_int： {ack_int.uid}, ack:{ack}")
            # 检查窗口是否可以滑动
            for i in range(self.recv_window):
                idx = base_idx + i
                if idx not in rec_idx_arr:
                    break
                all_data += rec_data_map[idx]
                rec_idx_arr.remove(idx)
                base_idx += 1
                max_idx = base_idx + self.recv_window - 1
        print("接收完成，退出")

