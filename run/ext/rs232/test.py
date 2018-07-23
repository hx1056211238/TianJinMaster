#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from rs232 import *


def list2string_HEX(lt):
    str = ""
    for i in range(0, len(lt)):
        str = str + hex(lt[i]).replace("0x", "").zfill(2)
    return str


rs = rs232()
rs.init()
k = list2string_HEX([0,255,255,0])


while 1:
    rs.sendto(0,"00000000FF",0)
    time.sleep(1)
    pass

rs.release()


