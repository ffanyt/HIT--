import method
import socket

prot = 1231
address = "127.0.0.1"
target_port = 1230

def server_start():
    # 读取文件
    # file = open("./client_send.txt", "r")
    # data = file.read()
    # file.close()
    # 创建udp socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((address, prot))
    recv_path = "./server_recv.txt"
    # 创建GBN对象
    gbn = method.Method()
    gbn.recv(recv_socket=server_socket, target_addr=address, target_port=target_port, path=recv_path)


# main
if __name__ == '__main__':
    server_start()
