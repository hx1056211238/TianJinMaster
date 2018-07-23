#!/usr/bin/env python
#-*- coding:utf-8 -*-

from setuptools import setup, Extension

hello_world = Extension('lc_hello_world', sources=["lc_hello.c"])

setup(ext_modules=[hello_world])
