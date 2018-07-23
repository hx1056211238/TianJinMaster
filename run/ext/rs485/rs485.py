#!/usr/bin/env python
# -*- coding: utf-8 -*-

import serial
import time
import sys
import threading
import platform
#import wiringpi
#import RPi.GPIO as GPIO

# BOARD编号方式，基于插座引脚编号
#GPIO.setmode(GPIO.BOARD)
# 输出模式
#GPIO.setup(12, GPIO.OUT)

G_b_count=0
G_b_time=0

G_ad_count=0
G_ad_time=0

G_s_count=0
G_s_time=0

G_set_count=0
G_set_time=0

G_r_io_count=0
G_r_io_time=0
G_s_io_count=0
G_s_io_time=0



class rs232(object):

    _obj=None#串口对象

    global G_b_count
    global G_b_time

    __th_recv = None
    _comm_busy = False
    _comm_recv_buffer = None
    _comm_recv_idx_module = -1
    s_buffer = ""
    _s_return = False

    #通讯错误记录
    _total_err_count=0
    _detail_err_count=[0]*10
    _series_err_count=0


    _cmd_lengh=None
    _stop=False

    _send=0
    _error=0

    _last_re_count = None

    
    def __init__(self):       
        pass

    
    """ ==============================
        外部函数，初始化通讯对象
        参数：port 0-N，指第几个COM口
        
    """
    def init(self, port=0, baud=19200):
        try:
            # 串口通讯对象 （用于与采样板通讯）
            if 'Windows' in platform.system():
                    self._obj = serial.Serial(port="COM" + str(port), baudrate=baud, bytesize=8, parity='N', stopbits=2, timeout=1, xonxoff=0, rtscts=0, writeTimeout = 2)
                    
            if "Linux" in platform.system():
                    self._obj = serial.Serial(port="/dev/serial" + str(port), baudrate=baud, bytesize=8, parity='N', stopbits=2, timeout=1, xonxoff=0, rtscts=0, writeTimeout = 1)
            return True
            
        except Exception, e:
            print "rs485 init: " + str(e)
            return False
        
        
    """ ==============================
        外部函数，释放对象引用的资源
        参数：
        
    """   
    def release(self):
        
        if self._obj != None:
            self._obj.close()
        self._obj = None
        #GPIO.cleanup()
        
        
        
    """ ==============================
    外部函数，与指定设备进行通讯
    参数：arbitration_id 设备ID / (RS版本是0-N，CAN版本是设备ID+命令字)
    data 发送内容
    recvLen 需要会送的内容（RS版本至0，由通讯协议动态获得回收内容应该的长度）
           
    """        
    def sendto(self, arbitration_id, data,recvLen=0):
        #global GPIO



        #主板
        if self._comm_busy:
            return False

        if data[3]==0x01:
            cmd_data_len=0
        elif data[3]==0x02:
            cmd_data_len=24
        elif data[3]==0x04:
            cmd_data_len=0
        elif data[3]==0x06:
            # cmd_data_len=50
            cmd_data_len=50
        elif data[3]==0x08:
            cmd_data_len=1
        elif data[3]==0x0A:
            cmd_data_len=60
        elif data[3]==0x2E:
            cmd_data_len=40
        elif data[3]==0x22:
            cmd_data_len=0
        elif data[3]==0x24:
            cmd_data_len=6
        elif data[3]==0x25:
            cmd_data_len=40

        #io板
        # if cmd_code==0x02:
        #     cmd_data_len=105
        # elif cmd_code==0x03:
        #     cmd_data_len=0

        self._cmd_lengh=cmd_data_len+5

        sendCount = 0
        #print "sendto:" + str(arbitration_id) + ": " + str(data)
        #for i in data:
        #    print str(data[i])
        
        for c in range(0,3):
            if self._stop == False:
                self._comm_busy = True
                self._comm_recv_buffer = None
                self._comm_recv_idx_module = -1
                #GPIO.output(12, GPIO.HIGH)
                #time.sleep(0.001)
                #self._ser.flush()

                #发送
                #print "send",data,self._detail_err_count
                beginTm=time.time()
                self._obj.flushInput()
                self._obj.write(data)
                self._obj.flush()

                #回收
                ret = False
                recv = self._obj.read(self._cmd_lengh)#str
                if len(recv)!=0:
                    recv_data=[0]*len(recv)
                    for i in range(0,len(recv)):
                        recv_data[i] = ord(recv[i])
                    #回收校验
                    (ret,idx_module,buffer) = self.do_check_recvBuffer(recv_data)
                    if ret==True:
                        #print "onbaod:",time.time()-beginTm
                        self._comm_recv_buffer = buffer
                        self._comm_recv_idx_module = idx_module
                        #break
                        #print "data:",recv_data
              
                        #print G_b_count,G_b_time

                    #通讯错误记录
                    if ret!=True:
                        print recv_data
                        (err_msg,err_code) = self.do_check_recvBuffer_error(recv_data)
                        if self._series_err_count<20:
                            with open("/home/pi/hf_formation/run/rs485.log","a+") as file:
                                file.write("beginTime,"+str(beginTm)+","+ \
                                    "total_err_count,"+str(self._total_err_count)+","+ \
                                    "detail_err_count,"+str(self._detail_err_count)+","+ \
                                    "now_err_msg,"+str(err_msg)+","+ \
                                    "now_err_type,"+str(err_code)+","+ \
                                    "recv,"+str(recv_data)+","+"send,"+str(data)+",\r\n" \
                                )
                            print "beginTime,"+str(beginTm)+","+ \
                                    "total_err_count,"+str(self._total_err_count)+","+ \
                                    "detail_err_count,"+str(self._detail_err_count)+","+ \
                                    "now_err_msg,"+str(err_msg)+","+ \
                                    "now_err_type,"+str(err_code)+","+ \
                                    "recv,"+str(recv_data)+","+"send,"+str(data)
                        self._series_err_count+=1
                        self._total_err_count+=1
                        self._detail_err_count[err_code]+=1
                        # self._stop=True
                    else:
                        self._series_err_count=0
                        self._detail_err_count[9]+=1

                #返回
                self._comm_busy=False
                if len(recv)!=self._cmd_lengh:
                    time.sleep(0.05)
                if ret==True:
                    return self._comm_recv_idx_module, self._comm_recv_buffer
        return self._comm_recv_idx_module, self._comm_recv_buffer

    def do_check_recvBuffer(self, buffer):
        # try:
            #buffer = bytearray()
            #buffer.extend(s_buffer)

            #for i in range(0,len(s_buffer)):
            #    data[i] = hex(ord(s_buffer[i]))
               
            #buffer.extend(data)
            #print type(s_buffer)

            ret = False
            done = False
            module = -1
            data_length = 0

            if buffer[0] == 0X55:
                ret = True
            else:
                return (False,-1,None)

            if buffer[1] == 0X00:
                done = True
            else:
                return (False,-1,None)

            module = buffer[2]
            data_length = buffer[3]

            if data_length == 0X00:
                return (True,module,None)

            if module<0:
                return (False,-1,None)
    
            if (len(buffer)-5)<data_length:
                return (False,module,None)

            #print "a",hex(self.getModCRC(buffer[0:len(buffer)-1]))
            #for k in range(0, len(buffer)):
            #    print "c:",hex(buffer[k])
            #print "c",buffer[-1]
            #print "d",buffer[len(buffer)-1]
            #print "buffer",buffer

            if self.getModCRC(buffer[0:len(buffer)-1])!=buffer[len(buffer)-1]:
                return (False,module,None)
            
            #else:
            #    print "buffer",buffer
        # except Exception,e:  
        #     print "rs485 check: ",e
        #     return (False,-1,None)  
            return  (True,module,buffer)



    """ ==============================
    判定当前buffer的错误是什么
    参数：
    buffer 回收到的数据
    返回值：错误信息 错误类型
    """
    def do_check_recvBuffer_error(self, buffer):
        try:
            #buffer = bytearray()
            #buffer.extend(s_buffer)

            #for i in range(0,len(s_buffer)):
            #    data[i] = hex(ord(s_buffer[i]))
               
            #buffer.extend(data)
            #print type(s_buffer)

            ret = False
            done = False
            module = -1
            data_length = 0
            if buffer!=[]:
                pass
            else:
                return ("none recv",0)
            if buffer[0] == 0X55:
                pass
            else:
                return ("recv head error",1)

            if buffer[1] == 0X00:
                pass
            else:
                return ("board receipt false",2)

            module = buffer[2]
            data_length = buffer[3]

            if data_length == 0X00:
                return (str(module)+"none date",3)

            if module<0:
                return (str(module)+"board lower zero",4)

            if (len(buffer)-5)<data_length:
                return (str(module)+"data len error",5)
            #print "a",hex(self.getModCRC(buffer[0:len(buffer)-1]))
            #for k in range(0, len(buffer)):
            #    print "c:",hex(buffer[k])
            #print "c",buffer[-1]
            #print "d",buffer[len(buffer)-1]
            #print "buffer",buffer
            if self.getModCRC(buffer[0:len(buffer)-1])!=buffer[len(buffer)-1] :
                return (str(module)+"crc error",6)
            
            #else:
            #    print "buffer",buffer
        except Exception,e:
            print "rs485 error check: ",e
            return ("unknow error",7)  
        return  ("none error",8)

    def getModCRC(self, lt):
        byte_crc = 0
        #print "lt:",lt
        for i in range(0, len(lt)):
                byte_crc = byte_crc + lt[i]
                #print "byte_crc1",byte_crc
                #print "lt:",lt[i]
                
        #print "byte_crc2",byte_crc       
        byte_crc = byte_crc % 256
        #print "byte_crc3",byte_crc
        return byte_crc
        
    """ ==============================
          reset bus. 
    """        
    def reset_bus(self):
        pass

    """ ==============================
    线程--串口通讯接收线程
              用于与采样板进行数据通讯
    参数：
            ==
    返回：
            ==
    """

