#!/usr/bin/env python
# -*- coding: utf-8 -*-
import smbus
import time
import array

def list_to_int(data):
    return int("".join(str(x) for x in list(reversed(data))),2)

def int_to_list(i):
    return bin(i)[2:].zfill(16)

class hf_iic(object):

    _bus = None
    _IO_CTL_AREA_A = [0,0,0,0,0,0,0,0]
    _IO_CTL_AREA_B = [0,0,0,0,0,0,0,0]
    _IO_CTL_AREA_C = [0,0,0,0,0,0,0,0]
    _IO_CTL_AREA_D = [0,0,0,0,0,0,0,0]

    def __init__(self):
        pass


    def init(self, port = 1):
        try:
            self._bus = smbus.SMBus(port)
            return True

        except Exception, e:
            print e
            return False

    def send(self):
        try:
            self._bus.write_block_data(0x30,1,[list_to_int(self._IO_CTL_AREA_A),list_to_int(self._IO_CTL_AREA_B),list_to_int(self._IO_CTL_AREA_C),list_to_int(self._IO_CTL_AREA_D), self.gen_io_check()])
            return True
        except Exception, e:
            print e
            return False        

        
    def get(self):


        
        bus = smbus.SMBus(1)
        '''
        ret = [1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 91] * 5
        
        if len(ret)>32:
                n = len(ret) / 32
                m = len(ret) % 32
                for i in range(0,n):
                        bus.write_i2c_block_data(0x30,0x31,ret[i*32:i*32+32])
                        #sock.sendto(ret[i*32:i*32+32], (remoteHost, remotePort)) 
                
                bus.write_i2c_block_data(0x30,0x31,ret[(i+1)*32:(i+1)*32+m])
                #sock.sendto(ret[(i+1)*32:(i+1)*32+m], (remoteHost, remotePort))
        else:
         
        
        '''
        for i in range(0,100):
            data= bus.read_i2c_block_data(0x30,0x01,31) 
            print data
            arr = [1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 90]
            #data= bus.write_i2c_block_data(0x30,0x02,arr) 
            data= bus.read_i2c_block_data(0x30,0x01,31) 
            
            
            #time.sleep(0.01)
            
            data= bus.read_i2c_block_data(0x30,0x01,31) 
            arr = [1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 91]
            #data= bus.write_i2c_block_data(0x30,0x02,arr) 
            data= bus.read_i2c_block_data(0x30,0x01,31) 
            
            #time.sleep(0.01)
            
            print i+1
        
        '''
        arr = [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 90]
        pi = pigpio.pi()
        h=pi.i2c_open(1, 0x30)
        pi.i2c_write_device(h,arr)
        
        
        pi = pigpio.pi()
        h=pi.i2c_open(1, 0x30)
        (count, data1) = pi.i2c_read_device(h,32)
        for i in range(0,10000):
            (count, data) = pi.i2c_read_device(h,32)
            if data1 != data:
                c = c+1
            s = ""
            for v in data1:
                s = s + str(v) + ","
            print s
        '''
        '''
        data= self._bus.read_i2c_block_data(0x30,1,31) 
        for i in range(0,1000):
            try:
                data1= self._bus.read_i2c_block_data(0x30,1,31) 
                print data1, "==" , i
                if data != data1:
                    c=c+1
                pass
            except Exception, e:
                c=c+1
            pass
            #time.sleep(0.01)
        '''
        print "===================================="
        return

    def set(self, k, v):
        if k>=30 and k<=37:
            #用A区
            pin = abs(k-37)
            self._IO_CTL_AREA_A[pin] = v
            pass
            
        elif k>=40 and k<=44:
            #用B区
            pin = k-40
            self._IO_CTL_AREA_B[pin] = v
            pass
        
        elif k>=19 and k<=26:
            #用C区
            pin = k-19
            self._IO_CTL_AREA_C[pin] = v
            pass
            
        elif k>=9 and k<=16:
            #用D区
            pin = k-9
            self._IO_CTL_AREA_D[pin] = v
            pass
            
        else:
            print "key:" + str(k) +" error."
    
    def check_byte(self,l):
        x = 0x5A
        for c in range(0,len(l)):
            x ^= l[c]
        return x
    
    def gen_io_check(self):
        return self.check_byte(list([list_to_int(self._IO_CTL_AREA_A),list_to_int(self._IO_CTL_AREA_B),list_to_int(self._IO_CTL_AREA_C),list_to_int(self._IO_CTL_AREA_D)]))
        
        
        
def test():
    iic = hf_iic()
    iic.init(1)
#   iic.set(28,1)
    #iic.set(23, 1)
    #iic.send()
    #time.sleep(3)
    #iic.set(23, 0)
    iic.get()

if __name__ == '__main__':
    test()

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
