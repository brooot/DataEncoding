#encoding=utf-8
import sys, time, os, random
from socket import *
from Xor import *
from choose_data import *
from multiprocessing import *
from config import *


sockfd = socket(AF_INET, SOCK_DGRAM)
# 设置id地址和端口号
# IP = "127.0.0.1"
# PORT = 6661
# self_ADDR = (IP, PORT)
# # 绑定自身地址和端口号
# sockfd.bind(self_ADDR)

# 目的地址列表
Dest_ADDR = [
                # ("10.1.18.79", 7000),
                ("10.1.18.44", 8000),
                # ("127.0.0.1", 9000),
                # ("127.0.0.1", 7774),
            ]

# m_info = '1@2@23'
# message =  m_info + '##' +  source_data[0]

manager = Manager()  # 管理进程间共享的变量

while True:
    send_num = 0
    # k = int(input("请输入发送分段的大小："))
    # if k > 1000:
    #     print("请输入一个最大为1000的数!")
    #     continue
    # subsection_num = k
    print("发送分段大小为: ", subsection_num)

    # 根据分段的个数k, 确定度的概率分布
    p = get_degree_distribution(subsection_num)
    for i in range(3):
        print("%ds 后开始发送数据" % (3-i))
        time.sleep(1)



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
                print("\n---------------------------\n收到",addr,"的ack\n---------------------------\n")
                if addr not in ack_neighbor:
                    ack_neighbor.append(addr)
                    if len(ack_neighbor) == len(Dest_ADDR):
                        still_need_sending.value = False
                sockfd.sendto("got_it".encode(),addr)
            
            else:
                print("主机 %s 发来消息：%s" % (addr, data.decode()))
        os._exit(1)
    # 是原来的主进程,则不断的发送编码信息,直到所有的接收端都解码
    else:
        t_begin = time.time()
        while still_need_sending.value:
            for neighbor in Dest_ADDR:
                if len(ack_neighbor) < len(Dest_ADDR) :
                    if neighbor not in ack_neighbor:
                        encoded_Data = get_encoded_data(subsection_num, p)
                        send_num += 1
                        time.sleep(send_delay)
                        sockfd.sendto(encoded_Data, neighbor)
                else:
                    break
        t_end = time.time()
        print("\n---------------------------\n接收方已经全部解码完成!\n\n")
        print("共用时: %lf 秒" % (t_end - t_begin))
        print("共发送了 %d 个数据" % send_num)
        _pid, _status = os.wait()
        # print("子进程的id号是: ", _pid)
        # print("退出状态是:",_status)
        break

    # a = input()
    # if a == "next":
    #     for addr in Dest_ADDR:
    #         sockfd.sendto("next".encode(), addr)
    #     print("sleeping")
    #     time.sleep(1000)
    # else:
    #     break
    
sockfd.close()