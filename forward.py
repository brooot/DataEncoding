#!/usr/bin/env python3
#encoding=utf-8
from socket import *
from multiprocessing import *
from Xor import *
from config import *
import sys, random, os, time


def recv_from_source():
    if len(sys.argv) < 3:
        print('''
            argv is error!
            run as
            python3 udp forward.py 127.0.0.1 8888
            ''')
        raise
    # 创建与源通信的套接字
    sockfd = socket(AF_INET, SOCK_DGRAM)
    # 绑定地址
    IP = sys.argv[1]
    PORT = int(sys.argv[2])
    ADDR = (IP, PORT)
    sockfd.bind(ADDR)
    recv_num = 0

    print("主机 " + ADDR[0] + ":" + str(ADDR[1]) + " 正在等待数据...\n")

    with open("NormalRecv" + str(ADDR) + ".txt",'wb') as f:
        while recv_num != subsection_num:
            # 接受数据(与tcp不同)
            data, addr = sockfd.recvfrom(1024)
            recv_num += 1
            # 数据存储
            f.write(data + "\n".encode())

    # 将解码出的数据存放到txt文件中
    print("共收到%d个数据" % recv_num)
    print("\n数据已存放在 NormalRecv" + str(ADDR) + ".txt 中")

    sockfd.close()


def main():
    p1 = Process(target = recv_from_source)
    p1.start()
    p1.join()


if __name__ == "__main__":
    main()


