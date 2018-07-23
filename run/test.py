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

sys.path.append("./ext/rs232")
sys.path.append("./ext/can")
sys.path.append("./ext/vcan")
sys.path.append("./protocol")

#import protocol_rs
import protocol_can

from hf_vcan import *

#_ser = rs232()
_ser = hf_vcan()
#_ser = hf_can
_ser.init(0)

G_PROTOCOL = protocol_can

G_RESET = 0
G_CHG_CC = 1  #//恒流充电
G_CHG_CV = 2  #//恒压充电
G_WAIT = 3    #//搁置
G_DISCHG = 4  #//恒流放电
G_CYCLE = 5
G_FINISH = 6

G_MODULE_COUNT  = 24    #采样板数量
G_BATTERY_COUNT = 16   #每块采样板电池数量
G_INIT_BATTERY_COUNT = 0 #上位机传下来的电池数量(不作使用)
G_RECV_DATA_BIT = 32   #接收电池电压数据位（8768L:24bit / 8256LH主板:32bit）
G_SEND_DATA_BIT = 32   #发送充放电电池电压数据位（8768L:16bit / 8256LH主板:32bit）

#系统变量
G_PROTOCOL.init(G_BATTERY_COUNT, G_SEND_DATA_BIT, G_RECV_DATA_BIT)



""" ==============================
线程--串口发送命令（2次超时）
参数：
        == buffer 发送的命令buffer
返回：
        ==
"""

_battery_data = []
#初始化电池数据
for c in range(0, G_MODULE_COUNT * G_BATTERY_COUNT):
        _battery_data.append({"chk_current":0, "chk_current_+":0, "chk_current_-":0, "chk_voltage":0, "chk_voltage_+": 0, "chk_voltage_-": 0, "chk_battery": 0})


def sendCommand(buffer):
        ret_idx_mod, ret_buffer = _ser.sendto("0", buffer, -1)
        print "mod", ret_idx_mod
        print ret_buffer
        if ret_buffer != None:
            print "done"
            '''
            if len(ret_buffer)>10:
                G_PROTOCOL.do_contactCheckBuffer2Json(ret_idx_mod, ret_buffer, _battery_data)
            '''
              

        pass
        
station = 2
vu = 42000
vi = 10000

print G_PROTOCOL.cmd_GetBatteryInformation(0)
sendCommand(G_PROTOCOL.cmd_GetBatteryInformation(0))

#sendCommand(G_PROTOCOL.cmd_Getcontact_check(0))
#sendCommand(G_PROTOCOL.cmd_Getcontact_check(0))
#time.sleep(1)
#sendCommand(G_PROTOCOL.cmd_Getcontact_check(0))
#sendCommand(G_PROTOCOL.cmd_Getcontact_check(0))
#sendCommand(G_PROTOCOL.cmd_Getcontact_check(0))

print _battery_data[0:4]
'''
print G_PROTOCOL.cmd_GetBatteryInformation(0).encode('hex')

import serial

test_string = "Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4Testing 1 2 3 4"

port_list = ["/dev/serial0"]
#port_list = ["/dev/ttyS0"]
for port in port_list:

    try:
        for i in range(0,16):
            #serialPort = serial.Serial(port, 19200, timeout = 2)
            serialPort  = serial.Serial(port=str(port), baudrate=19200, bytesize=8, parity='N', stopbits=2, timeout=1, xonxoff=0, rtscts=0)
            print "Opened port", port, "for testing:"
            bytes_sent = serialPort.write(G_PROTOCOL.cmd_GetBatteryInformation(0))
            print "Sent", bytes_sent, "bytes"
            loopback = serialPort.read(bytes_sent)
            print len(loopback)
            if loopback == test_string:
                print "Received", len(loopback), "valid bytes, Serial port", port, "working \n"
            else:
                print "Received incorrect data", loopback, "over Serial port", port, "loopback\n"
            serialPort.close()
    except IOError:
        print "Failed at", port, "\n"



#for i in range(0,16):
#    sendCommand(G_PROTOCOL.cmd_GetBatteryInformation(i))
#    #sendCommand(G_PROTOCOL.cmd_Setstop_flag(i,0))
#    time.sleep(3)
'''
