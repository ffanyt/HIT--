# README
代码由python完成

本代码为哈工大计算机网络实验二

实现了停-等协议、GBN协议和SR协议，并实现了全双工的文件传输，超时重传、校验和检验、滑动窗口、接收ACK等功能经测试均正常

博客内有更完善的信息，且如有问题请在blog下评论，blog地址：https://yutao.love/archives/ji-suan-ji-wang-luo-shi-yan-er

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