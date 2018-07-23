#!/usr/bin/env python
# -*- coding: utf-8 -*-
import smbus
import time



def list_to_int(data):
    return int("".join(str(x) for x in list(reversed(data))),2)

def int_to_list(i):
    return bin(i)[2:].zfill(16)

class hf_iic(object):

    _bus = None
    _IO_BUFFER = [0] * 32
    g_check_sumt = [0] * 2 
    g_check_sumr = [0] * 2
    
    def __init__(self):
        pass


    def init(self, port = 1):
        try:
            self._bus = smbus.SMBus(port)
            self.get()
            return True

        except Exception, e:
            print "iic: " + str(e)
            return False

    def send(self):
        for i in range(0,10):
            try:
                time.sleep(0.2)
                self.g_check_sumt[0],self.g_check_sumt[1] = self.check_byte(self._IO_BUFFER[0:30])
                #print "self._IO_BUFFER",self._IO_BUFFER
                #print "self.g_check_sumt",self.g_check_sumt
                self._IO_BUFFER[30] = self.g_check_sumt[0]
                self._IO_BUFFER[31] = self.g_check_sumt[1]
                #print "self._IO_BUFFER",self._IO_BUFFER
                self._bus.write_i2c_block_data(0x30, 0x02, self._IO_BUFFER)
                return True
            except Exception, e:
                print "iic: " + str(e)      
        
    def get(self):
        ret = False
        for i in range(0,10):
            try:
                time.sleep(0.2)
                data =  self._bus.read_i2c_block_data(0x30, 0x01, 32)
                self.g_check_sumr[0],self.g_check_sumr[1] = self.check_byte(data[0:30])
                #print "self.g_check_sumr",self.g_check_sumr
                #print "data",data
                if self.g_check_sumr[0] == data[30] and self.g_check_sumr[1] == data[-1]:
                    self._IO_BUFFER = data
                    ret = True
                    break
            except Exception, e:
                print "iic: " + str(e)
        if ret == False:
            return None
        else:
            return self._IO_BUFFER
        

    def set(self, k, v):
        if k>=0 and k<30:
            self._IO_BUFFER[k]=v
        else:
            print "iic key:" + str(k) +" error."
    
    def check_byte(self,l):
        total_sum = 0
        for c in range(0,len(l)):
            total_sum = total_sum + l[c]
        value_LI  = total_sum & 0xff
        value_HI  = (total_sum >> 8) & 0xff
        return value_LI,value_HI    
      
        
        
def test():
    iic = hf_iic()
    iic.init(1)
    #time.sleep(0.3)
#   iic.set(28,1)
    #iic.set(23, 1)
    #iic.send()
    #time.sleep(3)
    for i in range(12,28):
        iic.set(i, 1)
    #iic.set(11, 1)
    iic.send()
    print iic.get(),"====iic get ===="
    #iic.get()

if __name__ == '__main__':
    test()

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
