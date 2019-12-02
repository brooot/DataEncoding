#!/usr/bin/env python3
#encoding=utf-8
from socket import *
from multiprocessing import *
from Xor import *
from config import *
import sys, random, os, time

if len(sys.argv) < 3:
    print('''
        argv is error!
        run as
        python3 udp client_udp.py 127.0.0.1 8888
        ''')
    raise

sockfd = socket(AF_INET, SOCK_DGRAM)
# 绑定地址
IP = sys.argv[1]
PORT = int(sys.argv[2])
ADDR = (IP, PORT)
sockfd.bind(ADDR)


# 返回自己没有的码字部分
#            {'2','3'}   b"hello"
def recv_Handler(m_info_set, m_data):
    L = []
    for c_info in L_decoded.keys():  
        if c_info in m_info_set:   # 如果新码字中包含已解码码字,就将其剔除
            m_info_set.remove(c_info)  # 将该码字信息剔除
            L.append(L_decoded[c_info])  # 将其对应的字节码加入列表等待异或解码
    
    # print("L = ", L, "m_info_set",m_info_set)

    if (not L) and len(m_info_set)>1 and ([m_info_set, m_data] not in L_undecoded):  # 如果没有相同的数据,表示无法解码,放入未解码的列表中
        L_undecoded.append( [m_info_set, m_data] )
        # print("添加到未解码: ", [m_info_set, m_data])

    elif m_info_set:  # 表示剥除部分且还有剩余
        # 异或解码
        L.append(m_data)
        new_data = bytesList_Xor_to_Bytes(L)

        # 判断剩下的码字度是多少
        if len(m_info_set) == 1:  # 如果剩下的度为1, 递归解码
            # print("度为1,进行递归解码")
            recursion_Decode(list(m_info_set)[0], new_data)
        elif m_info_set and [m_info_set, m_data] not in L_undecoded:  # 否则加入到未解码列表中
            # print("度大于1,添加到未解码: ", [m_info_set, m_data])
            L_undecoded.append( [m_info_set, m_data] )
  



#   info: '2'  data: b"hello"     码字格式: [{'2','3'},b"hello world"]
def recursion_Decode(_info, _data):
    L_decoded[_info] = _data   # 将其加入到已解码集合中
    decode_List = []  # 等待递归解码列表
    for info, data in L_decoded.items():
        for cw in L_undecoded:
            c_info = cw[0]
            c_data = cw[1]
            if info in c_info: # 如果其中含有刚解码出的码字, 就将其剥离
                # 更新码字信息
                # print("从" ,c_info, "中删减码字信息",info,end='')
                c_info = c_info - {info}
                # print(" 得到 ",c_info)
                if len(c_info) == 0:  # 如果信息为空,就将该码字移出未解码列表
                    L_undecoded.remove(cw)
                    continue


                c_data= bytesList_Xor_to_Bytes([c_data, data])
                L_undecoded.remove(cw)
                if [c_info, c_data] not in L_undecoded:
                    L_undecoded.append([c_info, c_data])
               
                if len(c_info) == 1 and [c_info, c_data] not in decode_List:  # 若解码后的码字度为1, 加入递归解码的列表,等待递归解码
                    decode_List.append([c_info, c_data]) 

    for cw in decode_List:
        if cw[0] and cw[1][0] != 0:
            c_info = list(cw[0])[0]
        else:
            continue
        recursion_Decode(c_info, cw[1])


def Redecode_in_undecoded():
    pass













L_decoded = {}

L_undecoded = []

print("主机 " + ADDR[0] + ":" + str(ADDR[1]) + " 正在等待数据...\n")
err_num = 0
recv_num = 0
while True:
    # 接受数据(与tcp不同)
    data, addr = sockfd.recvfrom(1024*4)
    # 如果收到的数据有丢失,就遗弃该数据
    # if len(data) < 67:
    #     continue

    recv_num += 1
    # 数据解码
    data = data.decode()
    # print("data = ", repr(data))
    # print("数据长度: ", len(data))
    # message = "已收到来自%s的数据：%s" % (addr, data)
    # print(message)
    # 数据分割
    # 获取码字信息集合 { '2','3' }
    m_info_set = set(data.split("##",1)[0].split("@"))
    # 获取码字数据(字符串的字节码)
    m_data = data.split("##",1)[1].encode()
    print("收到码字数据的信息是：", m_info_set)
    if len(m_data) != 67:
        err_num += 1
        print("数据有丢失,长度是: ",len(m_data))
        break

    print("\n")
    

    # 使用刚刚接收到的数据进行解码
    recv_Handler(m_info_set, m_data)

    # 在未解码的码字中寻找解码机会
    Redecode_in_undecoded()
    

    print("\n未解码个数: ", len(L_undecoded))
    print("\n")
    print("已解码个数: ", len(L_decoded))

    print("\n------------------------------\n")
    # print("我是子进程")
    # os._exit(0)
# else:
    # 发送数据
    # send_message = "已经收到您的数据。"
    if len(L_decoded) == subsection_num:
        
        print("\n\n解码完成!")

        need_to_resend_ack = Value('i',True)
        pid = os.fork()
        if pid < 0:
            print("创建进程出错")
        # 子进程用来判断源端是否已经成功接收到ack,没有的话定时重新发送
        elif pid == 0:
            send_time = 1 # 第几次发送
            while need_to_resend_ack.value:
                # 向源端发送 ack
                send_message = "ok"
                print("第" + str(send_time) + "次 ",end='')
                print("向源端发送ack信息 ")
                sockfd.sendto(send_message.encode(), addr)
                if send_time == 1:
                    time.sleep(0.4)
                    send_time += 1
                else:
                    send_time += 1
                    time.sleep(3)

            os._exit(0)
        # 接受源端发来的确认信息
        else:
            while need_to_resend_ack.value:
                data, address = sockfd.recvfrom(1024)
                if addr == address and data.decode() == "got_it":
                    print("发送方已经收到ack")
                    need_to_resend_ack.value = False
            print("\n------------------------\n一轮接收完成!\n")

        print("已解码数据:")
        # 将解码出的数据存放到txt文件中
        with open("encoded_data of " + str(ADDR) + ".txt",'wb') as f:
            data_to_save = sorted(L_decoded.items(),key=lambda x:x[0])
            for line in data_to_save:
                print("二进制:",end='')
                for i in line[1]:
                    print(bin(i),end=' ')
                print("\n")
                print("解码内容:")
                print(line[0],':',line[1].decode(),end="\n\n--------------------------\n")
                record = line[1] + "\n".encode()
                f.write(record)
        print("解码数据已经存放在 encoded_data of " + str(ADDR) + ".txt中")
        # _pid, _status = os.wait()
        # print("子进程的id号是: ", _pid)
        # print("退出状态是:",_status)
        break
print("数据错误次数:", err_num)
print("共收到 %d 个码字." % recv_num)
sockfd.close()