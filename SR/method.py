import socket
import data_sended
import time_out
import RevACK
import random

loss = 0.5


class Method:
    send_window = 5
    recv_window = 2
    # 单个分组大小
    packet_size = 512
    # 序号的比特数
    seq_bits = 512

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
            # 启动接收线程
            rev = RevACK.RevAck(send_socket, ack_map, stop_flag, len(data))
            rev.start()
        end_end_flag = False
        # 发送数据
        while next_idx < num_of_packets or len(ack_map) > 0:
            if len(data) == 0:
                break
            old_base = base_idx
            old_size = len(ack_map)
            # 检查ack_map中的键值对，如果值为True，则将键值对删除
            for i in range(old_size):
                idx = (old_base + i + 1) % 256
                # 检查ack_map是否有idx的键值对
                if ack_map.get(idx) is None:
                    print(f"ack_map中没有{idx}这个键值对，跳过")
                    # break
                if ack_map[idx] is False:
                    break
                base_idx += 1
                ack_map.pop(idx)
                if end_flag and len(ack_map) == 0 and base_idx == len(data):
                    end_end_flag = True
                    break
            # 检查是否发送完毕
            if end_end_flag:
                print("所有的发送数据都被接收完成")
                rev.set_stop()
                # 等待线程结束
                rev.join()
                # print("test")
                break
            # 检查是否可以发送下一个窗口
            ack_num = base_idx + len(ack_map)
            i = 1
            while next_idx - base_idx < self.send_window and next_idx < num_of_packets:
                if next_idx > num_of_packets:
                    break
                new_id = (ack_num + i) % 256
                i += 1
                send_data = data_sended.Data(data[next_idx], new_id)
                send_package = send_data.package()
                unpacked_data = data_sended.Data.unpackage(send_package)
                # 设置概率丢包，丢包则不发送，但是要设置超时，超时后重发，直到收到ack，才发送下一个分组，否则一直重发
                # 设置随机变量
                rand = random.random()
                if rand > loss:
                    send_socket.sendto(send_package, (target_addr, target_port))
                else:
                    print(f"丢包，序号为{new_id}，数据为： {data[next_idx]}")
                print(
                    f"发送分组{next_idx}，序号为{new_id}，打包前数据为： {data[next_idx]}，但打包后为：{send_package},此时的ack_map为： {ack_map}")
                ack_map[new_id] = False # 将新的键值对加入ack_map
                # 启动超时线程
                time_out_new = time_out.TimeOut(ack_map, send_package, next_idx, new_id, send_socket, target_addr,
                                                target_port, stop_flag, time_out_list)
                time_out_new.start()
                time_out_list.append(time_out_new)
                next_idx += 1
                end_flag = True
        print("发送完成，退出")

        return

    def recv(self, recv_socket: socket, target_addr: str, target_port: int, path: str):
        time_max = 15
        recv_socket.settimeout(time_max)
        rec_idx_arr = []
        rec_data_map = {}
        all_data = b""
        base_idx = 1
        # next_idx = 0
        max_idx = base_idx + self.recv_window - 1
        # 准备写入文件
        f = open(path, "wb")
        print("开始接收")
        while True:
            # 接收数据
            try:
                recv_package, recv_addr = recv_socket.recvfrom(self.packet_size + 3) # 接收数据
            except Exception as e:
                print("接收完成，退出")
                with open(path, "wb") as f:
                    f.write(all_data)
                f.close()
                break
            addr_send = recv_addr[0] # 发送方的地址
            port_send = recv_addr[1] # 发送方的端口
            recv_data_unpackage = data_sended.Data.unpackage(recv_package)
            # 检查校验和
            if not data_sended.Data.check(recv_package): # 如果校验和错误，丢弃该分组
                print("校验和错误")
                continue
            # 分解data
            recv_id, recv_checksum, recv_data = recv_data_unpackage
            # 检查序号，若为期待的序号，则将数据存入字典
            if recv_id < base_idx: # 如果序号小于base_idx，说明该数据已经被接收，丢弃
                ack = data_sended.Data(None, recv_id)
                ack_package = ack.package()
                recv_socket.sendto(ack_package, (addr_send, port_send))
                print(f"该数据{recv_id}已经被接收，丢弃，base_idx为： {base_idx}，重新发送ack: {ack.uid}")
                continue
            if recv_id > max_idx: # 如果序号大于max_idx，说明该数据之前的数据还没有被接收，丢弃
                print(f"该数据{recv_id}之前数据未被接收，丢弃，此时的rev_idx_arr为： {recv_id}，max_idx为： {max_idx}")
                continue
            # 检查序号是否已经被接收
            if recv_id in rec_idx_arr:
                print(f"该数据{recv_id}已经被接收，丢弃")
                ack = data_sended.Data(None, recv_id)
                ack = ack.package()
                recv_socket.sendto(ack, (addr_send, port_send))
                continue
            # 将数据存入字典
            rec_idx_arr.append(recv_id)
            rec_data_map[recv_id] = recv_data
            # 发送ack
            ack_int = data_sended.Data(None, recv_id)
            ack = ack_int.package()
            rand = random.random()
            if rand > loss:
                recv_socket.sendto(ack, (addr_send, port_send))
            else:
                print(f"丢包，序号为{recv_id}")
            print(f"发送ack_int： {ack_int.uid}, ack:{ack}，接收的数据为： {recv_data}")
            # 检查窗口是否可以滑动
            print("此时的rec_idx_arr为：", rec_idx_arr, "此时的base_idx为：", base_idx, "此时的max_idx为：", max_idx)
            if base_idx in rec_idx_arr: # 如果base_idx在rec_idx_arr中，说明base_idx的数据都已经接收到了
                temp_base_idx = base_idx # 保存base_idx
                for i in range(self.recv_window): # 滑动窗口
                    idx = temp_base_idx + i
                    if idx not in rec_idx_arr: # 如果idx不在rec_idx_arr中，说明idx的数据还没有接收到，不能滑动窗口
                        break
                    all_data += rec_data_map[idx] # 将数据写入文件
                    rec_idx_arr.remove(idx) # 将idx从rec_idx_arr中删除
                    base_idx += 1 # base_idx向前移动
                    max_idx = base_idx + self.recv_window - 1 # 更新max_idx
