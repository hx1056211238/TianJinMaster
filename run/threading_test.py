#!/usr/bin/python
# -*- coding: UTF-8 -*-

import threading
import time

exitFlag = 0

class myThread (threading.Thread):   #继承父类threading.Thread
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):                   #把要执行的代码写到run函数里面 线程在创建后会直接运行run函数 
        print "Starting " + self.name
        #print_time(self.name, self.counter, -5)
        #dead_loop()
        factorial(100000000)
        print "Exiting " + self.name

def print_time(threadName, delay, counter):
    while counter:
        if exitFlag:
            thread.exit()
        #time.sleep(delay)
        #print "%s: %s" % (threadName, time.ctime(time.time()))
        counter -= 1
def dead_loop():
    while True:
        pass
def factorial(number): 
    fact = 1
    for n in range(1, number+1): 
        fact += n
    return fact 

# 创建新线程
thread1 = myThread(1, "Thread-1", -1)
thread2 = myThread(2, "Thread-2", -2)
thread3 = myThread(3, "Thread-3", -3)
thread4 = myThread(4, "Thread-4", -4)

# 开启线程
thread1.start()
thread2.start()
thread3.start()
thread4.start()

print "Exiting Main Thread"
