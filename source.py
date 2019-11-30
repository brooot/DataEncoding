#encoding=utf-8
import sys, time, os, random
from socket import *
from Xor import *
from choose_data import *
from multiprocessing import *


sockfd = socket(AF_INET, SOCK_DGRAM)
# 设置id地址和端口号
# IP = "127.0.0.1"
# PORT = 6661
# self_ADDR = (IP, PORT)
# # 绑定自身地址和端口号
# sockfd.bind(self_ADDR)

# 目的地址列表
Dest_ADDR = [
                ("127.0.0.1", 7000),
                ("127.0.0.1", 8000),
                # ("127.0.0.1", 7773),
                # ("127.0.0.1", 7774),
            ]

# m_info = '1@2@23'
# message =  m_info + '##' +  source_data[0]

manager = Manager()  # 管理进程间共享的变量

while True:
    encoded_data = []
    # 发送数据
    # if m == 's':
    # send_message(message)
    # data_coding(source_data, m)
    # # print(encoded_data)
    # send_message(encoded_data)
    k = int(input("请输入发送分段的大小："))
    if k > 1000:
        print("请输入一个最大为1000的数!")
        continue

    # 根据分段的个数k, 确定度的概率分布
    p = get_degree_distribution(k)
    for i in range(3):
        print("%ds 后开始发送数据" % (3-i))
        time.sleep(1)

    print("sending...\n")

    # 记录已经确认解码的邻居的列表
    ack_neighbor = manager.list()

    still_need_sending = Value('i', True)
    # 创建分支进程
    pid = os.fork()
    # 创建进程出错
    if pid < 0:
        print("创建进程出错.")
        break
    # 如果是新的进程,让其监听接收端发来的 ack 信息
    elif pid == 0:
        while still_need_sending.value:
            data, addr = sockfd.recvfrom(1024)
            if data.decode() == "ok":
                if addr not in ack_neighbor:
                    print("\n---------------------------\n收到",addr,"的ack\n---------------------------\n")
                    ack_neighbor.append(addr)
                    sockfd.sendto("got_it".encode(),addr)
                else:
                    print("重复收到来自", addr, "的ack")
            else:
                print("主机 %s 发来消息：%s" % (addr, data.decode()))
        os._exit(0)
    # 是原来的主进程,则不断的发送编码信息,直到所有的接收端都解码
    else:
        while still_need_sending.value:
            for neighbor in Dest_ADDR:
                if len(ack_neighbor) < len(Dest_ADDR):
                    encoded_Data = get_encoded_data(k, p)
                    # time.sleep(0.1)
                    sockfd.sendto(encoded_Data, neighbor)
                else:
                    still_need_sending.value = False
                    break
        print("\n---------------------------\n接收方已经全部解码完成!\n\n")
        break
    # _pid, _status = os.wait()
    # print("子进程的id号是: ", _pid)
    # print("退出状态是:",_status)

    # 需要开启多个进程来接收数据,当数据发送过快的时候,需要解码的时间,不能及时地接收数据
