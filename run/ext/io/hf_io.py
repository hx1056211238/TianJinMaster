# -*- coding: utf-8 -*  
import time
import threading
#import types
import json
import sys
import Queue
import socket
import os
#import urllib
#import httplib
#import copy
#import datetime
import signal
import logging
import RPi.GPIO as GPIO


logging.basicConfig(level=logging.ERROR,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='hf-io.log',
                filemode='w')

logging.error('program start:')



sys.path.append("./ext/vcan")
sys.path.append("./ext/iic")

#import hf_can
from hf_vcan import *
from iic import *

G_PATH = os.getcwd()


reload(sys)
sys.setdefaultencoding('utf-8') 



""" ==============================
类--switch case类
"""
# This class provides the functionality we want. You only need to look at
# this if you want to know how this works. It only needs to be defined
# once, no need to muck around with its internals.
class switch(object):
        def __init__(self, value):
                self.value = value
                self.fall = False
        def __iter__(self):
                """Return the match method once, then stop"""
                yield self.match
                raise StopIteration
        def match(self, *args):
                """Indicate whether or not to enter a case suite"""
                if self.fall or not args:
                        return True
                elif self.value in args: # changed for v1.5, see below
                        self.fall = True
                        return True
                else:
                        return False

""" ==============================
计算--16进制转10进制（含负数）
          signedFromHex16 FFFF
          signedFromHex24 FFFFFF
          signedFromHex32 FFFFFFFF
参数：
        n 数值
返回：
        10进制数字
"""
def signedFromHex16(s): 
    v = int(s, 16)
    if not 0 <= v < 65536: 
        raise ValueError, "hex number outside 16 bit range" 
    if v >= 32768: 
        v = v - 65536 
    return v 
 
def hexBYTE(dec):
    return ("%x"%(dec&0xff)).zfill(2) 

_ser = None
G_RET_LEN = "63"    #  30 CAN_IO + 32 TEMP  ,first is 46,the tmep is 26 ,the io is 20 
def initCAN():
    global _ser
    #if _ser != None:
    #    _ser.release()
    time.sleep(0.3)
    _ser = hf_vcan()
    if _ser is not None:
        _ser.init()
    else:
        return None

#CAN1 作为io控制板通讯端口
#_ser = hf_can
#_ser = hf_vcan()
#_ser.init(1)
initCAN()
_iic = hf_iic()
_iic.init(1)


#output io hash表，set[0]模块，set[1]模块的pin，set[2]0取正位1取反位，set[3]初始值与缓存值
G_OUT_HASH = {   
                              "POWER_FAN" : {"set":["I2C",11,1,0]},
                              "JIG_FAN": {"set":["I2C",12,1,0]},
                              "MC_ON": {"set":["I2C",20,1,1]},
                              "LED_RUN": {"set":["I2C",13,1,0]},
                              "LED_READY": {"set":["I2C",14,1,1]},
                              "LED_ERROR": {"set":["I2C",15,1,0]},
                              "JIG_POWER_ON": {"set":["I2C",21,1,1]} ,
                              "ALLBOX_OPEN": {"set":["I2C",26,1,0]} ,
                              "SMOKE_PLC": {"set":["I2C",24,1,0]} ,
                              "TEMPFUSE_PLC": {"set":["I2C",25,1,0]} ,
                              "BELL": {"set":["I2C",29,0,0]},
                              "OUT3":{"set":["I2C",23,1,0]},
                              "CELL_RESPONSE": {"set":["PI",15,1,0]},
                              "PICK_UP": {"set":["PI",16,1,1]},
                              "DROP_OFF": {"set":["PI",18,1,1]},
                              "OUT2": {"set":["PI",11,1,0]},
                              "DE": {"set":["PI",12,1,0]},
                              "OUT1": {"set":["PI",13,1,0]},
                              "GRIPPER_ON_SOL": {"set":["CAN",0,0,0]},
                              "POLE_LAMP1": {"set":["CAN",1,0,0]},
                              "POLE_LAMP2": {"set":["CAN",2,0,0]},
                              "ForwoBackrd_SOL": {"set":["CAN",3,0,0]},
                              "MODEL_SLECTION_CAN": {"set":["CAN",4,0,0]},
                              "JIG_FAN_CAN": {"set":["CAN",5,0,0]}}
'''                            "GRIPPER_ON_SOL": {"set":["CAN",0,0,0]},       #夹具板IO信号，机械手靠拢 （某些型号用到）
                              "POLE_LAMP1": {"set":["CAN",1,0,0]},                #夹具板IO信号，夹具夹紧电池（某些型号用到）
                              "POLE_LAMP2": {"set":["CAN",2,0,0]},                #夹具板IO信号，夹具夹紧电池（某些型号用到）
                              "JIG_UP_DOWN_SOL": {"set":["CAN",3,0,0]},     #夹具板IO信号，下压针板
                              "LATCH_ON_SOL": {"set":["CAN",4,0,0]},           #夹具板IO信号，夹紧托盘
                              "JIG_FAN_CAN": {"set":["CAN",5,0,0]}               #夹具板IO信号，夹具板风机，和JIG_FAN一样功能，看接线接哪里
'''
                         
#             }
                      
#input io hash表，set[0]模块，set[1]模块的pin，set[2]0取正位1取反位 
#JIG_FAN_ERR 作为风机异常输入     
#LATCH_ON_SOL               
G_IN_HASH = {   
                              "FIRE_CLOSE": {"set":["I2C",1,0]},
                              "ALLBOX_OPEN": {"set":["I2C",2,0]},
                              "TEMPFUSE": {"set":["I2C",3,0]},
                              "POWER_SW": {"set":["PI",31,1]},
                              "EMG": {"set":["PI",33,1]},
                              "CELL_EXIST": {"set":["PI",37,1]},
                              "AC_LOSS": {"set":["PI",36,1]} ,
                              "STACKER_IN": {"set":["PI",32,1]} ,
                              "FINISH": {"set":["PI",40,1]} ,
                              "Gripper_R1": {"set":["CAN",0,1]},
                              "Gripper_R2": {"set":["CAN",1,1]},
                              "Gripper_L1": {"set":["CAN",2,1]},
                              "Gripper_L2": {"set":["CAN",3,1]},

                              "GripperBack_R": {"set":["CAN",4,1]} ,
                              "GripperForword_R": {"set":["CAN",5,1]},
                              "GripperBack_L": {"set":["CAN",6,1]},
                              "GripperForword_L": {"set":["CAN",7,1]},

                              "Smoke_R": {"set":["CAN",8,0]} ,
                              "Smoke_L": {"set":["CAN",9,0]},
                              "Latch_On_Right": {"set":["CAN",10,1]},
                              "Latch_Off_Right": {"set":["CAN",11,1]},
                              "Latch_On_left": {"set":["CAN",12,1]} ,
                              "Latch_Off_left": {"set":["CAN",13,1]},
                              "Tray_Chamfer": {"set":["CAN",14,1]},
                              "Tray_Exist_RR": {"set":["CAN",15,1]},
                              "Tray_Exist_RF": {"set":["CAN",16,1]} ,
                              "Tray_Exist_LR": {"set":["CAN",17,1]},
                              "Tray_Exist_LF": {"set":["CAN",18,1]},
                              "JIG_FAN_ERR": {"set":["CAN",19,1]},
                              "MODEL_SLECTION_CAN_IN_LEFT": {"set":["CAN",20,1]} ,
                              "Spare3": {"set":["CAN",21,1]},
                              "MODEL_SLECTION_CAN_IN_RIGHT": {"set":["CAN",22,1]},
                              "Spare5": {"set":["CAN",23,1]},
                              "Debug": {"set":["CAN",24,1]},
                              "ForwordBack_SOL": {"set":["CAN",25,1]} ,
                              "Latch_On_SOL": {"set":["CAN",26,1]},
                              "Gripper_On_SOL": {"set":["CAN",27,1]},
                              "RESERVED1": {"set":["CAN",28,0]},
                              "RESERVED2": {"set":["CAN",29,0]}}
'''
                          "JIG_FAN_ERR": {"set":["CAN",0,0]} ,         #夹具板风机异常
                          "GRIPPER_BLOCK_O_C": {"set":["CAN",1,1]},      #GRIPPER_ON_SOL对应的信号，机械臂靠拢是否到位（某些型号用到）
                          "SMOKE_FRONT": {"set":["CAN",2,0]},        #前烟雾
                          "SMOKE_REAR": {"set":["CAN",3,0]},          #后烟雾
                          "LATCH_OFF_LEFT": {"set":["CAN",4,1]},     #左锁紧OFF信号，松开的意思
                          "LATCH_ON_LEFT": {"set":["CAN",5,1]},      #左锁紧ON信号，锁紧的意思，是否完全锁紧或者松开，要同时判定这两个信号一个为1一个为0
                          "TRAY_POSITION": {"set":["CAN",6,1]},       #托盘缺口位信号
                          "TRAY_IN": {"set":["CAN",7,1]},                   #托盘进入信号
                          "JIG_DOWN_SENSE": {"set":["CAN",8,1]},    #气缸下端传感器，1则为气缸弹开
                          "JIG_UP_SENSE": {"set":["CAN",9,1]},           #气缸上端传感器，1则为压紧
                          "LATCH_ON_RIGHT": {"set":["CAN",10,1]},    #同LATCH LEFT
                          "LATCH_OFF_RIGHT": {"set":["CAN",11,1]},
                          "DEBUG": {"set":["CAN",12,1]},                      #夹具板测试信号，夹具板有个debug跳线，debug后，夹具板不受命令控制，只受夹具板按键控制
                          "UP_DOWN_DEBUG": {"set":["CAN",13,1]},     #夹具板按键控制信号
                          "LATCH_DEBUG": {"set":["CAN",14,1]},           #夹具板按键控制信号
                          "GRIPPER_DEBUG": {"set":["CAN",15,1]}         #夹具板按键控制信号
'''

#                          }

#全sensor的数据                      
    
G_SENSOR = {"IN":{},"OUT":{}}
#16个充放电托盘温度
G_TEMP_CAN = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
#命令字队列
G_COMMAND_QUEUE = Queue.Queue(maxsize = 0)


for g_key in G_IN_HASH:
    G_SENSOR["IN"][g_key] = -1
    
for g_key in G_OUT_HASH:
    G_SENSOR["OUT"][g_key] =  G_OUT_HASH[g_key]["set"][3]

    
#print "G_SENSOR:" + str(G_SENSOR)

#16个CAN扩展IO
'''
GRIPPER_OPEN_CLOSE		1 （夹具-开/关）
GRIPPER_BLOCK_O_C		1（夹具块-开/关）
SMOKE_FRONT                 1（烟感-前）
SMOKE_REAR                   1（烟感-后）
Latch_Off_left                   1（左锁紧-关）
Latch_On_left                   1（左锁紧-开）
TRAY_POSITION               1（托盘位置）
TRAY_IN                           1（托盘放入）
JIG_DOWN_SENSE           1（治具压下）
JIG_UP_SENSE                 1（治具弹起）
Latch_On_Right                1（右锁紧开）
Latch_Off_Right                1（右锁紧关）
DEBUG                             1（调试）
UP_DOWN_DEBUG           1（压下弹起调试）
LATCH_DEBUG                 1（锁紧调试）
GRIPPER_DEBUG             1（夹具调试）
4字节预留
温度（24）                       12 个温度* 2字节
'''


#IO CTL Write 明细
#GRIPPER_ON_SOL		1（夹具-开/关）
#POLE_LAMP1				1（极性指示灯1）
#POLE_LAMP2				1（极性指示灯2）
#JIG_UP_DOWN_SOL    1（治具压下弹起）
#LATCH_ON_SOL			1（锁紧）
#JIG_FAN				    	1（治具风机）
CAN_IO_IN_CTL = [0, 0, 0, 0, 0, 0]

g_no_can = False

'''
=========
=========
初始化树莓派GPIO
=========
=========

'''
# BOARD编号方式，基于插座引脚编号 
GPIO.setmode(GPIO.BOARD)

# 初始化PI的输出IO
for g_key in G_OUT_HASH:
    if G_OUT_HASH[g_key]["set"][0] == "PI":
        print g_key 
        GPIO.setup(int(G_OUT_HASH[g_key]["set"][1]), GPIO.OUT)
        
# 初始化PI的输入IO
for g_key in G_IN_HASH:
    if G_IN_HASH[g_key]["set"][0] == "PI":
        # 输入IO全部拉高
        GPIO.setup(int(G_IN_HASH[g_key]["set"][1]), GPIO.IN, pull_up_down=GPIO.PUD_UP)

        

#this function is write pro    return 0     
def setCAN():

    retries = 16
    run_again_IO  = 0
    while run_again_IO < retries:  
        
        buf = [0] * 20  #just init the save the can output data
        for key in G_OUT_HASH:
            if G_OUT_HASH[key]["set"][0] == "CAN":
                # set[1] is pin number             pin value
                buf[G_OUT_HASH[key]["set"][1]] = G_OUT_HASH[key]["set"][3]^G_OUT_HASH[key]["set"][2]
        s = ""
        for i in buf:
            s = s + hexBYTE(i)
        # s is the all pin value 8pin为一个
        i=0
        
        for i in range(0, len(s)/16):
            ret_buffer = sendCAN("1300030" + str(i) + "#"+ s[i*16:i*16+16] +",0") #this place send write meassage
            
        i=i+1
        ret_buffer1 = None
        #print "s:",s -> 40个字符（20个点）
        #print "i:",i -> 2
        if len(s)%16>0:
            #补齐后面的，其实可以去掉
            k = 16-len(s)%16
            #                      主板地址+预留+命令字  当前帧序    数据          是否有返回
            #ret_buffer1 = sendCAN("1300030" + str(len(s)/16) + "#"+ s[(i*16):] + "0"*k +",1")
            ret_buffer1 = sendCAN("1300030" + str(len(s)/16) + "#"+ s[(i*16):]  +",1")
            if ret_buffer1 != None:
                break
            time.sleep(0.02)
            if run_again_IO > 4:   
                fs = open("/home/pi/hf_formation/run/data/debug_IO_Write.dat","a+")
                fs.write("*\n")
                fs.write("run_again_IO:")
                fs.write(str(run_again_IO))
                fs.write("\n")
                fs.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
                fs.write("*\n")       
        
    pass
    
    
    

def setPI():
    for key in G_OUT_HASH:
        if G_OUT_HASH[key]["set"][0] == "PI":
            GPIO.output(G_OUT_HASH[key]["set"][1], G_OUT_HASH[key]["set"][3]^G_OUT_HASH[key]["set"][2]) 
    pass
    
    
def setI2C():
    for key in G_OUT_HASH:
        if G_OUT_HASH[key]["set"][0] == "I2C":
            _iic.set(G_OUT_HASH[key]["set"][1], G_OUT_HASH[key]["set"][3]^G_OUT_HASH[key]["set"][2])
    _iic.send()
    pass

    
""" ==============================
线程--设置CAN板IO信状态
参数：
        == k,第几个IO
        == v,什么值
返回：
        == IO 状态LIST
"""  
'''
def do_set_CAN_IO_IN_def():
    global CAN_IO_IN_CTL
    ret_buffer = sendCAN("013F0300#0000000000000000,0")
    ret_buffer = sendCAN("013F0301#0000000000000000,0")
    ret_buffer = None
    ret_buffer = sendCAN("013F0302#0000000000000000,8")
    if ret_buffer != None:
        CAN_IO_IN_CTL = ret_buffer
        return True
    pass
'''    
""" ==============================
线程--设置CAN板IO信状态
参数：
        == k,第几个IO
        == v,什么值
返回：
        == IO 状态LIST
"""  
'''
def do_set_CAN_IO_IN(k,v):
    global CAN_IO_IN_CTL
    lt = copy.copy(CAN_IO_IN_CTL)
    lt[k] = v
    s = ""
    for i in range(0,6):
        s =  s + str(lt[i]).zfill(2)
    ret_buffer = sendCAN("013F0300#" + s + "0000,0")
    ret_buffer = sendCAN("013F0301#0000000000000000,0")
    ret_buffer = None
    ret_buffer = sendCAN("013F0302#0000000000000000,8")
    if ret_buffer != None:
        #print ret_buffer
        CAN_IO_IN_CTL = ret_buffer
        return True
    pass
'''


""" ==============================
线程--读取I2C板IO信息
参数：
        == 
返回：
        == IO 状态LIST
"""  
def get_I2C_Sensor_Buffer():
    ret_buffer = _iic.get()
    return ret_buffer
    
    
""" ==============================
线程--读取CAN板IO信息+温度信息
参数：
        == 
返回：
        == IO 状态LIST
"""  
def get_CAN_Sensor_Buffer():
    global G_RET_LEN
    ret_buffer = None
    ret_buffer = sendCAN("13000200#00," + G_RET_LEN)
    if ret_buffer == None:
        #G_RET_LEN = "44"
        ret_buffer = sendCAN("13000200#00," + "63")
    #print ret_buffer
    return ret_buffer
    
    
""" ==============================
线程--CAN发送命令（1次超时）
参数：
        == buffer 发送的命令buffer
返回：
        ==
"""  
#ret_buffer = sendCAN("013F030" + str(i) + "#"+ s[i*16:i*16+16] +",0")
#ret_buffer = sendCAN("013F030" + str(len(s)/16) + "#"+ s[(i*16):] + "0"*k +",8")

#ret_buffer = sendCAN("013F0200#00," + "64")     
def sendCAN(buffer):
        #sendto命令说明
        #lt = hf_can.sendto("0", "00400600#00,40", -1)
        #参数1：永远是"0",兼容232/485第一个参数是通知第几块板
        #参数2：数据位#具体数据，要回收数据长度
        #参数3：-1，则有回收数据（放在CAN最后一个包），否则至0，不回收数据，兼容232/485数据回收长度
        ret_buffer = None
        try:
            ret_idx_mod, ret_buffer = _ser.sendto_IO("0", buffer, -1) 
        except Exception,e:
            print "_ser.sendto: ", ret_buffer
        return ret_buffer
        

""" ==============================
动作--运算ui端发过来的json指令

参数：
        s_json:json命令的字符串
返回：
        结果的json字符串
"""
def do_json_command_solver(s_json):
        global G_TEMP_CAN
        global G_SENSOR
        global g_no_can
        global G_OUT_HASH
        global G_RET_LEN
        global _ser
        
        try:
                obj_json = json.loads(s_json)
                action = obj_json["action"]
        except Exception,e:
                logging.error('get json error:' + s_json)
                ret = '{"success":"false","msg":"json decode error"}'
                return ret            
        
        ret = '{"success":"false"}'
        
        for case in switch(action):
                #复位
                if case('sensor_reset'):
                        #_ser.init(1)
                        #initCAN()
                        _ser.reset_IO()
                        ret = '{"success":"true"}'
                        break
                        
                #读取CAN板IO信息
                if case('sensor_read'):
                        lt = []
                        for i in range(0,int(round((int(G_RET_LEN) - 30) / 2))):
                            lt.append( G_TEMP_CAN[i] )
                        obj = {"success": "true", "message":"", "action":"sensor_read","io":G_SENSOR,"temp_can":lt}
                        ret = json.dumps(obj)
                        break
                #设置CAN板IO信息
                if case('sensor_write'):
                    try:
                        out_sensors = obj_json["data"]
                        for key in out_sensors:
                            G_SENSOR["OUT"][key] = out_sensors[key]
                        for key in G_SENSOR["OUT"]:
                            G_OUT_HASH[key]["set"][3] = G_SENSOR["OUT"][key]
                        ret = '{"success":"true"}'
                        
                    except Exception,e:
                        ret = '{"success":"false", "msg":"' + str(e) + '"}'
                        return ret
                        '''
                        param = obj_json["io"]                       
                        for i in range(len(param)):
                            for (k,v) in  param[i].items():
                                #print "param[%s]=" % k,v
                               if int(k) < 20:
                                  do_set_CAN_IO_IN(int(k),v)
                               else:
                                  pass
                                  #_iic.set(int(k),v)
                               if int(k) == 25:
                                  pass
                                  if v==0:
                                     g_no_can = True
                                  if v==1:
                                     g_no_can = False
                        #_iic.send()
                        obj = {"success": "true", "message":"", "action":"sensor_write","io":G_SENSOR  ,"temp_can":G_TEMP_CAN}
                        ret = json.dumps(obj)
                        #do_set_CAN_IO_IN(3,1)
                        '''
                    break
                if case(): # default, could also just omit condition or 'if True'
                        print "Do not have active selection for:" + action
                      
        return ret

""" ==============================
线程--UDP接收线程

参数：
        ==
返回：
        ==
"""
class cls_udp_Thread(threading.Thread):
        def __init__(self, name):
                threading.Thread.__init__(self)
                self.t_name = name
        def run(self):
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
                sock.bind(('', 9099))       # 绑定同一个域名下的所有机器  
                while True: 
                        revcData, (remoteHost, remotePort) = sock.recvfrom(65526)
                        ret = do_json_command_solver(revcData)
                        #print "ret",ret
                        #print("[%s:%s] connect" % (remoteHost, remotePort))     # 接收客户端的ip, port  

                        #分包发送
                        if len(ret)>32768:
                                n = len(ret) / 32768
                                m = len(ret) % 32768
                                for i in range(0,n):
                                        print "io: " + str(len(ret[i*32768:i*32768+32768]))
                                        sock.sendto(ret[i*32768:i*32768+32768], (remoteHost, remotePort)) 
                                
                                #print len(ret[(i+1)*32768:(i+1)*32768+m])
                                
                                sock.sendto(ret[(i+1)*32768:(i+1)*32768+m], (remoteHost, remotePort))
                        else:
                                sock.sendto(ret, (remoteHost, remotePort))
                                
                        #print "revcData: ", revcData  
                        #print "sendDataLen: ", sendDataLen  

                sock.close() 
                
                
""" ==============================
线程--CAN读取控制
"""
class cls_worker_CAN_Thread(threading.Thread):
        global G_OUT_HASH
        global G_IN_HASH
        global G_SENSOR
        global G_TEMP_CAN
        
        m_can_off = False
        def __init__(self, name):
                threading.Thread.__init__(self)
                self.t_name = name
        def run(self):
                while True:
                    #print G_SENSOR
                    if G_SENSOR["OUT"]["JIG_POWER_ON"] == 0:
                        time.sleep(0.5)
                        self.m_can_off = True
                        print "io: =============================================="
                        continue
                    if self.m_can_off and G_SENSOR["OUT"]["JIG_POWER_ON"] == 1:
                        #initCAN()
                        _ser.reset_IO()
                        time.sleep(2)
                        self.m_can_off = False

                    setCAN()
                    time.sleep(0.2)
                    ret_buffer = None
                    ret_buffer = get_CAN_Sensor_Buffer()
                    #print "ret_buffer",ret_buffer

                    if ret_buffer != None:
                        #获取 INPUT IO 状态
                        for key in G_IN_HASH:
                            if G_IN_HASH[key]["set"][0] == "CAN":
                                pin = G_IN_HASH[key]["set"][1]
                                v = ret_buffer[pin]
                                v = v^G_IN_HASH[key]["set"][2]
                                G_SENSOR["IN"][key] = v
                                
                        #获取温度点数据
                        pos = 30
                        try:
                            for i in range(0, (len(ret_buffer)-30)/2):
                                data_hex = hexBYTE(ret_buffer[pos+1]) + hexBYTE(ret_buffer[pos+0])
                                G_TEMP_CAN[i] = round(float(signedFromHex16(data_hex)) / 10, 1)
                                pos = pos+2
                        except Exception,e:
                                pass
                    time.sleep(0.2)
                    pass
                    '''
                    print "Gripper_R1",G_SENSOR["IN"]['Gripper_R1'] 

                    print "G_SENSOR[\"IN\"][Gripper_R2]",G_SENSOR["IN"]['Gripper_R2']   
                    print "G_SENSOR[\"IN\"][Gripper_L1]",G_SENSOR["IN"]['Gripper_L1']  
                    print "G_SENSOR[\"IN\"][Gripper_L2]",G_SENSOR["IN"]['Gripper_L2']  
             
                    print "G_SENSOR[\"IN\"][Gripper(R)Back]",G_SENSOR["IN"]['GripperBack_R']  
                    print "G_SENSOR[\"IN\"][Gripper(R)Forword]",G_SENSOR["IN"]['GripperForword_R']   
                    print "G_SENSOR[\"IN\"][Gripper(L)Back]",G_SENSOR["IN"]['GripperBack_L']  
                    print "G_SENSOR[\"IN\"][Gripper(L)Forword]",G_SENSOR["IN"]['GripperForword_L'] 
             
                    print "G_SENSOR[\"IN\"][Smoke_R]",G_SENSOR["IN"]['Smoke_R']  
                    print "G_SENSOR[\"IN\"][Smoke_L]",G_SENSOR["IN"]['Smoke_L']   
                    print "G_SENSOR[\"IN\"][Latch_On_Right]",G_SENSOR["IN"]['Latch_On_Right']  
                    print "G_SENSOR[\"IN\"][Latch_Off_Right]",G_SENSOR["IN"]['Latch_Off_Right']  
             
                    print "G_SENSOR[\"IN\"][Latch_On_left]",G_SENSOR["IN"]['Latch_On_left']  
                    print "G_SENSOR[\"IN\"][Latch_Off_left]",G_SENSOR["IN"]['Latch_Off_left']   
                    print "G_SENSOR[\"IN\"][Tray_Chamfer]",G_SENSOR["IN"]['Tray_Chamfer']  
                    print "G_SENSOR[\"IN\"][Tray_Exist(RR)]",G_SENSOR["IN"]['Tray_Exist_RR'] 
             
                    print "G_SENSOR[\"IN\"][Tray_Exist(RF)]",G_SENSOR["IN"]['Tray_Exist_RF']  
                    print "G_SENSOR[\"IN\"][Tray_Exist(LR)]",G_SENSOR["IN"]['Tray_Exist_LR']   
                    print "G_SENSOR[\"IN\"][Tray_Exist(LF)]",G_SENSOR["IN"]['Tray_Exist_LF']  
                    print "G_SENSOR[\"IN\"][Spare1]",G_SENSOR["IN"]['Spare1']  
             
                    print "G_SENSOR[\"IN\"][Spare2]",G_SENSOR["IN"]['Spare2']  
                    print "G_SENSOR[\"IN\"][Spare3]",G_SENSOR["IN"]['Spare3']   
                    print "G_SENSOR[\"IN\"][Spare4]",G_SENSOR["IN"]['Spare4']  
                    print "G_SENSOR[\"IN\"][Spare5]",G_SENSOR["IN"]['Spare5'] 
             
                    print "G_SENSOR[\"IN\"][Debug]",G_SENSOR["IN"]['Debug']  
                    print "G_SENSOR[\"IN\"][ForwordBack_SOL]",G_SENSOR["IN"]['ForwordBack_SOL']   
                    print "G_SENSOR[\"IN\"][Latch_On_SOL]",G_SENSOR["IN"]['Latch_On_SOL']  
                    print "G_SENSOR[\"IN\"][Gripper_On_SOL]",G_SENSOR["IN"]['Gripper_On_SOL']  
             
                    print "G_TEMP_CAN1:",G_TEMP_CAN[0]
                    print "G_TEMP_CAN2:",G_TEMP_CAN[1]
                    print "G_TEMP_CAN3:",G_TEMP_CAN[2]
                    print "G_TEMP_CAN4:",G_TEMP_CAN[3]
                    print "G_TEMP_CAN5:",G_TEMP_CAN[4]
                    print "G_TEMP_CAN6:",G_TEMP_CAN[5]
                    print "G_TEMP_CAN7:",G_TEMP_CAN[6]
                    print "G_TEMP_CAN8:",G_TEMP_CAN[7]
                    print "G_TEMP_CAN9:",G_TEMP_CAN[8]
                    print "G_TEMP_CAN10:",G_TEMP_CAN[9]
                    print "G_TEMP_CAN11:",G_TEMP_CAN[10]
                    print "G_TEMP_CAN12:",G_TEMP_CAN[11]
                    print "G_TEMP_CAN13:",G_TEMP_CAN[12]
                    print "G_TEMP_CAN14:",G_TEMP_CAN[13]
                    print "G_TEMP_CAN15:",G_TEMP_CAN[14]
                    print "G_TEMP_CAN16:",G_TEMP_CAN[15]
                    '''



""" ==============================
线程--I2C读取控制
"""
class cls_worker_I2C_Thread(threading.Thread):
        global G_OUT_HASH
        global G_IN_HASH
        global G_SENSOR
        
        def __init__(self, name):
                threading.Thread.__init__(self)
                self.t_name = name
        def run(self):
                while True: 
                    setI2C()
                    time.sleep(0.3)
                    #print "I2C"
                    ret_buffer = None
                    ret_buffer = get_I2C_Sensor_Buffer()
                    if ret_buffer != None:
                        #获取 INPUT IO 状态
                        for key in G_IN_HASH:
                            if G_IN_HASH[key]["set"][0] == "I2C":
                                pin = G_IN_HASH[key]["set"][1]
                                v = ret_buffer[pin]
                                v = v^G_IN_HASH[key]["set"][2]
                                G_SENSOR["IN"][key] = v
                    time.sleep(0.3)
                    pass

""" ==============================
线程--PI读取控制
"""
class cls_worker_PI_Thread(threading.Thread):
        global G_OUT_HASH
        global G_IN_HASH
        global G_SENSOR
        
        def __init__(self, name):
                threading.Thread.__init__(self)
                self.t_name = name
        def run(self):
                while True: 
                    #print "PI"
                    setPI()
                    for key in G_IN_HASH:
                        if G_IN_HASH[key]["set"][0] == "PI":
                            pin = G_IN_HASH[key]["set"][1]
                            v = GPIO.input(pin)
                            v = v^G_IN_HASH[key]["set"][2]
                            G_SENSOR["IN"][key] = v
                        
                    time.sleep(0.05)
                    pass

                    
""" ==============================
线程--主线程
参数：
        ==
返回：
        ==
"""
def main():
    
    global G_SENSOR
    
    print "io: start"
    _th_udp = cls_udp_Thread('udp_thread')
    _th_udp.setDaemon(True)
    _th_udp.start()
    
    _th_i2c = cls_worker_I2C_Thread('i2c_thread')
    _th_i2c.setDaemon(True)
    _th_i2c.start()
    
    _th_can = cls_worker_CAN_Thread('can_thread')
    _th_can.setDaemon(True)
    _th_can.start()
    
    _th_pi = cls_worker_PI_Thread('pi_thread')
    _th_pi.setDaemon(True)
    _th_pi.start()
    
    
    while True:
        #i=1
        time.sleep(0.5)
        #print G_SENSOR
    pass
        

def exit_gracefully(signal, frame):
        #... log exiting information ...
        #... close any open files ...
        GPIO.cleanup()
                
        if _ser != None:
                _ser.init()
                
        print "hf-io is closed..."
        sys.exit(0)
        

if __name__ == '__main__':  
        try:  
                signal.signal(signal.SIGINT, exit_gracefully)
                main()  
        except KeyboardInterrupt:
                if _ser != None:
                        _ser.init()






