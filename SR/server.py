import method
import socket
import threading

prot = 1231
address = "127.0.0.1"
target_port = 1230

def server_start():
    # 读取文件
    file = open("files/server_send.txt", "r")
    data = file.read()
    file.close()
    # 创建udp socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((address, prot))
    recv_path = "files/server_recv.txt"
    # 创建GBN对象
    gbn = method.Method()
    # 开多线程
    recv_thread = threading.Thread(target=gbn.recv, args=(server_socket, address, 1230, recv_path))
    recv_thread.start()
    server_socket1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket1.bind((address, 1232))
    # 发送数据
    gbn.send(send_socket=server_socket1, data=data, target_addr=address, target_port=1233)
    print("服务器收发完成")


# main
if __name__ == '__main__':
    server_start()
