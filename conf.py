#!/usr/bin/python
# -*- coding: utf8 -*-

from common import *

# 配置文件读取类，e3g.conf
class e3gConf:
    def __init__(self,path):
        self.path = path;
    def parse(self):
        self.fd = open(self.path,"r");
        value = self.fd.readline();
        valueList = value.split(":");
        self.smsIp = valueList[1];
        self.smsPort = valueList[3];
	e3gPrint("DEBUG","smsip=%s,smsport=%s"%(self.smsIp,self.smsPort));
        value = self.fd.readline();
        valueList = value.split(":");
        self.e3gIp = valueList[1];
        self.e3gPort = valueList[3];
        value = self.fd.readline();
        valueList = value.split(":");
        self.memLimit = valueList[1];
        value = self.fd.readline();
        valueList = value.split(":");
        self.cpuLimit = valueList[1];
        value = self.fd.readline();
        valueList = value.split(":");
        self.model = valueList[1];
        value = self.fd.readline();
        valueList = value.split(":");
        self.pstype = valueList[1];
        value = self.fd.readline();
        valueList = value.split(":");
        self.password = valueList[1];
        value = self.fd.readline();
        valueList = value.split(":");
        self.keepAliveTime = valueList[1];
        value = self.fd.readline();
        valueList = value.split(":");
        self.dialingTime = valueList[1];
        value = self.fd.readline();
        valueList = value.split(":");
        self.downloadTime = valueList[1];
        value = self.fd.readline();
        valueList = value.split(":");
        self.dealingTime = valueList[1];
        value = self.fd.readline();
        valueList = value.split(":");
        self.rebootTime = valueList[1];
        value = self.fd.readline();
        valueList = value.split(":");
        self.threadManageDeviceNum = string.atoi(valueList[1]);
	e3gPrint("DEBUG","Device thread man num%d"%(self.threadManageDeviceNum));
        self.slot = "";
        self.fd.close();
        self.ipPool = "";
        self.maskPool = "";
        self.pcIp = "";
        return True;
