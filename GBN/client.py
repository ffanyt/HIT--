import method
import socket
prot = 1230
address = "127.0.0.1"
target_port = 1231

def client_start ():
    # 读取文件
    file = open("./client_send.txt", "r")
    data = file.read()
    file.close()
    # 创建udp socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 绑定
    client_socket.bind((address, prot))
    # 创建GBN对象
    gbn = method.Method()
    gbn.send(send_socket=client_socket, data=data, target_addr=address, target_port=target_port)
    print("发送成功")


# main
if __name__ == '__main__':
    client_start()