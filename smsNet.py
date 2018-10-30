#!/usr/bin/python
# -*- coding: utf8 -*-

from common import *
from e3gSock import *
from deviceAction import *

BACKLOG = 1000;
RECVBUFSIZ = 1024;

class md5Crypt:
    def __init__(self):
        pass;
    def md5(self,text):
        import md5;
        m = md5.new();
        m.update(text);
        return m.digest();

class statisClass:
    def __init__(self):
        self.i=0;
        self.lock = threading.Lock();
    def add(self):
        self.lock.acquire(1);
        self.i = self.i + 1;
        self.lock.release();
    def get (self):
        return self.i;
    
statis = statisClass();

class smsNetProcess(threading.Thread):
    def __init__(self,conf,queue):
        threading.Thread.__init__(self);
        self.newQueue = queue;
        self.conf = conf;
    def run(self):
        e3gPrint("INFO","Sms net start");
        self.smsNetServer = tcpServer(self.conf.smsIp,string.atoi(self.conf.smsPort),BACKLOG);
        while True:
	    e3gPrint("DEBUG","sms Listen..................");
            conn = self.smsNetServer.acceptClient();
            if conn == -1:
                continue;
            if conn == -2:
                break;
            thread.start_new_thread(e3gNewSms,(self.smsNetServer,self.conf,self.newQueue));

def e3gNewSms(smsNetServer,conf,newQueue):
    e3gPrint("INFO","Sms-> a new e3g request reached");
    data = smsNetServer.recv(RECVBUFSIZ);
    e3gPrint("INFO",data);
    statis.add();
    e3gPrint("INFO","Sms net recv %d e3g request"%(statis.get()));
    dataList = data.split(":");
    smsId = dataList[0];
    phone = dataList[2];
    context = dataList[3];
    dataList = context.split(";");
    token = dataList[11];
    smsNetServer.send(smsId);
    
    imsi = getImsi(phone);
    netPoint = getNetPoint(phone);
    protol = getProtol();
    #key = md5Crypt();
    #deCryptMsg = aesCrypt(key.md5(imsi));
    #deCryptMsg.decrypt(data);

    #deviceStatus:deviceId:token:phone:imsi:coolingTime:baseTime:startUpTime:netPoint:protol
    timeNow = time.localtime();
    timeNow = "%s-%s-%s-%s-%s-%s"%(timeNow[0],timeNow[1],timeNow[2],timeNow[3],timeNow[4],timeNow[5]);
    devData="0:%s:%s:%s:%s:%s:%s:%s:%s:%s"%(newQueue.deviceNum+1,token,phone,imsi,conf.dialingTime,\
						timeNow,timeNow,netPoint,protol);
    e3gPrint("DEBUG",devData);
    e3gPrint("INFO",netPoint+": Dialing....................");
    newQueue.put(devData);
    smsNetServer.close();
