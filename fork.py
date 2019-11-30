#encoding=utf8
import os, time
from multiprocessing import * 
# manager = Manager()
a = Value('f',1.20)
# fd1, fd2 = Pipe()

pid = os.fork()
if pid<0:
    print("error")
elif pid == 0:
    time.sleep(2)
    print("a=",a.value)
    a.value = 3.4
else:
    not_over = True
    while not_over:
        # data = fd1.recv()
        # print("主进程收到",data)

        if a.value != 3.4:
            print("a = ", a.value)
            print("继续接收")
            time.sleep(2) 
        else:
            not_over = False
            print("结束")
            break
    print("ok!")