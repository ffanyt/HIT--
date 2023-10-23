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
    # 开启多线程
    # gbn.send(send_socket=server_socket, data=data, target_addr=address, target_port=target_port)
    # recv_thread = gbn.recv(recv_socket=server_socket, target_addr=address, target_port=target_port, path=recv_path) #从1231端口接收，发送ack到对方1230端口
    # recv_thread.start()
    # 开多线程
    recv_thread = threading.Thread(target=gbn.recv, args=(server_socket, address, 1230, recv_path))
    recv_thread.start()
    # gbn.recv(recv_socket=server_socket, target_addr=address, target_port=target_port, path=recv_path)
    print("服务端接收成功")
    server_socket1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket1.bind((address, 1232))
    gbn.send(send_socket=server_socket1, data=data, target_addr=address, target_port=1233)
    print("服务端发送成功")


# main
if __name__ == '__main__':
    server_start()
