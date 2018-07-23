#!/usr/bin/env python
# -*- coding: utf-8 -*  
import os
import sys
import signal
import subprocess
import time
import threading
import traceback
import json
import logging
import socket
from urllib import urlretrieve
from hashlib import md5
'''
if os.path.exists("/home/pi/hf_formation/run/ext/main/hf_main.so"):
    current_cwd = os.getcwd()
    print current_cwd
    os.chdir("/home/pi/hf_formation/run/ext/")
    current_cwd = os.getcwd()
    os.system("find -name '*.py' |xargs rm -rf")
    print "delet py files"
    os.chdir(current_cwd)
'''
""" ==============================
下载文件
"""
def hf_download_file(url, fn):
    try:
        #print "hello"
        ret =  urlretrieve(url,fn)
        #print "hey"
        return ret 
    except:
        print "url error"
        return False

""" ==============================
文件md5sum
"""
def hf_md5sum(fn):
    hf_md5 = md5()
    with open(fn, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hf_md5.update(chunk)
    return hf_md5.hexdigest()

def do_setIO(io_out):
    obj = None
    #G_SENSOR["io"]["OUT"]
    try:
        obj = {"action":"sensor_write", "data":io_out}
        sendUDPMessage(json.dumps(obj), 9099)
    except Exception, e:
        pass
    pass

def do_Led_OFF():
    try:
        io_out = {}
        io_out["LED_READY"] = 0
        io_out["LED_RUN"] = 0
        io_out["LED_ERROR"] = 0
        do_setIO(io_out)
    except Exception, e:
        print "LED:", str(e)
        pass

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
                try:
                    sock.bind(('', 9098))       # 绑定同一个域名下的所有机器
                except socket.error as msg:
                    sock.close()
                    os.kill(os.getpid(), signal.SIGINT)
                while True: 
                        revcData, (remoteHost, remotePort) = sock.recvfrom(65526)
                        ret = do_json_command_solver(revcData)
                        #print("[%s:%s] connect" % (remoteHost, remotePort))     # 接收客户端的ip, port  

                        #分包发送
                        if len(ret)>32768:
                                n = len(ret) / 32768
                                m = len(ret) % 32768
                                for i in range(0,n):
                                        print "hf_main" + str(len(ret[i*32768:i*32768+32768]))
                                        sock.sendto(ret[i*32768:i*32768+32768], (remoteHost, remotePort)) 
                                sock.sendto(ret[(i+1)*32768:(i+1)*32768+m], (remoteHost, remotePort))
                        else:
                                sock.sendto(ret, (remoteHost, remotePort))
                sock.close() 

""" ==============================
线程--自动更新程序-线程

参数：
        ==
返回：
        ==
"""
class update_thread(threading.Thread):
        def __init__(self, name, fn):
                threading.Thread.__init__(self)
                self.t_name = name
                self._fn = fn
        def run(self):
            c = 0
            last_cpu_stat = False
            while c < 10:
                c += 1
                if check_cpu_stat():
                    do_Led_OFF()
                    if last_cpu_stat:
                        os.system("bash " + self._fn)
                        os.system("sync")
                        os.system("sync")
                        os.system("sync")
                        time.sleep(1)
                        os.system("sudo reboot")
                    else:
                        last_cpu_stat = True
                else:
                    last_cpu_stat = False
                time.sleep(15)

""" ==============================
动作--运算ui端发过来的json指令

参数：
        s_json:json命令的字符串
返回：
        结果的json字符串
"""
def do_json_command_solver(s_json):
        
        try:
                obj_json = json.loads(s_json)
                action = obj_json["action"]
        except Exception,e:
                logging.debug('get json error:' + s_json)
                ret = '{"success":"false","msg":"json decode error"}'
                return ret            
        
        ret = '{"success":"false"}'
        if action == "version_update":
            url = obj_json["url"]
            key = obj_json["key"]
            print "update url:",url
            print "key:",key
            ret = do_update_hf(url,key)
            #ret = '{"success":"true"}'
            print "version_update"
        else:
            print "Do not have active selection for:" + action
        return ret

""" ==============================
动作--check_cpu_stat()

参数：
        -
返回：
        -
"""
def check_cpu_stat():
    obj = {"action":"unit_stat_readall"}
    try:
        obj_json = json.loads(sendUDPMessage(json.dumps(obj),9088))
        if int(obj_json["data"][0]["station"]) != 0:
            return False
        return True
    except Exception, e:
        return True

""" ==============================
动作--do_update_hf()

参数：
        -
返回：
        -
"""
def do_update_hf(url,key):
    fn = G_PATH + "/hf_update_tmp" + ".sh"
    print "fn:",fn
    try:
        print "do_update_hf\n"
        ret = hf_download_file(url,fn)
        
        print "do_update_hf1\n"
        if ret == False:
            print "downlaod file error"
        if hf_md5sum(fn) == key:
            print "hf_md5sumfn== key"
            _up = update_thread('up_thread',fn)
            _up.start()
            print "key is right"
            return '{"success":"true"}'
        else:
            print "key is error"
            return '{"success":"false"}'
    except EnvironmentError:
        print "do_update_hf2\n"
        pass
    return '{"success":"false"}'

def sendUDPMessage(message, port=9088):
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


threads = []
G_PATH = os.getcwd()
class hf_run(threading.Thread):
    
    _proc = None
    _command = None
    retval = None
    _run = False
    _thread = None
    _kill_received = False
    _fh = None
    
    def __init__(self,command):
        threading.Thread.__init__(self)
        self._command = command
        self.daemon = True
    
    def run(self):
        global G_PATH
        #self._fh = open(G_PATH + "/" + str(self._command[-1]) + ".log", 'a+') 
        while not self._kill_received:
            print "running: " + str(self._command[-1])
            self._proc = subprocess.Popen(self._command, shell = False, stdout=None, bufsize=80, stderr=subprocess.STDOUT, cwd=G_PATH)
            self.retval = self._proc.wait()
            time.sleep(1)
        #self._fh.close()
        #self._fh = None


def test():
    global threads
    t = hf_run(["sleep","5"])
    t1 = hf_run(["ls","-l"])
    threads.append(t)
    threads.append(t1)
    t.start()
    t1.start()
    time.sleep(0.1)

    while len(threads) > 0:
        print "hf_main" + str(threads)
        try:
            # Join all threads using a timeout so it doesn't block
            # Filter out threads which have been joined or are None
            #threads = [t.join(1) for t in threads if t is not None and t.isAlive()]
            threads = [t for t in threads if t is not None and t.isAlive()]
            time.sleep(1)
        except KeyboardInterrupt:
            print "Ctrl-c received! Sending kill to threads..."
            for t in threads:
                t._kill_received = True
            
def main():
    global threads
    global G_PATH
    os.chdir(G_PATH)
    _th_udp = cls_udp_Thread('udp_thread')
    _th_udp.setDaemon(True)
    _th_udp.start()

    hf_control = hf_run(["sudo","-u","pi","python","hf-control.py"])
    hf_io = hf_run(["sudo","-u","pi","python","hf-io.py"])
    threads.append(hf_control)
    threads.append(hf_io)
    hf_io.start()
    time.sleep(2)
    hf_control.start()
    while len(threads) > 0:
        try:
            #threads = [t.join(1) for t in threads if t is not None and t.isAlive()]
            threads = [t for t in threads if t is not None and t.isAlive()]
        except KeyboardInterrupt:
            print "Ctrl-c received! Sending kill to threads..."
            for t in threads:
                t._kill_received = True
        time.sleep(1)
            
    
def exit_gracefully(signal, frame):
        #... log exiting information ...
        #... close any open files ...
        print "hf-main is closed..."
        sys.exit(0)
        

if __name__ == '__main__':
        try:  
            signal.signal(signal.SIGINT, exit_gracefully)
            main()  
            #test()
        except KeyboardInterrupt:
            pass
        except Exception,e:
            try:
                #logging.debug('main error :' + e)
                print "hf_main: " + str(e)
                exc_info = sys.exc_info()
                try:
                    raise TypeError("main error: ")
                except:
                    pass
                #traceback.print_exec()
            finally:
                traceback.print_exception(*exc_info)
                #del exe_info
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
