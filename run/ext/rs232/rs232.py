#!/usr/bin/env python
# -*- coding: utf-8 -*-

import serial
import time
import sys
import threading
import platform
import RPi.GPIO as GPIO

# BOARD编号方式，基于插座引脚编号
GPIO.setmode(GPIO.BOARD)
# 输出模式
GPIO.setup(12, GPIO.OUT)

class rs232(object):

    __th_recv = None
    _ser = None
    _comm_busy = False
    _comm_recv_buffer = None
    _comm_recv_idx_module = -1
    s_buffer = ""
    _s_return = False
    
    def __init__(self):       
        pass

    
    """ ==============================
        外部函数，初始化通讯对象
        参数：port 0-N，指第几个COM口
        
    """
    def init(self, port=0, baud=19200):
        try:
            self.__th_recv = self.cls_recv_Thread('recv_thread',self)
            self.__th_recv.setDaemon(True) 
            # 串口通讯对象 （用于与采样板通讯）
            if 'Windows' in platform.system():
                    self._ser = serial.Serial(port="COM" + str(port), baudrate=baud, bytesize=8, parity='N', stopbits=2, timeout=None, xonxoff=0, rtscts=0)
                    
            if "Linux" in platform.system():
                    self._ser = serial.Serial(port="/dev/serial" + str(port), baudrate=baud, bytesize=8, parity='N', stopbits=2, timeout=None, xonxoff=0, rtscts=0)
                    
            self.__th_recv.start()
            return True
            
        except Exception, e:
            print "rs232: " + str(e)
            return False
        
        
    """ ==============================
        外部函数，释放对象引用的资源
        参数：
        
    """   
    def release(self):
        
        if self._ser != None:
            self._ser.close()
            
        if self.__th_recv != None:
            self.__th_recv.stop()
            
        self.__th_recv = None
        self._ser = None
        
        
        
    """ ==============================
    外部函数，与指定设备进行通讯
    参数：arbitration_id 设备ID / (RS版本是0-N，CAN版本是设备ID+命令字)
    data 发送内容
    recvLen 需要会送的内容（RS版本至0，由通讯协议动态获得回收内容应该的长度）
           
    """        
    def sendto(self, arbitration_id, data, recvLen=0):

        if self._comm_busy == True:
            return False

        sendCount = 0
        for c in range(0,3):
                self._comm_busy = True
                self._comm_recv_buffer = None
                self._comm_recv_idx_module = -1
                self.s_buffer = ""
                self._s_return = False
                GPIO.output(12, GPIO.HIGH)
                time.sleep(0.001)
                self._ser.flushInput()
                self._ser.write(data)
                beginTm = time.time()
        
                while self._comm_busy==True and time.time()-beginTm<4:
                    time.sleep(0.05)
                self._comm_busy=False
                if self._s_return==True:
                    return self._comm_recv_idx_module, self._comm_recv_buffer
                else:
                    print "rs232: ======= OUT ====="
                    time.sleep(0.5)
                #检查 _comm_recv_buffer 是否有数据，非None证明是正常返回，否则False
                #print self._comm_recv_buffer
        
        return self._comm_recv_idx_module, self._comm_recv_buffer
                
                

    """ ==============================
    线程--串口通讯接收线程
              用于与采样板进行数据通讯
    参数：
            ==
    返回：
            ==
    """
    class cls_recv_Thread(threading.Thread):
        
        __parent = None
    
        def __init__(self, name, parent):
            threading.Thread.__init__(self)
            self.t_name = name
            self.__parent = parent
            
        def run(self):
            _ser_count = 0
            self.__parent.s_buffer = ""
            while True:
                if self.__parent._comm_busy == True:
                    # 获得接收缓冲区字符 
                    count = self.__parent._ser.inWaiting()
                    if count != 0:  
                        # 读取内容并回显
                        _ser_count = 0
                        time.sleep(0.001)
                        GPIO.output(12, GPIO.LOW)
                        recv = self.__parent._ser.read(count)
                        self.__parent.s_buffer += recv
                        if self.__parent.s_buffer != "":
                            #print type(s_buffer)
                            #print s_buffer.encode("hex")
                            (ret,idx_module,buffer) = self.do_check_recvBuffer(self.__parent.s_buffer)
                            
                            #if ret==True and buffer != None:
                                #do_batteryBuffer2Json(idx_module,buffer)
                            #    pass
                            # 获得正常数据，返回并告知主函数
                            if ret==True:
                                print "rs232: done"
                                self.__parent._s_return = True
                                self.__parent._comm_recv_buffer = buffer
                                self.__parent._comm_recv_idx_module = idx_module
                                self.__parent.s_buffer = "TRUE"
                                self.__parent._comm_busy = False
                                    
                        # 清空接收缓冲区      
                        self.__parent._ser.flushInput()
                        
                    else:
                        #self.__parent._ser.flushInput()
                        ##如果接收为0，则读取状态加1，3次超时为通讯错误，退出
                        #_ser_count = _ser_count + 1
                        #if _ser_count>3:
                        #        self.__parent._ser.flushInput()
                        #        time.sleep(0.2)
                        #        print str(_ser_count) + "================time_out=================="
                        #if _ser_count > 4:
                        #    print str(_ser_count) + "================time_out=================="
                        #    # 超时，返回，并且告知主函数
                        #    s_buffer = ""
                        #    self.__parent._comm_busy = False
                        pass
                else:
                    pass
                    #print recv.encode("hex")
                    
                # 必要的软件延时 
                time.sleep(0.001)
                    
                
        """ ==============================
        动作--检查返回的buffer是否ok-
        参数：
                s_buffer   回收的buffer字符
        返回：
                True/False,index_module,byteArray
        """
        def do_check_recvBuffer(self, s_buffer):
            try:
                buffer = bytearray()
                buffer.extend(s_buffer)
        
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
        
                if self.getModCRC(buffer[0:len(buffer)-2])!=buffer[len(buffer)-1]:
                        return (False,module,None)
                        
            except Exception,e:  
                    print Exception,"rs232: ",e
                    return (False,-1,None)
        
            return  (True,module,buffer)
 
 
        """ ==============================
        计算--命令数据的CRC校验码
        参数：
        lt 输入的命令全部内容
        """
        def getModCRC(self, lt):
            byte_crc = 0
            for i in range(0, len(lt)):
                    byte_crc = byte_crc + lt[i]
            byte_crc = byte_crc % 256
            return byte_crc
