#!/usr/bin/python
# -*- coding: utf8 -*-

import time
from conf import *
from common import *
from smsNet import *
from e3gReqMsg import *
from deviceAction import *

#------------------------------------
# E3g test program configuration path
#------------------------------------
PATH="e3g.conf"

#-------------------------------------
# Check the register device
#-------------------------------------

def getRegFromDb(sql):
    res = sql.select("phone","reg","1");
    return res;

def initDevice(newQueue,conf):
    e3gPrint("INFO","E3g test check the register device");
    sql = sqlite3Db("devinfo","dev.db");
    res = getRegFromDb(sql);
    i = 0;
    while i < len(res):
	timeNow = time.localtime();
	timeNow = "%s-%s-%s-%s-%s-%s"%(timeNow[0],timeNow[1],timeNow[2],timeNow[3],timeNow[4],timeNow[5]);
        devData = "3:%s::%s:%s:1:%s:%s:%s:%s"%(i+1,res[i][0],getImsi(res[i][0]),timeNow,timeNow,\
						getNetPoint(res[i][0]),getProtol());
	e3gPrint("DEBUG",devData);
        newQueue.put(devData);
        i = i + 1;
    #conf.ipPool = "192.168.100.20";
    #conf.maskPool = "255.255.255.0";
    #resIp,resMask = getAddressFromDb(sql);
    #while i < len(resIp):
    #    conf.ipPool = conf.ipPool+":"+resIp[i][0];
    #    conf.maskPool = conf.maskPool + ":" + resMask[i][0]); 
    #addIpAddress(conf.ipPool,conf.maskPool);
    
def getAddressFromDb(sql):
    resIp = sql.select("ip","reg","0");
    resIp += sql.select("ip","reg","1");
    resMask = sql.select("mask","reg","0");
    resMask += sql.select("mask","reg","1");
    return resIp,resMask;

def main():
    conf = e3gConf(PATH);
    newDeviceQueue = e3gQueue();
    regDeviceQueue = e3gQueue();   

    conf.parse();
    initDevice(newDeviceQueue,conf);
    smsNet_t = smsNetProcess(conf,newDeviceQueue);
    smsNet_t.start();
    # Fix me future
    #irl18Web_t = irl18Web();
    #irl18Web_t.start();
    device(conf,newDeviceQueue,regDeviceQueue); 
    e3gPrint("INFO","Device end");
    
if __name__ == "__main__":
    main();
