#!/usr/bin/python
# -*- coding: utf8 -*-

import time
import datetime
import random
import string
import thread
import threading
from Queue import Queue
from sqlite3 import dbapi2
import os

DEBUG = 0;

KEY="7b522e435b6f5a514b71716a24af60de";
IV="0000";
ALG="-aes-128-ecb"

class e3gQueue:
    def __init__(self):
        self.queue = Queue();
        self.rLock = threading.Lock();
        self.wLock = threading.Lock();
        self.numLock = threading.Lock();
        self.deviceNum = 0;
    def put(self,data):
        self.wLock.acquire(1);
        self.queue.put(data,1);
        self.wLock.release();
        self.numLock.acquire(1);
        self.deviceNum = self.deviceNum + 1;
        self.numLock.release();
    def get(self):
        self.rLock.acquire(1);
        data = self.queue.get(1);
        self.rLock.release();
        self.numLock.acquire(1);
        self.deviceNum = self.deviceNum - 1;
        self.numLock.release();
        return data;
    def getQueueNum(self):
        self.numLock.acquire(1);
        deviceNum = self.deviceNum;
        self.numLock.release();
        return deviceNum;

class sqlite3Db:
    def __init__(self,db,path):
        self.path = path;
        self.db = db;
        self.lock = threading.Lock();
    def select(self,what,where,value):
        conn = dbapi2.connect(self.path);
        conn.text_factory = str;
        cur = conn.cursor();
        cmd = 'select %s from %s where %s = "%s";'%(what,self.db,where,value);
        cur.execute(cmd);
        conn.commit();
        res = cur.fetchall();
        conn.close();
        return res;
    def update(self,which,where,value,wv):
        self.lock.acquire(1);
        conn = dbapi2.connect(self.path);
        conn.text_factory = str;
        cur = conn.cursor();
        cmd = 'update %s set %s=\'%s\' where %s=\'%s\';'%(self.db,which,value,where,wv);
        cur.execute(cmd);
        conn.commit();
        conn.close();
        self.lock.release();

class failedMessage:
    def __init__(self):
	self.failedTimes= 0;
	self.failedMsg = "";
	self.lastFailed = "";
    def put(self,msg,last):
	self.failedTimes += 1;
	self.failedMsg = msg;
	self.lastFailed = last;
	DebugFillTheFile("%s:failed times:%d\n"%(msg,self.failedTimes));
        
        
def enCrypto(data):
    global ALG,KEY,IV;
    cmd="echo \'%s\' | openssl enc %s -nosalt -K %s -iv %s"%(data,ALG,KEY,IV);
    pipe = os.popen(cmd);
    data = pipe.read();
    pipe.close();
    return data;

def e3gPrint(way,data):
    if way == "DEBUG":
        if DEBUG == 1:
            print "% DEBUG %% :  ",data;
    elif way == "INFO":
        print "% INFO %% :  ",data;
    elif way == "ERR":
        print "% ERROR %% :  ",data;
        
def debug_stop():
    if DEBUG == 1:
        while True:
            time.sleep(1);
            
def DebugFillTheFile(data):
    file = open("log.log",'a');
    file.write(data);
    file.close();
