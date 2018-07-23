#!/usr/bin/env python
# -*- coding: utf-8 -*  
import time
import threading
#import numpy
#import types
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
import traceback

import urllib2
#import urllib
import re
#G_DEVICE_TEMPERATURE 主板温度 一个主板就只有一个温度
#temp_can 夹具温度 SENSOR('temp_can')
logging.basicConfig(level=logging.ERROR,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='hf-control.log',
                filemode='w')

logging.error('program start:')



sys.path.append("./ext/rs232")
sys.path.append("./ext/rs485")
#sys.path.append("./ext/can")
sys.path.append("./ext/vcan")
sys.path.append("./protocol")



import protocol_rs485
import mcp2515
#import protocol_can
#import protocol_cancrc

#from rs232 import *
from rs485 import *
#import hf_can
#from hf_vcan import *

G_PARENT_PATH = "/.."
G_PATH = os.getcwd()
G_PATH_A = "/home/pi/hf_formation/run/data/history/"
G_PATH_Chilchen = None
G_START_STATION_TIME = None
G_DEBUG_BATTARRY_BAT = None
#获取当前的硬盘内存大小
def getDiskSpace():
    p = os.popen("df -m /")
    i = 0
    while True:
        i = i +1
        line = p.readline()
        if i==2:
            return(line.split()[1:5])


            
Disk_status = ""
#保存路径格式 /home/pi/hf_formation/run/data/history/日期/
def change_Disk_space():
    global G_PATH_Chilchen
    global G_PATH_A
    Disk_status = getDiskSpace()
    while int(Disk_status[2],10) <1024:
        file_list = []
        #遍历G_PATH_A目录下的所有路径
        for dirpath,dirnames,filenames in os.walk(G_PATH_A):
            #print "hello wold"
            #dirnames
            if len(dirnames) !=0:
                file_path = path+str(dirnames[0])
                if os.path.isdir(file_path):
                    for i in range(0,len(dirnames)):  
                        #type(dirnames[0])
                        #only one number user append
                        file_list.append(int(dirnames[i],10))
                        file_list1 = sorted(file_list,reverse=False)
                        #mydic = sorted(file_list.iteritems(),key = lambda asd:asd[0],reverse = False)
                else:
                    print "is not file_path"+file_path
            del_path = "rm -rf "+path+str(file_list1[0])
            os.system(del_path)
        Disk_status = getDiskSpace()    




        
def Create_battery_file():   
    global G_PATH_Chilchen
    global G_PATH_A
    global G_START_STATION_TIME
    #dat = None
    #dat = G_START_STATION_TIME
    #dat = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    #print "this is dat type:",type(dat)
    ls1 = re.split("[- :]",G_START_STATION_TIME)
    ls2 = [str(i) for i in ls1]
    path = G_PATH_A+ls2[0]+ls2[1]+ls2[2]+'/'+ ls2[3]+ls2[4]+ls2[5]
    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)
        print path+" makedir succese"
    else:
        print path+" is exists"
    G_PATH_Chilchen = path 
    #print path
  
  
    
    
reload(sys)
sys.setdefaultencoding('utf-8') 


'''
""" ==============================
计算--访问一个url
参数：
        url 地址
返回
        html 内容
"""
def getHtml(url):
        page = urllib.urlopen(url)
        html = page.read()
        return html
'''


""" ==============================
计算--读出文件
参数：
        filename 文件名
"""
def readfile(filename): 
        contents = ""
        try:
                fh = open(G_PATH + filename, 'r') 
                contents = fh.read()
                fh.close() 
        except Exception, e:
                logging.error('readfile error :' + str(e))
                pass
        return contents

""" ==============================
计算--以追加方式保存文件
参数：
        filename 文件名
        contents 追加内容
"""
def savefile(filename, contents, ty='a'): 
        try:
            fh = open(G_PATH + filename, ty) 
            fh.write(contents + "\n") 
        except Exception, e:
            logging.error('savefile error:' + e)
        fh.close() 


""" ==============================
计算--读出文件
参数：
        filename 文件名
"""
def getfile(filename): 
        contents = ""
        try:
                fh = open(filename, 'r') 
                contents = fh.read()
                fh.close() 
        except Exception, e:
                logging.error('readfile error :' + str(e))
                pass
        return contents
        
""" ==============================
计算--以追加方式保存文件
参数：
        filename 文件名
        contents 追加内容
"""
def writefile(filename, contents, ty='a'): 
        try:
            fh = open(filename, ty) 
            fh.write(contents + "\n") 
        except Exception, e:
            logging.error('savefile error:' + e)
        fh.close() 

        
        
""" ==============================
计算--清空文件内容
参数：
        filename 文件名
"""
def truncatefile(filename): 
        fh = open(G_PATH + filename, 'w+') 
        fh.truncate()
        fh.close()



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
动作--将工步整理成单循环形式-
参数：
        process   原process
返回：
        新process（无循环）
"""
def do_tranProcess(process):
    #new_process = {}
    cycle = 0
    step = 0
    obj_json = process
    new_process = copy.deepcopy(obj_json)
    
    #del new_process['process'][:]
    new_process['process'] = []
    for i in range( len(obj_json['process']) ):
        st = obj_json['process'][i]
        #如果是循环工步的话
        try:
            if st['station'] == 5:
                begin = int(st['beginStep'])-1
                end   = int(st['endStep'])-1
                tm    = int(st['times'])
                #找出0cycle的对应工步设置
                for k in range(0,len(new_process['process'])):
                    if new_process['process'][k]['cycle'] == 0 and new_process['process'][k]['step'] == begin:
                        begin = k
                    if new_process['process'][k]['cycle'] == 0 and new_process['process'][k]['step'] == end:
                        end = k
                
                for c in range(1,tm):
                    cycle = cycle + 1
                    for j in range(begin, end +1):
                        new_process['process'].append(new_process['process'][j].copy())
                        new_process['process'][-1]['cycle'] = new_process['process'][-1]['cycle'] + cycle
                step = step + 1
            else:
                st['cycle'] = 0
                st['step'] = step
                step = step + 1
                new_process['process'].append(st)
        except Exception, e:
            print "tranProcess error: ", str(e)

    #for i in range(0,len(new_process['process'])):
    #        print str(new_process['process'][i]['cycle']) + '-' + str(new_process['process'][i]['step'])
    last = {}
    last['cycle'] = 0
    last['step'] = step
    last['station'] = 6
    new_process['process'].append(last)
    #print new_process['process']
    try:
        for i in range(0, len(new_process['process'])):
            v = int(new_process['process'][i]['station'])
            new_process['process'][i]['station'] = v
            if 'time' in new_process['process'][i].keys() and new_process['process'][i]['time']:
                v = float(new_process['process'][i]['time'])
                new_process['process'][i]['time'] = v
            if 'upperVoltage' in new_process['process'][i].keys():
                if new_process['process'][i]['station'] in [1,2,4] and new_process['process'][i]['upperVoltage'] == "":
                    return None
                if new_process['process'][i]['upperVoltage']:
                    v = int(new_process['process'][i]['upperVoltage'])
                    new_process['process'][i]['upperVoltage'] = v
            if 'current' in new_process['process'][i].keys():
                if new_process['process'][i]['station'] in [1,2,4] and new_process['process'][i]['current'] == "":
                    return None
                if new_process['process'][i]['current']:
                    v = int(new_process['process'][i]['current'])
                    new_process['process'][i]['current'] = v
            if 'step' in new_process['process'][i].keys() and new_process['process'][i]['step']:
                v = int(new_process['process'][i]['step'])
                new_process['process'][i]['step'] = v
            if 'contact_check' in new_process['process'][i].keys() and new_process['process'][i]['contact_check']:
                v = int(new_process['process'][i]['contact_check'])
                new_process['process'][i]['contact_check'] = v
            if 'temp_supp_point' in new_process['process'][i].keys() and new_process['process'][i]['temp_supp_point']:
                v = float(new_process['process'][i]['temp_supp_point'])
                new_process['process'][i]['temp_supp_point'] = v
            if 'ccct_begin' in new_process['process'][i].keys() and new_process['process'][i]['ccct_begin']:
                v = float(new_process['process'][i]['ccct_begin'])
                new_process['process'][i]['ccct_begin'] = v
            if 'ccct_end' in new_process['process'][i].keys() and new_process['process'][i]['ccct_end']:
                v = float(new_process['process'][i]['ccct_end'])
                new_process['process'][i]['ccct_end'] = v
            if 'lowerVoltage' in new_process['process'][i].keys() and new_process['process'][i]['lowerVoltage']:
                v =int(new_process['process'][i]['lowerVoltage'])
                new_process['process'][i]['lowerVoltage'] = v
        pass
    except Exception, e:
        print "tranProcess: " + str(e)
        return None
        pass
        
    return new_process



"""
  ========================  主程序部分  =================================
"""
"""
  程序用于 3512 CN/8768LH 主板通讯协议
"""
"""
  =======================================================================
"""


'''
        全局变量定义
'''

#G_PROTOCOL = protocol_cancrc
#G_PROTOCOL = protocol_can
#G_PROTOCOL = protocol_rs
G_PROTOCOL = protocol_rs485

G_RESET = 0
G_CHG_CC = 1  #//恒流充电
G_CHG_CV = 2  #//恒压充电
G_WAIT = 3    #//搁置
G_DISCHG = 4  #//恒流放电
G_CYCLE = 5
G_FINISH = 6

G_MODULE_COUNT  = 10    #采样板数量
G_BATTERY_COUNT = 5   #每块采样板电池数量
G_BATTERY_COUNT_REAL = 48   #每块采样板电池数量

G_INIT_BATTERY_COUNT = 0 #上位机传下来的电池数量(不作使用)
G_RECV_DATA_BIT = 32   #接收电池电压数据位（8768L:24bit / 8256LH主板:32bit）
G_SEND_DATA_BIT = 32   #发送充放电电池电压数据位（8768L:16bit / 8256LH主板:32bit）

#系统变量
G_PROTOCOL.init(G_BATTERY_COUNT, G_SEND_DATA_BIT, G_RECV_DATA_BIT)
G_MAX_CHG = 60000
G_MAX_DISCHG = 60000
G_VERSION = "R807231524"

#动态变量
G_UNIT = ""
G_CHANNEL = ""
G_DEVICE_CODE = "FORMAT_0937"
G_WORKSTATION = "IC"
G_THIS_TRAY = ""
G_UNIT_STATUS = "IDLE"
#G_MES_URL = "http://192.168.0.116:2345"
#G_MES_URL = "http://www.sctmes.com:2345"
G_MES_URL = "http://192.168.125.240:2345"
G_ISINIT = False
G_LOOP_TIME = 5
G_CURVE_RATIO = 4
G_STEP_CURVE_SAVETIME = 0
G_DEVICE_TEMPERATURE_POINT = 1
G_COMMAND_QUEUE = Queue.Queue(maxsize = 0)
G_FAN_ON_TIME = 0
G_TEMP_SUPP_POINT = -1

G_TERMINALVOLTAGE_JSON = None
G_DO_RESET_START_TIME = None #None-野值, Not None-复位操作的开始时间
G_MAIN_START_TIME = None

G_PROCESS_CODE = ""
G_PROCESS_ORIGINAL = None #记录原始设定值，不展开的情况
G_PROCESS = None    #设定值LIST
G_PROCESS_IDX = 0   #当前设定值
G_DEBUG = 0
G_JIG_FAN_ON_START = 0 # 风机开始时间
G_JIG_FAN_ON_FLAG = 0
                    #设定值中需要*10获得精度的单位变量
G_PROCESS_LIST_PRECISE_ADJUSTMENT = ["current", "upperVoltage", "lowerVoltage", "stop_DeltaVoltage", 
                                                                      "stop_Current", "stop_Capacity", "curveDelta_voltage", "curveDelta_current"]

G_STEP_START_TIMESTAMP = 0
G_STEP_WORKTIME = 0
G_OPERATIONAL_MODE = "manual"  #"manual"#auto
G_DEVICE_EXP = 0
#G_DEVICE_MSG = {0:"", 1:"电池电压过高", 2:"电池接触检查异常"}
G_DEVICE_MSG = ""
G_DEVICE_TEMPERATURE = [0] * (G_MODULE_COUNT * G_DEVICE_TEMPERATURE_POINT)

#电池接触检查
G_CONTACT_CHECKED = False
G_CONTACT_CHECK_EXP = 0

#电压过高检查
G_OVER_VALTAGE_COUNT = 0

G_SENSOR = None

G_BATTERY_MAP = [0] * (G_MODULE_COUNT * G_BATTERY_COUNT)
G_BATTERY_UNMAP = [0] * (G_MODULE_COUNT * G_BATTERY_COUNT)
G_TEMPERATURE_MAP = [0] * (G_MODULE_COUNT * G_BATTERY_COUNT)

G_STACKER_STATUS = 0

G_TEMPERATURE_OVER_COUNT = [0] * G_MODULE_COUNT
G_JIG_TEMPERATURE_OVER_COUNT = 0
G_AUTO_TRAYIN_JJ_COUNT = 0

G_CURRENT_ERROR_COUNT = [0] *  (G_MODULE_COUNT * G_BATTERY_COUNT)

G_MES_TRAY_INFO = None

G_EXP_RECOVERY_BRANCH = 2 # 0-野值 1-继续 2-再做一次接触检查 3-MES信息不符重检
G_COMM_EXP_COUNTER = 0 #记录主板通讯异常的次数

G_LEAKAGE_CURRENT_DEBUG = 0
 
 
G_DEBUG_LED = 0
G_DEBUG_LED_TIME = None
_ser = None

del_list = []
file_dir = '/home/pi/hf_formation/run/data/'
del_list = os.listdir(file_dir)
for i in del_list:
    if (os.path.splitext(i)[1] == '.dat' or os.path.splitext(i)[1] == '.kdat')and str(os.path.splitext(i)[0]).isdigit() :
        tmp = str(os.path.splitext(i)[0])
        #print "tmp:",tmp
        #print "int_tmp:",int(tmp,10)
        all_battery = G_MODULE_COUNT * G_BATTERY_COUNT
        #print "all",all_battery
        
        if int(tmp,10) >= all_battery:
            print "os.path.splitext(i)[0]",int(str(os.path.splitext(i)[0]),10)
            os.remove(file_dir + str(os.path.splitext(i)[0] + os.path.splitext(i)[1]))
         



def init_can(reset=True,use_crc=True):
    global _ser
    _ser = rs232()
    #_ser = hf_vcan()
    #_ser = hf_can()
    #_ser.init(0,reset,use_crc) # vcan_init
    _ser.init(0,baud=115200)#rs485
    
def init_battery():
    global _battery_data_stop_flag_check
    global _battery_data_last_voltage
    global _battery_data_last_current
    _battery_data_stop_flag_check = [[0 for col in range(G_BATTERY_COUNT)] for row in range(G_MODULE_COUNT)]
    _battery_data_last_voltage = [0] * (G_MODULE_COUNT * G_BATTERY_COUNT)
    _battery_data_last_current = [0] * (G_MODULE_COUNT * G_BATTERY_COUNT)


def init_battery_map():
    global G_BATTERY_MAP
	
    for i in range(0,len(G_BATTERY_MAP)):
        G_BATTERY_MAP[i] = i
    for i in range(0, len(G_BATTERY_MAP)):
        G_BATTERY_UNMAP[G_BATTERY_MAP[i]] = i
    #print idx




    
    
def init_battery_map_chkchgv():
    global G_BATTERY_MAP
    c=0
    for i in range(0,8):
        R = 16-i*2
        L = 16-i*2-1
        R=R-1
        L=L-1
        for j in range(0,8):
            G_BATTERY_MAP[R+16*j] = c
            c=c+1
        for j in range(0,8):
            G_BATTERY_MAP[L+16*j] = c
            c=c+1    

    for i in range(0,8):
        R = 16-i*2
        L = 16-i*2-1
        R=R-1
        L=L-1
        for j in range(8,16):
            G_BATTERY_MAP[R+16*j] = c
            c=c+1
        for j in range(8,16):
            G_BATTERY_MAP[L+16*j] = c
            c=c+1
#	
#    for i in range(0,len(G_BATTERY_MAP)):
#        G_BATTERY_MAP[i] = i
    for i in range(0, len(G_BATTERY_MAP)):
        G_BATTERY_UNMAP[G_BATTERY_MAP[i]] = i

    #print idx
   

def init_temperature_map():
    global G_TEMPERATURE_MAP
    global G_BATTERY_COUNT
    pos = 0
    for i in range(0, 12):
        for j in range(0,4):  
            if (i*4+j)%6==0 and (i*4+j) >0: 
                pos = pos + 1               
            G_TEMPERATURE_MAP[i*4+j] = pos 
            print "G_TEMPERATURE_MAP[i*G_BATTERY_COUNT+j]:",i*4+j,"pos:",pos
    G_TEMPERATURE_MAP[48] = 0
    G_TEMPERATURE_MAP[49] = 0   

 

init_battery_map()
init_temperature_map()
init_can()

# 所有电池数据结构 (含所有控制板)
_battery_data = []
_battery_kv = []
_battery_data_stop_flag_check = []
_battery_data_last_voltage = [0] * (G_MODULE_COUNT * G_BATTERY_COUNT)
_battery_data_last_current = [0] * (G_MODULE_COUNT * G_BATTERY_COUNT)
_battery_data_contact_check = []
_battery_last_data_buffer = [0] * (G_MODULE_COUNT * 8)

#初始化电池数据
for count_battery in range(0, G_MODULE_COUNT * G_BATTERY_COUNT):
    _battery_data.append({"station":0, "step":0, "cycle":0, "time":0, "voltage": 0, "current": 0, "capacity": 0, "temperature": 0, "stop_flag":0, "stop_msg":"", "stop_time":0, "exp":"", "energy":0,"status_mod":0,"ccct_begin":0,"ccct_end":0, "terminal_exp": 0})
    _battery_data_contact_check.append({"chk_finish":0,"chk_current":0, "chk_current_+":0, "chk_current_-":0, "chk_voltage":0, "chk_voltage_+":0, "chk_voltage_-":0, "chk_battery":0})
    _battery_kv.append({'skip_save_once': False,'skip_save_once_start_time':0})

""" ==============================
动作-- init电池关键数据点
参数：
        
返回：
        Null
"""
def do_init_battery_key():
    global _battery_kv , _battery_data, G_PROCESS, G_PROCESS_IDX
    
    _battery_kv = []
    for i in range(0, G_MODULE_COUNT * G_BATTERY_COUNT):
        _battery_kv.append({
            "skip_save_once" : False,
            "skip_save_once_start_time" : 0,
            "capacity": round(_battery_data[i]['capacity'],1),
            "quantity": round(_battery_data[i]['energy'],1),
            "time":round(_battery_data[i]['time'],1),
            "open_voltage": _battery_data[i]['voltage'],
            #"open_current": _battery_data[i]['current'],
            "CVCurrentCha": _battery_data[i]['current']-5 if (_battery_data[i]['current']*0.01<5) else _battery_data[i]['current']*0.99 ,
            "AVG_voltage": _battery_data[i]['voltage'],
            "mid_voltage": None,
            #"sum_voltage": _battery_data[i]['voltage'],
            "count_voltage": 1,
            "end_voltage": 0,
            "end_current": 0,
            "temperature": 0,
            "ccct": None,
            "cvct": 0,
            "cccc": 0,
            "cvcc": 0,
            "cccp": 0,
            "cvcp": 0,
            "begin_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") ,
            "end_time": 0
            })
        
init_battery()
do_init_battery_key()

    
def sendHttpMessage(url, data):
    sendDone = False
    sendTime = 0
    ret = None
    f = None
    jobj = None
    while sendTime<5 and sendDone == False:
        try:
            params = json.dumps(data)
            req = urllib2.Request(url, headers = { "Content-Type": "application/x-www-form-urlencoded", "Accept": "*/*",  "User-Agent": "JApp/Gunio", }, data = params)
            f = urllib2.urlopen(req, timeout=5)
            ret = f.read()
            f.close()
            sendDone = True
            sendTime = sendTime +1
        except Exception,e:
            sendTime = sendTime +1
            if f != None:
                f.close
            time.sleep(1)
            pass

    if ret==None:
        raise Exception("MES通讯错误")
        #raise deviceException("MES通讯错误")
        
    try:
        jobj = json.loads(ret)
        if jobj["errcode"] >0:
            raise Exception(jobj["errmsg"])
    except Exception, e:
        raise Exception("MES返回JSON异常")
        
    return jobj
    

    
def sendUDPMessage(message, port=9099):
    address = ('127.0.0.1', port)
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setblocking(0)
    r_buffer = ""
    time.sleep(0.02)
    tmBegin = time.time()
    s.sendto(message, address)
    
    while time.time()-tmBegin < 2:
        try:
            data, addr = s.recvfrom(65526)
            r_buffer = r_buffer + data
            json.loads(r_buffer)
            s.close()
            return r_buffer
        except Exception, e:
            pass   
        time.sleep(0.05)
    s.close()  
    return ""



""" ==============================
线程--UDP接收线程
          用于与UI端进行json命令通讯（即时返回）
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
                sock.bind(('', 9088))       # 绑定同一个域名下的所有机器  
                while True: 
                    try:
                        revcData, (remoteHost, remotePort) = sock.recvfrom(65526)
                        #print "recvData:",recvData
                        #print "a\n"
                        ret = do_json_command_solver(revcData)
                        #print("[%s:%s] connect" % (remoteHost, remotePort))     # 接收客户端的ip, port  
                        #"{'success':'true'}" json.dumps(_battery_data)
                        #print "b\n"
                        #分包发送
                        if len(ret)>32768:
                                #savefile("/battery_data.dat", ret, "w")
                                n = len(ret) / 32768
                                m = len(ret) % 32768
                                #print "nm: " + str(n) + "-" + str(m)
                                for i in range(0,n):
                                        #print ret[i*32768:i*32768+32768]
                                        sock.sendto(ret[i*32768:i*32768+32768], (remoteHost, remotePort)) 
                                
                                #print ret[(i+1)*32768:(i+1)*32768+m]
                                
                                sock.sendto(ret[(i+1)*32768:(i+1)*32768+m], (remoteHost, remotePort))
                        else:
                                sock.sendto(ret, (remoteHost, remotePort))
                        #print "c\n"       
                    except Exception, e:
                        print "udp thread:", str(e)
                        obj_ret = {}
                        obj_ret['success'] = False
                        obj_ret['msg'] = 'ip error'
                        ret = json.dumps(obj_ret)
                        sock.sendto(ret, (remoteHost, remotePort))
                        pass
                        #print "revcData: ", revcData  
                        #print "sendDataLen: ", sendDataLen  

                sock.close() 
                
                
""" ==============================
线程-- IO读取线程
参数：
        ==
返回：
        ==
"""
class cls_io_recv_Thread(threading.Thread):
        def __init__(self, name):
                threading.Thread.__init__(self)
                self.t_name = name

        def run(self):
            global G_SENSOR
            global G_DEVICE_TEMPERATURE
            global G_CHANNEL
            global G_UNIT
            global G_OPERATIONAL_MODE
            global G_THIS_TRAY
            global G_MES_URL
            global G_DEVICE_CODE
            global G_PROCESS
            global G_PROCESS_IDX            

            while True: 
                #每2s获取IO状态和设备温度信息
                #读取IO IN
                ret_msg = sendUDPMessage('{"action":"sensor_read"}')
                if ret_msg != "":
                    obj = json.loads(ret_msg)
                    obj["temp_board"] = G_DEVICE_TEMPERATURE
                    obj["unit"] = G_UNIT
                    obj["channel"] = G_CHANNEL
                    G_SENSOR = copy.deepcopy(obj)
                    #print "G_SENSOR",G_SENSOR
                    del obj
                else:
                    G_SENSOR = None
                    
                time.sleep(0.5)
                pass
                
""" ==============================
线程-- MES信息上传线程
参数：
        ==
返回：
        ==
"""
class cls_mes_heartbeat_Thread(threading.Thread):
        m_lastStation = 0
        m_station =0
        def __init__(self, name):
                threading.Thread.__init__(self)
                self.t_name = name

        def run(self):
            global G_DEVICE_CODE
            global G_UNIT_STATUS

            while True: 
                #每2s获取IO状态和设备温度信息
                #读取IO IN
                try:
                    if get_device_exp()>=4000:
                        sendHttpMessage(G_MES_URL, {"action": "set_device_status", "param": {"DEVICE_CODE": G_DEVICE_CODE, "STATUS": G_UNIT_STATUS, "MSG": "ERR:" + str(get_device_exp())}})
                    else:
                        sendHttpMessage(G_MES_URL, {"action": "set_device_status", "param": {"DEVICE_CODE": G_DEVICE_CODE, "STATUS": G_UNIT_STATUS}})
                except Exception,e:
                    set_device_exp(4000, "MES系统连接异常" + str(e))
                    print e
                finally:
                    time.sleep(1)
                    pass
                
'''
@fn		lftp_uploader
@brief		function to upload file to ftp server
@param[in]	param_dict
		The parameter for this function
@param[in]	param_dict['ipaddr']
		IP address
@param[in]	param_dict['user_name']
		User name
@param[in]	param_dict['passwd']
		Password
@param[in]	param_dict['file_name']
		File name
@param[in]	param_dict['extra_opts']
		Extra options
@return		=0, success; !=0, fail
'''  
def lftp_uploader(param_dict):
    site = ""
    user = ""
    passwd = ""
    file = ""
    extra_opts = ""
    cmd = ""
    command = ""

    key_sets = ["site", "user", "passwd", "file", "cmd", "extra_opts"]

    for key in key_sets:
        if  key in param_dict.keys():
            if  param_dict[key] != None:
                if  key == "site":
                    site = param_dict[key]
                elif key == "user":
                    user = param_dict[key]
                elif key == "passwd":
                    passwd = param_dict[key]
                elif key == "file":
                    file = param_dict[key]
                elif key == "extra_opts":
                    extra_opts = param_dict[key]
                elif key == "cmd":
                    cmd = param_dict[key]

    #print "site = ", site
    #print "user = ", user
    #print "passwd = ", passwd
    #print "file = ", file
    #print "cmd = ", cmd
    #print "extra_opts = ", extra_opts

    command  = "lftp -e "
    command += "\"open -u " + user + "," + passwd + " " + site + ";"
    command += extra_opts
    command += "cd "+ file + "; "
    command += "mput ./data/*; "
    command += "exit; "
    command += "\" &"

    #print command

    os.system(command)    

'''
@fn		do_upload_battery_data_files
@brief		This function upload battery data files to ftp server
'''
def do_upload_battery_data_files():
    global G_DEVICE_CODE
    global G_MES_URL

    batch = ""
    lot = ""
    tray = ""
    process_code = ""
    this_tray = ""
    mes_tray_info = ""
    site = ""
    file_name = "/batch/lot/tray/process_code"
    param_dict = {}

    param_dict['site'] = "www.sctmes.com:1234"
    param_dict['user'] = "http"
    param_dict['passwd'] = "123"
    param_dict['cmd'] = "-e 'mirror'"
    param_dict['extra_opts'] = "extra_opts"  

    try:
        jobj = sendHttpMessage(G_MES_URL, {"action": "get_device_this_tray", "param": {"DEVICE_CODE": G_DEVICE_CODE}})
        if  jobj["errcode"] >0:
            set_device_exp(4003, jobj["errmsg"])
                                    
        this_tray = jobj["rtval"]["tray"]

        jobj = sendHttpMessage(G_MES_URL, {"action": "get_process_route", "param": {"TRAY": this_tray}})
        if  jobj["errcode"] >0:
            set_device_exp(4003, jobj["errmsg"])

        process_code = jobj["rtval"]["lastProcess"]
    
        jobj_battery = sendHttpMessage(G_MES_URL, {"action": "get_tray_info","process_code":process_code, "param": {"TRAY": this_tray}})
        if  jobj_battery["errcode"] >0:
            set_device_exp(4003, jobj_battery["errmsg"])

        mes_tray_info = jobj_battery["rtval"];

        #print mes_tray_info

        batch = mes_tray_info['BATCH']
        lot = mes_tray_info['LOT']
        tray = mes_tray_info['TRAY']
     
        file_name = str(batch)+"/"+str(lot)+"/"+str(tray)+"/"+str(process_code)  
        print "Remote ftp dir name:", file_name

        site = list(re.findall(r'[0-9]+(?:\.[0-9]+){3}', G_MES_URL))[0]
    except Exception, e:
        print str(e)
        return
        
    param_dict['file'] = file_name
    param_dict['site'] = site 
    param_dict['user'] = "mes"
    param_dict['passwd'] = "mes"
    param_dict['cmd'] = ""
    param_dict['extra_opts']  = "set net:timeout 10; "
    param_dict['extra_opts'] += "set net:max-retries 2; "
    param_dict['extra_opts'] += "set net:reconnect-interval-base 5; "
    param_dict['extra_opts'] += "set net:reconnect-interval-multiplier 1; "

    lftp_uploader(param_dict)
                
def send_mes_set_process_result():
    global G_THIS_TRAY
    global G_PROCESS_CODE
    global G_DEVICE_CODE
    global G_MODULE_COUNT
    global G_BATTERY_COUNT
    global G_TEMP_SUPP_POINT
    global G_MES_TRAY_INFO
    
    jsontext_process_data = readfile("/data/process.dat")
    jsontext_tray_info        = readfile("/data/mes_tray_info.dat")
    '''
    jsontext_process_data = getfile(G_PATH_Chilchen +"/process.dat")
    jsontext_tray_info        = getfile(G_PATH_Chilchen +"/mes_tray_info.dat")
    '''
    

    if jsontext_process_data != "":
        obj_json = json.loads(jsontext_process_data)
        G_THIS_TRAY = obj_json["tray"]
        if 'temp_supp_point' in obj_json['process'][0].keys():
            G_TEMP_SUPP_POINT = obj_json['process'][0]["temp_supp_point"]
        
        if G_PROCESS_CODE == "":
            try:
                jobj = sendHttpMessage(G_MES_URL, {"action": "get_process_route", "param": {"TRAY": G_THIS_TRAY}})
            except Exception, e:
                set_device_exp(4000, str(e))
                print e
                return
            
            if jobj["errcode"] >0:
                set_device_exp(4003, jobj["errmsg"])
                return
            #获取PROCESS CODE
            G_PROCESS_CODE = jobj["rtval"]["nextProcess"]
        pass
        
    if jsontext_tray_info != "":
        G_MES_TRAY_INFO = json.loads(jsontext_tray_info)
        pass
    
    #准备结果数据
    m_begin = 0
    m_step = 0
    m_temp_supp = 0
    m_ng = 0
    data = {"action":"set_process_result", "process_code":G_PROCESS_CODE , "param":{"TRAY":G_THIS_TRAY, "DEVICE_CODE":G_DEVICE_CODE}}
    m_battery_count = len(G_MES_TRAY_INFO["BATTERY_IDS"])
    
    for i in range(0, G_MODULE_COUNT * G_BATTERY_COUNT):
        #超过登陆的电池数目，跳出
        if i > m_battery_count-1:
            break
    
        s = readfile("/data/" + str(i).zfill(4) + ".kdat")
        #s = getfile( G_PATH_Chilchen +'/' + str(i).zfill(4) + ".kdat")
        l = s.split("\n")
        
        if i==0:
            data['param']['PIN_CHECK']  = []
            data['param']['NG']  = []
            data['param']['TEMPERATURE']  = []
            #初始化结果数据的结构
            for p in range(0, len(l)-1):
                data['param']['OCV' + str(p).zfill(2)]  = []
                data['param']['ENDV' + str(p).zfill(2)]  = []
                data['param']['ENDC' + str(p).zfill(2)]  = []
                data['param']['ENDT' + str(p).zfill(2)]  = []
                data['param']['SPWT' + str(p).zfill(2)] = [] #step worktime
                data['param']['COCC' + str(p).zfill(2)] = [] #cut-off charging current
                
        m_step = 0
        for ls in l:
            if ls=="":
                break
            a = ls.split(",")
            capacity = a[0]
            quantity = a[1]
            time = a[2]
            open_voltage = a[3]
            AVG_voltage = a[4]
            mid_voltage = a[5]
            end_voltage = a[6]
            end_current = a[7]
            temperature = a[8]
            ccct = a[9]
            cvct = a[10]
            cccc = a[11]
            cvcc = a[12]
            cccp = a[13]
            cvcp = a[14]
            begin_time = a[15]
            end_time = a[16]
            stop_flag =int(a[17])
            stop_msg =a[18]
            
            if G_TEMP_SUPP_POINT>0:
                #本工步温度作为补偿温度
                if G_TEMP_SUPP_POINT==m_step+1:
                    m_temp_supp = temperature
                    
            data['param']['OCV' + str(m_step).zfill(2)].append(round(float(open_voltage), 1))
            data['param']['ENDV' + str(m_step).zfill(2)].append(round(float(end_voltage), 1))
            data['param']['ENDC' + str(m_step).zfill(2)].append(round(float(capacity), 1))
            data['param']['ENDT' + str(m_step).zfill(2)].append(round(float(temperature), 1))
            data['param']['SPWT' + str(m_step).zfill(2)].append(round(float(time), 1)) 
            data['param']['COCC' + str(m_step).zfill(2)].append(round(float(end_current), 1)) 
            
            m_step = m_step + 1        
        pass
        
        if int(G_MES_TRAY_INFO["ACTIVE"][i]) == 1:
            if stop_flag > 3000:
                #单点NG
                data['param']['PIN_CHECK'].append(1)
                data['param']['NG'].append(stop_flag)
                if G_TEMP_SUPP_POINT>0:
                    data['param']['TEMPERATURE'].append(m_temp_supp)
                pass
            else:
                data['param']['PIN_CHECK'].append(0)
                data['param']['NG'].append(0)
                if G_TEMP_SUPP_POINT>0:
                    data['param']['TEMPERATURE'].append(m_temp_supp)
        else:
                data['param']['PIN_CHECK'].append(0)
                data['param']['NG'].append(0)
                if G_TEMP_SUPP_POINT>0:
                    data['param']['TEMPERATURE'].append(m_temp_supp)
                
    try:
        jobj = sendHttpMessage(G_MES_URL, data)
    except Exception, e:
        set_device_exp(4000, "MES系统连接异常" + str(e))
        print e
        pass
    print "done"
    print json.dumps(data, sort_keys = True)
 
""" ==============================
线程--UDP接收线程
          用于与UI端进行json命令通讯（即时返回）
参数：
        ==
返回：
        ==
"""
def tray_exit():
    if G_SENSOR is not None:
        if  G_SENSOR["io"]["IN"]["Tray_Exist_RR"] == 1\
        or G_SENSOR["io"]["IN"]["Tray_Exist_RF"] == 1\
        or G_SENSOR["io"]["IN"]["Tray_Exist_LR"] == 1\
        or G_SENSOR["io"]["IN"]["Tray_Exist_LF"] == 1:
            return True
        else:
            return False
    else:
        return False
        
        
class exception_deal_Thread(threading.Thread):
        def __init__(self, name):
                threading.Thread.__init__(self)
                self.t_name = name

        def run(self):
            global G_SENSOR
            global G_FAN_ON_TIME
            global G_JIG_TEMPERATURE_OVER_COUNT
            global G_EXP_RECOVERY_BRANCH
            global G_DO_RESET_START_TIME
            global G_MAIN_START_TIME
            global G_JIG_FAN_ON_START
            global G_JIG_FAN_ON_FLAG

                        
            G_FAN_ON_TIME = time.time()
            #_last_power_status = 1
            _last_device_exp = 0
            _set_process_result = 0
            while True: 
                #C类异常
                #print "exp:" + str(get_device_exp())
                
                if _last_device_exp<4000:
                    if get_device_exp()>=4000 and get_device_exp()<4100:
                        do_exception_C()
                        
                    if get_device_exp()>=4100 and get_device_exp()<4199:
                        do_exception_B()
                        
                    if get_device_exp()>=4200 :
                        do_exception_A()
                    _last_device_exp = get_device_exp()
                    
                if get_device_exp()==0:
                    _last_device_exp = 0  

                #当有高级设备异常发生时，也要更新SMOKE_PLC和TEMPFUSE_PLC，安全第一 -_-!
                if  G_SENSOR != None and get_device_exp()>=4000:
                    if  G_SENSOR["io"]["IN"]["FIRE_CLOSE"] == 0 and tray_exit() == True:
                        #实时更新SMOKE_PLC 和 TEMPFUSE_PLC
                        smoke = G_SENSOR["io"]["IN"]["Smoke_R"] == 1 or G_SENSOR["io"]["IN"]["Smoke_L"] == 1
           
                        #temp_fuse = G_SENSOR["io"]["IN"]["TEMPFUSE"]
                
                        io_out = {}

                        io_out["SMOKE_PLC"] = 0
                        io_out["ALLBOX_OPEN"] = 0
                        io_out["TEMPFUSE_PLC"] = 0

                        if  smoke:
                            io_out["SMOKE_PLC"] = 1
                        '''
                        if  temp_fuse:
                            io_out["TEMPFUSE_PLC"] = 1
                        if  smoke or temp_fuse:
                            io_out["ALLBOX_OPEN"] = 1
                        '''
                        do_setIO(io_out)

                #如果已经有高级设备异常 (4000开始才是高级设备异常，最高优先级) ，则不判断
                if get_device_exp()<4000:
                    #当有IO进程，进行机柜IO判定
                    if G_SENSOR != None:
                        '''
                        #风机异常 开机前、复位后10s内不判定 G_PI_START_TIME中位机开机时间
                        if  G_DO_RESET_START_TIME is not None:
                            if  time.time() - G_DO_RESET_START_TIME > 10:
                                if  G_SENSOR["io"]["IN"]["JIG_FAN_ERR"] == 1:
                                    set_device_exp(4305, "风机异常")
                        elif G_DO_RESET_START_TIME is None and G_MAIN_START_TIME is not None:
                            if  time.time() - G_MAIN_START_TIME > 10:
                                if  G_SENSOR["io"]["IN"]["JIG_FAN_ERR"] == 1:
                                    set_device_exp(4305, "风机异常")
                        '''   
                        
                        if time.time() - G_JIG_FAN_ON_START > 10 and G_JIG_FAN_ON_FLAG ==1:
                            if  G_SENSOR["io"]["IN"]["JIG_FAN_ERR"] == 1:
                                set_device_exp(4305, "风机异常")
                                
                        
                                
                        #当EMG按键按下，触发B类警报
                        #print "emg",G_SENSOR["io"]["IN"]["EMG"]
                        if G_SENSOR["io"]["IN"]["EMG"] == 1:
                            do_exception_B()
                            set_device_exp(4303, "紧急停止")
                            
                        #夹具温度高于50度报警
                        #print "tmp_can:",G_SENSOR['temp_can']
                        if  G_SENSOR['temp_can'] != None:
                            temp_over = False
                            for t in G_SENSOR['temp_can']:
                                if t > 50:
                                    temp_over = True
                                    break
                                    
                            if  temp_over == True:
                                G_JIG_TEMPERATURE_OVER_COUNT  = G_JIG_TEMPERATURE_OVER_COUNT +1
                                if  G_JIG_TEMPERATURE_OVER_COUNT > 4:
                                    #夹具温度高于50度 +3次 报警
                                    set_device_exp(4207, "夹具温度过高报警")
                            else:
                                G_JIG_TEMPERATURE_OVER_COUNT = 0
                                
                        io_out = {}

                        io_out["SMOKE_PLC"] = 0
                        io_out["ALLBOX_OPEN"] = 0
                        io_out["TEMPFUSE_PLC"] = 0
                        
                        #烟雾或者温度保险丝异常，触发
                        if  G_SENSOR["io"]["IN"]["Smoke_R"] == 1 or G_SENSOR["io"]["IN"]["Smoke_L"] == 1:
                            #烟雾报警
                            set_device_exp(4301, "烟雾报警")
                            if tray_exit() == True:
                                if  G_SENSOR["io"]["IN"]["FIRE_CLOSE"] == 0:
                                    io_out["SMOKE_PLC"] = 1
                                    io_out["ALLBOX_OPEN"] = 1
                           
                        if  G_SENSOR["io"]["IN"]["TEMPFUSE"] == 1:
                            #温度保险丝报警
                            set_device_exp(4302, "温度保险丝报警")
                            if  G_SENSOR["io"]["IN"]["Tray_Exist_RR"] == 1\
                            or G_SENSOR["io"]["IN"]["Tray_Exist_RF"] == 1\
                            or G_SENSOR["io"]["IN"]["Tray_Exist_LR"] == 1\
                            or G_SENSOR["io"]["IN"]["Tray_Exist_LF"] == 1:
                                if  G_SENSOR["io"]["IN"]["FIRE_CLOSE"] == 0:
                                    io_out["TEMPFUSE_PLC"] = 1
                                    io_out["ALLBOX_OPEN"] = 1
                        
                        #print "allbox_open",G_SENSOR["io"]["IN"]["ALLBOX_OPEN"]
                        '''
                        if  G_SENSOR["io"]["IN"]["ALLBOX_OPEN"] == 1:
                            set_device_exp(4303, "紧急停止")
                        '''   
                        do_setIO(io_out)
                        
                time.sleep(0.5)
                pass    


            
""" ==============================
线程--UDP接收线程
          用于与UI端进行json命令通讯（即时返回）
参数：
        ==
返回：
        ==
"""
class cls_comm_control_Thread(threading.Thread):
        def __init__(self, name):
                threading.Thread.__init__(self)
                self.t_name = name

        def run(self):
            global G_SENSOR
            global G_DEVICE_TEMPERATURE
            global G_DEVICE_CODE
            global G_PROCESS
            global G_PROCESS_IDX
            global G_STEP_CURVE_SAVETIME
            global G_STEP_WORKTIME
            global G_CONTACT_CHECKED
            global G_CONTACT_CHECK_EXP
            global G_FAN_ON_TIME
            global G_JIG_TEMPERATURE_OVER_COUNT
            global G_AUTO_TRAYIN_JJ_COUNT
            global G_EXP_RECOVERY_BRANCH
            
            global G_DEBUG_LED_TIME
            global G_DEBUG_LED
            
            G_STACKER_STATUS = 0
            G_FAN_ON_TIME = time.time()
            
            
            #_last_power_status = 1
            _last_device_exp = 0
            _set_process_result = 0
            while True: 
                try:
                    #判断4分钟后停止风机,for debug，添加Process ！= None的判断，实际生产去掉
                    #自动发送设定值逻辑  (判断有托盘在设备里面，开始下压托盘，并且读取MES设定值并发送)
                    if G_DEBUG_LED ==0 or (G_DEBUG_LED==1 and time.time()-G_DEBUG_LED_TIME > 10):
                        G_DEBUG_LED = 0
                        status = "IDLE"
                        if G_PROCESS != None:
                            if  G_PROCESS['process'][G_PROCESS_IDX]['station'] == 6 \
                                and G_PROCESS_IDX != -1:

                                status = "FINISH"
                                do_Led_Ready()
                            else:
                                status = "RUN"
                                _set_process_result = 0
                                #do_fan_on()
                                do_Led_Run()
                            
                        #if G_OPERATIONAL_MODE == "manual":
                        #    status = "PAUSE"
                        
                        if get_device_exp()>=4000 :
                            status = "TROUBLE"
                            do_fan_off()
                            do_Led_Error()
                            
                        if status == "IDLE":
                            do_Led_Ready()
                        G_UNIT_STATUS = status                         
                        pass
                except Exception, e:
                    #set_device_exp(4000, "MES系统连接异常" + str(e))
                    print "auto loop: " + str(e)
                    pass      
                
                time.sleep(1)
                pass

def do_on_stacker_empty():
    global G_SENSOR
    if G_SENSOR["io"]["IN"]["FINISH"] == 0 and G_SENSOR["io"]["IN"]["STACKER_IN"] == 0:
        return True
    return False
                
def do_on_stacker_busy():
    global G_SENSOR
    if G_SENSOR["io"]["IN"]["FINISH"] == 0 and G_SENSOR["io"]["IN"]["STACKER_IN"] == 1:
        return True
    return False
    
def do_on_stacker_finish():
    global G_SENSOR
    if G_SENSOR["io"]["IN"]["FINISH"] == 1 and G_SENSOR["io"]["IN"]["STACKER_IN"] == 1:
        return True
    return False
        
def do_stacker_pickup():
    try:
        io_out = {}
        io_out["PICK_UP"] = 1
        io_out["DROP_OFF"] = 0
        io_out["CELL_RESPONSE"] = 0
        do_setIO(io_out)
    except Exception, e:
        print "STACKER: ", str(e)
        pass

def do_stacker_dropoff():
    try:
        io_out = {}
        io_out["PICK_UP"] = 0
        io_out["DROP_OFF"] = 1
        io_out["CELL_RESPONSE"] = 0
        do_setIO(io_out)
    except Exception, e:
        print "STACKER: ", str(e)
        pass

def do_stacker_busy():
    try:
        io_out = {}
        io_out["PICK_UP"] = 0
        io_out["DROP_OFF"] = 0
        io_out["CELL_RESPONSE"] = 0
        do_setIO(io_out)
    except Exception, e:
        print "STACKER: ", str(e)
        pass

                
def do_turn_mc( val ):
    try:
        io_out = {}
        io_out["MC_ON"] = int(val)
        do_setIO(io_out)
    except Exception, e:
        print "turn mc:", str(e)
        pass
    pass

    
def do_Led_Ready():
    try:
        io_out = {}
        io_out["LED_READY"] = 1
        io_out["LED_RUN"] = 0
        io_out["LED_ERROR"] = 0
        do_setIO(io_out)
    except Exception, e:
        print "LED:", str(e)
        pass


def do_Led_Run():
    try:
        io_out = {}
        io_out["LED_READY"] = 0
        io_out["LED_RUN"] = 1
        io_out["LED_ERROR"] = 0
        do_setIO(io_out)
    except Exception, e:
        print "LED:", str(e)
        pass
        
def do_Led_Error():
    try:
        io_out = {}
        io_out["LED_READY"] = 0
        io_out["LED_RUN"] = 0
        io_out["LED_ERROR"] = 1
        do_setIO(io_out)
    except Exception, e:
        print "LED:", str(e)
        pass   
    
    
""" ==============================
动作--托盘松开

参数：
        null
返回：
        null
"""
def do_tray_release():
    print "do_tray_release"
    global G_SENSOR
    io_out = {}    
    #open griper
    try:
        if G_SENSOR["io"]["IN"]["Gripper_R1"] == -1 and G_SENSOR["io"]["IN"]["Gripper_R2"] == -1:
            print "have not can board"
            return True

        io_out.clear()
        io_out["GRIPPER_ON_SOL"] = 0
        do_setIO(io_out)
        print "do_tray_release open the griper"       
        io_done = False   
        start = time.time()
        while time.time()-start < 20 :
            time.sleep(0.5)    
            if  G_SENSOR["io"]["IN"]["Gripper_L1"] ==0  \
                and G_SENSOR["io"]["IN"]["Gripper_L2"] ==0 \
                and G_SENSOR["io"]["IN"]["Gripper_R1"] ==0 \
                and G_SENSOR["io"]["IN"]["Gripper_R2"] ==0 :
                io_out.clear()
                io_out["ForwoBackrd_SOL"] = 0
                do_setIO(io_out)  
                print "return th origin"
                io_done = True
                break
        if not io_done:
            set_device_exp(4006, "TRAY松开异常")
            return False

        if  G_SENSOR["io"]["IN"]["GripperBack_L"] ==1 \
            and G_SENSOR["io"]["IN"]["GripperBack_R"]==1:
            print "sucess release thea tray"    
            #break              
    except Exception, e:
        print "tray:", str(e)
        pass 
    pass 


def do_tray_release_without_check():
    print "do_tray_release"
    global G_SENSOR
    io_out = {}    
    #open griper
    try:
        if G_SENSOR["io"]["IN"]["Gripper_R1"] == -1 and G_SENSOR["io"]["IN"]["Gripper_R2"] == -1:
            print "have not can board"
            return True

        io_out.clear()
        io_out["GRIPPER_ON_SOL"] = 0
        do_setIO(io_out)
        print "do_tray_release open the griper"       
        io_done = False   
        start = time.time()
        while time.time()-start < 20 :
            time.sleep(0.1)    
            if  G_SENSOR["io"]["IN"]["Gripper_L1"] ==0  \
                and G_SENSOR["io"]["IN"]["Gripper_L2"] ==0 \
                and G_SENSOR["io"]["IN"]["Gripper_R1"] ==0 \
                and G_SENSOR["io"]["IN"]["Gripper_R2"] ==0 :
                io_out.clear()
                io_out["ForwoBackrd_SOL"] = 0
                do_setIO(io_out)  
                print "return th origin"
                io_done = True
                break
        if not io_done:
            set_device_exp(4006, "TRAY松开异常")
            return False

        if  G_SENSOR["io"]["IN"]["GripperBack_L"] ==1 \
            and G_SENSOR["io"]["IN"]["GripperBack_R"]==1:
            print "sucess release thea tray"    
            #break              
    except Exception, e:
        print "tray:", str(e)
        pass 
    pass 

   
def do_power_fan_off():
    io_out = {}
    io_out["POWER_FAN"] = 0
    do_setIO(io_out)
    pass
	
	
def do_fan_on():
    global G_JIG_FAN_ON_START
    global G_JIG_FAN_ON_FLAG
    io_out = {}
    io_out["POWER_FAN"] = 1
    io_out["JIG_FAN"] = 1
    io_out["JIG_FAN_CAN"] = 1
    do_setIO(io_out)
    G_JIG_FAN_ON_START = time.time()
    G_JIG_FAN_ON_FLAG = 1
    pass
    
def do_fan_off():
    global G_JIG_FAN_ON_FLAG
    io_out = {}
    io_out["POWER_FAN"] = 0
    io_out["JIG_FAN"] = 0
    io_out["JIG_FAN_CAN"] = 0
    do_setIO(io_out)
    G_JIG_FAN_ON_FLAG = 0
    pass
    
    
""" ==============================
动作--托盘扣紧

参数：
        null
返回：
        null
"""
def do_tray_fastening():
    print "do_tray_fastening"
    global G_SENSOR
    io_out = {}
    start = time.time()
    io_done = False
    while time.time()-start<20:
        print "time:", str(time.time()-start)
        time.sleep(0.5)
        if  G_SENSOR["io"]["IN"]["GripperForword_L"] == 0 \
            and  G_SENSOR["io"]["IN"]["GripperForword_R"] == 0 \
            and G_SENSOR["io"]["IN"]["GripperBack_L"] == 1 \
            and G_SENSOR["io"]["IN"]["GripperBack_L"] == 1:
            io_done = True
            break   
                    
    if not io_done:
        set_device_exp(4010, "不在原点")
        do_tray_release()
        return False



    io_out["GRIPPER_ON_SOL"] = 1
    do_setIO(io_out)
    start = time.time()
    io_done = False
    while time.time()-start<20:
        time.sleep(0.5)
        if G_SENSOR["io"]["IN"]["Gripper_L1"] == 1 \
           and  G_SENSOR["io"]["IN"]["Gripper_L2"] == 1 \
           and G_SENSOR["io"]["IN"]["Gripper_R1"] == 1 \
           and  G_SENSOR["io"]["IN"]["Gripper_R2"] == 1:
            io_done = True
            print "do_tray_fastening,GRIPPER_ON_SOL =1"
            break           
    if not io_done:
        set_device_exp(4004, "LATCH锁紧异常")
        do_tray_release_without_check()
        return False


        
    io_out.clear()
    io_out["GRIPPER_ON_SOL"] = 0
    do_setIO(io_out)
    start = time.time()
    io_done = False
    while time.time()-start<20:
        print "time1:", str(time.time()-start)
        time.sleep(0.5)
        if G_SENSOR["io"]["IN"]["Gripper_L1"] == 0 \
           and  G_SENSOR["io"]["IN"]["Gripper_L2"] == 0 \
           and G_SENSOR["io"]["IN"]["Gripper_R1"] == 0 \
           and  G_SENSOR["io"]["IN"]["Gripper_R2"] == 0:
            io_done = True
            print "do_tray_fastening,GRIPPER_ON_SOL =0"
            break           
    if not io_done:
        set_device_exp(4007, "LATCH松开异常")
        return False

""" ==============================
动作--托盘压紧

参数：
        null
返回：
        null
"""
def do_tray_compact():

    global G_SENSOR
    
    #do_reset()
    #set_device_exp(0, "")
    #time.sleep(2)
    #当没有CAN板的时候，直接返回
    #if G_SENSOR and G_SENSOR["io"]["IN"]["LATCH_ON_LEFT"] == -1 and G_SENSOR["io"]["IN"]["JIG_DOWN_SENSE"]==-1:
    #    return True
    #print "G_SENSOR["io"]["IN"]["Tray_Exist_RR"]",G_SENSOR["io"]["IN"]["Tray_Exist_RR"]

    try:
        if  G_SENSOR["io"]["IN"]["Gripper_R1"] == -1 \
            and G_SENSOR["io"]["IN"]["Gripper_R2"] == -1:
            print "have not can board"
            return True

        print "Tray_Exist_LR",G_SENSOR["io"]["IN"]["Tray_Exist_LR"]

        if  G_SENSOR["io"]["IN"]["Tray_Exist_LR"] == 0 \
            or G_SENSOR["io"]["IN"]["Tray_Exist_LF"]==0 \
            or G_SENSOR["io"]["IN"]["Tray_Exist_RR"] == 0 \
            or G_SENSOR["io"]["IN"]["Tray_Exist_RF"]==0:
            print "not_in the place"
            do_tray_release()
            set_device_exp(4009, "TRAY_IN异常")
            return False
        else:
            print "in place"
        #do_tray_fastening()       
        if  G_SENSOR["io"]["IN"]["Tray_Exist_LR"] == 1 \
            and G_SENSOR["io"]["IN"]["Tray_Exist_RF"]==1 \
            and G_SENSOR["io"]["IN"]["Tray_Exist_LR"] == 1 \
            and G_SENSOR["io"]["IN"]["Tray_Exist_LF"]==1:
            if G_SENSOR["io"]["IN"]["Tray_Chamfer"] == 1:
                print "TRAY缺口位异常"
                set_device_exp(4008, "TRAY缺口位异常")
                do_tray_release()
                return False
            # tray ok ,continue to do next
            else:

                io_out = {}
                io_out.clear()
                io_out["GRIPPER_ON_SOL"] = 0        #open the gripper
                do_setIO(io_out)
                start = time.time()
                io_done = False
                while time.time() - start < 20:
                    time.sleep(0.5)
                    if  G_SENSOR["io"]["IN"]["Gripper_L1"] == 0 \
                        or  G_SENSOR["io"]["IN"]["Gripper_L2"] == 0 \
                        or  G_SENSOR["io"]["IN"]["Gripper_R1"] == 0 \
                        or  G_SENSOR["io"]["IN"]["Gripper_R2"] == 0 : #see the gripper is open

                        io_out.clear()
                        io_out["ForwoBackrd_SOL"] = 1 #go to forword 
                        do_setIO(io_out)
                        print "open ForwoBackrd_SOL "
                        io_done = True
                        break
                if not io_done:
                    set_device_exp(4004, "Latch松开异常")
                    do_tray_release()
                    return False  

                    
                start = time.time()
                io_done = False
                while time.time() - start < 20:
                    time.sleep(0.5)
                    #comform is to the forward
                    if G_SENSOR["io"]["IN"]["GripperForword_L"] == 1 \
                        and  G_SENSOR["io"]["IN"]["GripperForword_R"] == 1 \
                        and  G_SENSOR["io"]["IN"]["GripperBack_L"] == 0 \
                        and  G_SENSOR["io"]["IN"]["GripperBack_R"] == 0 :
                            io_done = True
                            break    
                if not io_done:   
                    set_device_exp(4004, "LATCH锁紧异常")
                    do_tray_release()
                    return False
                    
                for i in range(0,2):
                    io_out["GRIPPER_ON_SOL"] = 1
                    do_setIO(io_out)
                    start1 = time.time()
                    io_done = False
                    while time.time()-start1<20:
                        time.sleep(1)
                        if G_SENSOR["io"]["IN"]["Gripper_L1"] == 1 \
                           and  G_SENSOR["io"]["IN"]["Gripper_L2"] == 1 \
                           and G_SENSOR["io"]["IN"]["Gripper_R1"] == 1 \
                           and  G_SENSOR["io"]["IN"]["Gripper_R2"] == 1:
                            io_done = True
                            print "do_tray_fastening,GRIPPER_ON_SOL =1"
                            break           
                    if not io_done:
                        set_device_exp(4004, "LATCH锁紧异常")
                        do_tray_release_without_check()
                        return False
                    

                    
                    io_out.clear()
                    io_out["GRIPPER_ON_SOL"] = 0
                    do_setIO(io_out)
                    start2 = time.time()
                    io_done = False
                    while time.time()-start2<20:
                        print "time1:", str(time.time()-start)
                        time.sleep(1)
                        if G_SENSOR["io"]["IN"]["Gripper_L1"] == 0 \
                           and  G_SENSOR["io"]["IN"]["Gripper_L2"] == 0 \
                           and G_SENSOR["io"]["IN"]["Gripper_R1"] == 0 \
                           and  G_SENSOR["io"]["IN"]["Gripper_R2"] == 0:
                            io_done = True
                            print "do_tray_fastening,GRIPPER_ON_SOL =0"
                            break           
                    if not io_done:
                        set_device_exp(4007, "LATCH松开异常")
                        return False    
                                

                        
                start3 = time.time()
                io_done = False
                while time.time() - start3 < 20:
                    time.sleep(0.5)
                    #comform is to the forward
                    if G_SENSOR["io"]["IN"]["GripperForword_L"] == 1 \
                        and  G_SENSOR["io"]["IN"]["GripperForword_R"] == 1 \
                        and  G_SENSOR["io"]["IN"]["GripperBack_L"] == 0 \
                        and  G_SENSOR["io"]["IN"]["GripperBack_R"] == 0 :
                        io_out.clear()
                        io_out["GRIPPER_ON_SOL"] = 1  
                        do_setIO(io_out)
                        print "close Gripper" 
                        io_done = True
                        break     
                if not io_done:   
                    set_device_exp(4004, "LATCH锁紧异常")
                    do_tray_release()
                    return False
                    
                    
        time.sleep(1)
        return True                    
    except Exception, e:
        print "tray:", str(e)
        pass  
    pass


   
    
""" ==============================
动作--处理0级异常警报

参数：
        null
返回：
        null
"""
def do_exception_0():
    set_device_exp(0, "")
    time.sleep(1)
    try:
        io_out = {}
        io_out["LED_ERROR"] = 0
        io_out["LED_RUN"] = 0
        io_out["LED_READY"] = 1
        #io_out["JIG_UP_DOWN_SOL"] = 0
        #io_out["ForwoBackrd_SOL"] = 0
        do_tray_release_without_check()
        #io_out["LATCH_ON_SOL"] = 0
        io_out['MC_ON'] = 1
        io_out["BELL"] = 0
        do_setIO(io_out)
    except Exception, e:
        print "exc0:", str(e)
        pass      
    
    pass


    
""" ==============================
动作--处理C级异常警报

参数：
        null
返回：
        null
"""
def do_exception_C():
    do_reset()
    time.sleep(1)
    try:
        io_out = {}
        io_out["LED_ERROR"] = 1
        io_out["LED_RUN"] = 0
        io_out["LED_READY"] = 0
        io_out["BELL"] = 0
        do_setIO(io_out)
    except Exception, e:
        print "excC:", str(e)
        pass      
    
    pass
    
    
def do_exception_B():
    do_reset()
    time.sleep(0.1)
    #time.sleep(5)
    try:
        io_out = {}
        io_out["LED_ERROR"] = 1
        io_out["LED_RUN"] = 0
        io_out["LED_READY"] = 0
        io_out["MC_ON"] = 1
        io_out["BELL"] = 1
        do_setIO(io_out)
        #等待复位命令完成后发送气缸放下动作
        do_tray_release_without_check()
        #time.sleep(1)
        #io_out.clear()
        #io_out["JIG_UP_DOWN_SOL"] = 0
        #do_setIO(io_out)
        #气缸放下约3s后发送锁弹开动作
        #time.sleep(3)
        #io_out.clear()
        #io_out["LATCH_ON_SOL"] = 0
        #do_setIO(io_out)
    except Exception, e:
        print "excB:", str(e) 
        pass
    
    pass
    
    
def do_exception_A():
    do_reset()
    time.sleep(5)
    try:
        io_out = {}
        io_out["LED_ERROR"] = 1
        io_out["LED_RUN"] = 0
        io_out["LED_READY"] = 0
        io_out["MC_ON"] = 0
        io_out["BELL"] = 1
        do_setIO(io_out)
        #等待复位命令完成后发送气缸放下动作
        do_tray_release_without_check()
        #time.sleep(1)
        #io_out.clear()
        #io_out["JIG_UP_DOWN_SOL"] = 0
        #do_setIO(io_out)
        #气缸放下约3s后发送锁弹开动作
        #time.sleep(3)
        #io_out.clear()
        #io_out["LATCH_ON_SOL"] = 0
        #do_setIO(io_out)
    except Exception, e:
        print "excB:", str(e) 
        pass
    
    pass

    
def do_reset_can():
    obj = None
    try:
        obj = {"action":"sensor_reset", "data":1}
        sendUDPMessage(json.dumps(obj))
    except Exception, e:
        pass
    pass

    
    
def do_setIO(io_out):
    obj = None
    if len(io_out)==0:
        return
    #G_SENSOR["io"]["OUT"]
    try:
        obj = {"action":"sensor_write", "data":io_out}
        sendUDPMessage(json.dumps(obj))
    except Exception, e:
        pass
    pass

    
def do_single_point_modification(obj_json):
    global _battery_data
    print "c"
    try:
        print "d"
        channel = int(obj_json["channel"])
        voltage = float(obj_json["voltage"])
        current = float(obj_json["current"])
        capacity = float(obj_json["capacity"])
        print "a"
        if  channel >= 0:
            if  voltage is not None:
                _battery_data[channel]['voltage'] = voltage
                print "b"
            if  current is not None :
                _battery_data[channel]['current'] = current
            if  capacity is not None:
                _battery_data[channel]['capacity'] = capacity

    except Exception, e:
        print "f"
        pass

def do_multiple_points_modification(obj_json):
    #print 'do_multiple_points_modification'
    pass
    

def do_single_point_periodic_modification(obj_json):
    #print 'do_single_point_periodic_modification'
    #times, voltage, current, capacity, voltage_increment, current_increment, capacity_increment, channel
    
    try:

        channel = int(obj_json["channel"])
        voltage = float(obj_json["voltage"])
        current = float(obj_json["current"])
        capacity = float(obj_json["capacity"])
        times = int(obj_json["times"])
        voltage_increment = int(obj_json["voltage_increment"])
        current_increment = float(obj_json["current_increment"])
        capacity_increment = float(obj_json["capacity_increment"])


    except Exception, e:
        pass

def do_multiple_points_periodic_modification(obj_json):
    #print 'do_multiple_points_periodic_modification'
    pass    
    
""" ==============================
动作--运算ui端发过来的json指令

参数：
        s_json:json命令的字符串
返回：
        结果的json字符串
"""
def do_json_command_solver(s_json):
        global G_UNIT 
        global G_CHANNEL
        global G_ISINIT
        global G_STEP_WORKTIME
        global G_STEP_CURVE_SAVETIME
        global G_LOOP_TIME
        global G_CURVE_RATIO
        global G_PROCESS
        global G_PROCESS_IDX
        global G_INIT_BATTERY_COUNT
        global G_PROCESS_ORIGINAL
        global G_DEVICE_EXP
        global G_CONTACT_CHECKED
        global G_CONTACT_CHECK_EXP
        global G_OPERATIONAL_MODE
        global G_SENSOR
        global G_MES_URL
        global G_WORKSTATION
        global G_DEVICE_CODE
        global G_VERSION
        global G_FAN_ON_TIME
        global G_TERMINALVOLTAGE_JSON
        global G_STACKER_STATUS
        global G_EXP_RECOVERY_BRANCH
        global G_OPERATIONAL_MODE
        global G_LEAKAGE_CURRENT_DEBUG
        global G_DEBUG

        global G_PATH_Chilchen
        global G_PATH
        global G_START_STATION_TIME
        
        global G_DEBUG_LED_TIME
        global G_DEBUG_LED
        
        global G_BATTERY_COUNT_REAL
        
        obj_ret = {}
        obj_ret['success'] = False
        try:
                obj_json = json.loads(s_json)
                #print "line 2031: obj_json:",obj_json
                action = obj_json["action"]
        except Exception,e:
                logging.error('get json error:' + s_json + str(e))
                obj_ret['msg'] = 'json decode error'
                #ret = "{'success':'false','msg':'json decode error'}"
                return json.dumps(obj_ret)
                
        #ret = "{'success':'false'}"
        
        for case in switch(action):
        
                if  case('debug'):
                    G_DEBUG = int(obj_json["status"]) #0-关闭debug功能, 1-打开debug功能
                    print 'G_DEBUG = ', G_DEBUG
                    obj_ret['success'] = True
                    break

                if  case('hack_battery_data'):
                    if  G_DEBUG:
                        behavior = int(obj_json["behavior"])
                        print 'behavior = ', behavior
                        if  behavior == 1:
                            do_single_point_modification(obj_json)
                        elif behavior == 2:
                            do_multiple_points_modification(obj_json)
                        elif behavior == 3:
                            do_single_point_periodic_modification(obj_json)
                        elif behavior == 4:
                            do_multiple_points_periodic_modification(obj_json)

                        obj_ret['success'] = True
                    else:
                        obj_ret['success'] = False
                    break
                if  case('set_tray_ng'):
                    if  get_device_exp() >= 4000:
                        try:
                            #设置当前托盘的ng状态
                            jobj = sendHttpMessage(G_MES_URL, {"action": "get_device_this_tray", "param": {"DEVICE_CODE": G_DEVICE_CODE}})
                            if  jobj["errcode"] >0:
                                set_device_exp(4003, jobj["errmsg"])
                                    
                            this_tray = jobj["rtval"]["tray"]

                            jobj = sendHttpMessage(G_MES_URL, {"action": "get_process_route", "param": {"TRAY": this_tray}})
                            if  jobj["errcode"] >0:
                                set_device_exp(4003, jobj["errmsg"])

                            process_code = jobj["rtval"]["lastProcess"]
    
                            jobj_battery = sendHttpMessage(G_MES_URL, {"action": "get_tray_info","process_code":process_code, "param": {"TRAY": this_tray}})
                            if  jobj_battery["errcode"] >0:
                                set_device_exp(4003, jobj_battery["errmsg"])

                            mes_tray_info = jobj_battery["rtval"];

                            tray = mes_tray_info['TRAY']

                            sendHttpMessage(G_MES_URL, {"action": "set_tray_ng", "param": {"TRAY": tray, "DEVICE_CODE":G_DEVICE_CODE, "MSG":"ERR:"+(str(get_device_exp()))}})

                            obj_ret['success'] = True
                        except Exception, e:
                            print str(e)
                            obj_ret['success'] = False
                    else:
                            obj_ret['success'] = False
                    break
                #调试使用
                if  case('leakage_debug'):
                    G_LEAKAGE_CURRENT_DEBUG = 1 #漏电流测试接口
                    obj_ret['success'] = True
                    break

                if  case('debug'):
                    do_upload_battery_data_files()
                    obj_ret['success'] = True
                    break

                #异常恢复
                if  case('exp_recovery'):
                    if  G_DEVICE_EXP == 4105: 
                        G_EXP_RECOVERY_BRANCH = int(obj_json["exp_recovery_branch"])
                        if  G_EXP_RECOVERY_BRANCH == 1 or G_EXP_RECOVERY_BRANCH == 2:
                            do_reset()
                            do_init_battery()
                            do_init_battery_key()
                            do_exception_0()
                            #if  G_SENSOR["io"]["IN"]["TRAY_IN"] == 1 or G_SENSOR["io"]["IN"]["TRAY_POSITION"] == 1:
                            #    G_STACKER_STATUS = 1
                            #else:
                            #    G_STACKER_STATUS = 0                 
                            obj_ret['success'] = True
                        else:
                            obj_ret['success'] = False
                    elif G_DEVICE_EXP == 4106:
                        do_reset()
                        do_init_battery()
                        do_init_battery_key()
                        do_exception_0()
                        obj_ret['success'] = True
                    else:
                        obj_ret['success'] = False
                    break

                #初始化主板信息
                if case('init'):
                    try:
                            G_UNIT    = int(obj_json["unit"])
                            G_CHANNEL = int(obj_json["channel"])
                            G_DEVICE_CODE = obj_json["device_code"]
                            G_WORKSTATION = obj_json["workstation"]
                            G_MES_URL = obj_json["mes_url"]
                            G_LOOP_TIME   = int(obj_json["loop_time"])
                            G_CURVE_RATIO = int(obj_json["curve_ratio"])
                            G_INIT_BATTERY_COUNT = int(obj_json["battery"])
                            G_ISINIT = True
                            
                            obj = {}
                            obj["unit"] = G_UNIT
                            obj["channel"] = G_CHANNEL
                            obj["device_code"] = G_DEVICE_CODE
                            obj["workstation"] = G_WORKSTATION
                            obj["mes_url"] = G_MES_URL
                            obj["loop_time"] = G_LOOP_TIME
                            obj["curve_ratio"] = G_CURVE_RATIO
                            obj["max_chg"] = G_MAX_CHG
                            obj["max_dischg"] = G_MAX_DISCHG
                            obj["battery"] = G_INIT_BATTERY_COUNT
                            obj["version"] = G_VERSION
                            savefile(G_PARENT_PATH + "/hf.conf", json.dumps(obj), "w")
                            #writefile(G_PATH_Chilchen + "/hf.conf", json.dumps(obj), "w") 
                            #ret = "{'success':'true'}"
                            obj_ret['success'] = True
                            if 'ntp' in obj_json.keys():
                                os.system('sudo date -s ' +'\"'+ obj_json["ntp"]+'\"')
                    except Exception,e:
                            #ret = "{'success':'false'}"
                            obj_ret['success'] = False
                    break
                
                #初始化主板信息//all版本不再使用
                if case('init_all'):
                    #ret = "{'success':'false'}"
                    break
                
                #初始化巡检周期
                if case('init_refresh'):
                    if 'loop_time' in obj_json.keys():
                        G_LOOP_TIME   = obj_json["loop_time"]
                    if 'curve_ratio' in obj_json.keys():
                        G_CURVE_RATIO = obj_json["curve_ratio"]
                    if 'operational_mode' in obj_json.keys():
                        if obj_json["operational_mode"] in ("auto","manual"):
                            G_OPERATIONAL_MODE = obj_json["operational_mode"]
                    #ret = "{'success':'true'}"
                    obj_ret['success'] = True
                    break

                #启动Process工作
                if case('start'):
                    obj_ret['action'] = 'start'
                    if G_PROCESS and G_PROCESS['process'][G_PROCESS_IDX]['station'] != 6:
                        obj_ret['success'] = False
                        break
                    device_exp = get_device_exp()
                    if  device_exp > 4000:
                        obj_ret['success'] = False
                        break
                    G_PROCESS_ORIGINAL = obj_json
                    G_PROCESS = do_tranProcess(obj_json)
                    if G_PROCESS == None:
                        #ret = "{'action':'start','success':'false'}"
                        obj_ret['action'] = 'start'
                        obj_ret['success'] = False
                        return json.dumps(obj_ret)
                    G_PROCESS_IDX = -1
                    G_STEP_WORKTIME = 0
                    G_STEP_CURVE_SAVETIME = 0
                    G_CONTACT_CHECKED = False
                    G_CONTACT_CHECK_EXP = 0
                    # full disk ,del the disk
                    change_Disk_space()
                    #create the mulv name
                    #Create_battery_file()
                    G_START_STATION_TIME = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    print "save the time:",G_START_STATION_TIME
                    #del the last battery data
                    for i in range(0,len(_battery_data)):
                            truncatefile("/data/" + str(i).zfill(4) + ".dat")
                            truncatefile("/data/" + str(i).zfill(4) + ".kdat")
                            _battery_data[i]['stop_flag'] = 0
                            _battery_data[i]['stop_msg'] = ""
                    truncatefile("/data/process.dat")
                    truncatefile("/data/BT.dat")
                    #save the current proccess
                    savefile("/data/process.dat", json.dumps(obj_json), "w")
                    #ret = "{'action':'start','success':'true'}"
                    obj_ret['success'] = True
                    if 'ntp' in obj_json.keys():
                        os.system('sudo date -s ' +'\"'+ obj_json["ntp"]+'\"')
                    break


                if case('send_process_result'):
                    send_mes_set_process_result()
                    obj_ret['success'] = True
                    break
                if case('reset'):
                    G_DO_RESET_START_TIME = time.time()
                    do_reset()
                    do_reset_can()
                    do_init_battery()
                    do_init_battery_key()
                    #do_restart()
                    set_device_exp(0,"")
                    do_exception_0()
                    print "this is reset"
					#堆垛机相关的
                    #if G_SENSOR["io"]["IN"]["TRAY_IN"] == 1 or G_SENSOR["io"]["IN"]["TRAY_POSITION"] == 1:
                    #    G_STACKER_STATUS = 1
                    #else:
                    #    G_STACKER_STATUS = 0
                    
                    #ret = "{'success':'true'}"
                    obj_ret['success'] = True
                    break
                #获取设备状态
                if case('battery_data'):
                    #ret = "{'success':'true'}"
                    obj_ret['success'] = True
                    
                    bat_tmp = [0] * G_BATTERY_COUNT_REAL
                    for i in range(0,G_BATTERY_COUNT_REAL):
                        #print str(i) + "==" + str(_battery_data[i]["current"])+ "=="  + str(_battery_data[i]["voltage"])
                        bat_tmp[i] = copy.copy(_battery_data[G_BATTERY_MAP[i]])
                        
                        
                    
                    if G_INIT_BATTERY_COUNT > G_MODULE_COUNT*G_BATTERY_COUNT:
                            #print "type:",type(G_INIT_BATTERY_COUNT)
                            #print "type:",type(G_BATTERY_COUNT*G_MODULE_COUNT)
                            #tmp = []
                            #for i in range(0,G_INIT_BATTERY_COUNT - G_MODULE_COUNT*G_BATTERY_COUNT):
                            #        tmp.append({"station":0, "step":0, "cycle":0, "time":0, "voltage": 0, "current": 0, "capacity": 0, "temperature": 0, "stop_flag":0,  "stop_msg":"", "stop_time":0, "exp":"50", "energy": 0})
                    
                            obj = {"success": True, "message":"", "action":"battery_data", "unit":G_UNIT, "channel": G_CHANNEL , "data":
                                    bat_tmp
                                    }
                    else:
                            obj = {"success": True, "message":"", "action":"battery_data", "unit":G_UNIT, "channel": G_CHANNEL , "data":
                                    bat_tmp
                                    }
                    
                    
                    for i in range(0, len(obj['data'])):
                            del obj['data'][i]['status_mod']
                            del obj['data'][i]['ccct_end']
                            del obj['data'][i]['ccct_begin']
                            del obj['data'][i]['terminal_exp']
                            
                            obj['data'][i].update(temp=obj['data'][i].pop('temperature'))
                            
                            obj['data'][i]['time'] = round(obj['data'][i]['time'],1)
                            obj['data'][i]['capacity'] = round(obj['data'][i]['capacity'],1)
                            obj['data'][i]['energy'] = round(obj['data'][i]['energy'],1)
                            #if abs(obj['data'][i]['voltage']) < 200:
                            #    obj['data'][i]['voltage'] = 0
                            #if abs(obj['data'][i]['current']) < 10:
                            #    obj['data'][i]['current'] = 0
                            
                    #ret = json.dumps(obj)
                    obj_ret = obj
                    
                    break
                #获取设备状态
                if case('unit_stat_readall'):
                    #ret = "{'success':'true'}"
                    obj_ret['success'] = True
                    station = 0
                    step = 0
                    cycle = 0
                    if G_PROCESS_IDX > -1 and G_PROCESS is not None:
                            station = G_PROCESS['process'][G_PROCESS_IDX]['station']
                            step  = G_PROCESS['process'][G_PROCESS_IDX]['step']
                            cycle = G_PROCESS['process'][G_PROCESS_IDX]['cycle']
                            
                    obj = {"success": "true", "message":"", "action":"unit_stat_readall", "is_init": str(G_ISINIT).lower() , "v":G_VERSION, "data":
                                [{
                                    "unit":G_UNIT, "channel": G_CHANNEL,"stat":"online","station":station,"time":round(G_STEP_WORKTIME/60, 1),"operational_mode":G_OPERATIONAL_MODE,
                                    "step":step, "cycle":cycle, "exp":G_DEVICE_EXP,"exp_msg":G_DEVICE_MSG, "sensor":[],"temperature":[],"tag1":"","tag2":""
                                }]
                          }

                    #ret = json.dumps(obj)
                    obj_ret = obj
                    break
                #获取设备状态
                if case('unit_stat'):
                    #ret = "{'success':'true'}"
                    obj_ret['success'] = True
                    station = 0
                    step = 0
                    cycle = 0
                    if G_PROCESS_IDX > -1 and G_PROCESS is not None:
                            station = G_PROCESS['process'][G_PROCESS_IDX]['station']
                            step  = G_PROCESS['process'][G_PROCESS_IDX]['step']
                            cycle = G_PROCESS['process'][G_PROCESS_IDX]['cycle']
                            
                    #obj = {"success": True, "Tray_Exist":tray_exit(),"message":"", "action":"unit_stat_readall", "is_init": str(G_ISINIT).lower() , "v":G_VERSION, "data":
                    obj = {"success": True, "message":"", "action":"unit_stat_readall", "is_init": G_ISINIT , "v":G_VERSION, "data":
                                [{
                                    "unit":G_UNIT, "channel": G_CHANNEL,"stat":"online","station":station,"time":round(G_STEP_WORKTIME/60, 1),"operational_mode":G_OPERATIONAL_MODE,
                                    "step":step, "cycle":cycle, "exp":G_DEVICE_EXP,"exp_msg":G_DEVICE_MSG, "sensor":[],"temperature":[],"tag1":"","tag2":"","Tray_Exist":tray_exit()
                                }]
                          }

                    #ret = json.dumps(obj)
                    obj_ret = obj
                    break
                if case('sensor_read'):
                    #ret_msg = ""
                    try:
                        obj = None
                        #ret = '{"success":"false"}'
                        obj_ret['success'] = int(False)
                        if G_SENSOR == None:
                            #ret = '{"success":"false","message":"without I/O process"}'
                            obj_ret['message'] = 'without I/O process'
                        else:
                            #ret = json.dumps(G_SENSOR)
                            obj_ret = G_SENSOR
                        #ret_msg = 
                        sendUDPMessage(s_json)
                    except Exception,e:
                        #ret = '{"success":"false","message":"' + str(e) + '"}'
                        obj_ret['message'] = str(e)
                        pass

                    break
                        
                if case('sensor_write'):
                
                    G_FAN_ON_TIME = time.time()
                    print "sensor_write data:", obj_json["data"]
                    
                    if G_PROCESS is  None :
                    #and  obj_json["data"].has_key('Model_Selection_CAN'):
                        do_setIO(obj_json["data"])
                        #ret = "{'success':'true'}"
                        obj_ret['success'] = True

                    if G_PROCESS is  not None and  obj_json["data"].has_key('Model_Selection_CAN') is False:
                    #and  obj_json["data"].has_key('Model_Selection_CAN'):
                        do_setIO(obj_json["data"])
                        #ret = "{'success':'true'}"
                        obj_ret['success'] = True
                    else:
                        obj_ret['success'] = False
                        
                    G_DEBUG_LED_TIME = time.time()
                    G_DEBUG_LED = 1
                    print "sensor read"
                    
                    '''
                    ret_msg = sendUDPMessage(s_json)
                    if ret_msg=="" :
                        ret = "{'success':'false'}"
                    else:
                        ret = '{"unit":' + str(G_UNIT) + ', "channel":' + str(G_CHANNEL) + "," + ret_msg[1:]
                        print "sensor_write:", str(ret)
                    '''
                    #ret = "{'success':'true'}"
                    #obj_ret['success'] = True
                    break
                
                if case('version_update'):
                    obj_ret = json.loads(sendUDPMessage(s_json,9098))
                    break
                #if case('terminal_voltage_read'):
                    ## for debug 调试用，实际使用不应该用这种锁死进程的方法
                    #jobj = {'success':'true'}
                    #mod = int(obj_json["mod"])
                    #G_COMMAND_QUEUE.put(G_PROTOCOL.cmd_GetTerminalVoltage( mod ))
                    #G_TERMINALVOLTAGE_JSON = None
                    #tm_begin = time.time()
                    #while time.time() - tm_begin < 5:
                        #if G_TERMINALVOLTAGE_JSON != None:
                            #break
                        #time.sleep(0.5)
                        #pass
                    
                    #if G_TERMINALVOLTAGE_JSON != "":
                        #jobj = {'success':'true', "action":"terminal_voltage_read", 'retval':G_TERMINALVOLTAGE_JSON}
                    #else:
                        #jobj = {'success':'false', "action":"terminal_voltage_read"}
                    
                    #ret = json.dumps(jobj)
                    #break
                if case(): # default, could also just omit condition or 'if True'
                    print "Do not have active selection for:" + action
        ret = json.dumps(obj_ret)
        ret.replace("\n", "").replace("\r", "")
        return ret


""" ==============================
动作--运算判断是否跳转下个工步
      跳转条件/1.时间到 2.所有电池都寄存了 3.当前工步Idx为-1
参数：
        Null
返回：
        跳转与否 True/False
"""
def do_check_go_next_step():
        global G_PROCESS
        global G_PROCESS_IDX
        global G_STEP_WORKTIME
        global G_MODULE_COUNT
        global G_BATTERY_COUNT
        global _battery_data_stop_flag_check
        global G_BATTERY_COUNT_REAL
        
        ret = False
        if G_PROCESS_IDX == -1:
                ret = True

        #启动工作后判断的 
        if G_PROCESS_IDX > -1:
                #如果当前工步是6（结束），就不再跳工步了
                if int(G_PROCESS['process'][G_PROCESS_IDX]['station']) != 6 :
                        
                        #检查时间是否已经到位
                        if G_STEP_WORKTIME >= float(G_PROCESS['process'][G_PROCESS_IDX]['time'])*60 :
                                ret = True
                                
                        #检查是不是所有电池都是stop_flag状态
                        stopFlagCount = 0
                        for i in range(0, G_MODULE_COUNT):
                                for j in range (0, G_BATTERY_COUNT):
                                        stopFlagCount = stopFlagCount + _battery_data_stop_flag_check[i][j]
                                
                        if stopFlagCount == G_BATTERY_COUNT_REAL:
                            ret = True
                
        return ret
        
        

""" ==============================
restart
"""
def do_restart():
    os.kill(os.getpid(), signal.SIGINT)
        
""" ==============================
动作-- 重设为初始状态
参数：
        Null
返回：
        Null
"""
def do_reset():
    global G_COMMAND_QUEUE
    global G_PROTOCOL
    global G_PROCESS
    global G_PROCESS_IDX
    global G_STEP_WORKTIME
    global G_STEP_CURVE_SAVETIME
    global _battery_data
    global G_PROCESS_ORIGINAL
    global G_CONTACT_CHECKED
    global G_CONTACT_CHECK_EXP
    global G_TEMP_SUPP_POINT
    
    
    #把之前的Queue都清除掉
    while not G_COMMAND_QUEUE.empty():
        try:
            G_COMMAND_QUEUE.get(False)
        except Exception,e:
            logging.error('reset error:' + e)
            continue
        G_COMMAND_QUEUE.task_done()

    #init_can(False)
    #mymcp2515 = mcp2515.mcp2515()
    #mymcp2515.reset()
    for i in range(0, G_MODULE_COUNT):
        #设定寄存状态为1
        G_COMMAND_QUEUE.put(G_PROTOCOL.cmd_Setstop_flag(i,1))
        #设定充放电工步为复位
        G_COMMAND_QUEUE.put(G_PROTOCOL.cmd_SetStation(i, 0, 0, 0, 0, 5, 2, 3000, 3000))
        #清空G_PROCESS
    G_PROCESS = None
    G_PROCESS_ORIGINAL = None
    G_PROCESS_IDX = -1
    G_STEP_WORKTIME = 0
    G_STEP_CURVE_SAVETIME = 0
    G_CONTACT_CHECK_EXP = 0
    G_CONTACT_CHECKED = False
    G_TEMP_SUPP_POINT = -1
    #set_device_exp(0, "")
    do_fan_off()
""" ==============================
动作-- 重设电池数据为初始状态
参数：
        Null
返回：
        Null
"""
def do_init_battery():
    global _battery_data
    global G_STEP_WORKTIME
    for i in range(0,len(_battery_data)):
        _battery_data[i]['station'] = 0
        _battery_data[i]['time'] = G_STEP_WORKTIME
        _battery_data[i]['step'] = 0
        _battery_data[i]['cycle'] = 0
        _battery_data[i]['stop_flag'] = 0
        _battery_data[i]['stop_time'] = 0
        _battery_data[i]['stop_msg'] = ""
        _battery_data[i]['terminal_exp'] = 0
        
                    
""" ==============================
动作-- 设置设备异常
参数：
        Null
返回：
        Null
"""
def set_device_exp(err, msg=None):
    global G_DEVICE_EXP
    global G_DEVICE_MSG
    if msg != None and isinstance(msg, str):
        G_DEVICE_MSG = msg
    G_DEVICE_EXP = err

    
def get_device_exp():
    global G_DEVICE_EXP
    global G_DEVICE_MSG
    return G_DEVICE_EXP
    
    
""" ==============================
动作-- 检查设备标准，机柜本身的异常，不涉及IO
       并下发工步寄存命令
参数：
        Null
返回：
        Null
"""
def do_check_device_normal_exp():
        global G_PROCESS
        global G_OVER_VALTAGE_COUNT
        global G_DO_RESET_START_TIME
        global G_DEBUG_BATTARRY_BAT
        if get_device_exp() < 4000:
        
            #电池电压过高异常
            c = 0
            for i in range(0, G_BATTERY_COUNT_REAL):
                if _battery_data[i]['voltage'] >4300:
                    fs = open("/home/pi/hf_formation/run/data/valtage.log","a+")
                    fs.write(str(_battery_data))
                    fs.write(str(G_DEBUG_BATTARRY_BAT))
                    fs.close()
                    
                    c = c + 1
                pass
            if c > 0:
                G_OVER_VALTAGE_COUNT = G_OVER_VALTAGE_COUNT + 1
            else:
                G_OVER_VALTAGE_COUNT = 0
                
            if G_OVER_VALTAGE_COUNT>=2:
                set_device_exp(4202,"电压过高异常")
                
            for i in range(0,G_BATTERY_COUNT_REAL):
                if G_DO_RESET_START_TIME != None and time.time() - G_DO_RESET_START_TIME >10 :
                    if _battery_data[i]['voltage'] < -300:
                        set_device_exp(4206,"负电压异常")
                    
            #电池电流异常，非工作时候有150mA电流
            c = 0
            
            if G_PROCESS == None or G_PROCESS['process'][G_PROCESS_IDX]['station'] == 3 or G_PROCESS['process'][G_PROCESS_IDX]['station'] == 6 :
                if G_DO_RESET_START_TIME != None and time.time() - G_DO_RESET_START_TIME >10 :
                    for i in range(0, G_BATTERY_COUNT_REAL):
                        if _battery_data[i]['current'] >(G_MAX_CHG*3)/1000:
                            _battery_data[i]['stop_flag'] = 3056
                            _battery_data[i]['stop_msg'] = "漏电流异常"
                            c = c + 1
                            fs = open("/home/pi/hf_formation/run/data/debug_lou.dat","a+")
                            fs.write(str(_battery_data))
                            fs.write(str(G_PROCESS))
                            fs.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
                            fs.write("*\n")
                            fs.close()  
                if c > 4:
                    set_device_exp(4203,"漏电流异常")
                    
            #充放电状态，如果电池是寄存状态的，还有150mA电流，漏电流异常
            if  G_PROCESS != None:
                if  G_PROCESS['process'][G_PROCESS_IDX]['station'] in [1,2,4]:
                    if  G_STEP_WORKTIME > 20:
                        for i in range(0, G_BATTERY_COUNT_REAL):
                            if  _battery_data[i]['stop_flag'] >0 and (round(G_STEP_WORKTIME/60, 1) - _battery_data[i]['stop_time']) > 0.5:
                                if  abs(_battery_data[i]['current']) > (G_MAX_CHG*3)/1000:
                                    _battery_data[i]['stop_flag'] = 3056
                                    _battery_data[i]['stop_msg'] = "漏电流异常"
                                    set_device_exp(4203,"漏电流异常")
                            
                
            #充电状态，如果电池电压突然下降1000mV，电压异常
            if G_PROCESS != None:
                if G_PROCESS['process'][G_PROCESS_IDX]['station'] == 1 or G_PROCESS['process'][G_PROCESS_IDX]['station'] == 2:
                    for i in range(0, G_BATTERY_COUNT_REAL):
                        if _battery_data_last_voltage[i] - _battery_data[i]['voltage'] > 1000:
                            set_device_exp(4204,"充电电压下降异常")
                            break
                            
        return


""" ==============================
动作-- 检查电池异常
       并下发工步寄存命令
参数：
        Null
返回：
        Null
"""
def do_check_battery_exp():
    global G_PROCESS
    global G_PROCESS_IDX
    global _battery_data

    if (G_PROCESS != None) and int(G_PROCESS['process'][G_PROCESS_IDX]['station']) == 6:
        for i in range(0,G_BATTERY_COUNT_REAL):
            if _battery_data[i]['stop_flag']==0:    
                if _battery_data[i]['voltage'] < -500:
                    _battery_data[i]['stop_flag'] = 3050
                    _battery_data[i]['stop_msg'] = "电压异常"

""" ==============================
动作-- 电池接触检查
       并下发工步寄存命令
参数：
        Null
返回：
        Null
"""
def do_contact_check():
    global G_MODULE_COUNT
    global G_COMMAND_QUEUE
    global G_CONTACT_CHECKED
    global G_CONTACT_CHECK_EXP
    global G_PROCESS
    global G_PROCESS_IDX
    global G_PROTOCOL
    global _battery_data_contact_check
    global _battery_data
    global G_EXP_RECOVERY_BRANCH
    global G_OPERATIONAL_MODE
    global G_BATTERY_COUNT_REAL
    

    for i in range(0,len(_battery_data_contact_check)):
        _battery_data_contact_check[i]['chk_finish'] = 0
    
    station = int(G_PROCESS['process'][G_PROCESS_IDX]['station'])
    if ((not G_CONTACT_CHECKED) and (station==1 or station==2 or station==4 or station==3) and (G_CONTACT_CHECK_EXP > 0)):
        for midx in range(0,G_MODULE_COUNT):
            sendCommand(G_PROTOCOL.cmd_Setcontact_check(midx))
        time.sleep(1.2)
        
        contact_start_time = time.time()
        #等待所有电池接触检查完成
        while True and G_PROCESS is not None and time.time() - contact_start_time <10:
            finishCount = 0
            for midx in range(0,G_MODULE_COUNT):
                #如果这块板没完成接触检查，就继续发命令
                if _battery_data_contact_check[midx * G_BATTERY_COUNT + 0]['chk_finish'] ==0:
                    sendCommand(G_PROTOCOL.cmd_Getcontact_check(midx))
            time.sleep(0.01)    
            for i in range(0,len(_battery_data_contact_check)):
                if _battery_data_contact_check[i]['chk_finish'] == 1:
                    finishCount = finishCount + 1
                    #print "finishCount",finishCount
                    
            if finishCount >= G_BATTERY_COUNT_REAL:
                break
            pass
        
        
        G_CONTACT_CHECKED = True
        
        ccc = 0
        #for i in range(0,len(_battery_data_contact_check)):
        #这里只是做前面的48个
        for i in range(0,G_BATTERY_COUNT_REAL):
            if (_battery_data_contact_check[i]['chk_battery'] == 1):
                if((_battery_data_contact_check[i]['chk_current'] == 1) or (_battery_data_contact_check[i]['chk_voltage'] == 1)):
                    ccc += 1
                    if  (_battery_data[i]['stop_flag'] == 3020):
                        _battery_data[i]['stop_flag'] = 3051
                        _battery_data[i]['stop_msg'] = "OCV+接触检查异常"
                    else:
                        _battery_data[i]['stop_flag'] = 3046
                        _battery_data[i]['stop_msg'] = "接触检查异常" 
        
        print "contact check...... : " + str(ccc)
        print "G_EXP_RECOVERY_BRANCH", G_EXP_RECOVERY_BRANCH
        print "ccc", ccc
        print "G_CONTACT_CHECK_EXP", G_CONTACT_CHECK_EXP
        if  G_CONTACT_CHECK_EXP > 0 and ccc >= G_CONTACT_CHECK_EXP:
            #do_reset()
            if  G_OPERATIONAL_MODE == 'auto' and G_EXP_RECOVERY_BRANCH == 2:
                set_device_exp(4105, "电池接触检查异常")
                return False
            elif G_OPERATIONAL_MODE == 'manual':
                set_device_exp(4105, "电池接触检查异常")
                return False
    return True

""" ==============================
动作-- 检查工步寄存条件
       并下发工步寄存命令
参数：
        Null
返回：
        Null
"""
def do_check_step_stop_condition():
        
    global _battery_data
    global _battery_kv
    global G_PROCESS
    global G_PROCESS_IDX
    global G_BATTERY_COUNT
    global G_MODULE_COUNT   
    global G_COMMAND_QUEUE
        
    global G_DEVICE_TEMPERATURE
    global G_DEVICE_TEMPERATURE_POINT
     
    global _battery_data_stop_flag_check
    global _battery_data_last_voltage
    global _battery_data_last_current
    global _battery_last_data_buffer
    global G_TEMPERATURE_OVER_COUNT
    global G_STEP_WORKTIME
    global G_CURRENT_ERROR_COUNT  
    global G_BATTERY_COUNT_REAL
    

    '''
              Variable                      Value             Meaning
    _battery_data[i]['status_mod']            0                正常
    _battery_data[i]['status_mod']            1           恒流充电电压到停止
    _battery_data[i]['status_mod']            2           放电电压到停止
    _battery_data[i]['status_mod']            3           通道不使用
    _battery_data[i]['status_mod']            4           恒压充电的进入恒压状态
    _battery_data[i]['status_mod']            5           恒压充电的电流终止
    '''

    #电池异常/寄存检查
    for i in range(0, G_BATTERY_COUNT_REAL):
        if  _battery_data[i]['stop_flag']>0:
            continue
                
        #Exception: <<上限电压到>>
        #充电时，当前电池的电压上升至 "上限电压" 点, 触发本异常 并 寄存电池   恒流充电
        if  G_PROCESS['process'][G_PROCESS_IDX]['station'] == 1:
            if  'upperVoltage' in G_PROCESS['process'][G_PROCESS_IDX].keys():
                if  G_PROCESS['process'][G_PROCESS_IDX]['upperVoltage'] != "":
                    if  _battery_data[i]['voltage'] >= float(G_PROCESS['process'][G_PROCESS_IDX]['upperVoltage']):
                        _battery_data[i]['status_mod'] = 4
                        if  G_PROCESS['process'][G_PROCESS_IDX]['station'] == 1:
                            _battery_data[i]['stop_flag'] = 2
                            _battery_data[i]['stop_msg'] = "上限电压到"
                            _battery_data[i]['voltage'] = float(G_PROCESS['process'][G_PROCESS_IDX]['upperVoltage'])
                            
        #Exception: <<上限电压到>>
        #充电时，当前电池的电压上升至 "上限电压" 点, 触发本异常 并 寄存电池  恒压充电
        if  G_PROCESS['process'][G_PROCESS_IDX]['station'] ==2:
            if  'upperVoltage' in G_PROCESS['process'][G_PROCESS_IDX].keys():
                if  G_PROCESS['process'][G_PROCESS_IDX]['upperVoltage'] != "":
                    if  _battery_data[i]['voltage'] >= float(G_PROCESS['process'][G_PROCESS_IDX]['upperVoltage'])-5:
                        _battery_data[i]['status_mod'] = 4

                            
        #Exception: <<下限电压到>>
        #放电时，当前电池的电压下降至 "下限电压" 点，触发本异常 并 寄存电池
        if  G_PROCESS['process'][G_PROCESS_IDX]['station'] == 4:
            if  'lowerVoltage' in G_PROCESS['process'][G_PROCESS_IDX].keys():
                if  G_PROCESS['process'][G_PROCESS_IDX]['lowerVoltage'] != "":
                    if  _battery_data[i]['voltage'] <= float(G_PROCESS['process'][G_PROCESS_IDX]['lowerVoltage']):
                        _battery_data[i]['stop_flag'] = 3
                        _battery_data[i]['stop_msg'] = "下限电压到"
                        _battery_data[i]['status_mod'] = 2
                        #tmp =  abs(abs(float(_battery_data[i]['voltage'])) - abs(float(G_PROCESS['process'][G_PROCESS_IDX]['lowerVoltage'])))
                        #if tmp < abs(float(G_PROCESS['process'][G_PROCESS_IDX]['lowerVoltage'])/1000):
                        _battery_data[i]['voltage'] = float(G_PROCESS['process'][G_PROCESS_IDX]['lowerVoltage'])
                            
        #Exception: <<终止电流到>>
        #充电时，当前电池的电流下降至 "终止电流" 点，触发本异常 并 寄存电池
        if  G_PROCESS['process'][G_PROCESS_IDX]['station'] == 2  and G_STEP_WORKTIME > 6:
            if  'stop_Current' in G_PROCESS['process'][G_PROCESS_IDX].keys():
                if  G_PROCESS['process'][G_PROCESS_IDX]['stop_Current'] != "":
                    voltage_offset = abs(abs(float(_battery_data[i]['voltage']))  - abs(float(G_PROCESS['process'][G_PROCESS_IDX]['upperVoltage'])))
                    if  _battery_data[i]['current'] <= float(G_PROCESS['process'][G_PROCESS_IDX]['stop_Current']) and (voltage_offset <= 5 or _battery_data[i]['status_mod']==4):
                        _battery_data[i]['stop_flag'] = 5
                        _battery_data[i]['stop_msg'] = "终止电流到"
                        _battery_data[i]['status_mod'] = 5
                        tmp = abs(abs(float(_battery_data[i]['current'])) - abs(float(G_PROCESS['process'][G_PROCESS_IDX]['stop_Current'])))
                        if tmp < abs(float(G_PROCESS['process'][G_PROCESS_IDX]['stop_Current'])/1000):
                            _battery_data[i]['current'] = float(G_PROCESS['process'][G_PROCESS_IDX]['stop_Current'])
        
        '''
        #Exception: <<端子接触异常>>
        #当硬件检查到电路的电阻大于正常范围时，触发本异常 并 寄存电池
        if  G_PROCESS['process'][G_PROCESS_IDX]['station'] in [1,2,4]:
            if  G_STEP_WORKTIME > 20:
                if  _battery_data[i]['terminal_exp'] == 1:
                    _battery_data[i]['stop_flag'] = 3019
                    _battery_data[i]['stop_msg'] = "端子接触异常"  
        '''
 
        #Exception: <<电压超差异常>>                                         
        #当前电池的电压大于"上限电压" 点时，触发本异常 并 寄存电池
        if  'upperVoltage' in G_PROCESS['process'][G_PROCESS_IDX].keys() and G_STEP_WORKTIME > 20:        
            if  G_PROCESS['process'][G_PROCESS_IDX]['upperVoltage'] != "":      
                delta = 50           
                if  _battery_data[i]['voltage'] > float(G_PROCESS['process'][G_PROCESS_IDX]['upperVoltage']) + delta:
                    _battery_data[i]['stop_flag'] = 3010
                    _battery_data[i]['stop_msg'] = "电压超差异常"
             
        #当前电池的电压小于"下限电压" 点时，触发本异常 并 寄存电池
        if  'lowerVoltage' in G_PROCESS['process'][G_PROCESS_IDX].keys() and G_STEP_WORKTIME > 20:        
            if  G_PROCESS['process'][G_PROCESS_IDX]['lowerVoltage'] != "":      
                delta = 50           
                if  _battery_data[i]['voltage'] < float(G_PROCESS['process'][G_PROCESS_IDX]['lowerVoltage']) - delta:
                    _battery_data[i]['stop_flag'] = 3010
                    _battery_data[i]['stop_msg'] = "电压超差异常"

        #Exception: <<电压异常>>
        #搁置工步时，当前电池的电压大于  "上限电压"点，或者小于"下限电压"点时，     触发本异常 并 寄存电池                  
        if  (G_PROCESS['process'][G_PROCESS_IDX]['station'] == 3 ) and G_STEP_WORKTIME > 20:
            if  'lowerVoltage' in G_PROCESS['process'][G_PROCESS_IDX].keys():        
                if  G_PROCESS['process'][G_PROCESS_IDX]['lowerVoltage'] != "":
                    if  _battery_data[i]['voltage'] < float(G_PROCESS['process'][G_PROCESS_IDX]['lowerVoltage']):
                        _battery_data[i]['stop_flag'] = 3012
                        _battery_data[i]['stop_msg'] = "电压异常"
                                                
            if  'upperVoltage' in G_PROCESS['process'][G_PROCESS_IDX].keys():        
                if  G_PROCESS['process'][G_PROCESS_IDX]['upperVoltage'] != "":
                    if  _battery_data[i]['voltage'] > float(G_PROCESS['process'][G_PROCESS_IDX]['upperVoltage']):
                        _battery_data[i]['stop_flag'] = 3011
                        _battery_data[i]['stop_msg'] = "电压异常"                                              
              
        #Exception: <<充电-ΔV异常>>
        #充电时，当前电池的电压反而在下降，触发本异常 并 寄存电池
        if  G_PROCESS['process'][G_PROCESS_IDX]['station'] in [1, 2] and G_STEP_WORKTIME > 20:
            if  'stop_DeltaVoltage' in G_PROCESS['process'][G_PROCESS_IDX].keys():
                 if  G_PROCESS['process'][G_PROCESS_IDX]['stop_DeltaVoltage'] != "" :
                     if  _battery_data[i]['stop_flag']==0:    
                         if  _battery_data_last_voltage[i] > 0:
                             delta = 50
                             if  float(G_PROCESS['process'][G_PROCESS_IDX]['stop_DeltaVoltage']) < delta:
                                 delta =  float(G_PROCESS['process'][G_PROCESS_IDX]['stop_DeltaVoltage'])
                                 if  _battery_data_last_voltage[i] - _battery_data[i]['voltage'] > delta:
                                     _battery_data[i]['stop_flag'] = 3004
                                     _battery_data[i]['stop_msg'] = "充电-ΔV异常" 
 
        #Exception: <<放电-ΔV异常>>
        #放电时，当前电池的电压反而上升，触发本异常 并 寄存电池
        if  G_PROCESS['process'][G_PROCESS_IDX]['station'] == 4 and G_STEP_WORKTIME > 20 and _battery_data[i]['stop_flag'] == 0:
            if  'stop_DeltaVoltage' in G_PROCESS['process'][G_PROCESS_IDX].keys():
                if  G_PROCESS['process'][G_PROCESS_IDX]['stop_DeltaVoltage'] != "":
                    if  _battery_data_last_voltage[i] > 0:
                        delta = 50
                        if  _battery_data[i]['voltage'] - _battery_data_last_voltage[i] > delta:
                            _battery_data[i]['stop_flag'] = 3005
                            _battery_data[i]['stop_msg'] = "放电-ΔV异常"
                                                   
        #Exception: <<过容量异常>>
        #当前电池的容量 大于 设定容量，触发本异常 并 寄存电池
        if  'stop_Capacity' in G_PROCESS['process'][G_PROCESS_IDX].keys():    
            if  G_PROCESS['process'][G_PROCESS_IDX]['stop_Capacity'] != "" and G_STEP_WORKTIME > 20:
                if  _battery_data[i]['stop_flag']==0:
                    if  _battery_data[i]['capacity'] > float(G_PROCESS['process'][G_PROCESS_IDX]['stop_Capacity']):
                        _battery_data[i]['stop_flag'] = 3006
                        _battery_data[i]['stop_msg'] = "过容量异常"
                                
        #Exception: <<放电电流异常>>
        #放电时，如果电池的电流抖动大于 G_MAX_DISCHG / 1000 并且 电池的电压不处于 "下限电压" 点附近，触发本异常 并 寄存电池
        if  G_PROCESS['process'][G_PROCESS_IDX]['station'] == 4 and G_STEP_WORKTIME > 20:
            if  _battery_data[i]['stop_flag'] == 0:
                delta = G_MAX_DISCHG / 1000
                offset_current = abs(abs(_battery_data[i]['current']) - abs(int((G_PROCESS['process'][G_PROCESS_IDX]['current']))))
                if  offset_current > delta:
                    print "3102"
                    #接近下限电压时，电流的抖动会比较大；在这种情况，我们不处理
                    if  _battery_data[i]['voltage'] - G_PROCESS['process'][G_PROCESS_IDX]['lowerVoltage'] < 2:
                        pass
                    else:
                        #放电时，电流抖动过大；这里记录电流抖动的次数，当抖动次数大于4次后，触发本异常 并 寄存电池
                        print "3109"
                        G_CURRENT_ERROR_COUNT[i] = G_CURRENT_ERROR_COUNT[i] + 1
                        if  G_CURRENT_ERROR_COUNT[i] > 7:
                            if  abs(int((G_PROCESS['process'][G_PROCESS_IDX]['current'])))>500 or G_STEP_WORKTIME > 60:
                                _battery_data[i]['stop_flag'] = 3041
                                _battery_data[i]['stop_msg'] = "放电电流异常"
                else:
                    G_CURRENT_ERROR_COUNT[i] = 0
                            
                    #for debug 电流异常，将当前接触数据保存日志
                    #mod = int(i/G_BATTERY_COUNT)
                    #sendCommand(G_PROTOCOL.cmd_GetTerminalVoltage( mod ))

        #Exception: <<恒压充电电流上升异常>>
        #如果是恒压充电，判断如果电压小于上限电压-50mv时候，电流不为设定电流，则电流异常
        if  G_PROCESS['process'][G_PROCESS_IDX]['station'] in [2] and G_STEP_WORKTIME > 20:
            if  _battery_data[i]['stop_flag'] == 0:
                #Exception: <<恒压电流上升异常>>
                #恒压充电进入恒压阶段后，电流上升 delta 毫安，触发本异常 并 寄存电池
                if  _battery_data[i]['status_mod'] == 4:
                    delta = G_MAX_CHG/50
                    if  _battery_data[i]['current'] - _battery_data_last_current[i] > delta:
                        print "now_current:",_battery_data[i]['current']
                        print "last current:",_battery_data_last_current[i]
                        print "index:",i
                        _battery_data[i]['stop_flag'] = 3049
                        _battery_data[i]['stop_msg'] = "恒压电流上升异常"
                                    
                #Exception: <<恒压充电电流异常>>
                #恒压充电工步 处于 恒流充电阶段时，电池的电流不为 设定电流时，触发本异常 并 寄存电池
                delta = 5
                if  _battery_data[i]['voltage'] <= int((G_PROCESS['process'][G_PROCESS_IDX]['upperVoltage'])) - delta and _battery_data[i]['status_mod'] != 4:
                    delta = G_MAX_CHG*3/1000
                    offset_current = abs(abs(_battery_data[i]['current']) - abs(int((G_PROCESS['process'][G_PROCESS_IDX]['current']))))
                    if  offset_current > delta:
                        G_CURRENT_ERROR_COUNT[i] = G_CURRENT_ERROR_COUNT[i] + 1
                        if  G_CURRENT_ERROR_COUNT[i] > 0:
                            _battery_data[i]['stop_flag'] = 3042
                            _battery_data[i]['stop_msg'] = "恒压充电电流异常"
                    else:
                        G_CURRENT_ERROR_COUNT[i] = 0
                    
                else:
                #Exception: <<恒压充电电流异常>>
                #充电时进入恒压阶段时，电池的电流 大于 设定电流时，触发本异常 并 寄存电池
                    delta = G_MAX_CHG/1000
                    if  _battery_data[i]['current'] > int((G_PROCESS['process'][G_PROCESS_IDX]['current'])) + delta:
                        if  abs(int((G_PROCESS['process'][G_PROCESS_IDX]['current'])))>500 or G_STEP_WORKTIME > 45:
                            _battery_data[i]['stop_flag'] = 3042
                            _battery_data[i]['stop_msg'] = "恒压充电电流异常"

                #Exception: <<恒压充电电压保护异常>>
                #充电时，充电电流大于半度 并 充电时间超过 600秒，电池的当前电压 少于 2000，触发本异常 并 寄存电池
                if  G_STEP_WORKTIME > 600 and int(G_PROCESS['process'][G_PROCESS_IDX]['current']) > (G_MAX_CHG / 2):
                    if  _battery_data[i]['voltage'] < 2000:
                        _battery_data[i]['stop_flag'] = 3047
                        _battery_data[i]['stop_msg'] = "恒压充电电压保护异常"
                
                #Exception: <<恒压充电电压异常>>
                #充电时 并 充电时间超过 1 分钟，电池的当前电压少于 50 mV，触发本异常 并 寄存电池
                if  G_STEP_WORKTIME > 60:
                    if  _battery_data[i]['voltage'] < 50:
                        _battery_data[i]['stop_flag'] = 3048
                        _battery_data[i]['stop_msg'] = "恒压充电电压异常"
       
        #如果是恒流充电，判断电流异常
        if  G_PROCESS['process'][G_PROCESS_IDX]['station'] in [1] and G_STEP_WORKTIME > 20:
            if  _battery_data[i]['stop_flag'] == 0:
                #Exception: <<恒流充电电流异常>>
                #恒流充时电，电池的当前电流 大于 设定电流 + delta，触发本异常 并 寄存电池
                delta = G_MAX_CHG*3 / 1000
                offset_current = abs(abs(_battery_data[i]['current']) - abs(int((G_PROCESS['process'][G_PROCESS_IDX]['current']))))
                if  offset_current > delta:
                    G_CURRENT_ERROR_COUNT[i] = G_CURRENT_ERROR_COUNT[i] + 1
                    if  G_CURRENT_ERROR_COUNT[i] > 7:
                        if  abs(int((G_PROCESS['process'][G_PROCESS_IDX]['current'])))>500 or G_STEP_WORKTIME > 45:
                            _battery_data[i]['stop_flag'] = 3043
                            _battery_data[i]['stop_msg'] = "恒流充电电流异常"
                else:
                    G_CURRENT_ERROR_COUNT[i] = 0

                #Exception: <<恒流充电电压保护异常>>
                #恒流充电时，充电电流大于半度 并 工作时间大于 600 秒，电池的电压 少于 2000 mV, 触发本异常 并 寄存电池
                if  G_STEP_WORKTIME > 600 and int(G_PROCESS['process'][G_PROCESS_IDX]['current']) > (G_MAX_CHG / 2):
                    if  _battery_data[i]['voltage'] < 2000:
                        _battery_data[i]['stop_flag'] = 3047
                        _battery_data[i]['stop_msg'] = "恒流充电电压保护异常"
               
                #Exception: <<恒流充电电压异常>>
                #恒流充电 并 充电时间大于 60 秒，电池的电压小于 50mV，触发本异常 并 寄存电池
                if G_STEP_WORKTIME > 60:
                    if  _battery_data[i]['voltage'] < 50:
                        _battery_data[i]['stop_flag'] = 3048
                        _battery_data[i]['stop_msg'] = "恒流充电电压异常"
                
        
        
        if G_PROCESS['process'][G_PROCESS_IDX]['station'] == 2 and G_STEP_WORKTIME > 20:
            if 'cct_begin' in G_PROCESS['process'][G_PROCESS_IDX].keys() and 'cct_end' in G_PROCESS['process'][G_PROCESS_IDX].keys():
                if G_PROCESS['process'][G_PROCESS_IDX]['cct_begin'] != "" and G_PROCESS['process'][G_PROCESS_IDX]['cct_end'] != "":
                    if _battery_data[i]['stop_flag'] == 0 and _battery_data[i]['ccct_end'] > 0:
                        if _battery_data[i]['ccct_end'] < (float(G_PROCESS['process'][G_PROCESS_IDX]['cct_begin']) * 60) or _battery_data[i]['ccct_end'] > (float(G_PROCESS['process'][G_PROCESS_IDX]['cct_end']) * 60):
                            _battery_data[i]['stop_flag'] = 3007
                            _battery_data[i]['stop_msg'] = "cct异常"
                    if _battery_data[i]['stop_flag'] == 0  and _battery_data[i]['ccct_end'] == 0 and  G_STEP_WORKTIME > (float(G_PROCESS['process'][G_PROCESS_IDX]['cct_end']) * 60):
                        _battery_data[i]['stop_flag'] = 3007
                        _battery_data[i]['stop_msg'] = "cct异常"
                                    
        #主板散热器温度异常检查
    for i in range(0, G_MODULE_COUNT):
        over_temp = False
        for j in range(0, G_DEVICE_TEMPERATURE_POINT):
            #如果主板采样有一个点大于90°，整主板停掉
            if  G_DEVICE_TEMPERATURE[i*G_DEVICE_TEMPERATURE_POINT + j]>90:
                over_temp = True
                break
        if  over_temp:
            G_TEMPERATURE_OVER_COUNT[i] = G_TEMPERATURE_OVER_COUNT[i] + 1
        else:
            G_TEMPERATURE_OVER_COUNT[i] = 0
                
        if  G_TEMPERATURE_OVER_COUNT[i] > 4:
            for j in range(0, G_BATTERY_COUNT):
                _battery_data[ i*G_BATTERY_COUNT + j ]['stop_flag'] = 3052
                _battery_data[ i*G_BATTERY_COUNT + j ]['stop_msg'] = "散热器温度异常"
            pass

            
    #_battery_data[48]['stop_flag'] = 1
    #_battery_data[49]['stop_flag'] = 1 
                
    print "_battery_data_stop_flag_check:",_battery_data_stop_flag_check    
    #如果stop_flag不为0, 则寄存电池
    module_index = 0
    for module_index in range(0, G_MODULE_COUNT):
        stop_status = [0] * G_BATTERY_COUNT # 1-寄存, 0-不寄存
        for battery_index in range(0, G_BATTERY_COUNT):
            
            #对于49 50 电池不处理
            if module_index == G_MODULE_COUNT-1 and battery_index >G_BATTERY_COUNT-3:
                break
                
            #遍历每个电池的数据，查找有寄存标记的电池(stop_flag != 0)
            if  _battery_data[module_index * G_BATTERY_COUNT + battery_index]['stop_flag'] != 0:
                
                #如果当前的电池的stop_time未被记录，则设置stop_time
                if  _battery_data[module_index * G_BATTERY_COUNT + battery_index]['stop_time'] == 0:
                    _battery_data[module_index * G_BATTERY_COUNT + battery_index]['stop_time'] = round(G_STEP_WORKTIME/60, 1)  
                #标记当前电池为 已被寄存 的电池
                stop_status[battery_index] = 1
                #如果当前的电池是第一次被寄存时，保存当前电池的曲线数据和关键数据
                if  _battery_data_stop_flag_check[module_index][battery_index] != stop_status[battery_index]:
                    #保存电池的曲线数据
                    _battery_kv[module_index * G_BATTERY_COUNT + battery_index]['skip_save_once'] = False
                    do_save_one_battery_point(module_index * G_BATTERY_COUNT + battery_index)
                    #if  _battery_data[module_index * G_BATTERY_COUNT + battery_index]['stop_flag'] in [2,3,8,5]:
                    #_battery_data_stop_flag_check[module_index][battery_index] = 1
                    _battery_kv[module_index * G_BATTERY_COUNT + battery_index]['skip_save_once'] = True
                    _battery_kv[module_index * G_BATTERY_COUNT + battery_index]['skip_save_once_start_time'] = time.time()
                    #保存电池的关键数据
                    do_save_one_battery_key_point(module_index * G_BATTERY_COUNT + battery_index)
                    #跳过一次保存曲线数据
                    
            else :
                stop_status[battery_index] = 0
        
        #与同一块板上次采样Stop结果做比较，如果不同，则再按照最新的发一次Stop给采样板
        if  cmp(_battery_data_stop_flag_check[module_index] , stop_status) != 0:
            if int(G_PROCESS['process'][G_PROCESS_IDX]['station']) !=3:
                #觉得这里不需要等待了
                ret_cmd = G_PROTOCOL.cmd_Setstop_flagByList(module_index, stop_status)       
                sendCommand(ret_cmd)
            _battery_data_stop_flag_check[module_index] = list(stop_status)
				
				
						
      
""" ==============================
线程--保存电池数据点
参数：
        == 
返回：
        ==
"""                                                 
def do_save_one_battery_point(i):
    global G_BATTERY_UNMAP	
    m = G_BATTERY_UNMAP[i]
    global G_PROCESS
    global G_PROCESS_IDX
    global _battery_data
    global _battery_kv
    global G_TEMPERATURE_MAP


    if _battery_kv[i]['skip_save_once'] or time.time() - _battery_kv[i]['skip_save_once_start_time'] <4 :
        _battery_kv[i]['skip_save_once'] = False
        return
    #_battery_kv[i]['skip_save_once'] = True
    tmp_v = _battery_data[i]['voltage']
    tmp_c =_battery_data[i]['current']
   # if abs(tmp_v) < 200:
   #     tmp_v = 0
   # if abs(tmp_c) < 10:
   #     tmp_c = 0
    #if G_PROCESS['process'][G_PROCESS_IDX]['station'] != 6:
    '''
    writefile(G_PATH_Chilchen+ '/' +
             str(m).zfill(4) + ".dat", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  + "," +
             str(_battery_data[i]['cycle'])  + "," +
             str(_battery_data[i]['step'])  + "," +
             str(_battery_data[i]['station'])  + "," +
             str(round(_battery_data[i]['time'],1))  + "," +
             str(tmp_v)  + "," +
             str(tmp_c)  + "," +
             str(round(_battery_data[i]['capacity'],1))  + "," +
             str(round(_battery_data[i]['energy'],1))  + "," +
             str(_battery_data[i]['temperature'])  + "," +
             str(_battery_data[i]['stop_flag'])  + "," +
             (_battery_data[i]['stop_msg'])  + "")
    
    if i == G_MODULE_COUNT:
        #BT1 = G_DEVICE_TEMPERATURE
        #G_DEVICE_TEMPERATURE = [1,2,3,4] 
        #print type(G_DEVICE_TEMPERATURE)
        #print "this is G_DEVICE_TEMPERATURE",G_DEVICE_TEMPERATURE
        
        #G_DEVICE_TEMPERATURE = [0]*G_MODULE_COUNT
        #if G_DEVICE_TEMPERATURE is not None:
        BT = {}
        BTT = {}
        key = None
        value = None
        for i in range(0,len(G_DEVICE_TEMPERATURE)):
            key= "BD"+str(i) 
            value = G_DEVICE_TEMPERATURE[i]
            BT[key] = value

        #G_DEVICE_TEMPERATURE
        
        #print "BT:",BT
        #print "BTT",BTT
        #BTT
        BTT = {'station':str(G_PROCESS['process'][G_PROCESS_IDX]['station']),'time':datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        BTT["bardTemp"] = BT
        #print str(G_PROCESS['process'][G_PROCESS_IDX]['station'])
        #print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writefile(G_PATH_Chilchen + "/BT.dat",str(BTT))
    '''
    savefile("/data/" + str(m).zfill(4) + ".dat", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  + "," +
             str(_battery_data[i]['cycle'])  + "," +
             str(_battery_data[i]['step'])  + "," +
             str(_battery_data[i]['station'])  + "," +
             str(round(_battery_data[i]['time'],1))  + "," +
             str(tmp_v)  + "," +
             str(tmp_c)  + "," +
             str(round(_battery_data[i]['capacity'],1))  + "," +
             str(round(_battery_data[i]['energy'],1))  + "," +
             str(_battery_data[i]['temperature'])  + "," +
             str(_battery_data[i]['stop_flag'])  + "," +
             (_battery_data[i]['stop_msg'])  + "")
    if i == G_MODULE_COUNT:
        #BT1 = G_DEVICE_TEMPERATURE
        #G_DEVICE_TEMPERATURE = [1,2,3,4] 
        #print type(G_DEVICE_TEMPERATURE)
        #print "this is G_DEVICE_TEMPERATURE",G_DEVICE_TEMPERATURE
        
        #G_DEVICE_TEMPERATURE = [0]*G_MODULE_COUNT
        #if G_DEVICE_TEMPERATURE is not None:
        '''
        BT = {}
        BTT = {}
        key = None
        value = None
        for i in range(0,len(G_DEVICE_TEMPERATURE)):
            key= "BD_"+str(i) 
            value = G_DEVICE_TEMPERATURE[i]
            BT[key] = value

        #G_DEVICE_TEMPERATURE
        
        #print "BT:",BT
        #print "BTT",BTT
        #BTT
        BTT = {'station':str(G_PROCESS['process'][G_PROCESS_IDX]['station']),'time':datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        BTT["BoardTemp"] = BT
        #print str(G_PROCESS['process'][G_PROCESS_IDX]['station'])
        #print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        '''
        #savefile("/data/BT.dat",str(BTT))
        ls1 = G_DEVICE_TEMPERATURE
        ls2 = [str(i) for i in ls1]
        ls3 = ','.join(ls2)
        savefile("/data/BT.dat", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  + "," +
        str(G_PROCESS['process'][G_PROCESS_IDX]['cycle'])  + "," +
        str(G_PROCESS['process'][G_PROCESS_IDX]['step'])  + "," +
        str(G_PROCESS['process'][G_PROCESS_IDX]['station'])  + "," +
        str(round(G_STEP_WORKTIME/60, 1))  + "," +ls3)

    return

""" ==============================
线程--保存所有电池数据点
参数：
        == 
返回：
        ==
"""                                                 
def do_save_battery_point( savenow = False):
    global G_STEP_CURVE_SAVETIME
    global G_STEP_WORKTIME
    global G_BATTERY_COUNT_REAL
    if G_STEP_WORKTIME > 20 or savenow:
        for i in range(0,G_BATTERY_COUNT_REAL):
            do_save_one_battery_point(i)
    G_STEP_CURVE_SAVETIME = G_STEP_WORKTIME
    return


    
    """ ==============================
计算--数值的16进制LIST，以低-高位排列
参数：
        value 数值
返回：
        16进制LIST低-高位排列
"""
def list2string_HEX(lt):
    s = ""
    for i in range(0, len(lt)):
        s = s + hex(lt[i]).replace("0x", "").zfill(2)
    return s
    

def hack_batterydata(module_index):
    global _battery_kv, _battery_data , _battery_last_data_buffer, _battery_data_contact_check, G_PROCESS, G_PROCESS_IDX
    global G_STEP_WORKTIME
    global G_DEVICE_TEMPERATURE
    global G_BATTERY_COUNT
    global G_SENSOR
    global G_TEMPERATURE_MAP
    global G_BATTERY_UNMAP
    global G_TERMINALVOLTAGE_JSON
    global G_OPERATIONAL_MODE
    global G_BATTERY_COUNT_REAL

    if  G_PROCESS is not None:
        #恒流充电时(采样电流为正数, 设定电流为正数)做电流数据优化
        if  G_PROCESS['process'][G_PROCESS_IDX]['station'] == 1:
            for i in range(0, G_BATTERY_COUNT):
                channel_index = module_index * G_BATTERY_COUNT + i
                
                if channel_index  >= G_BATTERY_COUNT_REAL:
                    break
                    
                if  _battery_data[channel_index]['stop_flag'] == 0: 
                    offset_current = _battery_data[channel_index]['current'] - G_PROCESS['process'][G_PROCESS_IDX]['current']
                    if  abs(offset_current)<=20:
                        if  abs(G_PROCESS['process'][G_PROCESS_IDX]['current']) <= 500:
                            delta = round(offset_current/4, 1)
                        else:
                            delta = round(offset_current/2, 1)
                        _battery_data[channel_index]['current'] = G_PROCESS['process'][G_PROCESS_IDX]['current'] + delta

    if  G_PROCESS is not None:
        #恒流放电时(采样电流为负数, 设定电流为正数)做电流数据优化
        if  G_PROCESS['process'][G_PROCESS_IDX]['station'] == 4:
            for i in range(0, G_BATTERY_COUNT):
                channel_index = module_index * G_BATTERY_COUNT + i
                if channel_index  >= G_BATTERY_COUNT_REAL:
                    break
                    
                if  _battery_data[channel_index]['stop_flag'] == 0: 
                    offset_current = _battery_data[channel_index]['current'] - (0-abs(G_PROCESS['process'][G_PROCESS_IDX]['current']))
                    if  abs(offset_current)<=120:
                        if  abs(G_PROCESS['process'][G_PROCESS_IDX]['current']) <= 500:
                            delta = round(offset_current/4, 1)
                        else:
                            delta = round(offset_current/2, 1)
                        _battery_data[channel_index]['current'] = (0-abs(G_PROCESS['process'][G_PROCESS_IDX]['current'])) + delta
   
    if  G_PROCESS is not None:
        #恒压充电时(采样电流为正数，设定电流为正数)做电流数据优化
        if  G_PROCESS['process'][G_PROCESS_IDX]['station'] == 2:
            for i in range(0, G_BATTERY_COUNT):
                channel_index = module_index * G_BATTERY_COUNT + i
                
                if channel_index  >= G_BATTERY_COUNT_REAL:
                    break
                    
                if  _battery_data[channel_index]['stop_flag'] == 0 and _battery_data[channel_index]['status_mod'] != 4:  
                    offset_current = _battery_data[channel_index]['current'] - G_PROCESS['process'][G_PROCESS_IDX]['current']
                    if  abs(offset_current)<=20:
                        if  abs(G_PROCESS['process'][G_PROCESS_IDX]['current']) <= 500:
                            delta = round(offset_current/4, 1)
                        else:
                            delta = round(offset_current/2, 1)
                        _battery_data[channel_index]['current'] = G_PROCESS['process'][G_PROCESS_IDX]['current'] + delta 

    if  G_PROCESS is not None:
        #恒压放电时(采样电流为负数，设定电流为正数)做电流数据优化
        if  G_PROCESS['process'][G_PROCESS_IDX]['station'] == 12:
            for i in range(0, G_BATTERY_COUNT):
                channel_index = module_index * G_BATTERY_COUNT + i
                
                if channel_index  >= G_BATTERY_COUNT_REAL:
                    break
                    
                if  _battery_data[channel_index]['stop_flag'] == 0 and _battery_data[channel_index]['status_mod'] != 4:  
                    offset_current = _battery_data[channel_index]['current'] - (0-abs(G_PROCESS['process'][G_PROCESS_IDX]['current']))
                    if  abs(offset_current)<=20:
                        if  abs(G_PROCESS['process'][G_PROCESS_IDX]['current']) <= 500:
                            delta = round(offset_current/4, 1)
                        else:
                            delta = round(offset_current/2, 1)
                        _battery_data[channel_index]['current'] = (0-abs(G_PROCESS['process'][G_PROCESS_IDX]['current'])) + delta


                        
""" ==============================
线程--串口发送命令（1次超时）
参数：
        == rbuffer 发送的命令buffer
返回：
        ==
"""        
def sendCommand(cmd):
        global _battery_kv, _battery_data , _battery_last_data_buffer, _battery_data_contact_check, G_PROCESS, G_PROCESS_IDX
        global G_STEP_WORKTIME
        global G_DEVICE_TEMPERATURE
        global G_BATTERY_COUNT
        global G_SENSOR
        global G_TEMPERATURE_MAP
        global G_BATTERY_UNMAP
        global G_TERMINALVOLTAGE_JSON
        global G_OPERATIONAL_MODE

        global G_PATH_Chilchen
        global G_DEBUG_BATTARRY_BAT
        ret_buffer = None
        #rbuffer = cmd.split("$")[0]
        rbuffer = cmd
        cmd_num = cmd[3]
        #print "cmd",cmd
        #print "cmd_num",cmd_num
        #cmd_split = cmd.split("$")[1]
        #print "cmd_split",cmd_split
        #cmd_num = int(cmd.split("$")[1])
        #print "cmd",cmd
        #print "cmd_num",cmd_num
        ret_idx_mod = None
        #sendto命令说明
        #lt = hf_can.sendto("0", "00400600#00,40", -1)
        #参数1：永远是"0",兼容232/485第一个参数是通知第几块板
        #参数2：数据位#具体数据，要回收数据长度
        #参数3：-1，则有回收数据（放在CAN最后一个包），否则至0，不回收数据，兼容232/485数据回收长度
        try:
            ret_idx_mod, ret_buffer = _ser.sendto("0", rbuffer, -1)
            #print "sendcommand 3107: ret_buffer",ret_buffer
        except Exception,e:
            print "sendCommand error: " + rbuffer, str(e)
     
     
        if ret_buffer != None:
            if cmd_num == 0x6: #回收的是电池数据
                #G_DEBUG_BATTARRY_BAT = str(ret_buffer.encode("hex"))
                G_PROTOCOL.do_batteryBuffer2Json(ret_idx_mod, ret_buffer, _battery_data, G_STEP_WORKTIME, G_PROCESS, G_PROCESS_IDX, G_DEVICE_TEMPERATURE)
                #print 'ret_buffer = ', ret_buffer
                #print "_battery_data",_battery_data 
                

                hack_batterydata(ret_idx_mod) 
                
                
                if G_SENSOR:
                    for i in range(0, G_BATTERY_COUNT):
                        _battery_data[ret_idx_mod * G_BATTERY_COUNT + i]['temperature'] = G_SENSOR['temp_can'][G_TEMPERATURE_MAP[G_BATTERY_UNMAP[ret_idx_mod * G_BATTERY_COUNT + i]]]
                        #if _battery_kv[ret_idx_mod * G_BATTERY_COUNT + i]['skip_save_once']:
                        _battery_kv[ret_idx_mod * G_BATTERY_COUNT + i]['skip_save_once'] = False
            '''
            elif cmd_num == 0X33:#回收的是寄存电池时的数据
                #G_PROTOCOL.do_batteryLastBuffer2Json(ret_idx_mod,ret_buffer,_battery_data, G_STEP_WORKTIME, G_PROCESS, G_PROCESS_IDX)
                _battery_last_data_buffer = ret_buffer
            elif cmd_num == 0X0A:#获取端子的电压
                G_TERMINALVOLTAGE_JSON = G_PROTOCOL.do_batteryTerminalVoltage2Json(ret_idx_mod, ret_buffer)
                #debug 将当前端子电压数据保存起来
                #print "temp_json" + G_TERMINALVOLTAGE_JSON
                savefile("/data/TV_debug_" + str(ret_idx_mod).zfill(4) + ".dat", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  + " , " +
                         str(G_TERMINALVOLTAGE_JSON)  + " , T1=" + str(G_DEVICE_TEMPERATURE[ret_idx_mod * G_DEVICE_TEMPERATURE_POINT + 0]) + " , T2=" + str(G_DEVICE_TEMPERATURE[ret_idx_mod * G_DEVICE_TEMPERATURE_POINT + 1]))
            '''
            if cmd_num == 0x24:
                G_PROTOCOL.do_contactCheckBuffer2Json(ret_idx_mod, ret_buffer, _battery_data_contact_check)
            return True
        else:
            if ret_idx_mod:
                #print "idx_mod: " + str(ret_idx_mod)
                G_DEVICE_TEMPERATURE[ret_idx_mod * G_DEVICE_TEMPERATURE_POINT + 0] = 0
                #G_DEVICE_TEMPERATURE[ret_idx_mod * G_DEVICE_TEMPERATURE_POINT + 1] = 0
            return False
        
""" ==============================
动作-- 保存电池关键数据点
参数：
        status: 1-工步开始 2-工步执行 3-工步结束
返回：
        Null
"""
def do_save_one_battery_key_point(i):
    #k_capacity = 0 #容量
    #k_quantity = 0 #电量
    #k_time = 0 #工作时间
    #k_open_voltage = 0 #开路电压
    ######k_open_current = 0 #开路电流
    #k_AVG_voltage = 0  #平均电压
    #k_mid_voltage = 0  #中值电压，曲线中间点电压 (不算寄存后的点)
    #k_end_voltage = 0 #终止电压
    #k_end_current = 0 #终止电流
    #k_temperature = 0 #电池最高温度
    #k_ccct = 0 #恒流充电时间（曲线上充电电流恒流部分的时间，注：恒流恒压充电，则不计算恒压部分时间）
    #k_cvct = 0 #恒压充电时间（曲线上充电恒压部分的时间）
    #k_cccc = 0 #恒流充电容量
    #k_cvcc = 0 #恒压充电容量
    #k_cccp = 0 #恒流充电容量比例（恒流部分容量/整个工步容量）
    #k_cvcp = 0 #恒压充电容量比例
    #k_begin_time = 0 #开始时间
    #k_end_time = 0 #结束时间
    global G_BATTERY_UNMAP
    global _battery_kv , _battery_data, G_PROCESS, G_PROCESS_IDX, G_STEP_WORKTIME
    m = G_BATTERY_UNMAP[i]
    
    
    _battery_kv[i]['capacity'] = round(_battery_data[i]['capacity'],1)
    _battery_kv[i]['quantity'] = round(_battery_data[i]['energy'],1)
    _battery_kv[i]['time'] = round(_battery_data[i]['time'],1)
    _battery_kv[i]['count_voltage'] += 1
    _battery_kv[i]['AVG_voltage'] += (_battery_data[i]['voltage'] - _battery_kv[i]['AVG_voltage']) / ( _battery_kv[i]['count_voltage'])
    #_battery_kv[i]['mid_voltage'] = _battery_data[i]['']
    _battery_kv[i]['end_voltage'] = _battery_data[i]['voltage']
    _battery_kv[i]['end_current'] = _battery_data[i]['current']
    #_battery_kv[i]['temperature'] = _battery_data[i]['']
    #if _battery_data[i]['ccct_end'] == 0 and _battery_kv[i]['end_current'] > 0:
    #    _battery_data[i]['ccct_end'] = G_STEP_WORKTIME
    
    if _battery_data[i]['ccct_end'] == 0:
        _battery_kv[i]['ccct'] = round(_battery_data[i]['time'], 1)
    else:
        _battery_kv[i]['ccct'] = round(_battery_data[i]['ccct_end'], 1)
        
    if _battery_data[i]['ccct_end'] > 0:
        _battery_kv[i]['cvct'] = round(_battery_data[i]['time'] - _battery_kv[i]['ccct'], 1)
    else:
        _battery_kv[i]['cvct'] = 0
        
    #_battery_kv[i]['cccc'] = _battery_data[i]['']
    _battery_kv[i]['cvcc'] = round(_battery_data[i]['capacity'] - _battery_kv[i]['cccc'], 1)
    if _battery_data[i]['capacity'] != 0:
        _battery_kv[i]['cccp'] = round(_battery_kv[i]['cccc'] / _battery_data[i]['capacity'], 1)
        _battery_kv[i]['cvcp'] = round(_battery_kv[i]['cvcc'] / _battery_data[i]['capacity'], 1)
    _battery_kv[i]['end_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    _battery_kv[i]['stop_msg'] = _battery_data[i]['stop_msg']
    if G_PROCESS['process'][G_PROCESS_IDX]['station'] != 6:
        savefile("/data/" + str(m).zfill(4) + ".kdat",
                str(_battery_kv[i]['capacity'])  + "," +
                str(_battery_kv[i]['quantity'])  + "," +
                str(_battery_kv[i]['time'])  + "," +
                str(_battery_kv[i]['open_voltage'])  + "," +
                str(round(_battery_kv[i]['AVG_voltage'],1))  + "," +
                str(_battery_kv[i]['mid_voltage'])  + "," +
                str(_battery_kv[i]['end_voltage'])  + "," +
                str(_battery_kv[i]['end_current']) + "," +
                str(_battery_kv[i]['temperature'])  + "," +
                str(_battery_kv[i]['ccct'])  + "," +
                str(_battery_kv[i]['cvct'])  + "," +
                str(_battery_kv[i]['cccc'])  + "," +
                str(_battery_kv[i]['cvcc'])  + "," +
                str(_battery_kv[i]['cccp'])  + "," +
                str(_battery_kv[i]['cvcp'])  + "," +
                str(_battery_kv[i]['begin_time'])  + "," +
                str(_battery_kv[i]['end_time'])  + "," +
                str(_battery_data[i]['stop_flag'])  + "," +
                str(_battery_kv[i]['stop_msg']) + "")
    
        '''
        savefile("/data/" + str(m).zfill(4) + ".kdat",
                str(_battery_kv[i]['capacity'])  + "," +
                str(_battery_kv[i]['quantity'])  + "," +
                str(_battery_kv[i]['time'])  + "," +
                str(_battery_kv[i]['open_voltage'])  + "," +
                str(round(_battery_kv[i]['AVG_voltage'],1))  + "," +
                str(_battery_kv[i]['mid_voltage'])  + "," +
                str(_battery_kv[i]['end_voltage'])  + "," +
                str(_battery_kv[i]['end_current']) + "," +
                str(_battery_kv[i]['temperature'])  + "," +
                str(_battery_kv[i]['ccct'])  + "," +
                str(_battery_kv[i]['cvct'])  + "," +
                str(_battery_kv[i]['cccc'])  + "," +
                str(_battery_kv[i]['cvcc'])  + "," +
                str(_battery_kv[i]['cccp'])  + "," +
                str(_battery_kv[i]['cvcp'])  + "," +
                str(_battery_kv[i]['begin_time'])  + "," +
                str(_battery_kv[i]['end_time'])  + "," +
                str(_battery_data[i]['stop_flag'])  + "," +
                str(_battery_kv[i]['stop_msg']) + "")
        '''
    
""" ==============================
动作-- 保存电池关键数据点
参数：
        status: 1-工步开始 2-工步执行 3-工步结束
返回：
        Null
"""
def do_save_battery_key_point(status):
    #k_capacity = 0
    #k_quantity = 0
    #k_time = 0
    #k_open_voltage = 0 #开路电压
    #k_open_current = 0 #开路电流
    #k_AVG_voltage = 0  #平均电压
    #k_mid_voltage = 0  #中值电压，曲线中间点电压 (不算寄存后的点)
    #k_end_voltage = 0 #终止电压
    #k_end_current = 0 #终止电流
    #k_temperature = 0 #电池最高温度
    #k_ccct = 0 #恒流充电时间（曲线上充电电流恒流部分的时间，注：恒流恒压充电，则不计算恒压部分时间）
    #k_cvct = 0 #恒压充电时间（曲线上充电恒压部分的时间）
    #k_cccc = 0 #恒流充电容量
    #k_cvcc = 0 #恒压充电容量
    #k_cccp = 0 #恒流充电容量比例（恒流部分容量/整个工步容量）
    #k_cvcp = 0 #恒压充电容量比例
    #k_begin_time = 0
    #k_end_time = 0
    
    global _battery_kv , _battery_data, G_PROCESS, G_PROCESS_IDX, G_MODULE_COUNT, G_BATTERY_COUNT, _bat, tery_data_stop_flag_check, G_STEP_CURVE_SAVETIME, G_STEP_WORKTIME, G_TEMP_SUPP_POINT
    global G_BATTERY_COUNT_REAL
    
    if status == 1:
        do_init_battery_key()
    
    elif status == 2:
        for i in range(0, G_BATTERY_COUNT_REAL):
            _battery_kv[i]['count_voltage'] += 1
            _battery_kv[i]['AVG_voltage'] += (_battery_data[i]['voltage'] - _battery_kv[i]['AVG_voltage']) / ( _battery_kv[i]['count_voltage'])
            if not _battery_kv[i]['mid_voltage'] and not G_PROCESS:
                pass
        for i in range(0, G_BATTERY_COUNT_REAL):
            _battery_kv[i]['temperature'] = _battery_data[i]['temperature']
        '''
        if (G_TEMP_SUPP_POINT > 0) and (G_STEP_WORKTIME > (G_TEMP_SUPP_POINT * 60)):
            for i in range(0, G_MODULE_COUNT * G_BATTERY_COUNT):
                _battery_kv[i]['temperature'] = _battery_data[i]['temperature']
            G_TEMP_SUPP_POINT = -1
        '''
    elif status == 3:
        for i in range(0, G_BATTERY_COUNT_REAL):
            bl = _battery_data_stop_flag_check[i/G_BATTERY_COUNT] 
            if bl[i%G_BATTERY_COUNT] == 0:
                bl[i%G_BATTERY_COUNT] = 1
                _battery_data_stop_flag_check[i/G_BATTERY_COUNT] = list(bl)
                _battery_data[i]['stop_flag'] = 1
                _battery_data[i]['stop_msg'] = "时间到"
                if _battery_data[i]['stop_time'] == 0:
                    _battery_data[i]['stop_time'] = round(G_STEP_WORKTIME/60, 1)
                if G_STEP_CURVE_SAVETIME != G_STEP_WORKTIME and _battery_data[i]['stop_flag']==1:
                    _battery_kv[i]['skip_save_once'] = False
                    do_save_one_battery_point(i)
                    _battery_kv[i]['skip_save_once_start_time'] = time.time()
                    _battery_kv[i]['skip_save_once'] = True
                do_save_one_battery_key_point(i)
        return
    

""" ==============================
线程--主线程
参数：
        ==
返回：
        ==
"""
def main():
        
        global G_PROCESS
        global G_PROCESS_IDX
        global G_STEP_WORKTIME
        global G_STEP_CURVE_SAVETIME
        global G_STEP_START_TIMESTAMP
        global _battery_data
        global _battery_data_stop_flag_check
        global _battery_data_last_voltage
        global _battery_data_last_current
        global G_UNIT
        global G_CHANNEL
        global G_LOOP_TIME
        global G_CURVE_RATIO
        global G_ISINIT
        global G_INIT_BATTERY_COUNT
        global G_MAX_CHG
        global G_MAX_DISCHG
        global G_CONTACT_CHECK_EXP
        global G_SENSOR
        global G_DEVICE_TEMPERATURE
        global G_DEVICE_CODE
        global G_MES_URL
        global G_DEVICE_CODE
        global G_VERSION
        
        jsontext_config = readfile(G_PARENT_PATH + "/hf.conf")
        

        if jsontext_config != "":
                obj_json = json.loads(jsontext_config)
                G_UNIT    = int(obj_json["unit"])
                G_CHANNEL = int(obj_json["channel"])
                G_DEVICE_CODE = obj_json["device_code"]
                G_MES_URL = obj_json["mes_url"]
                G_LOOP_TIME   = int(obj_json["loop_time"])
                G_CURVE_RATIO = int(obj_json["curve_ratio"])
                #G_MAX_CHG = int(obj_json["max_chg"])
                #G_MAX_DISCHG = int(obj_json["max_dischg"])
                G_INIT_BATTERY_COUNT = int(obj_json["battery"])
                #G_VERSION = obj_json["version"]
                G_ISINIT = True                
                pass
                
        #_th_recv = cls_recv_Thread('recv_thread')
        #_th_recv.setDaemon(True)
        #_th_recv.start()  #启动串口收信息线程
        
        
        #control与UI通讯的线程
        _th_udp = cls_udp_Thread('udp_thread')
        _th_udp.setDaemon(True)
        _th_udp.start()
        
        _th_comm_control = cls_comm_control_Thread('comm_control_thread')
        _th_comm_control.setDaemon(True)
        _th_comm_control.start()

        _exception_deal_Thread = exception_deal_Thread('exception_deal_Thread')
        _exception_deal_Thread.setDaemon(True)
        _exception_deal_Thread.start()
        
        
        _th_recv_control = cls_io_recv_Thread('comm_io_recv_thread')
        _th_recv_control.setDaemon(True)
        _th_recv_control.start()
        
        #_th_mes_heartbeat = cls_mes_heartbeat_Thread('mes_heartbeat_thread')
        #_th_mes_heartbeat.setDaemon(True)
        #_th_mes_heartbeat.start()

        while True:
            try:
                exc_info=sys.exc_info()
                '''
                while True:
                    print "do_main_loop:"
                    #print "G_SENSOR:",G_SENSOR
                    time.sleep(1)
                    do_tray_compact()
                    do_tray_release()   
                '''            
                do_main_loop()
            except SystemExit:
                print "call sys exit!"
                return
            except Exception,e:
                print "main loop:" + str(e)
                pass
            finally:
                traceback.print_exception(*exc_info)#print None
        

'''
@fn		do_check_comm_exp
@brief		This function sets communication exception for main boards if possible
'''
def do_check_comm_exp(none_count):
    global G_COMM_EXP_COUNTER
    global G_OPERATIONAL_MODE
    global G_PROCESS

    device_exp = get_device_exp()

    if  none_count>0 and device_exp < 4000 and G_PROCESS is None and G_OPERATIONAL_MODE == "auto":
        G_COMM_EXP_COUNTER = G_COMM_EXP_COUNTER + 1
        if  G_COMM_EXP_COUNTER > 1:
            set_device_exp(4010, "主板通讯异常")

    if  none_count == 0:
        G_COMM_EXP_COUNTER = 0
    pass

""" ==============================
线程--主线程循环
参数：
        ==
返回：
        ==
"""
def do_main_loop():
        global G_PROCESS
        global G_PROCESS_IDX
        global G_STEP_WORKTIME
        global G_STEP_CURVE_SAVETIME
        global G_STEP_START_TIMESTAMP
        global _battery_data
        global _battery_data_stop_flag_check
        global _battery_data_last_voltage
        global G_UNIT
        global G_CHANNEL
        global G_LOOP_TIME
        global G_CURVE_RATIO
        global G_ISINIT
        global G_INIT_BATTERY_COUNT
        global G_MAX_CHG
        global G_MAX_DISCHG
        global G_CONTACT_CHECK_EXP
        global G_CONTACT_CHECKED
        global G_OPERATIONAL_MODE
        global G_DEVICE_EXP
        global G_TEMP_SUPP_POINT
        global G_CURRENT_ERROR_COUNT
        global G_EXP_RECOVERY_BRANCH
        global G_MES_TRAY_INFO
        global _battery_data_contact_check
        global G_BATTERY_MAP
        global G_LEAKAGE_CURRENT_DEBUG
        global G_START_STATION_TIME
        global G_BATTERY_COUNT_REAL
        
        
        module_none_count = [0] * G_MODULE_COUNT
        
        get_ocv_ret = 0  #1-有OCV数据, 0-无OCV数据 

        times = 0
        while True:
                i=1

                #当命令不为null，给模块下发命令
                #print "line 3445 G_PROCESS:",G_PROCESS
                while G_COMMAND_QUEUE.qsize()>0 :
                        #print datetime.datetime.now().strftime('%b-%d-%y %H:%M:%S')  + " : command"
                        cmd = G_COMMAND_QUEUE.get_nowait()
                        #print "cmd: " + cmd
                        sendCommand(cmd)
                        time.sleep(0.2)
                
            
               
                #巡检所有采样板信息                    
                none_count = 0
                for i in range(0,G_MODULE_COUNT):
                        #print "get module data:" + str(i)
                        if G_DEVICE_EXP>4000 and G_COMMAND_QUEUE.qsize()>0:
                            break
                        start_time_one_board = time.time()   
                        ret = sendCommand(G_PROTOCOL.cmd_GetBatteryInformation(i))
                        times = times + 1
                        #print "times:",times
                        
                        #print "one board time need time:",start_time_one_board - time.time()
                        if not ret:
                                print "this is is error"
                                none_count += 1
                                #每块主板收数据，如果返回None超过4次，则这块板电池数据清0
                                module_none_count[i] += 1
                                #print datetime.datetime.now().strftime('%b-%d-%y %H:%M:%S') + " : Time OUT [" + str(i) +"]"
                                if module_none_count[i]>5:
                                    for j in range(0,G_BATTERY_COUNT):           
                                            _battery_data[i*G_BATTERY_COUNT+j]['voltage'] = 0
                                            _battery_data[i*G_BATTERY_COUNT+j]['current'] = 0
                        else:
                            module_none_count[i] = 0
                            
                        #time.sleep(0.05)

                if none_count == G_MODULE_COUNT:
                    _ser.reset_bus()
                    time.sleep(5)
                
                #判定主板通讯异常
                do_check_comm_exp(none_count)
 
                #判定设备异常
                do_check_device_normal_exp()
                        
                #判定电池异常
                do_check_battery_exp()
                
                #判定电池终止（寄存条件）（PROCESS不为NULL的时候启动工作之后进行判定）
                if G_PROCESS is not None:
                        if G_PROCESS_IDX > -1:
                                #do_fan_on()    
                                #检查工步寄存条件  保存寄存的曲线数据
                                do_check_step_stop_condition()
                                #6为结束工步，不保存数据
                                if G_PROCESS['process'][G_PROCESS_IDX]['station'] != 6:
                                    #保存电池采样信息
                                    do_save_battery_key_point(2)
                                    #判断是否超出上一次巡检周期的时间，超出就保存，并重置保存时间
                                    #    3 * 1  每次3秒采集
                                    p = G_LOOP_TIME * G_CURVE_RATIO
                                    
                                    if G_STEP_WORKTIME - G_STEP_CURVE_SAVETIME > p:
                                        do_save_battery_point(True)
                                else:
                                    do_fan_off()
                                    if G_OPERATIONAL_MODE != "auto":
                                        do_tray_release()
                                    G_EXP_RECOVERY_BRANCH = 2
                        
                #更新最后一次采样电压
                for i in range(0,G_BATTERY_COUNT_REAL):
                    _battery_data_last_voltage[i] = _battery_data[i]['voltage']
                    _battery_data_last_current[i] = _battery_data[i]['current']

                #如果有启动命令，则启动模板工作
                #station    工作状态（1个字节） 0－复位 1－恒流充电 2－恒压充电 4－放电 （BYTE）
                if G_PROCESS is not None:
                        #如果是第一工步前
                        if  G_PROCESS_IDX==-1:
                            get_ocv_ret = 0 
                            #开启IC电源
                            #for i in range(0,G_MODULE_COUNT):
                            #G_PROTOCOL.cmd_SetICPower(i, 1)
                            if G_OPERATIONAL_MODE != "auto":
                                if not do_tray_compact():
                                    do_reset()
                                    continue

                        vu = 0
                        vi = 0
                        station = 0
                        stop_flag = 0
                        G_STEP_WORKTIME = (time.time() - G_STEP_START_TIMESTAMP) if (G_PROCESS['process'][G_PROCESS_IDX]['station'] != 6) else 0
                        #print G_STEP_WORKTIME
                        if G_PROCESS_IDX > -1:
                                for i in range(0,G_BATTERY_COUNT_REAL):
                                        _battery_data[i]['station'] = G_PROCESS['process'][G_PROCESS_IDX]['station']
                                        #_battery_data[i]['time'] = round(G_STEP_WORKTIME/60, 1)
                                        _battery_data[i]['step'] = G_PROCESS['process'][G_PROCESS_IDX]['step']
                                        _battery_data[i]['cycle'] = G_PROCESS['process'][G_PROCESS_IDX]['cycle']
                                        
                        #判断是否跳转工步<关键>
                        if do_check_go_next_step():
                                #_battery_data[48]['stop_flag'] = 1
                                #_battery_data[49]['stop_flag'] = 1
                                '''
                                #time_over 设定值 三个状态 type_A / type_B / off
                                #如果有TYPE_A TYPE_B判定，则判定TYPE_A TYPE_B
                                #type A 检查异常 在设定时间内不能到达终止条件
                                #     CCC 工步在设定时间内不能到达上限电压
                                #     CCD 工步在设定时间内不能到达下限电压
                                #     CCCV工步在设定时间内不能到达终止电流
                                #type B 检查异常 在设定时间内到达了终止条件
                                #     CCC 工步在设定时间内到达上限电压
                                #     CCD 工步在设定时间内到达下限电压
                                '''
                                if 'time_over' in G_PROCESS['process'][G_PROCESS_IDX].keys():
                                    if G_PROCESS['process'][G_PROCESS_IDX]['time_over'].lower() in ('type_a', 'type_b', 'off'):
                                            if G_PROCESS['process'][G_PROCESS_IDX]['time_over'].lower() == "type_a":
                                                for i in range(0,G_BATTERY_COUNT_REAL):
                                                    if  _battery_data[i]['stop_flag'] == 1:
                                                        _battery_data[i]['stop_flag'] = 3044
                                                        _battery_data[i]['stop_msg'] = "type_A 检查异常"

                                            if G_PROCESS['process'][G_PROCESS_IDX]['time_over'].lower() == "type_b":
                                                for i in range(0,G_BATTERY_COUNT_REAL):
                                                    if  _battery_data[i]['stop_flag'] in [2,3,5,8]:
                                                        _battery_data[i]['stop_flag'] = 3045
                                                        _battery_data[i]['stop_msg'] = "type_B 检查异常"
                                        
                                if G_PROCESS_IDX > -1:
                                    #do_save_battery_point()
                                    do_save_battery_key_point(3)
                                    #for i in range(0,len(_battery_data)):
                                    #    _battery_data[i]['time'] = round(float(G_PROCESS['process'][G_PROCESS_IDX]['time']),1)
                                    
                                G_STEP_WORKTIME = 0
                                G_STEP_CURVE_SAVETIME = 0
                                G_STEP_START_TIMESTAMP = time.time()
                                G_PROCESS_IDX = G_PROCESS_IDX + 1
                                

                                #清空电流异常计数器
                                for i in range(0,G_BATTERY_COUNT_REAL):
                                    G_CURRENT_ERROR_COUNT[i]=0
                                
                                #初始化电池寄存数据
                                init_battery()
                                
                                #初始化新工步的电池数据
                                for i in range(0,len(_battery_data)):
                                        #大于等于3000为异常，不再恢复
                                        if _battery_data[i]['stop_flag']<3000:
                                            _battery_data[i]['stop_flag'] = 0
                                            _battery_data[i]['stop_msg'] = ""
                                        _battery_data[i]['time'] = 0
                                        _battery_data[i]['station'] = G_PROCESS['process'][G_PROCESS_IDX]['station']
                                        _battery_data[i]['step'] = G_PROCESS['process'][G_PROCESS_IDX]['step']
                                        _battery_data[i]['cycle'] = G_PROCESS['process'][G_PROCESS_IDX]['cycle']
                                        _battery_data[i]['capacity'] = 0
                                        _battery_data[i]['energy'] = 0
                                        _battery_data[i]['ccct_end'] = 0
                                        _battery_data[i]['ccct_begin'] = 0
                                
                                #print "G_PROCESS_IDX:" + str(G_PROCESS['process'][G_PROCESS_IDX])
                                start = time.time()
                                
                                if G_PROCESS_IDX==0:
                                    if 'temp_supp_point' in G_PROCESS['process'][G_PROCESS_IDX].keys():
                                        G_TEMP_SUPP_POINT = float(G_PROCESS['process'][G_PROCESS_IDX]['temp_supp_point'])
                                    
                                if  not get_ocv_ret:
                                    enda = time.time()
                                    #停止板的充放电，拿OCV
                                
                                    for i in range(0,G_MODULE_COUNT):
                                        sendCommand(G_PROTOCOL.cmd_Setstop_flag(i,1))
                                        time.sleep(0.05)
                                        
                                    for i in range(0,G_MODULE_COUNT):
                                        #sendCommand(G_PROTOCOL.cmd_SetStation(i, 0, 0, 0, 0, 5, 2, 3000, 3000))
                                        sendCommand(G_PROTOCOL.cmd_SetStation(i, 0, 36000, 0, 0, 5, 2, 3000, 3000))
                                        time.sleep(0.05)

                                    endb = time.time()
                                    time.sleep(1.2)
                                    #保存OCV信息
                                    #巡检所有采样板信息
                                    for i in range(0,G_MODULE_COUNT):
                                        #print "get module data:" + str(i)
                                        sendCommand(G_PROTOCOL.cmd_GetBatteryInformation(i))  
                                                
                                        time.sleep(0.05)
                                    endc = time.time()
                                    for i in range(0,len(_battery_data)):
                                        _battery_data[i]['current'] = 0
                                        #赋值恒流充电开始
                                        if _battery_data[i]['ccct_begin'] ==0:
                                            _battery_data[i]['ccct_begin'] = G_STEP_WORKTIME

                                    #time.sleep(3)
                                    do_save_battery_point(True)
                                    do_save_battery_key_point(1)
                                    endd = time.time()
                                
                                    print "a: %f s" % (enda - start)
                                    print "b: %f s" % (endb - start)
                                    print "c: %f s" % (endc - start)
                                    print "d: %f s" % (endd - start)
                                    #获取OCV结束
                                
                                    #判断OCV有没有低于当前工步设定的下限电压，如果有则停掉该电池，报电池OCV异常
                                    if  'lowerVoltage' in G_PROCESS['process'][G_PROCESS_IDX].keys():
                                        if  G_PROCESS['process'][G_PROCESS_IDX]['lowerVoltage'] != "":
                                            for i in range(0,G_BATTERY_COUNT_REAL):
                                                if  _battery_data[i]['voltage'] < float(G_PROCESS['process'][G_PROCESS_IDX]['lowerVoltage']):
                                                    #如果是第一个工步的OCV异常叫做OCV异常3020，其他工步的统称电压异常3021
                                                    if  G_PROCESS_IDX==0:
                                                        _battery_data[i]['stop_flag'] = 3020
                                                        _battery_data[i]['stop_msg'] = "OCV异常"
                                                    else:
                                                        if  _battery_data[i]['stop_flag'] < 3000:
                                                            _battery_data[i]['stop_flag'] = 3021
                                                            _battery_data[i]['stop_msg'] = "电压异常" 
                                    get_ocv_ret = 1
                                    
                                #接触检查
                                if 'contact_check' in G_PROCESS['process'][G_PROCESS_IDX].keys():
                                    if G_PROCESS['process'][G_PROCESS_IDX]['contact_check']:
                                        G_CONTACT_CHECK_EXP = int(G_PROCESS['process'][G_PROCESS_IDX]['contact_check'])
                                        #设置值>0为做接触检查异常整机停机
                                        if G_CONTACT_CHECK_EXP > 0:
                                            if not do_contact_check():
                                                continue

                                
                                #检查是否存在电池信息不符的情况
                                if  G_OPERATIONAL_MODE == "auto":
                                    mes_lost_sync_exp_flag = 0
                                    #print "G_BATTERY_MAP"
                                    #print G_BATTERY_MAP
                                    #print "_battery_data_contact_check"
                                    #for i in range(0, G_MODULE_COUNT*G_BATTERY_COUNT):
                                    #    print i, "=",2+ int(_battery_data_contact_check[i]['chk_battery'])
                                    #print "G_MES_TRAY_INFO['ACTIVE']",  G_MES_TRAY_INFO["ACTIVE"]
                                    #48个电池
                                    for i in range(0,G_BATTERY_COUNT_REAL):
                                        if  int(_battery_data_contact_check[G_BATTERY_MAP[i]]['chk_battery']) != G_MES_TRAY_INFO["ACTIVE"][i]:
                                            mes_lost_sync_exp_flag = 1
                                            #if  (_battery_data[G_BATTERY_MAP[i]]['stop_flag'] == 0):
                                            _battery_data[G_BATTERY_MAP[i]]['stop_flag'] = 3053
                                            _battery_data[G_BATTERY_MAP[i]]['stop_msg'] = "MES电池信息不符"
                                    if  mes_lost_sync_exp_flag:
                                        set_device_exp(4106, "MES电池信息不符")
                                        continue
                                
                                station = int(G_PROCESS['process'][G_PROCESS_IDX]['station'])
                                print "G_PROCESS_IDX",G_PROCESS_IDX
                                print "station",station
                                
                                #工步启动前，获得开路数据<关键>
                                G_STEP_WORKTIME = 0

                                '''
                                #全部其他数字变量乘10作为完成变量
                                for (k,v) in G_PROCESS['process'][G_PROCESS_IDX].items():
                                        if v != '':
                                                if k in G_PROCESS_LIST_PRECISE_ADJUSTMENT:
                                                        if type(v) is not types.BooleanType:
                                                                G_PROCESS['process'][G_PROCESS_IDX][k] = int(float(v)*10)
                                '''
                                vi_low = 0
                                #恒压充电
                                if station == 2:
                                    do_fan_on()
                                    vi = int(float(G_PROCESS['process'][G_PROCESS_IDX]['current'])*10)
                                    vu = int(float(G_PROCESS['process'][G_PROCESS_IDX]['upperVoltage'])*10)
                                    if 'stop_Current' in G_PROCESS['process'][G_PROCESS_IDX].keys():
                                        if G_PROCESS['process'][G_PROCESS_IDX]['stop_Current'] != "":
                                            try:
                                                vi_low = int(float(G_PROCESS['process'][G_PROCESS_IDX]['stop_Current'])*10)
                                            except:
                                                vi_low = 300
                                    stop_flag = 0
                                        
                                #恒流充电        
                                if station == 1:
                                    do_fan_on()
                                    vi = int(float(G_PROCESS['process'][G_PROCESS_IDX]['current'])*10)
                                    #由主板控制的话不需要+30，如果是RS232控制寄存则+30
                                    #vu = int((float(G_PROCESS['process'][G_PROCESS_IDX]['upperVoltage'])+30)*10) 
                                    vu = int((float(G_PROCESS['process'][G_PROCESS_IDX]['upperVoltage']+10))*10)  
                                    stop_flag = 0                                        
                                #搁置
                                if station == 3:
                                    do_fan_on()
                                    do_power_fan_off()
                                    station = 0
                                    vi = 0
                                    vu = 36000
                                    stop_flag = 1
                                        
                                #恒流放电
                                if station == 4:
                                    do_fan_on()
                                    vi = int(float(G_PROCESS['process'][G_PROCESS_IDX]['current'])*10)
                                    vi = 0 - abs(vi)  #如果是放电，则发下去的电流数值为负数
                                    vu = int(float(G_PROCESS['process'][G_PROCESS_IDX]['lowerVoltage']-100)*10)
                                    stop_flag = 0
                                #循环工步（已经拆分）
                                if station == 5:
                                        print "cycle step"
                                
                                #结束工步
                                if station == 6:
                                    do_fan_off()
                                    #结束工步后，就不保存数据了
                                    #station = 0
                                    vi = 0
                                    vu = 36000
                                    stop_flag = 1
                                    Create_battery_file()
                                    time.sleep(0.5)
                                    os.system("cp /home/pi/hf_formation/run/data/*.dat "+G_PATH_Chilchen+" -rf")
                                        
                                stop_flag_list = [0] * G_BATTERY_COUNT
                                for i in range(0, G_MODULE_COUNT):
                                        for j in range(0,G_BATTERY_COUNT):   
                                                
                                                if i ==G_MODULE_COUNT-1 and j > G_BATTERY_COUNT-3:
                                                    break
                                                    
                                                    
                                                if _battery_data[i*G_BATTERY_COUNT+j]['stop_flag']<3000:
                                                    stop_flag_list[j] = stop_flag
                                                    _battery_data[i*G_BATTERY_COUNT+j]['stop_time'] = 0
                                                else:
                                                    stop_flag_list[j] = 1
                                        
                                        G_COMMAND_QUEUE.put(G_PROTOCOL.cmd_Setstop_flagByList( i, stop_flag_list))
                                        #G_COMMAND_QUEUE.put(G_PROTOCOL.cmd_Setstop_flag( i, stop_flag))
                                
                                time.sleep(0.5)
                                
                                if station == 6:
                                     for i in range(0,G_MODULE_COUNT):
                                            #G_COMMAND_QUEUE.put(G_PROTOCOL.cmd_SetStation(i, station, vu, vi))
                                            G_PROTOCOL.cmd_SetICPower(i, 0)                                   
                                        
                                time.sleep(0.5)

                                #时间到在这里下发寄存命令
                                for i in range(0,G_MODULE_COUNT):
                                        for j in range(0,G_BATTERY_COUNT):
                                                
                                                if i ==G_MODULE_COUNT-1 and j >G_BATTERY_COUNT-3:
                                                    break
                                                    
                                                if _battery_data[i*G_BATTERY_COUNT+j]['stop_flag']<3000:
                                                    _battery_data[i*G_BATTERY_COUNT+j]['stop_time'] = 0
                                                    stop_flag_list[j] = stop_flag
                                                else:
                                                    stop_flag_list[j] = 1
                                                    
                                        #G_COMMAND_QUEUE.put(G_PROTOCOL.cmd_SetStation(i, station, vu, vi))
                                        ret_cmd = G_PROTOCOL.cmd_SetStation(i, station, vu, vi, 0, 3, 8, 12000, vi_low, stop_flag_list)
                                        #G_COMMAND_QUEUE.put(ret_cmd)
                                        #print "ret_cmd",ret_cmd
                                        sendCommand(ret_cmd)
                                        #sendCommand(G_PROTOCOL.cmd_SetStation(i, 0, 36000, 0, 0, 5, 2, 3000, 3000))
                                        
                                #做完ocv和前期工作，再开始计时
                                get_ocv_ret = 0 #下一个工步要做一次ocv
                                #time.sleep(2)
                                G_STEP_START_TIMESTAMP = time.time()
                                
def exit_gracefully(signal, frame):
        #... log exiting information ...
        #... close any open files ...
                
        if _ser != None:
                _ser.release()
                
        print "hf-control is closed..."
        sys.exit(0)
        

if __name__ == '__main__':  
        try:  
                signal.signal(signal.SIGINT, exit_gracefully)
                main()  
        except KeyboardInterrupt:
                if _ser != None:
                        _ser.release()
        except Exception,e:
            try:
                print "main:" + str(e)
                exc_info = sys.exc_info()
                try:
                    raise TypeError("main error: ")
                except:
                    pass
            finally:
                pass
                traceback.print_exception(*exc_info)
                #del exe_info
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4 
