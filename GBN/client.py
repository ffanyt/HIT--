import method
import socket
import threading

prot = 1230
address = "127.0.0.1"
target_port = 1231


def client_start():
    # 读取文件
    file = open("./files/client_send.txt", "r")
    recv_path = "./files/client_recv.txt"
    data = file.read()
    file.close()
    # 创建udp socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 绑定
    client_socket.bind((address, prot))
    # 创建GBN对象
    gbn = method.Method()
    # 开启多线程
    # send_thread = threading.Thread(target=gbn.send, args=(client_socket, data, address, target_port))
    # gbn.send(send_socket=client_socket, data=data, target_addr=address, target_port=target_port)
    send_thread = threading.Thread(target=gbn.send,
                                   args=(client_socket, data, address, target_port))  # 从1230端口发送到1231端口
    send_thread.start()
    print("客户端发送成功")
    # gbn.recv(recv_socket=client_socket, target_addr=address, target_port=target_port, path=recv_path)
    client_socket1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket1.bind((address, 1233))
    gbn.recv(recv_socket=client_socket1, target_addr=address, target_port=1232, path=recv_path)
    print("客户端接收成功")


# main
if __name__ == '__main__':
    client_start()
