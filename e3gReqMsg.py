#!/usr/bin/python
# -*- coding: utf8 -*-

from common import *

class irl18Web(threading.Thread):
    def __init__(self):
        e3gPrint("INFO","Create a thread");
        threading.Thread.__init__(self);
    def run(self):
        e3gPrint("INFO","irl18 web server start");
        #irl18MessageGet();
def irl18MessageGet():
    e3gPrint("INFO","Get message from irl18");
