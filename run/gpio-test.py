#!/usr/bin/env python
# encoding: utf-8

import RPi.GPIO
import time
import wingdbstub

# ָ��GPIO�ڵ�ѡ��ģʽΪGPIO���ű��ģʽ������������ģʽ��
RPi.GPIO.setmode(RPi.GPIO.BCM)

# ָ��GPIO14������LED�������ӵ�GPIO��ţ���ģʽΪ���ģʽ
# �������GPIO�ڵ�ѡ��ģʽָ��Ϊ����ģʽ�Ļ��������Ӧ��ָ��8�Ŷ�����14�š�
RPi.GPIO.setup(18, RPi.GPIO.OUT)

# ѭ��10��
for i in range(0, 10):
	# ��GPIO14����ߵ�ƽ��LED������
	RPi.GPIO.output(18, True)
	# ����һ��ʱ��
	time.sleep(0.5)
	# ��GPIO14����͵�ƽ��LED����
	RPi.GPIO.output(18, False)
	# ����һ��ʱ��
	time.sleep(0.5)

# �������GPIO�ڣ�����Ҳ���ԣ�����ÿ�γ������ʱ����һ�£���ϰ�ߣ�
RPi.GPIO.cleanup()