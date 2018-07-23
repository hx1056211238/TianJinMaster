'''
@file		mcp2515.py
@author		Joe.Zhong <wenxing.cn@gmail.com>
@date		2017-12-02
@brief		This file implements the mcp2515 class
'''

import mcp2515_context as mcp2515_con
import spidev
import time

'''
@class		mcp2515
@brief		The abstraction of a mcp2515 device


@fn		readRegister
@brief		This function reads the content in a given register
@param[in]	param_dict
		The parameter in python dict format for this routine
@param[in]	param_dict['in']['address']
		A register address of mcp2515
@param[out]	param_dict['out']['value']
		The content in the given register if the result of invoking this routine is positive
@return		=None, fail; =0, success


@fn		readRegisterS
@brief		This function reads contents in a mcp2515's register region sucessively
@param[in]	param_dict
		The parameter in python dict format for this routine
@param[in]	param_dict['in']['start_address']
		The start address of a mcp2515 register region 
@param[in]	param_dict['in']['count']
		The number of bytes will be read from given register region
@param[out]	param_dict['out']['contents']
		The contents read from registers
@return		=None, fail; =0, success


@fn		setRegister
@brief		This function sets the content of a given mcp2515 register
@param[in]	param_dict
		The parameter in python dictionary format for this routine
@param[in]	param_dict['in']['address']
		A valid register address of mcp2515
@param[in]	param_dict['in']['value']
		The content to write to the given register
@return		=None, fail; =0, success


@fn		setRegisterS
@brief		This function sets mcp2515 registers with given values sucessively
@param[in]	param_dict
		The parameter in python dictionary format for this routine
@param[in]	param_dict['in']['start_address']
		The start address of a mcp2515 register region 
@param[in]	param_dict['in']['contents']
		The contents to write to registers respectively
@param[in]	param_dict['in']['count']
		The number of registers
@return		=None, fail; =0, success


@fn		modifyRegister
@brief		Allows the user to set or clear individual bits in a particular register
@param[in]	param_dict
		The parameter in python dictionary format
@param[in]	param_dict['in']['address']
		A valid register address of mcp2515
@param[in]	param_dict['in']['mask']
		Mask bits
@param[in]	param_dict['in']['value']
		Value of individual bits
@return		=None, fail; =0, success


@fn		readStatus
@brief		Read some of the often used status bits for message reception and transmission
@param[in]	param_dict
		The parameter in python dict format for this routine
@param[out]	param_dict['out']['status']	
		Some of the often used status bits
@return		=None, fail; =0, success	


@fn		reset
@brief		This function Resets mcp2515's internal registers to the default state
                and sets the Configuration mode
@return		=None, fail; =0, success


@fn		setMode
@brief		This function sets the operational mode of a mcp2515 device
		The operational mode can be 
                1. Configuration mode
                2. Normal mode
                3. Sleep mode
                4. Listen-Only mode
                5. Loopback mode
@param[in]	param_dict
		The parameter in python dictionary format
@param[in]	param['in']['mode']
		The operational mode
@return		=None, fail; =0, success


@fn		configRate
@brief		This function sets the CNF1, CNF2 and CNF3 registers of a mcp2515 device
@param[in]	param_dict
		The parameter in python dict format for this routine
@param[in]	param_dict['in']['clock']
		The frequency of the oscillator
@param[in]	param_dict['in']['speed']
		The speed of can bus
@return		=None, fail, =0, success


@fn		initCANBuffers
@brief		This function initializes buffers, masks, and filters
@return		=None, fail; =0, success

@fn		init
@brief		This function initializes a mcp2515 device
@param[in]	param_dict
		The parameter in python dict format for this routine
@param[in]	param_dict['in']['port']
		The spi port that connects with mcp2515
		prot = 0 ----- spidev0.0
		prot = 1 ----- spidev0.1
@return		=None, fail; =0, success


@fn		set_mf_id
@brief		This function sets the ID for a mask or a filter
@param[in]	param_dict
		The parameter in python dict format for this routine
@param[in]	param_dict['in']['id']
		a valid SID or EID
@param[in]	param_dict['in']['flag']
		=1, EID; =0, SID
@param[in]	param_dict['in']['address']
		A valid register address of a mask or a filter
@return		=None, fail; =0, success


@fn		set_tx_buf_id
@brief		This function sets a standard id or extended id for a tx buffer
@param[in]	param_dict
		The parameter in python dict format for this routine
@param[in]	param_dict['in']['address']
		The register address relating to TXBnSIDH of a tx buffer 
@param[in]	param_dict['in']['flag']
		=1, EID; =0, SID
@param[in]	param_dict['in']['id']
		a valid SID or EID
@return		=None, fail; =0, success


@fn		get_rx_buf_id
@brief		This function gets a standard id or extended id from a rx buffer
@param[in]	param_dict
		The parameter in python dict format for this routine
@param[in]	param_dict['in']['address']
		A valid register address relating to RXBnSIDH of a rx buffer 
@param[out]	param_dict['out']['flag']
		=1, EID; =0, SID
@param[out]	param_dict['out']['id']
		a valid SID or EID
@return		=None, fail; =0, success


@fn		getNextFreeTXBuf
@brief		get a free transmit buffer
@param[in]	param_dict
		The parameter in python dict format for this routine
@param[out]	param_dict['out']['address']
		The start address of a transmit buffer
                Each of transmit buffers occupies 14 bytes, the start address points to the control register(TXBnCTRL)
@return		=None, fail; =0, success


@fn		setMask_id
@brief		This function sets id for a mask
@param[in]	param_dict
		The parameter in python dict format for this routine
@param[in]	param_dict['in']['number']
		The number of a mask
@param[in]	param_dict['in']['flag']
		=1, EID; =0, SID
@param[in]	param_dict['in']['id']
		A valid SID or EID
@return		=None, fail; =0, success


@fn		setFilter_id
@brief		This function sets id for a filter
@param[in]	param_dict
		The parameter in python dict format for this routine
@param[in]	param_dict['in']['number']
		The number of a filter
@param[in]	param_dict['in']['flag']
		=1, EID; =0, SID
@param[in]	param_dict['in']['id']
		A valid SID or EID
@return		=None, fail; =0, success
		

@fn		sendCANMsg
@brief		This function sends a CAN message to CAN bus
@param[in]	param_dict
		The parameter in python dict format for this routine
@param[in]	param_dict['in']['id']
		a valid SID or EID
@param[in]	param_dict['in']['flag']
		=1, EID; =0, SID
@param[in]	param_dict['in']['rtr']
                Remote Transmission Request bit
                =1, Transmitted message will be a remote transmit request
                =0, Transmitted message will be a data frame
@param[in]	param_dict['in']['length']
		The length of the transmit message
@param[in]	param_dict['in']['message']
		The CAN message that will be sent to CAN bus
@return		=None, fail; =0, success


@fn		readCANMsg
@brief		This function reads a CAN message from receive buffer
@param[in]	param_dict
		The parameter in python dict format for this routine
@param[in]	param_dict['in']['id']
		A valid SID or EID
@param[in]	param_dict['in']['length']
		The length of the transmit message
@param[in]	param_dict['in']['time_interval']
                The time interval in seconds to read CAN message from CAN bus with respect to the given ID
@param[out]	param_dict['out']['message']
		The CAN message that reads from receive buffers with amount of data equal to length
@return		=None, fail; =0, success

@fn         readCANMsg_anyway
@brief		This function reads a CAN message from receive buffer with respect to length without checking CAN ID
@param[in]	param_dict
            The parameter in python dict format for this routine
@param[in]	param_dict['in']['length']
		    The length of the transmit message
@param[in]	param_dict['in']['time_interval']
		    The time interval in seconds to read CAN message from CAN bus
@param[out]	param_dict['out']['message']
		    The CAN message that reads from receive buffers with amount of data equal to length
@rerturn	=None, fail; =0, success


@fn         clear_interrupt_flag
@brief      This function clears all interrupt flag in status register
@return     =None, fail; =0, success


@fn		deinit
@brief		This function does the reverse operations to init		
	
'''

class mcp2515:
    port = None
    clock = None
    speed = None
    mode = None
    spi = None
    tx_data = None
    tx_dlc = None
    rx_data = None
    rx_dlc = None

    def debug(this):
        this.spi = spidev.SpiDev(0, 1)

    def readRegister(this, param_dict):
        ret = None
        key = None
        address = None
        value = None
        key_filters = None
        byte_streams = [] # [read_instruction, address, Don't Care]

        if  param_dict is None:
            print "readRegister, incorrect parameter"
            return None

        if  param_dict.get('in') is None or param_dict.get('out') is None:
            print 'readRegister, illegal parameter'
            return None

        key_filters = ['address']

        for key in key_filters:
            if  key in param_dict['in'].keys():
                if  key == 'address':
                    address = param_dict['in'][key]

        if  None in [address]:
            print "readRegister, illegal parameter"
            return None

        byte_streams = [mcp2515_con.MCP_READ, address, 0x00]

        #print "byte_streams = ", byte_streams

        ret = this.spi.xfer2(byte_streams)
        
        if  ret is None:
            print "readRegister->xfer2(spi) fail"
            return None
        if mcp2515_con.MCP_CANSTAT == address:
            print "address = ", address, "value = ", ret

        param_dict['out']['value'] = ret[2]
        
        return 0

    def readRegisterS(this, param_dict):
        ret = None
        key = None
        count = None
        contents = None
        key_filters = None
        byte_streams = [] # [read_instruction, address, Don't Care]
        start_address = None

        if  param_dict is None:
            print "readRegisterS, incorrect parameter"
            return None

        if  param_dict.get('in') is None or param_dict.get('out') is None:
            print 'readRegisterS, illegal parameter'
            return None

        key_filters = ['count', 'start_address']

        for key in key_filters:
            if  key in param_dict['in'].keys():
                if  key == 'start_address':
                    start_address = param_dict['in'][key]
                elif key == 'count':
                    count = param_dict['in'][key]

        if  None in [count, start_address]:
            print "readRegisterS, illegal parameter"
            return None

        byte_streams = [0]*(count+2)
        byte_streams[0] = mcp2515_con.MCP_READ
        byte_streams[1] = start_address

        ret = this.spi.xfer2(byte_streams)
        if  ret is None:
            print 'readRegisterS->spi.xfer2, fail'
            return None

        contents = [0]*count

        for i in range(0, count):
            contents[i] = ret[i+2]
        

        param_dict['out']['contents'] = contents

        return 0

    def setRegister(this, param_dict):
        ret = None
        key = None
        address = None
        value = None
        key_filters = None
        byte_streams = [] # [write_instruction, address, data]

        if  param_dict is None:
            print "setRegister, incorrect parameter"
            return None

        if  param_dict.get('in') is None:
            print 'setRegister, illegal parameter'
            return None

        key_filters = ['address', 'value']

        for key in key_filters:
            if  key in param_dict['in'].keys():
                if  key == 'address':
                    address = param_dict['in'][key]
                elif key == 'value':
                    value = param_dict['in'][key]

        if  None in [address, value]:
            print "setRegister, illegal parameter"
            return None

        byte_streams = [mcp2515_con.MCP_WRITE, address, value]

        #print "byte_streams = ", byte_streams
        
        ret = this.spi.xfer2(byte_streams)
        if  ret is None:
            print 'setRegister->spi.xfer2, fail'
            return None

        return 0

    def setRegisterS(this, param_dict):
        ret = None
        start_address = None
        contents = [None]
        count = None
        key = None
        key_filters = None
        byte_streams = [] # [write_instruction, address, value[0], value[1], ..., value[n-1]]

        if  param_dict is None:
            print "setRegisterS, incorrect parameter"
            return None

        if  param_dict.get('in') is None:
            print 'setRegisterS, illegal parameter'
            return None

        key_filters = ['start_address', 'contents', 'count']

        for key in key_filters:
            if  key in param_dict['in'].keys():
                if  key == 'start_address':
                    start_address = param_dict['in'][key]
                elif key == 'contents':
                    contents = param_dict['in'][key]
                elif key == 'count':
                    count = param_dict['in'][key]

        if  None in [start_address, contents, count]:
            print "setRegisterS, illegal parameter"
            return None

        byte_streams = [0] * (count + 2)
        byte_streams[0] = mcp2515_con.MCP_WRITE
        byte_streams[1] = start_address
        for i in range(0, count):
            byte_streams[i+2] = contents[i]
        
        #print "byte_streams = ", byte_streams

        ret = this.spi.xfer2(byte_streams)
        if  ret is None:
            print 'setRegisterS->spi.xfer2, fail'
            return None

        return 0

    def modifyRegister(this, param_dict):
        ret = None
        address = None
        mask = None
        value = None
        key = None
        key_filters = None
        byte_streams = [] # [modify_instruction, address, mask, data]

        if  param_dict is None:
            print "modifyRegister, incorrect parameter"    
            return None

        if  param_dict.get('in') is None:
            print "modifyRegister, illegal parameter"
            return None

        key_filters = ['address', 'mask', 'value']

        for key in key_filters:
            if  key in param_dict['in'].keys():      
                if  key == "address":                    
                    address = param_dict['in'][key]
                elif key == "mask":
                    mask = param_dict['in'][key]
                elif key == "value":
                    value = param_dict['in'][key]

        if  None in [address, mask, value]:
            print "modifyRegister, illegal parameter"
            return None

        byte_streams = [mcp2515_con.MCP_BITMOD, address, mask, value]
        
        #print "byte_streams = ", byte_streams

        ret = this.spi.xfer2(byte_streams)
        if  ret is None:
            print 'modifyRegister->spi.xfer2, fail'
            return None

        return 0

    def readStatus(this, param_dict):
        ret = None

        byte_streams = [] #[read_status_instruction, Don't Care]
        
        if  param_dict is None:
            print "init, incorrect parameter"
            return None

        if  param_dict.get('out') is None:
            print "readStatus, illegal parameter"
            return None

        byte_streams = [mcp2515_con.MCP_READ_STATUS, 0x00]

        #print 'byte_streams = ', byte_streams

        ret = this.spi.xfer2(byte_streams)
        if  ret is None:
            print "readStatus->xfer2(spi) fail"
            return None

        param_dict['out']['status'] = ret[1]

        return 0

        
        
    def clear_interrupt_flag(this):
        time.sleep(0.05)
        #print "readCANMsg_anyway completion = 0"
        #print "dict_message = ", dict_message
        dict_message = None
        #clear full interrupt flag bit
        mask = mcp2515_con.MCP_RX0IF_MASK
        value = mcp2515_con.MCP_RX0IF_MASK ^ mcp2515_con.MCP_RX0IF_MASK
        ret = this.spi.xfer2([mcp2515_con.MCP_BITMOD, mcp2515_con.MCP_CANINTF, mask, value])
        if  ret is None:
            print 'readCANMsg_anyway->spi.xfer2, fail'
            return None
                                         
        #clear full interrupt flag bit
        mask = mcp2515_con.MCP_RX1IF_MASK
        value = mcp2515_con.MCP_RX1IF_MASK ^ mcp2515_con.MCP_RX1IF_MASK
        ret = this.spi.xfer2([mcp2515_con.MCP_BITMOD, mcp2515_con.MCP_CANINTF, mask, value])
        if  ret is None:
            print 'readCANMsg_anyway->spi.xfer2, fail'
            return None                       
        return None
        
    def reset(this):
        ret = None
        byte_streams = [] # [reset_instruction]
        byte_streams = [mcp2515_con.MCP_RESET]
        #print "byte_streams = ", byte_streams

        
        ret = this.spi.xfer2(byte_streams)
        if  ret is None:
            print 'reset->xfer2(spi) fail'
            return None
        else:
            #wait for at least 1/8M * 118
            time.sleep(0.1)

        param = {}
        param = {'in':{"mode":mcp2515_con.MODE_CONFIG}}
        ret = this.setMode(param)
        if  ret is None:
            print "init -> setMode, fail"
            return None
          

        '''
        param = {}
        param = {'in':{"mode":0x08}}
        ret = this.setMode(param)
        
             
        
        #param_dict = [mcp2515_con.MCP_READ_STATUS] 
        value = 0x00
        param_dict = {'in':{'address':mcp2515_con.MCP_CANSTAT, "value":value}, 'out':{}}        
        ret = this.readRegister(param_dict)
        
        print "this.readRegister(param_dict):",ret
        '''
            
        return 0

        
    def setMode(this, param_dict):
        ret = None
        key = None
        mode = None
        mask = None
        value = None
        address = None
        key_filters = None
        param = None

        if  param_dict is None:
            print "setMode, incorrect parameter"
            return None

        if  param_dict.get('in') is None:
            print "setMode, illegal parameter"
            return None

        key_filters = ['mode']

        for key in key_filters:
            if  key in param_dict['in'].keys():
                if  key == "mode":
                    mode = param_dict['in'][key]

        if  None in [mode]:
            print "setMode, illegal parameter"
            return None

        value = mode
        mask = mcp2515_con.MODE_MASK
        address = mcp2515_con.MCP_CANCTRL

        param = {"in":{'address':address, 'value':mode, 'mask':mask}}
        ret = this.modifyRegister(param)
        if  ret is None:
            print "setMode, modifyRegister fail"
            return None

        this.mode = mode

        return 0

    def configRate(this, param_dict):
        key = None
        ret = None
        CNF1 = None
        CNF2 = None
        CNF3 = None
        clock = None
        speed = None
        param = None
        key_filters = None

        if  param_dict is None:
            print "configRate, incorrect parameter"
            return None

        if  param_dict.get('in') is None:
            print "configRate, illegal parameter"
            return None

        key_filters = ['clock', 'speed']

        for key in key_filters:
            if  key in param_dict['in'].keys():
                if  key == 'clock':
                    clock = param_dict['in'][key]
                elif key == "speed":
                    speed = param_dict['in'][key]

        if  None in [clock, speed]:
            print "configRate, illegal parameter"
            return None

        #print "clock = ", clock
        #print "speed = ", speed

        if  clock == mcp2515_con.MCP_8MHZ:
            if  speed == mcp2515_con.CAN_100KBPS:
                #print "CAN_100KBPS"
                CNF1 = mcp2515_con.MCP_8MHz_100kBPS_CFG1
                CNF2 = mcp2515_con.MCP_8MHz_100kBPS_CFG2
                CNF3 = mcp2515_con.MCP_8MHz_100kBPS_CFG3
            elif speed == mcp2515_con.CAN_125KBPS:
                #print "CAN_125KBPS"
                CNF1 = mcp2515_con.MCP_8MHz_125kBPS_CFG1
                CNF2 = mcp2515_con.MCP_8MHz_125kBPS_CFG2
                CNF3 = mcp2515_con.MCP_8MHz_125kBPS_CFG3
            elif speed == mcp2515_con.CAN_250KBPS:
                #print "CAN_250KBPS"
                CNF1 = mcp2515_con.MCP_8MHz_250KBPS_CFG1
                CNF2 = mcp2515_con.MCP_8MHz_250KBPS_CFG2
                CNF3 = mcp2515_con.MCP_8MHz_250KBPS_CFG3
                
            else:
                print "unknow speed for can bus"
                return None
        else:
            print "unknow clock for can bus"
            return None

        #print "CNF1 = ", hex(CNF1), "CNF2 = ", hex(CNF2), "CNF3 = ", hex(CNF3)

        param = {}
        param = {'in':{"address":mcp2515_con.MCP_CNF1, "value":CNF1}}
        ret = this.setRegister(param)
        if  ret is None:
            print "configRate -> setRegister(CNF1), fail"
            return None

        param = {}
        param = {'in':{"address":mcp2515_con.MCP_CNF2, "value":CNF2}}
        ret = this.setRegister(param)
        if  ret is None:
            print "configRate -> setRegister(CNF2), fail"
            return None

        param = {}
        param = {'in':{"address":mcp2515_con.MCP_CNF3, "value":CNF3}}
        ret = this.setRegister(param)
        if  ret is None:
            print "configRate -> setRegister(CNF3), fail"
            return None

        return 0

    def deinit(this):
        if  this.spi is not None:
            this.spi.close()
   
    def init(this, param_dict):
        ret = None
        key = None
        port = None
        mask = None
        clock = None
        speed = None
        param = None
        value = None
        address = None
        key_filters = None
        
        if  param_dict is None:
            print "init, incorrect parameter"
            return None

        if  param_dict.get('in') is None:
            print "init, illegal parameter"
            return None

        key_filters = ['port', 'clock', 'speed']

        for key in key_filters:
            if  key in param_dict['in'].keys():
                if  key == 'port':
                    port = param_dict['in'][key]
                elif key == 'clock':
                    clock = param_dict['in'][key]
                elif key == 'speed':
                    speed = param_dict['in'][key]

        if  None in [port, clock, speed]:
            print "init, illegal parameter"
            return None

        #print "port = ", port
        #print "clock = ", clock
        #print "speed = ", speed

        if  this.spi is None:
            this.spi = spidev.SpiDev()
            print "spiddev.SpiDev()"
            #this.spi.close()
            this.spi.open(0,port)
            
        if  this.spi is None:
            print "init, cannot get a spi controller"
            return None


        
        #time.sleep(0.1)    
        this.reset()
        time.sleep(0.02)
        
        
        param = {}
        param = {'in':{"mode":mcp2515_con.MODE_CONFIG}}
        ret = this.setMode(param)
        if  ret is None:
            print "init -> setMode, fail"
            return None

        
        
        param = {}
        param = {'in':{"clock":clock, "speed":speed}}
        ret = this.configRate(param)
        if  ret is None:
            print "init -> configRate, fail"
            return None

        #initialize buffers, masks, and filters
        ret = this.initCANBuffers()
        if  ret is None:
            print "init -> initCANBuffers, fail"
            return None

        #enable interrupt (RX0IE and RX1IE)
        address = mcp2515_con.MCP_CANINTE
        value = mcp2515_con.MCP_RX0IF | mcp2515_con.MCP_RX1IF
        param = {}
        param = {'in':{"address":address, "value":value}}
        ret = this.setRegister(param)
        if  ret is None:
            print "init -> setRegister, fail"
            return None

        #set RX0BF and RX1BF as Digital Output Mode
        address = mcp2515_con.MCP_BFPCTRL
        value = mcp2515_con.MCP_BxBFS_MASK | mcp2515_con.MCP_BxBFE_MASK
        param = {}
        param = {'in':{'address':address, 'value':value}}
        ret = this.setRegister(param)
        if  ret is None:
            print "init->setRegister, fail"
            return None
        
        #set TXnRTS as Digital Input
        address = mcp2515_con.MCP_TXRTSCTRL
        value = 0x00
        param = {}
        param = {'in':{"address":address, "value":value}}
        ret = this.setRegister(param)
        if  ret is None:
            print "init->setRegister, fail"
            return None

        #set receive behaviors
        address = mcp2515_con.MCP_RXB0CTRL
        mask = mcp2515_con.MCP_RXB_RX_MASK | mcp2515_con.MCP_RXB_BUKT_MASK
        value = mcp2515_con.MCP_RXB_RX_STDEXT | mcp2515_con.MCP_RXB_BUKT_MASK
        param = {}
        param = {'in':{"address":address, "value":value, "mask":mask}}
        ret = this.modifyRegister(param)
        if  ret is None:
            print "init->modifyRegister, fail"
            return None
            
        address = mcp2515_con.MCP_RXB1CTRL
        mask = mcp2515_con.MCP_RXB_RX_MASK
        value = mcp2515_con.MCP_RXB_RX_STDEXT #No Remote Transfer Request received
        param = {}
        param = {'in':{"address":address, "value":value, "mask":mask}}
        this.modifyRegister(param)
        if  ret is None:
            print "init->modifyRegister, fail"
            return None

            
        param = {}
        param = {'in':{"mode":0x08}}
        ret = this.setMode(param)
        
            
        this.port = port
        this.clock = clock
        this.speed = speed


            
            
        return 0
            
    def setFilter_id(this, param_dict):
        id = None
        ret = None
        key = None
        mode = None
        flag = None
        mask = None
        param = None
        value = None
        number = None
        address = None
        key_filters = None

        if  param_dict is None:
            print "setFilter_id, incorrect parameter"
            return None

        if  param_dict.get('in') is None:
            print "setFilter_id, illegal parameter"
            return None

        key_filters = ['number', 'flag', 'id']

        for key in key_filters:
            if  key in param_dict['in'].keys():
                if  key == "number":
                    number = param_dict['in'][key]
                elif key == 'flag':
                    flag = param_dict['in'][key]
                elif key == 'id':
                    id = param_dict['in'][key]

        if  None in [number, flag, id]:
            print "setFilter_id, illegal parameter"
            return None

        value = mcp2515_con.MODE_CONFIG
        mask = mcp2515_con.MODE_MASK
        address = mcp2515_con.MCP_CANCTRL

        param = {"in":{'address':address, 'value':value, 'mask':mask}}
        ret = this.modifyRegister(param)
        if  ret is None:
            print "setFilter_id, modifyRegister fail"
            return None        

        if  number == 0:
            param = {}
            param = {'in':{"address":mcp2515_con.MCP_RXF0SIDH, "flag":flag, "id":id}}
            ret = this.set_mf_id(param)
            if  ret is None:
                print "setFilter_id -> set_mf_id(RXF0SIDH), fail"
                return None
        elif number == 1:
            param = {}
            param = {'in':{"address":mcp2515_con.MCP_RXF1SIDH, "flag":flag, "id":id}}
            ret = this.set_mf_id(param)
            if  ret is None:
                print "setFilter_id -> set_mf_id(RXF1SIDH), fail"
                return None
        elif number == 2:
            param = {}
            param = {'in':{"address":mcp2515_con.MCP_RXF2SIDH, "flag":flag, "id":id}}
            ret = this.set_mf_id(param)
            if  ret is None:
                print "setFilter_id -> set_mf_id(RXF2SIDH), fail"
                return None
        elif number == 3:
            param = {}
            param = {'in':{"address":mcp2515_con.MCP_RXF3SIDH, "flag":flag, "id":id}}
            ret = this.set_mf_id(param)
            if  ret is None:
                print "setFilter_id -> set_mf_id(RXF3SIDH), fail"
                return None
        elif number == 4:
            param = {}
            param = {'in':{"address":mcp2515_con.MCP_RXF4SIDH, "flag":flag, "id":id}}
            ret = this.set_mf_id(param)
            if  ret is None:
                print "setFilter_id -> set_mf_id(RXF4SIDH), fail"
                return None
        elif number == 5:
            param = {}
            param = {'in':{"address":mcp2515_con.MCP_RXF5SIDH, "flag":flag, "id":id}}
            ret = this.set_mf_id(param)
            if  ret is None:
                print "setFilter_id -> set_mf_id(RXF5SIDH), fail"
                return None
        else:
            print "setFilter_id, illegal parameter"
            return None

        if  this.mode is not None:
            if  this.mode != mcp2515_con.MODE_CONFIG:
                param = {}
                param = {'in':{'mode':this.mode}}
                ret = this.setMode(param)
                if  ret is None:
                    print "setFilter_id -> setMode, fail"
                    return None

        return 0

    def setMask_id(this, param_dict):
        print "mcp2515->setMask_id"
        id = None
        ret = None
        key = None
        mode = None
        flag = None
        mask = None
        value = None
        param = None
        number = None
        address = None
        key_filters = None

        if  param_dict is None:
            print "setMask_id, incorrect parameter"
            return None

        if  param_dict.get('in') is None:
            print "setMask_id, illegal parameter"
            return None

        key_filters = ['number', 'flag', 'id']

        for key in key_filters:
            if  key in param_dict['in'].keys():
                if  key == "number":
                    number = param_dict['in'][key]
                elif key == 'flag':
                    flag = param_dict['in'][key]
                elif key == 'id':
                    id = param_dict['in'][key]

        if  None in [number, flag, id]:
            print "setMask_id, illegal parameter"
            return None

        value = mcp2515_con.MODE_CONFIG
        mask = mcp2515_con.MODE_MASK
        address = mcp2515_con.MCP_CANCTRL

        param = {"in":{'address':address, 'value':value, 'mask':mask}}
        ret = this.modifyRegister(param)
        if  ret is None:
            print "setMask_id, modifyRegister fail"
            return None

        if  number == 0:
            param = {}
            param = {'in':{"address":mcp2515_con.MCP_RXM0SIDH, "flag":flag, "id":id}}
            ret = this.set_mf_id(param)
            if  ret is None:
                print "setMask_id -> set_mf_id(RXM0SIDH), fail"
                return None
        elif number == 1:
            param = {}
            param = {'in':{"address":mcp2515_con.MCP_RXM1SIDH, "flag":flag, "id":id}}
            ret = this.set_mf_id(param)
            if  ret is None:
                print "setMask_id -> set_mf_id(RXM1SIDH), fail"
                return None
        else:
            print "setMask_id->setMode, illegal parameter"
            return None

        if  this.mode is not None:
            if  this.mode != mcp2515_con.MODE_CONFIG:
                param = {}
                param = {'in':{'mode':this.mode}}
                ret = this.setMode(param)
                if  ret is None:
                    print "setMask_id -> setMode, fail"
                    return None

        return 0

    def set_mf_id(this, param_dict):
        id = None
        ret = None
        key = None
        flag = None
        param = None
        can_id = None
        base_id = None
        contents = None
        extended_id = None
        address = None
        key_filters = None

        if  param_dict is None:
            print "set_mf_id, incorrect parameter"
            return None

        if  param_dict.get('in') is None:
            print "set_mf_id, illegal parameter"
            return None

        key_filters = ['id', 'flag', 'address']

        for key in key_filters:
            if  key in param_dict['in'].keys():
                if  key == "id":
                    id = param_dict['in'][key]
                elif key == 'flag':
                    flag = param_dict['in'][key]
                elif key == 'address':
                    address = param_dict['in'][key]

        if  None in [id, flag, address]:
            print "set_mf_id, illegal parameter"
            return None

        contents = [0] * 4
        can_id = int(id & 0xFFFFFFFF)
        extended_id =  int(can_id & 0x3FFFF)
        base_id = int((can_id >> 18) & 0x7FF)

        #print 'id = ', hex(can_id), 'flag = ', flag, 'address = ', hex(address)
        #print 'base_id = ', hex(base_id), 'extended_id = ', hex(extended_id)

        if  flag == 1:
            contents[3] = extended_id & 0xFF #set (EID0 - EID7)
            contents[2] = (extended_id >> 8) & 0xFF  #set (EID8 - EID15)
            contents[1] =  (extended_id >> 16)&0x03 #set (EID17 - EID16)
            contents[1] = contents[1] | ((base_id & 0x07)<<5) #set (SID0 - SID2)
            contents[1] = contents[1] | mcp2515_con.MCP_TXB_EXIDE_M #set ext id flag if it is a filter
            contents[0] = (base_id >> 3) & 0xFF  #set (SID3 - SID10)
        elif flag == 0:
            contents[0] = (base_id >> 3) & 0xFF  #set (SID3 - SID10)
            contents[1] = contents[1] | ((base_id & 0x07)<<5) #set (SID0 - SID2)
            contents[2] = int(0) #set (EID8 - EID15) = 0
            contents[3] = int(0) #set (EID0 - EID7) = 0
            
        #print 'contents = ', contents

        param = {}
        param = {'in':{"start_address":address, "contents":contents, "count":len(contents)}}
        ret = this.setRegisterS(param)
        if  ret is None:
            print "set_mf_id -> setRegisterS, fail"
            return None

        return 0
            
    def set_tx_buf_id(this, param_dict):
        id = None
        ret = None
        key = None
        flag = None
        param = None
        contents = None
        can_id = None
        base_id = None
        address = None
        key_filters = None
        extended_id = None

        if  param_dict is None:
            print "set_tx_buf_id, incorrect parameter"
            return None

        if  param_dict.get('in') is None:
            print "set_tx_buf_id, illegal parameter"
            return None

        key_filters = ['id', 'flag', 'address']

        for key in key_filters:
            if  key in param_dict['in'].keys():
                if  key == "id":
                    id = param_dict['in'][key]
                elif key == 'flag':
                    flag = param_dict['in'][key]
                elif key == 'address':
                    address = param_dict['in'][key]

        if  None in [id, flag, address]:
            print "set_tx_buf_id, illegal parameter"
            return None

        contents = [0] * 4
        can_id = int(id & 0xFFFFFFFF)
        extended_id =  int(can_id & 0x3FFFF)
        base_id = int((can_id >> 18) & 0x7FF)

        #print 'id = ', hex(can_id), 'flag = ', flag, 'address = ', hex(address)
        #print 'base_id = ', hex(base_id), 'extended_id = ', hex(extended_id)

        if  flag == 1:
            contents[3] = extended_id & 0xFF #set (EID0 - EID7)
            contents[2] = (extended_id >> 8) & 0xFF  #set (EID8 - EID15)
            contents[1] =  (extended_id >> 16)&0x03 #set (EID17 - EID16)
            contents[1] = contents[1] | ((base_id & 0x07)<<5) #set (SID0 - SID2)
            contents[1] = contents[1] | mcp2515_con.MCP_TXB_EXIDE_M #set ext id flag if it is a filter
            contents[0] = (base_id >> 3) & 0xFF  #set (SID3 - SID10)
        elif flag == 0:
            contents[0] = (base_id >> 3) & 0xFF  #set (SID3 - SID10)
            contents[1] = contents[1] | ((base_id & 0x07)<<5) #set (SID0 - SID2)
            contents[2] = int(0) #set (EID8 - EID15) = 0
            contents[3] = int(0) #set (EID0 - EID7) = 0
            
        #print 'contents = ', contents

        param = {}
        param = {'in':{"start_address":address, "contents":contents, "count":len(contents)}}
        ret = this.setRegisterS(param)
        if  ret is None:
            print "set_tx_buf_id -> setRegisterS, fail"
            return None

        return 0

    def get_rx_buf_id(this, param_dict):
        id = None
        ret = None
        key = None
        param = None
        address = None
        contents = None
        key_filters = None

        if  param_dict is None:
            print "get_rx_buf_id, incorrect parameter"
            return None

        if  param_dict.get('in') is None or param_dict.get('out') is None:
            print "get_rx_buf_id, illegal parameter"
            return None

        key_filters = ['address']

        for key in key_filters:
            if  key in param_dict['in'].keys():
                if key == 'address':
                    address = param_dict['in'][key]

        if  None in [address]:
            print "get_rx_buf_id, illegal parameter"
            return None

        param = {}
        param = {'in':{'start_address':address, 'count':4}, 'out':{}}
        ret = this.readRegisterS(param)
        if  ret is None:
            print 'get_rx_buf_id->readRegisterS, fail'
            return None

        contents = param['out']['contents']
        
        print 'contents = ', contents

        id = (contents[0]<<3) + (contents[1]>>5)
        param_dict['out']['flag'] = 0

        if  ((contents[1] & mcp2515_con.MCP_TXB_EXIDE_M) == mcp2515_con.MCP_TXB_EXIDE_M):            
            id = (id<<2) + (contents[1] & 0x03)
            id = (id<<8) + contents[2]
            id = (id<<8) + contents[3]
            param_dict['out']['flag'] = 1
        else:
            id = id << 18
            

        param_dict['out']['id'] = id

        return 0

    def initCANBuffers(this):
        ret = None
        reg1 = None
        reg2 = None
        reg3 = None
        ret = None
        std = 0
        ext = 1
        mask = 0
        filter = 0 
        param = None
  
        # RXM0SIDH
        param = {}
        param = {'in':{"address":mcp2515_con.MCP_RXM0SIDH, "flag":ext, "id":mask}}
        ret = this.set_mf_id(param)
        if  ret is None:
            print "initCANBuffers -> set_mf_id(RXM0SIDH), fail"
            return None

        # RXM1SIDH
        param = {}
        param = {'in':{"address":mcp2515_con.MCP_RXM1SIDH, "flag":ext, "id":mask}}
        ret = this.set_mf_id(param)
        if  ret is None:
            print "initCANBuffers -> set_mf_id(RXM1SIDH), fail"
            return None

        # RXF0SIDH
        param = {}
        param = {'in':{"address":mcp2515_con.MCP_RXF0SIDH, "flag":ext, "id":filter}}
        ret = this.set_mf_id(param)
        if  ret is None:
            print "initCANBuffers -> set_mf_id(RXF0SIDH), fail"
            return None

        # RXF1SIDH
        param = {}
        param = {'in':{"address":mcp2515_con.MCP_RXF1SIDH, "flag":std, "id":filter}}
        ret = this.set_mf_id(param)
        if  ret is None:
            print "initCANBuffers -> set_mf_id(RXF1SIDH), fail"
            return None

        # RXF2SIDH
        param = {}
        param = {'in':{"address":mcp2515_con.MCP_RXF2SIDH, "flag":ext, "id":filter}}
        ret = this.set_mf_id(param)
        if  ret is None:
            print "initCANBuffers -> set_mf_id(RXF2SIDH), fail"
            return None

        # RXF3SIDH
        param = {}
        param = {'in':{"address":mcp2515_con.MCP_RXF3SIDH, "flag":std, "id":filter}}
        ret = this.set_mf_id(param)
        if  ret is None:
            print "initCANBuffers -> set_mf_id(RXF3SIDH), fail"
            return None

        # RXF4SIDH
        param = {}
        param = {'in':{"address":mcp2515_con.MCP_RXF4SIDH, "flag":ext, "id":filter}}
        ret = this.set_mf_id(param)
        if  ret is None:
            print "initCANBuffers -> set_mf_id(RXF4SIDH), fail"
            return None

        # RXF5SIDH
        param = {}
        param = {'in':{"address":mcp2515_con.MCP_RXF5SIDH, "flag":std, "id":filter}}
        ret = this.set_mf_id(param)
        if  ret is None:
            print "initCANBuffers -> set_mf_id(RXF5SIDH), fail"
            return None

        reg1 = mcp2515_con.MCP_TXB0CTRL
        reg2 = mcp2515_con.MCP_TXB1CTRL
        reg3 = mcp2515_con.MCP_TXB2CTRL

        for i in range(0, 14):
            param = {}
            param = {'in':{'address':reg1, 'value':0}}
            ret = this.setRegister(param)
            if  ret is None:
                print 'initCANBuffers->setRegister, fail'
                return None
            
            param = {}
            param = {'in':{'address':reg2, 'value':0}}
            ret = this.setRegister(param)
            if  ret is None:
                print 'initCANBuffers->setRegister, fail'
                return None

            param = {}
            param = {'in':{'address':reg3, 'value':0}}
            ret = this.setRegister(param)
            if  ret is None:
                print 'initCANBuffers->setRegister, fail'
                return None

            reg1 = reg1 + 1
            reg2 = reg2 + 1
            reg3 = reg3 + 1

        param = {}
        param = {'in':{'address':mcp2515_con.MCP_RXB0CTRL, 'value':0}}
        ret = this.setRegister(param)
        if  ret is None:
            print 'initCANBuffers->setRegister, fail'
            return None

        param = {}
        param = {'in':{'address':mcp2515_con.MCP_RXB1CTRL, 'value':0}}
        ret = this.setRegister(param)
        if  ret is None:
            print 'initCANBuffers->setRegister, fail'
            return None

        return 0

    def getNextFreeTXBuf(this, param_dict):
        param = None
        value = None
        tx_ctrl_reg_sets = [mcp2515_con.MCP_TXB0CTRL, mcp2515_con.MCP_TXB1CTRL, mcp2515_con.MCP_TXB2CTRL]

        if  param_dict is None:
            print "getNextFreeTXBuf, incorrect parameter"
            return None        

        if  param_dict.get('out') is None:
            print "getNextFreeTXBuf, illegal parameter"
            return None

        for i in range(0, 3):
            param = {}
            param = {'in':{'address':tx_ctrl_reg_sets[i]}, 'out':{}}
            ret = this.readRegister(param)
            if  ret is not None:
                value = param['out']['value']
                if  (value & mcp2515_con.MCP_TXB_TXREQ_M) == 0:
                    param_dict['out']['address'] = tx_ctrl_reg_sets[i]
                    return 0
            else:
                print "getNextFreeTXBuf, readRegister fail"
                return None

        return None

    def sendCANMsg(this, param_dict):
        id = None
        key = None
        ret = None
        dlc = None
        rtr = None
        flag = None
        value = None
        param = None
        count = None
        left = None
        length = None
        address = None
        message = None
        timeout = None
        retries = None
        key_filters = None
        tx_buf_reg_address = None
        tx_buf_id_reg_address = None
        tx_buf_dlc_reg_address = None
        tx_buf_con_reg_address = None

        if  param_dict is None:
            print "sendCANMsg, incorrect parameter"
            return None

        if  param_dict.get('in') is None:
            print "sendCANMsg, illegal parameter"
            return None

        key_filters = ['id', 'flag', 'message', 'length', 'rtr']

        for key in key_filters:
            if  key in param_dict['in'].keys():
                if  key == "id":
                    id = param_dict['in'][key]
                elif key == 'flag':
                    flag = param_dict['in'][key]
                elif key == 'message':
                    message = param_dict['in'][key]
                elif key == 'length':
                    length = param_dict['in'][key]
                elif key == 'rtr':
                    rtr = param_dict['in'][key]

        if  None in [id, flag, message, length, rtr]:
            print "sendCANMsg, illegal parameter"
            return None

        #print "message = ", message

        this.tx_data = [0] * 8

        count = length / 8
        left = length % 8

        if  left > 0:
            count = count + 1

        if  count > 0:

            for i in range(0, count):

                if  ((i+1) * 8) <= length:
                    dlc = 8
                else:
                    dlc = length - (i * 8)

                #print 'dlc = ', dlc

                for j in range(0, dlc):
                    this.tx_data[j] = message[i*8 + j]

                param = {'out':{}}
                ret = this.getNextFreeTXBuf(param)
                if  ret is not None:
                    #print 'buffer = ', hex(param['out']['address'])
                    tx_buf_con_reg_address = param['out']['address']
                    tx_buf_reg_address = tx_buf_con_reg_address + 6

                    #Write can message to transmit buffer
                    param = {}
                    param = {'in':{'start_address':tx_buf_reg_address, 'contents':this.tx_data, 'count':dlc}}
                    ret = this.setRegisterS(param)
                    if  ret is None:
                        print "sendCANMsg->setRegisterS, fail"
                        return None

                    #Set DLC
                    if  rtr:
                        dlc = dlc | mcp2515_con.MCP_RTR_MASK
                    tx_buf_dlc_reg_address = tx_buf_con_reg_address + 5
                    param = {}
                    param = {'in':{'address':tx_buf_dlc_reg_address, 'value':dlc}}
                    ret = this.setRegister(param)
                    if  ret is None:
                        print "sendCANMsg->setRegister, fail"
                        return None

                    #Set CAN ID
                    tx_buf_id_reg_address = tx_buf_con_reg_address + 1
                    param = {}
                    param = {'in':{'address':tx_buf_id_reg_address, 'flag':flag, 'id':id}}
                    ret = this.set_tx_buf_id(param)
                    if  ret is None:
                        print "sendCANMsg->set_tx_buf_id, fail"
                        return None

                    #Request a transmission
                    param = {}
                    param = {'in':{'address':tx_buf_con_reg_address, 'mask':mcp2515_con.MCP_TXB_TXREQ_M, 'value':mcp2515_con.MCP_TXB_TXREQ_M}}
                    ret = this.modifyRegister(param)
                    if  ret is None:
                        print "sendCANMsg->modifyRegister, fail"
                        return None

                    #Check the completion of transmission
                    timeout = 999 # -_-!  I like 999, no other reasons
                    for retries in range(0, timeout):
                        param = {}
                        param = {'in':{'address':tx_buf_con_reg_address}, 'out':{}}
                        ret = this.readRegister(param)
                        if  ret is not None:
                            value = param['out']['value']
                            if  (value & 0x08) == 0:
                                break
                    if  retries == timeout -1:
                        print "=========timeout========="
                        return None

                    #for z in range(0, dlc):
                    #    print 'tx_data ', z, ' = ', this.tx_data[z]

        return 0

    def readCANMsg_anyway(this, param_dict):
        id = None
        ret = None
        key = None
        rtr = None
        dlc = None
        ctrl = None
        flag = None
        mask = None
        value = None
        param = None
        status = None
        counter = None
        length = None
        message = None
        contents = None
        rx_buf_id = None
        spi_buffer = None
        completion = None
        key_filters = None
        byte_streams = None
        dict_message = None
        time_interval = None
        rx_data_length = None
        rev_start_time = None
        rx_buf_reg_address = None
        rx_buf_id_reg_address = None
        rx_buf_dlc_reg_address = None
        rx_buf_con_reg_address = None

        if  param_dict is None:
            print "readCANMsg_anyway, incorrect parameter"
            return None

        if  param_dict.get('in') is None or param_dict.get('out') is None:
            print "readCANMsg_anyway, illegal parameter"
            return None

        key_filters = ['length', 'time_interval']

        for key in key_filters:
            if  key in param_dict['in'].keys():
                if key == 'length':
                    length = param_dict['in'][key]
                elif key == 'time_interval':
                    time_interval = param_dict['in'][key]

        if  None in [length, time_interval]:
            print "readCANMsg_anyway, illegal parameter"
            return None

        counter = 0
        completion = 0
        rx_data_length = 0
        message = [0] * length
        dict_message = {}
        rev_start_time = time.time()

        #print "length = ", length, "time_interval = ", time_interval
        
        while ((time.time() - rev_start_time) < time_interval) and (completion == 0):
            # read status from status register
            #byte_streams = [mcp2515_con.MCP_READ_STATUS, 0x00]
            ret = this.spi.xfer2([0xA0, 0x00])
            if  ret is not None:
                if  (ret[1] & 0x01):
                    #print 'read can message from rxb0'
                    rx_buf_con_reg_address = mcp2515_con.MCP_RXB0CTRL

                    #get CAN ID
                    rx_buf_id_reg_address = rx_buf_con_reg_address + 1

                    ret = this.spi.xfer2([mcp2515_con.MCP_READ, rx_buf_id_reg_address, 0, 0, 0, 0])
                    if  ret is None:
                        print "readCANMsg_anyway, read CAN ID fail"
                        break
                        #return None
                    
                    rx_buf_id = (ret[2]<<3) + (ret[3]>>5)
                    if  ((ret[3] & mcp2515_con.MCP_TXB_EXIDE_M) == mcp2515_con.MCP_TXB_EXIDE_M): 
                        rx_buf_id = (rx_buf_id<<2) + (ret[3] & 0x03)
                        rx_buf_id = (rx_buf_id<<8) + ret[4]
                        rx_buf_id = (rx_buf_id<<8) + ret[5]
                    else:
                        rx_buf_id = rx_buf_id << 18

                    #print "rx_buf_id = ", hex(rx_buf_id)

                    #get dlc
                    rx_buf_dlc_reg_address = rx_buf_con_reg_address + 5
                    ret = this.spi.xfer2([mcp2515_con.MCP_READ, rx_buf_dlc_reg_address, 0x00])
                    if  ret is None:
                        print "readCANMsg_anyway, read dlc fail"
                        break
                        #return None
                    dlc = ret[2] & mcp2515_con.MCP_DLC_MASK

                    #print "dlc = ", dlc

                    #get rx buf
                    rx_buf_reg_address = rx_buf_con_reg_address + 6
                    byte_streams =  [0] * (dlc + 2)
                    byte_streams[0] = mcp2515_con.MCP_READ
                    byte_streams[1] = rx_buf_reg_address
                    spi_buffer = this.spi.xfer2(byte_streams)
                    if  spi_buffer is None:
                        print "readCANMsg_anyway, read rx buf fail"
                        break
                        #return None

                    #save CAN message to memory
                    if  (rx_data_length + dlc) <= length:
                        for i in range(0, dlc):
                            message[i] = spi_buffer[2 + i]
                        #print "spi buf = ", spi_buffer
                        #print "message = ", message
                        rx_data_length = rx_data_length + dlc
                    else:
                        print "rx_data_length00:",rx_data_length,"  dlc:",dlc,"  length:",length
                        print 'readCANMsg_anyway, rx buffer overload' 
                        break
                        #return None

                    #clear full interrupt flag bit
                    mask = mcp2515_con.MCP_RX0IF_MASK
                    value = mcp2515_con.MCP_RX0IF_MASK ^ mcp2515_con.MCP_RX0IF_MASK
                    ret = this.spi.xfer2([mcp2515_con.MCP_BITMOD, mcp2515_con.MCP_CANINTF, mask, value])
                    if  ret is None:
                        print 'readCANMsg_anyway->spi.xfer2, fail'
                        break
                        #return None

                    dict_message.update({rx_buf_id:message[0:dlc]})
                    counter = counter + 1
                if (ret[1] & 0x02):
                    #print 'read can message from rxb1'
                    rx_buf_con_reg_address = mcp2515_con.MCP_RXB1CTRL

                    #get CAN ID
                    rx_buf_id_reg_address = rx_buf_con_reg_address + 1

                    ret = this.spi.xfer2([mcp2515_con.MCP_READ, rx_buf_id_reg_address, 0, 0, 0, 0])
                    if  ret is None:
                        print "readCANMsg_anyway, read CAN ID fail"
                        break
                        #return None
                    
                    rx_buf_id = (ret[2]<<3) + (ret[3]>>5)
                    if  ((ret[3] & mcp2515_con.MCP_TXB_EXIDE_M) == mcp2515_con.MCP_TXB_EXIDE_M): 
                        rx_buf_id = (rx_buf_id<<2) + (ret[3] & 0x03)
                        rx_buf_id = (rx_buf_id<<8) + ret[4]
                        rx_buf_id = (rx_buf_id<<8) + ret[5]
                    else:
                        rx_buf_id = rx_buf_id << 18

                    #print "rx_buf_id = ", hex(rx_buf_id)

                    #get dlc
                    rx_buf_dlc_reg_address = rx_buf_con_reg_address + 5
                    ret = this.spi.xfer2([mcp2515_con.MCP_READ, rx_buf_dlc_reg_address, 0x00])
                    if  ret is None:
                        print "readCANMsg_anyway, read dlc fail"
                        break
                        #return None
                    dlc = ret[2] & mcp2515_con.MCP_DLC_MASK

                    #print "dlc = ", dlc

                    #get rx buf
                    rx_buf_reg_address = rx_buf_con_reg_address + 6
                    byte_streams =  [0] * (dlc + 2)
                    byte_streams[0] = mcp2515_con.MCP_READ
                    byte_streams[1] = rx_buf_reg_address
                    spi_buffer = this.spi.xfer2(byte_streams)
                    if  spi_buffer is None:
                        print "readCANMsg_anyway, read rx buf fail"
                        break
                        #return None

                    #save CAN message to memory
                    if  (rx_data_length + dlc) <= length:
                        for i in range(0, dlc):
                            message[i] = spi_buffer[2 + i]
                        #print "spi buf = ", spi_buffer
                        #print "message = ", message
                        rx_data_length = rx_data_length + dlc
                    else:
                        print "rx_data_length:",rx_data_length,"  dlc:",dlc,"  length:",length
                        print 'readCANMsg_anyway, rx buffer overload' 
                        break
                        #return None

                    #clear full interrupt flag bit
                    mask = mcp2515_con.MCP_RX1IF_MASK
                    value = mcp2515_con.MCP_RX1IF_MASK ^ mcp2515_con.MCP_RX1IF_MASK
                    ret = this.spi.xfer2([mcp2515_con.MCP_BITMOD, mcp2515_con.MCP_CANINTF, mask, value])
                    if  ret is None:
                        print 'readCANMsg_anyway->spi.xfer2, fail'
                        break
                        #return None

                    dict_message.update({rx_buf_id:message[0:dlc]})

                    counter = counter + 1

                if  rx_data_length == length:
                    completion = 1
                    break
                
        #print "counter = ", counter
        
        if  completion == 0:
            #time.sleep(0.01)
            #print "readCANMsg_anyway completion = 0"
            #print "dict_message = ", dict_message
            dict_message = None
            #clear full interrupt flag bit
            mask = mcp2515_con.MCP_RX0IF_MASK
            value = mcp2515_con.MCP_RX0IF_MASK ^ mcp2515_con.MCP_RX0IF_MASK
            ret = this.spi.xfer2([mcp2515_con.MCP_BITMOD, mcp2515_con.MCP_CANINTF, mask, value])
            if  ret is None:
                print 'readCANMsg_anyway->spi.xfer2, fail'
                return None
                                             
            #clear full interrupt flag bit
            mask = mcp2515_con.MCP_RX1IF_MASK
            value = mcp2515_con.MCP_RX1IF_MASK ^ mcp2515_con.MCP_RX1IF_MASK
            ret = this.spi.xfer2([mcp2515_con.MCP_BITMOD, mcp2515_con.MCP_CANINTF, mask, value])
            if  ret is None:
                print 'readCANMsg_anyway->spi.xfer2, fail'
                return None                       
            return None

            
        param_dict['out']['message'] = dict_message
        return 0

    def readCANMsg(this, param_dict):
        id = None
        ret = None
        key = None
        rtr = None
        dlc = None
        ctrl = None
        flag = None
        mask = None
        value = None
        param = None
        status = None
        length = None
        message = None
        contents = None
        rx_buf_id = None
        completion = None
        key_filters = None
        time_interval = None
        rx_data_length = None
        rev_start_time = None
        rx_buf_reg_address = None
        rx_buf_id_reg_address = None
        rx_buf_dlc_reg_address = None
        rx_buf_con_reg_address = None

        if  param_dict is None:
            print "readCANMsg, incorrect parameter"
            return None

        if  param_dict.get('in') is None or param_dict.get('out') is None:
            print "readCANMsg, illegal parameter"
            return None

        key_filters = ['id', 'length', 'time_interval']

        for key in key_filters:
            if  key in param_dict['in'].keys():
                if  key == "id":
                    id = param_dict['in'][key]
                elif key == 'length':
                    length = param_dict['in'][key]
                elif key == 'time_interval':
                    time_interval = param_dict['in'][key]
   
        if  None in [id, length, time_interval]:
            print "readCANMsg, illegal parameter"
            return None

        completion = 0
        rx_data_length = 0
        message = [0] * length
        rev_start_time = time.time()

        while ((time.time() - rev_start_time) < time_interval) and (completion == 0):
            #time.sleep(0.3)
            param = {'out':{}}
            ret = this.readStatus(param)
            if  ret is not None:
                status = param['out']['status']
                if  (status & 0x01):
                    #print 'read can message from rxb0'
                    rx_buf_con_reg_address = mcp2515_con.MCP_RXB0CTRL
                elif (status & 0x02):
                    #print 'read can message from rxb1'
                    rx_buf_con_reg_address = mcp2515_con.MCP_RXB1CTRL
                else:
                    #print 'No CAN message'
                    continue

                #get can id from rx buffer
                rx_buf_id_reg_address = rx_buf_con_reg_address + 1
                param = {}
                param = {'in':{'address':rx_buf_id_reg_address}, 'out':{}}
                ret = this.get_rx_buf_id(param)
                if  ret is None:
                    print 'readCANMsg->get_rx_buf_id, fail'
                    return None

                rx_buf_id = param['out']['id']
                flag = param['out']['flag']

                #get rtr flag
                param = {}
                param = {'in':{'address':rx_buf_con_reg_address}, 'out':{}}
                ret = this.readRegister(param)
                if  ret is None:
                    print 'readCANMsg->readRegister, fail'
                    return None

                ctrl =  param['out']['value']
                if  (ctrl & 0x08):
                    rtr = 1
                else:
                    rtr = 0

                #get dlc
                rx_buf_dlc_reg_address = rx_buf_con_reg_address + 5
                param = {}
                param = {'in':{'address':rx_buf_dlc_reg_address}, 'out':{}}
                ret = this.readRegister(param)
                if  ret is None:
                    print 'readCANMsg->readRegister, fail'
                    return None

                dlc = param['out']['value'] & mcp2515_con.MCP_DLC_MASK

                #get rx buf
                rx_buf_reg_address = rx_buf_con_reg_address + 6
                param = {}
                param = {'in':{'start_address':rx_buf_reg_address, 'count':dlc}, 'out':{}}
                ret = this.readRegisterS(param)
                if  ret is None:
                    print 'readCANMsg->readRegisterS, fail'
                    return None

                contents = param['out']['contents']
 
                #clear full interrupt flag bit
                if  (status & 0x01):
                    mask = mcp2515_con.MCP_RX0IF_MASK
                    value = mcp2515_con.MCP_RX0IF_MASK ^ mcp2515_con.MCP_RX0IF_MASK
                else:
                    mask = mcp2515_con.MCP_RX1IF_MASK
                    value = mcp2515_con.MCP_RX1IF_MASK ^ mcp2515_con.MCP_RX1IF_MASK
                param = {}
                param = {'in':{'address':mcp2515_con.MCP_CANINTF, 'mask':mask, 'value':value}}
                ret = this.modifyRegister(param)
                if  ret is None:
                    print "readCANMsg->modifyRegister, fail"
                    return None

                #print 'rx_buf_id = ', rx_buf_id
                #print 'rtr = ', rtr, 'rx dlc = ', dlc
                #print 'rx buf = ', contents

                if  id == rx_buf_id:
                    if  (rx_data_length + dlc) <= length:
                        for i in range(0, dlc):
                            message[rx_data_length + i] = contents[i]
                        rx_data_length = rx_data_length + dlc
                    else:
                        print 'readCANMsg, rx buffer overload' 
                        return None
                else:
                    print 'rx buffer id unmatched'
                    return None

                if  rx_data_length == length:
                    completion = 1
                    break

        if  completion == 0:
            print 'readCANMsg reads message fail'
            return None

        return 0
    

