#!/usr/bin/env python
import os, sys, getopt
import subprocess

G_PATH = os.path.split(os.path.realpath(__file__))[0]

def print_help():
    print str(__file__) + " -u unit -c channel -p data_base_passwd --count=battery_count --lot=lot_id --user=data_base_user_name --ip=data_base_ip --data-path=data_path --tray=tray_id"

def run_cmd(_command):
    _proc = subprocess.Popen(_command, shell = False, bufsize=80, stderr=subprocess.STDOUT, cwd=G_PATH)
    return _proc.wait()

class mysql_cmd():
    count = 0
    unit = None
    channel = None
    passwd = ""
    lot = None
    user = ""
    ip = ""
    data_path = None
    tray = None
    def run(self, _command):
        mc = ["mysql", "--local-infile", "-h" + self.ip, "-u" + self.user, "-p" + self.passwd, "-e"]
        mc.extend(_command)
#        print mc
        return run_cmd(mc)

def data_upload_helper(_mc):
#    if not _mc.count or not _mc.unit or not _mc.channel or not _mc.passwd or not _mc.user or not _mc.ip or not _mc.data_path:
#        print_help()
#        sys.exit(2)
    for i in range(0,_mc.count):
        _mc.run(["load data local infile \"" + _mc.data_path + "/" + str(i).zfill(4) + ".dat\" into table hf_mes_curve_data.hf_curve_data character set utf8 FIELDS TERMINATED BY \",\" (create_time,cycle,step,station,tm,voltage,current,capacity,energy,temperature,stop_flag,stop_msg) SET unit=" + str(_mc.unit) + ",channel=" + str(_mc.channel) + ", battery=" + str(i) + ", lot=\"" + _mc.lot + "\", tray=\"" + _mc.tray + "\";"])
#    _mc.run(["call hf_mes_curve_data.proc_analyze_battery_keyvalue(\""  + _mc.lot + "\",\"" + _mc.tray + "\");"])

def data_upload(count,lot,user,ip,data_path,tray,unit,channel,passwd):
    _mc = mysql_cmd()
    _mc.count = count
    _mc.lot = lot
    _mc.user = user
    _mc.ip = ip
    _mc.data_path = data_path
    _mc.tray = tray
    _mc.unit = unit
    _mc.channel = channel
    _mc.passwd = passwd
    data_upload_helper(_mc)

def data_upload_main(argv):
    try:
        opts, args = getopt.getopt(argv,"hu:c:p:",["count=","lot=","user=","ip=","data-path=","tray="])
    except getopt.GetoptError:
        print_help() 
        sys.exit(2)
    _mc = mysql_cmd()
    for opt, arg in opts:
        if opt == '-h':
            print_help()
            sys.exit()
        elif opt == '--count':
            _mc.count = int(arg)
        elif opt == '--lot':
            _mc.lot = arg
        elif opt == '--user':
            _mc.user = arg
        elif opt == '--ip':
            _mc.ip = arg
        elif opt == '--data-path':
            _mc.data_path = arg
        elif opt == '--tray':
            _mc.tray = arg
        elif opt == '-u':
            _mc.unit = int(arg)
        elif opt == '-c':
            _mc.channel = int(arg)
        elif opt == '-p':
            _mc.passwd = arg
#        elif opt in ("-i", "--ifile"):
#            inputfile = arg
#        elif opt in ("-o", "--ofile"):
#            outputfile = arg
    #run_cmd(["sleep","5"])
    #run_cmd(["ls","-l"])
    data_upload_helper(_mc)

def test():
    data_upload(256,"lot0001","root","192.168.0.144","data","tray00001",0,0,"hf123!@#")
if __name__ == "__main__":
    test()
    #data_upload_main(sys.argv[1:])
