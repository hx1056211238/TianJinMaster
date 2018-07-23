# -*- coding: utf-8 -*  

import json
import platform
G_DEVICE_TEMPERATURE_POINT = 1
G_BATTERY_COUNT = 5
G_SEND_DATA_BIT = 32
G_RECV_DATA_BIT = 32

def init(batteryCount, sendDataBit, recvDataBit):
    global G_BATTERY_COUNT, G_SEND_DATA_BIT, G_RECV_DATA_BIT
    
    G_BATTERY_COUNT = batteryCount
    G_SEND_DATA_BIT = sendDataBit
    G_RECV_DATA_BIT = recvDataBit
    pass
    
    
    
""" ==============================
计算--命令数据的CRC校验码
参数：
        lt 输入的命令全部内容
"""
def getModCRC(lt):
    byte_crc = 0
    for i in range(0, len(lt)):
        byte_crc = byte_crc + lt[i]
    byte_crc = byte_crc % 256
    return byte_crc


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



""" ==============================
计算--数值的16进制LIST，以高-低位排列
参数：
        value 数值
返回：
        16进制LIST高-低位排列
"""
def getHEX_HI_LO(value):
    if value < 0:
        value = 65536 + value
    value_HI = value/256
    value_LO = value % 256
    value_HEX = [value_HI,value_LO]
    return value_HEX


""" ==============================
计算--数值的16进制LIST，以低-高位排列
参数：
        value 数值
返回：
        16进制LIST低-高位排列
"""
def getHEX_LO_HI16(value):
    if value < 0:
        value = 65536 + value
    value_HI = value/256
    value_LO = value % 256
    value_HEX = [value_LO,value_HI]
    return value_HEX

def getHEX_LO_HI24(value):
    if value < 0:
        value = 16777216 + value
    value_HI = value/65536
    value_MODH = value % 65536
    value_MI = value_MODH/256
    value_LO = value_MODH % 256
    value_HEX = [value_LO,value_MI,value_HI]
    return value_HEX


def getHEX_LO_HI32(value):
    if value < 0:
        value = 4294967296 + value
    value_T = int(value/16777216)
    value_MODT = value % 16777216
    value_HI = int(value_MODT/65536)
    value_MODH = value_MODT % 65536
    value_MI = int(value_MODH/256)
    value_LO = int(value_MODH % 256)
    value_HEX = [value_LO,value_MI,value_HI,value_T]
    return value_HEX

""" ==============================
计算--10进制转16进制
参数：
        n 数值
返回：
        16进制字符串
"""
def hexDWORD(dec):
    return "0x%s"%("00000000%s"%(hex(dec&0xffffffff)[2:-1]))[-8:]

def hexBYTE(dec):
    return ("%x"%(dec&0xff)).zfill(2)


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

def signedFromHex24(s): 
    v = int(s, 16)
    if not 0 <= v < 16777216: 
        raise ValueError, "hex number outside 24 bit range" 
    if v >= 8388608: 
        v = v - 16777216 
    return v

def signedFromHex32(s): 
    v = int(s, 16)
    if not 0 <= v < 4294967296: 
        raise ValueError, "hex number outside 32 bit range" 
    if v >= 2147483648:
        v = v - 4294967296 
    return v


""" ==============================
命令--获取模块采样数据
获得采样模块的数据命令 06
参数：
        idx_module 模块id 0-N
返回：
        命令的 byte buffer
"""
def cmd_GetBatteryInformation(idx_module):
    cmd_num  = 0X06
    data_length = 0X00
    cmd_list = [idx_module,0XAB,0XCD,cmd_num,data_length]
    data_length = len(cmd_list) - 5
    cmd_list[4] = data_length        
    cmd_CRC  = getModCRC(cmd_list)
    #计算CRC后，在list最后添加
    cmd_list.append(cmd_CRC)
    #print "rs485.cmd: " + str(cmd_list)
    #print cmd_list
    return cmd_list
    #return list2string_HEX(cmd_list).decode("hex") 
    #+ "$" + str(cmd_num)

#国安是两个通道
#天劲是5个通道

""" ==============================
命令--模块设定工作状态命令
获得采样模块的数据命令 01
参数：
        idx_module 模块id 0-N
        station    工作状态（1个字节） 0－复位 1－恒流充电 2－恒压充电 4－放电 （BYTE）
        vu         恒压值（WORD）
        vi         恒流值（WORD）
返回：
        命令的 byte buffer
"""
def cmd_SetStation(idx_module, station, vu, vi, supply_charge, chk_time, chk_tap, chk_over_vu, chk_over_vi, work_point = 0XFFFF):
    cmd_num  = 0X01
    data_length = 0X00
    cmd_list = [idx_module,0XAB,0XCD,cmd_num,data_length,station]
    reserve = [0x00,0x00]
    if G_SEND_DATA_BIT==16: 
        cmd_list.extend(getHEX_LO_HI16(vu))
        cmd_list.extend(getHEX_LO_HI16(vi))
    if G_SEND_DATA_BIT==24:
        cmd_list.extend(getHEX_LO_HI24(vu))
        cmd_list.extend(getHEX_LO_HI24(vi))        
    if G_SEND_DATA_BIT==32:
        cmd_list.extend(getHEX_LO_HI32(vu))
        cmd_list.extend(getHEX_LO_HI32(vi))                
    cmd_list.extend([supply_charge, chk_time, chk_tap])
    cmd_list.extend(getHEX_LO_HI32(chk_over_vu))
    cmd_list.extend(reserve)
    #cmd_list.extend(getHEX_LO_HI32(chk_over_vu*5000))
    #cmd_list.extend(getHEX_LO_HI32(chk_over_vi))
    #cmd_list.extend([0XFF,0XFF])
    data_length = len(cmd_list) - 5
    cmd_list[4] = data_length
    cmd_CRC  = getModCRC(cmd_list)
    #计算CRC后，在list最后添加
    cmd_list.append(cmd_CRC)
    #print "cmd_list",cmd_list
    #print list2string_HEX(cmd_list)
    #print "rs485.cmd: " + str(cmd_list)
    #print cmd_list
    return cmd_list
    #+ "$" + str(cmd_num)
# guoan: 命令 长度（长度到校验码之前的长度） 工步（1） 恒流电压（4个字节） 电流（4） 补电开关（1） 异常次数（1，如果超过这个值判定为接触异常） 
#        接触次数（1，每测试4个通道的电压电流值时，检测一次接触） 允许最大电压差值（4）
#
#天劲：  命令  长度   工步  恒压值（4）  恒流值（4）  补电开关（1）  段子检查次数（1）   段子检查间隔（1）  段子电压差值（4） 预留（2）   


""" ==============================
命令--写模块电池寄存命令
获得采样模块的数据命令 04
参数：
        idx_module 模块id 0-N
        status     寄存状态 0为不寄存 1为寄存
返回：
        命令的 byte buffer
"""
def cmd_Setstop_flag(idx_module, status):
    global G_BATTERY_COUNT
    cmd_num  = 0X04
    data_length = 0X00
    cmd_list = [idx_module,0XAB,0XCD,cmd_num,data_length]
    battery_list = [status] * G_BATTERY_COUNT
    cmd_list.extend(battery_list)
    #print "status: " + str(status)
    #battery_list = status
    #cmd_list.extend([status])
    data_length = len(cmd_list) - 5
    cmd_list[4] = data_length
    cmd_CRC  = getModCRC(cmd_list)
    #计算CRC后，在list最后添加
    cmd_list.append(cmd_CRC)
    #print "rs485.cmd: " + str(cmd_list)
    #print cmd_list
    return cmd_list
    #return list2string_HEX(cmd_list).decode("hex") 
    #+ "$" + str(cmd_num)



""" ==============================
命令--写模块电池寄存命令-
          针对外部对每个电池寄存状态定义
获得采样模块的数据命令 04
参数：
        idx_module   模块id 0-N
        battery_list 电池寄存状态标志的list
                     寄存状态 0为不寄存 1为寄存
                                 [0,0,0,0,1,1,1,0,0,0...]
返回：
        命令的 byte buffer
"""
def cmd_Setstop_flagByList(idx_module, battery_list):
    cmd_num  = 0X04
    data_length = 0X00
    cmd_list = [idx_module,0XAB,0XCD,cmd_num,data_length]
    cmd_list.extend(battery_list)
    data_length = len(cmd_list) - 5
    cmd_list[4] = data_length
    cmd_CRC  = getModCRC(cmd_list)
    #计算CRC后，在list最后添加
    cmd_list.append(cmd_CRC)
    #print "rs485.cmd: " + str(cmd_list)
    #print cmd_list
    return cmd_list
    #return list2string_HEX(cmd_list).decode("hex") 
    #+ "$" + str(cmd_num)


""" ==============================
命令--设置IC工作电源状态
设置IC工作电源状态 8
参数：
        idx_module 模块id 0-N
返回：
        无
"""
def cmd_SetICPower(idx_module, status = 1):
    cmd_num  = 0X8
    data_length = 0
    cmd_list = [idx_module,0xAB,0xCD,cmd_num,data_length]
    cmd_list.extend(status)
    data_length = len(cmd_list) -5 
    cmd_list[4] = data_length
    cmd_CRC = getModCRC(cmd_list)
    cmd_list.append(cmd_CRC)
    print cmd_list
    return cmd_list
    #return list2string_HEX(cmd_list).decode("hex") 
    #+ "$" + str(cmd_num)

    """ ==============================
命令--写模块电池接触检查命令
获得采样模块的数据命令 22
参数：
        idx_module 模块id 0-N
返回：
        命令的 byte buffer
"""
def cmd_Setcontact_check(idx_module):
    cmd_num  = 0X22
    data_length = 18
    
    cmd_list = [idx_module,0xAB,0xCD,cmd_num,data_length]
    reset_station_list = [0X00,0X02]
    cmd_list.extend(reset_station_list)
    cmd_list.extend(getHEX_LO_HI32(42000))
    cmd_list.extend(getHEX_LO_HI32(1000))
    cmd_list.extend(getHEX_LO_HI32(10000))
    cmd_list.extend(getHEX_LO_HI16(3000))
    cmd_list.extend(getHEX_LO_HI16(10000))
    cmd_CRC = getModCRC(cmd_list)
    cmd_list.append(cmd_CRC)
    print cmd_list
    return cmd_list
    
""" ==============================
命令--接触检查
设置IC工作电源状态 8
参数：
        idx_module 模块id 0-N
返回：
        无
"""

    
def cmd_Getcontact_check(idx_module):
    cmd_num  = 0X24
    data_length = 0
    cmd_list = [idx_module,0xAB,0xCD,cmd_num,data_length]
   
    cmd_CRC = getModCRC(cmd_list)
    cmd_list.append(cmd_CRC)
    print cmd_list
    return cmd_list
    #return list2string_HEX(cmd_list).decode("hex") 
    #+ "$" + str(cmd_num)
    


""" ==============================
动作--获取电池数据后转换为json格式-
参数：
        _buffer   回收的buffer的bytearray
返回：
        电池的json格式
"""
def do_batteryBuffer2Json(idx_module, _buffer, _battery_data, G_STEP_WORKTIME, G_PROCESS, G_PROCESS_IDX, G_DEVICE_TEMPERATURE = None):
    global G_BATTERY_COUNT
    cols = G_BATTERY_COUNT
    rows = 3
    battery_list = [[0 for col in range(cols)] for row in range(rows)]
    # battery_list[0] 代表电压共 16个数值
    # battery_list[1] 代表电流共 16个数值
    try:
        #如果有数据，就解释数据
        pos = 4
        if G_RECV_DATA_BIT==24:
            for i in range(0, len(battery_list[0])):
                data_hex = hexBYTE(_buffer[pos+2]) + hexBYTE(_buffer[pos+1]) + hexBYTE(_buffer[pos])
                battery_list[0][i] = signedFromHex24(data_hex)
                pos = pos + 3
            for i in range(0, len(battery_list[1])):
                data_hex = hexBYTE(_buffer[pos+2]) + hexBYTE(_buffer[pos+1]) + hexBYTE(_buffer[pos])
                battery_list[1][i] = signedFromHex24(data_hex)
                pos = pos + 3


        if G_RECV_DATA_BIT==32:
            for i in range(0, len(battery_list[0])):
                data_hex = hexBYTE(_buffer[pos+3]) + hexBYTE(_buffer[pos+2]) + hexBYTE(_buffer[pos+1]) + hexBYTE(_buffer[pos])
                battery_list[0][i] = signedFromHex32(data_hex)
                pos = pos + 4 

            for i in range(0, len(battery_list[1])):
                data_hex = hexBYTE(_buffer[pos+3]) + hexBYTE(_buffer[pos+2]) + hexBYTE(_buffer[pos+1]) + hexBYTE(_buffer[pos])
                battery_list[1][i] = signedFromHex32(data_hex)
                pos = pos + 4


        #温度点1 两个字节
        data_hex = hexBYTE(_buffer[pos+1]) + hexBYTE(_buffer[pos])
        temp1 = round(float(signedFromHex16(data_hex)) / 10, 1)
        pos = pos + 2
        
        
        #温度点2 两个字节
        data_hex = hexBYTE(_buffer[pos+1]) + hexBYTE(_buffer[pos])
        temp2 = round(float(signedFromHex16(data_hex)) / 10, 1)
        pos = pos + 2 
        

    
        #电流线端子异常（2个字节）  工作时巡检电流线接触检查 1 – 端子接触异常  0 – 端子接触正常
        bd = bin(_buffer[pos+1])[2::].zfill(8) + bin(_buffer[pos])[2::].zfill(8)
        arr = [0]*len(bd)
        i=len(bd)-1
        for c in bd:
            arr[i] = int(c)
            i=i-1
        # arr则是电池的端子异常信息
        pos = pos + 2
        
        for i in range(0, G_BATTERY_COUNT):
            _battery_data[idx_module * G_BATTERY_COUNT + i]['terminal_exp'] = arr[i]
            
        #print temp1 , " ===== " , temp2
        #print "idx_module",idx_module
        G_DEVICE_TEMPERATURE[idx_module * G_DEVICE_TEMPERATURE_POINT + 0] = temp1
        #G_DEVICE_TEMPERATURE[idx_module * G_DEVICE_TEMPERATURE_POINT + 1] = temp2
        #print buffer[pos::]
        for i in range(0, len(battery_list[2])):
            battery_list[2][i] = _buffer[pos]
            pos = pos + 1
                
                
                
        #数据写入到json结构里
        t = round(G_STEP_WORKTIME/60, 1)
        on_process = False
        if G_PROCESS is not None and G_PROCESS_IDX>-1 and G_PROCESS['process'][G_PROCESS_IDX]['station'] in [1,2,4]:
            for i in range(0, G_BATTERY_COUNT):
                _battery_data[idx_module * G_BATTERY_COUNT + i]['voltage'] = battery_list[0][i]/10.0;
                _battery_data[idx_module * G_BATTERY_COUNT + i]['current'] = battery_list[1][i]/10.0;
                #如果已经启动工作，并且为充放电工步，计算容量/能量
                _battery_data[idx_module * G_BATTERY_COUNT + i]['capacity'] = _battery_data[idx_module * G_BATTERY_COUNT + i]['capacity'] + round(abs(battery_list[1][i]/10.0)/60 * (t - _battery_data[idx_module * G_BATTERY_COUNT + i]['time']),6)
                _battery_data[idx_module * G_BATTERY_COUNT + i]['energy'] = _battery_data[idx_module * G_BATTERY_COUNT + i]['energy'] + round(abs(battery_list[1][i]/10.0)/60 * (t - _battery_data[idx_module * G_BATTERY_COUNT + i]['time']) * _battery_data[idx_module * G_BATTERY_COUNT + i ]['voltage'], 1)/1000.0
                #_battery_data[idx_module * G_BATTERY_COUNT + i]['energy'] =   round(_battery_data[idx_module * G_BATTERY_COUNT + i]['capacity']/1000 * _battery_data[idx_module * G_BATTERY_COUNT + i]['voltage'],1)
                _battery_data[idx_module * G_BATTERY_COUNT + i]['time'] = t
        else:
            for i in range(0, G_BATTERY_COUNT):
                _battery_data[idx_module * G_BATTERY_COUNT + i]['voltage'] = battery_list[0][i]/10.0;
                _battery_data[idx_module * G_BATTERY_COUNT + i]['current'] = battery_list[1][i]/10.0;
                _battery_data[idx_module * G_BATTERY_COUNT + i]['time'] = t

    except Exception,e:  
        #savefile("/data/log.txt", str(e))
        print "rs485: " + str(e)

    if 'Windows' in platform.system():
        #print json.dumps(_battery_data, ensure_ascii=False).decode('utf-8').encode('gb2312')
        pass

    if "Linux" in platform.system():
        #print json.dumps(_battery_data, ensure_ascii=False)
        pass

""" ==============================
动作--电池接触数据数据后转换为json格式-
参数：
        buffer   回收的buffer的bytearray
返回：
        电池的json格式
"""
def do_contactCheckBuffer2Json(idx_module, rebuffer, _battery_data_contact_check):
    global G_BATTERY_COUNT
    cols = G_BATTERY_COUNT
    rows = 8
    battery_list = [[0 for col in range(cols)] for row in range(rows)]
    #if idx_module == 0:
    #   print "===============" + str(idx_module) + "======================="
    #    print rebuffer
    #   print "=============== END ======================="
    #print "battery_list",battery_list

    #print "rebuffer"
    #print  list2string_HEX(rebuffer)
    data = list2string_HEX(rebuffer)
    print "data:",data
    #print list2string_HEX(rebuffer)[4]
    finish = rebuffer[4]
    #print "finish",finish
    #finish = hexBYTE(rebuffer[4])
    #print "finish",finish
    #print type(finish)

    for i in range(0, G_BATTERY_COUNT):
        for j in range(0,8):
            battery_list[j][i] = (rebuffer[5+i]>>j )  &  1
        '''
        bv = bin(rebuffer[i+1])[2::].zfill(8)
        #电流线接触不良 1 否则0
        battery_list[0][i] = bv[7]
        #电流线+正极接触不良 1 否则0
        battery_list[1][i] = bv[6]
        #电流线-负极接触不良 1 否则0
        battery_list[2][i] = bv[5]
        #保留
        battery_list[3][i] = bv[4]
        #电压线接触不良 1 否则0
        battery_list[4][i] = bv[3]
        #电压线+正极接触不良 1 否则0
        battery_list[5][i] = bv[2]
        #电压线-负极接触不良 1 否则0
        battery_list[6][i] = bv[1]
        #有无电池标记 1为有电池
        battery_list[7][i] = bv[0]
        '''
    
    #print "battery_list",battery_list  

    for i in range(0, G_BATTERY_COUNT):
        _battery_data_contact_check[idx_module * G_BATTERY_COUNT + i]['chk_finish']   =  finish
        _battery_data_contact_check[idx_module * G_BATTERY_COUNT + i]['chk_current']   = battery_list[0][i];
        _battery_data_contact_check[idx_module * G_BATTERY_COUNT + i]['chk_current_+'] = battery_list[1][i];
        _battery_data_contact_check[idx_module * G_BATTERY_COUNT + i]['chk_current_-'] = battery_list[2][i];
        _battery_data_contact_check[idx_module * G_BATTERY_COUNT + i]['chk_voltage']   = battery_list[4][i];
        _battery_data_contact_check[idx_module * G_BATTERY_COUNT + i]['chk_voltage_+'] = battery_list[5][i];
        _battery_data_contact_check[idx_module * G_BATTERY_COUNT + i]['chk_voltage_-'] = battery_list[6][i];
        _battery_data_contact_check[idx_module * G_BATTERY_COUNT + i]['chk_battery'] =   battery_list[7][i];
                
        pass
 
 