# -*- coding: utf-8 -*  
import time
import threading
import types
import json
import sys
import Queue
import socket
import os
#import urllib
#import httplib
import copy
import datetime
import signal
import logging

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='hf-control.log',
                filemode='w')

logging.debug('program start:')



sys.path.append("./ext/rs232")
sys.path.append("./ext/can")
sys.path.append("./protocol")

#import protocol_rs
import protocol_can


from rs232 import *
import hf_can


"""
  =======================================================================
"""


'''
        全局变量定义
'''

G_PROTOCOL = protocol_can

G_RESET = 0
G_CHG_CC = 1  #//恒流充电
G_CHG_CV = 2  #//恒压充电
G_WAIT = 3    #//搁置
G_DISCHG = 4  #//恒流放电
G_CYCLE = 5
G_FINISH = 6

G_MODULE_COUNT  = 16    #采样板数量
G_BATTERY_COUNT = 16   #每块采样板电池数量
G_INIT_BATTERY_COUNT = 0 #上位机传下来的电池数量(不作使用)
G_RECV_DATA_BIT = 32   #接收电池电压数据位（8768L:24bit / 8256LH主板:32bit）
G_SEND_DATA_BIT = 32   #发送充放电电池电压数据位（8768L:16bit / 8256LH主板:32bit）

#系统变量
G_PROTOCOL.init(G_BATTERY_COUNT, G_SEND_DATA_BIT, G_RECV_DATA_BIT)

#动态变量
G_UNIT = ""
G_CHANNEL = ""
G_ISINIT = False
G_LOOP_TIME = 5
G_CURVE_RATIO = 4
G_STEP_CURVE_SAVETIME = 0
G_COMMAND_QUEUE = Queue.Queue(maxsize = 0)

G_PROCESS_ORIGINAL = None #记录原始设定值，不展开的情况
G_PROCESS = None    #设定值LIST
G_PROCESS_IDX = 0   #当前设定值
                    #设定值中需要*10获得精度的单位变量
G_PROCESS_LIST_PRECISE_ADJUSTMENT = ["current", "upperVoltage", "lowerVoltage", "stop_DeltaVoltage", 
                                     "stop_Current", "stop_Capacity", "curveDelta_voltage", "curveDelta_current"]

G_STEP_START_TIMESTAMP = 0
G_STEP_WORKTIME = 0

#485发送控制GPIO18为高电平，接收时候控制为低电平
'''
try:
        import RPi.GPIO
        # 指定GPIO口的选定模式为GPIO引脚编号模式（而非主板编号模式）
        RPi.GPIO.setwarnings(False) 
        RPi.GPIO.setmode(RPi.GPIO.BCM)
        
        RPi.GPIO.setup(18, RPi.GPIO.OUT)
        RPi.GPIO.output(18,True)
        time.sleep(0.5)
except Exception, e:
        logging.debug('no GPIO:')
        print "no GPIO"
        
 '''       
_ser = rs232()
_ser.init("/dev/ttyAMA0")
_ser.sendto("0","3222334ioeurighi34uy34i7ty8ruehrigh3oi4uyt87rfegirgheoui4y3874683yijhgeljgheiurgo8374yoiurheighoueyrg8734grhbekuygo83yg4oi3uygfueguofyg343222334ioeurighi34uy34i7ty8ruehrigh3oi4uyt87rfegirgheoui4y3874683yijhgeljgheiurgo8374yoiurheighoueyrg8734grhbekuygo83yg4oi3uygfueguofyg343222334ioeurighi34uy34i7ty8ruehrigh3oi4uyt87rfegirgheoui4y3874683yijhgeljgheiurgo8374yoiurheighoueyrg8734grhbekuygo83yg4oi3uygfueguofyg343222334ioeurighi34uy34i7ty8ruehrigh3oi4uyt87rfegirgheoui4y3874683yijhgeljgheiurgo8374yoiurheighoueyrg8734grhbekuygo83yg4oi3uygfueguofyg343222334ioeurighi34uy34i7ty8ruehrigh3oi4uyt87rfegirgheoui4y3874683yijhgeljgheiurgo8374yoiurheighoueyrg8734grhbekuygo83yg4oi3uygfueguofyg343222334ioeurighi34uy34i7ty8ruehrigh3oi4uyt87rfegirgheoui4y3874683yijhgeljgheiurgo8374yoiurheighoueyrg8734grhbekuygo83yg4oi3uygfueguofyg343222334ioeurighi34uy34i7ty8ruehrigh3oi4uyt87rfegirgheoui4y3874683yijhgeljgheiurgo8374yoiurheighoueyrg8734grhbekuygo83yg4oi3uygfueguofyg343222334ioeurighi34uy34i7ty8ruehrigh3oi4uyt87rfegirgheoui4y3874683yijhgeljgheiurgo8374yoiurheighoueyrg8734grhbekuygo83yg4oi3uygfueguofyg343222334ioeurighi34uy34i7ty8ruehrigh3oi4uyt87rfegirgheoui4y3874683yijhgeljgheiurgo8374yoiurheighoueyrg8734grhbekuygo83yg4oi3uygfueguofyg34",0)

'''
time.sleep(0.5)
RPi.GPIO.output(18,False)
'''

time.sleep(0.5)
while True:
    i=1
    time.sleep(0.02)





