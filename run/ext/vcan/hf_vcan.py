import mcp2515
import threading
import time
import os
from mcp2515 import *



hf_vcan_object = None
def getModCRC(lt):
    byte_crc = 0
    #print "lt:",lt
    #print "len(lt):",len(lt)
    for i in range(0, len(lt)-1):
            byte_crc = byte_crc + lt[i]     
    byte_crc = byte_crc % 256
    #print "byte_crc3",byte_crc
    return byte_crc  
    

def signedFromHex32(s): 
    v = int(s, 16)
    if not 0 <= v < 4294967296: 
        raise ValueError, "hex number outside 32 bit range" 
    if v >= 2147483648:
        v = v - 4294967296 
    return v
    
def hexBYTE(dec):
    return ("%x"%(dec&0xff)).zfill(2)
        
class hf_vcan(object):
    __th_recv = None
    _ser = None
    _comm_busy = False
    _comm_recv_buffer = None
    _comm_recv_idx_module = -1
    s_buffer = ""
    _s_return = False 
    _th_received_flag = False
    param = None
    instance = None
    sending_id = None
    ret_len = None
    right = 0
    count_sum_IO = 0
    count_right_IO = 0
    count_error_IO = 0
    run_again_IO = 0
    
    
    count_sum = 0
    count_right = 0
    count_error = 0
    run_again = 0
    count_again_one = 0
    count_again_two = 0
    count_again_three = 0
    count_again_four = 0
    count_again_five = 0
    count_again_six = 0
    count_again_seven = 0
    count_again_eight = 0
    count_again_nine = 0
    count_again_ten = 0
    
    count_send_error = 0
    count_send_errorIO = 0
    def init(self, port=1,use_crc = False):
        try: 
            #print "self.instance:",self.instance
            #if self.instance == None:
            self.instance= mcp2515()
            if port == 1:
                print "port:",port
                self.param = {'in':{'port':port, 'clock':mcp2515_con.MCP_8MHZ, 'speed':mcp2515_con.CAN_100KBPS}}
            if port == 0:
                print "port:",port
                self.param = {'in':{'port':port, 'clock':mcp2515_con.MCP_8MHZ, 'speed':mcp2515_con.CAN_250KBPS}}
            self.instance.deinit()
            ret = self.instance.init(self.param)
            
            if   ret is not None:
                print 'init done'
            else:
                return None
            print "hey"
        except Exception, e:
            print "can: " + str(e)
            #return None  
        finally:
            print "this is finally"            
            
    def reset(self):
        self.param = {'in':{'port':0, 'clock':mcp2515_con.MCP_8MHZ, 'speed':mcp2515_con.CAN_250KBPS}}
        ret = self.instance.init(self.param)
        return True

    def reset_IO(self):
        self.param = {'in':{'port':1, 'clock':mcp2515_con.MCP_8MHZ, 'speed':mcp2515_con.CAN_100KBPS}}
        ret = self.instance.init(self.param)
        return True
        


                        
    def sendto_IO(self, board, data, save):
        #global GPIO
        self.ret_len = 0
        dat = None
        sendCount = 0
        self._comm_recv_buffer = None
        self.sending_id = None
        self._comm_recv_idx_module = -1
        self.s_buffer = ""
        self._s_return = False
        self._comm_busy = True
        beginTm = time.time()
        message = None
        id_message = None
        id = 0

        tmp = data.split(',')
        self.ret_len = int(tmp[-1]) #received lenghth
        #print "ret_len",self.ret_len    
   
        retries = 16
        self.run_again_IO  = 0
        while self.run_again_IO < retries:  
            time.sleep(0.02)
            self.count_sum_IO = self.count_sum_IO + 1
            for c in tmp[:-1]:
                d = c.split('#')   
                self.sending_id = int(d[0], 16)  
                message = []*8
                for i in range(0, len(d[1]),2):
                    dat = int(d[1][i:i+2],16)
                    message.append(dat)
                #print "instance1234:",self.instance
                if self.instance == None:
                    #print "this is none2"
                    return self._comm_recv_idx_module, None
                
                #for self.run_again in range(0,16):
                self.param = {'in':{'message':message, 'length':len(message) , 'id':self.sending_id, 'flag':1, 'rtr':0}, 'out':{}}
                #print "self.param:",self.param
                ret_send = self.instance.sendCANMsg(self.param)   
  
                if self.ret_len ==0:  
                    return self._comm_recv_idx_module, None
                    
                #print "ret_send:",self.ret_send
                if ret_send == None:
                    print "sendCANMsg errror ,continue to sendCANMsg"
                    continue
                    #return self._comm_recv_idx_module, None
                
                if ret_send is not None:
                    self._comm_recv_buffer = []
                    # write command reurn 1 bits
                    self.param = {'in':{'length':self.ret_len, 'time_interval':0.1}, 'out':{}}
                    ret  = self.instance.readCANMsg_anyway(self.param)

                    if ret  is not None:
                        dic_IO = self.param['out']['message']
                        mydic_IO = sorted(dic_IO.iteritems(),key = lambda asd:asd[0],reverse = False)
                        
                        list_IO = []
                        for i in range(0,len(mydic_IO)):
                            list_IO.extend(mydic_IO[i][1])

                        received_error_IO = 0
                        for j in range(0,len(mydic_IO)):
                            if self.sending_id >>8 != mydic_IO[j][0]>>8:
                                received_error_IO = 1
                                print "hello"
                                break
                                
                            if j >1:
                                if mydic_IO[j][0]- mydic_IO[j-1][0] != 1:
                                    received_error_IO = 1
                                    break
                                
                        if received_error_IO == 1:
                            print "received data error,the id is error"
                            time.sleep(0.05)
                            break
                        
                        
                            
                        if self.ret_len == len(list_IO) and getModCRC(list_IO) == list_IO[-1]:
                            #print "list_IO:",list_IO
                            return self._comm_recv_idx_module,list_IO
                            
                    else:
                        if self.ret_len ==1:
                            time.sleep(0.5)
                            return self._comm_recv_idx_module, None
                        
                        
                        self.run_again_IO = self.run_again_IO + 1
                        if self.run_again_IO >14:
                            self.count_error_IO = self.count_error_IO +1

                        if self.run_again_IO > 4:
                        
                            fs = open("/home/pi/hf_formation/run/data/debug_IO.dat","a+")
                            fs.write("*\n")
                
                            fs.write("run_again_IO:")
                            fs.write(str(self.run_again_IO))
                            fs.write(" ")
                        
                            fs.write("count_sum:")
                            fs.write(str(self.count_sum_IO))
                            fs.write(" ")
 
                            fs.write("count_error_IO:")
                            fs.write(str(self.count_error_IO))
                            fs.write(" ")
                            
                            fs.write("send_data:")
                            fs.write(str(c))
                            fs.write(" ")
                            fs.write("\n")
                            fs.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
                            fs.write("*\n")
                            fs.close()                          
                        time.sleep(0.05)
        return self._comm_recv_idx_module, None
        
        

                            
   
    def sendto(self, board, data, save):
        #global GPIO
        self.ret_len = 0
        dat = None
        sendCount = 0
        self._comm_recv_buffer = None
        self.sending_id = None
        self._comm_recv_idx_module = -1
        self.s_buffer = ""
        self._s_return = False
        self._comm_busy = True
        beginTm = time.time()
        message = None
        id_message = None
        id = 0
        #vcan.sendto("0", "01e00100#0000000000000000,01e00101#0000000502000000,01e00102#b80b0000ffff,1", -1)
        tmp = data.split(',')
        self.ret_len = int(tmp[-1]) #received lenghth
        #print "ret_len",self.ret_len   

        
        retries = 16
        self.run_again = 0
        received_error_data = 0
        while self.run_again < retries:   
            time.sleep(0.02)
            self.count_sum = self.count_sum + 1
            for c in tmp[:-1]:
                d = c.split('#')   
                #print "d0:",d[0]
                self.sending_id = int(d[0], 16) 
                
                self._comm_recv_idx_module = int(int(d[0][:4], 16) >> 5)
                message = []*8
                for i in range(0, len(d[1]),2):
                    dat = int(d[1][i:i+2],16)
                    message.append(dat)
                if self.instance == None:
                    #print "this is none2"
                    return self._comm_recv_idx_module, None
                #for self.run_again in range(0,16):
                #print "message:",message
                #print "self.sending_id",hex(self.sending_id)
                self.param = {'in':{'message':message, 'length':len(message) , 'id':self.sending_id, 'flag':1, 'rtr':0}, 'out':{}}
                ret_send = self.instance.sendCANMsg(self.param)   

                #print "ret_send:",self.ret_send
                #print "c:",c
                #print "tmp[-2]:",tmp[-2]
                # not last one
                if c != tmp[-2] :
                    continue
                    
                    
                # last one but can error
                if ret_send == None and c == tmp[-2]:
                    print "sendCANMsg errror ,continue to sendCANMsg"
                    
                    break
                    #return self._comm_recv_idx_module, None
                    
                
                if ret_send is not None:
                    self._comm_recv_buffer = []
                    # write command reurn 1 bits
                    self.param = {'in':{'length':self.ret_len, 'time_interval':0.1}, 'out':{}}
                    ret  = self.instance.readCANMsg_anyway(self.param)
                    
                    #print "self.count_sum",self.count_sum,"self.count_error",self.count_error
                    #print "self.count_again_one",self.count_again_one,"self.count_again_two",self.count_again_two,"self.count_again_three",self.count_again_three
                    #print "self.count_again_four",self.count_again_four,"self.count_again_five",self.count_again_five
                    #print "self.count_again_six",self.count_again_six,"self.count_again_seven",self.count_again_seven,"self.count_again_eight",self.count_again_eight
                    #print "self.count_again_nine",self.count_again_nine,"self.count_again_ten",self.count_again_ten
                    
                    if ret  is not None:
                        self.count_right = self.count_right +1
                        
                        if self.run_again ==1:
                            self.count_again_one = self.count_again_one+1
                        if self.run_again==2:
                            self.count_again_two = self.count_again_two+1
                        if self.run_again == 3:
                            self.count_again_three = self.count_again_three +1
                        if self.run_again ==4:
                            self.count_again_four = self.count_again_four+1
                        if self.run_again==5:
                            self.count_again_five = self.count_again_five+1
                        if self.run_again ==6:
                            self.count_again_six = self.count_again_six+1
                        if self.run_again==7:
                            self.count_again_seven = self.count_again_seven+1
                        if self.run_again == 8:
                            self.count_again_eight = self.count_again_eight +1
                        if self.run_again ==9:
                            self.count_again_nine = self.count_again_nine+1
                        if self.run_again==10:
                            self.count_again_ten = self.count_again_ten+1
                           
                        
                        dic = self.param['out']['message']
                        #print "dic",dic
                        mydic = sorted(dic.iteritems(),key = lambda asd:asd[0],reverse = False)
                        #mydic = sorted(dic)
                        #print "message_zhuban: = ", mydic
                        
                        
                        received_error_data = 0
                        for i in range(0,len(mydic)):
                            if self.sending_id >>8 != mydic[i][0]>>8:
                                received_error_data = 1
                                print "hello_board"
                                break
                                
                            #bard_num = int(str(mydic[i][:4], 16) >> 5)
                            if i >1:
                                if mydic[i][0]- mydic[i-1][0] != 1:
                                    received_error_data = 1
                                    break
									
                            #print "bard_num:",mydic[i][0]>>21
                            #print  "self._comm_recv_idx_module:",self._comm_recv_idx_module 
                            if (mydic[i][0]>>21) != self._comm_recv_idx_module:
                                fs = open("/home/pi/hf_formation/run/data/debug_error_data.dat","a+")
                                fs.write(str(mydic))
                                fs.close()
                                received_error_data = 1
                                break
                                
                        if received_error_data == 1:
                            print "received data error,the id is error"
                            time.sleep(0.05)
                            break
                           
                            
                        self.run_again = 0            
                        list = []
                        for i in range(0,len(mydic)):
                            list.extend(mydic[i][1])
                        #print "list:",list,"len:",len(list)  
                        #print "getModCRC:",getModCRC(list)
                        if self.ret_len == len(list)  and getModCRC(list) == list[-1]:
                            
                            if self.ret_len > 126:
                                cols = 16
                                rows = 2
                                pos = 0
                                battery_list1 = [[0 for col in range(cols)] for row in range(rows)]
                                for i in range(0, len(battery_list1[0])):
                                    data_hex = hexBYTE(list[0:len(list)-1][pos+3]) + hexBYTE(list[0:len(list)-1][pos+2]) + hexBYTE(list[0:len(list)-1][pos+1]) + hexBYTE(list[0:len(list)-1][pos])
                                    battery_list1[0][i] = signedFromHex32(data_hex)
                                    pos = pos + 4 
                                  
                                for i in range(0, len(battery_list1[1])):
                                    data_hex = hexBYTE(list[0:len(list)-1][pos+3]) + hexBYTE(list[0:len(list)-1][pos+2]) + hexBYTE(list[0:len(list)-1][pos+1]) + hexBYTE(list[0:len(list)-1][pos])
                                    battery_list1[1][i] = signedFromHex32(data_hex)
                                    pos = pos + 4
          
                                #print "battery_list1[0][i]:",battery_list1[0][0]
                                #print "battery_list1[1][i]:",battery_list1[1][0]
                                for i in range(0, len(battery_list1[1])):
                                    if battery_list1[0][i] > 45000 or battery_list1[1][i] > 70000:
                                        fs = open("/home/pi/hf_formation/run/data/debug_error.dat","a+")
                                        fs.write(str(battery_list1[0][i]))
                                        fs.write(str(battery_list1[1][i]))
                                        fs.write("*\n")
                                        fs.write("dic:")
                                        fs.write(str(dic))
                                        fs.write("\n")
                            
                                        fs.write("mydic:")
                                        fs.write(str(mydic))
                                        fs.write("\n")
                                        fs.write("now_time:")
                                        fs.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
                                        fs.write("*\n")
                                        fs.close() 
                                        break
                            return self._comm_recv_idx_module, list[0:len(list)-1]                           
                    else:
                        self.run_again = self.run_again + 1
                        if self.run_again > 4:
                            fs = open("/home/pi/hf_formation/run/data/debug.dat","a+")
                            fs.write("*\n")
                
                            fs.write("run_again:")
                            fs.write(str(self.run_again))
                            fs.write(" ")
                        
                            fs.write("count_sum:")
                            fs.write(str(self.count_sum))
                            fs.write(" ")
                            
                            fs.write("send_data:")
                            fs.write(str(c))
                            fs.write(" ")
                            fs.write("\n")
                            fs.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
                            fs.write("*\n")
                            fs.close()    
                            
                        if self.run_again >14:
                            self.count_error = self.count_error +1
                            
                            fs = open("/home/pi/hf_formation/run/data/debug.dat","a+")
                            fs.write("******************************************\n")
                           
                            fs.write("run_again:")
                            fs.write(str(self.run_again))
                            fs.write(" ")
                        
                            fs.write("count_sum:")
                            fs.write(str(self.count_sum))
                            fs.write(" ")
                            
                            fs.write("send_data:")
                            fs.write(str(c))
                            fs.write(" ")
                            fs.write("\n")
                            fs.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
                            fs.write("******************************************\n")
                            fs.close() 
 
                        if self.run_again > 2:
                            self.param = {'in':{'port':0, 'clock':mcp2515_con.MCP_8MHZ, 'speed':mcp2515_con.CAN_250KBPS}}
                            ret = self.instance.init(self.param)
                            time.sleep(0.01)
                            break
                        
   
                            
                        time.sleep(0.02)
        return self._comm_recv_idx_module, None
      
