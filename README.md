# README

**代码仅供学习交流**

代码由python完成，有根据某项目进行参考，部分直接用python重写，但是很遗憾现在无法找到项目地址

本代码为哈工大计算机网络实验二

实现了停-等协议、GBN协议和SR协议，并实现了全双工的文件传输，超时重传、校验和检验、滑动窗口、接收ACK等功能经测试均正常



## 代码结构

server.py为服务端代码

client.py为客户端代码

method.py为客户端和服务端共用的方法

data_sended.py内为数据打包解包、计算校验和、检查校验和功能

time_out.py内为计时器功能

RevACK.py为接收ACK的功能

## 运行方式

只需运行server.py和client.py即可

需保证在`./files`文件夹下有`client_send.txt`和`server_send.txt`'文件
