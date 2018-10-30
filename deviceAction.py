#!/usr/bin/python
# -*- coding: utf8 -*-

from common import *
from e3gSock import *
import smsNet

class threadManage:
    def __init__(self):
        self.upMsgThreadNum = 1;
        self.newDeviceThreadNum = 1;
        self.newLock = threading.Lock();
        self.regLock = threading.Lock();
        self.newExitLock = threading.Lock();
        self.regExitLock = threading.Lock();
    def upThreadAdd(self):
        self.regLock.acquire(1);
        self.upMsgThreadNum = self.upMsgThreadNum + 1;
        self.regLock.release();
    def newDeviceThreadAdd(self):
        self.newLock.acquire(1);
        self.newDeviceThreadNum = self.newDeviceThreadNum + 1;
        self.newLock.release();
    def getUpExit(self):
        self.regExitLock.acquire(1);
    def getNewExit(self):
        self.newExitLock.acquire(1);
    def putUpExit(self):
        self.regExitLock.release();
    def putNewExit(self):
        self.newExitLock.release();
    def getUpNum(self):
        return self.upMsgThreadNum;
    def getNewNum(self):
        return self.newDeviceThreadNum;
    def upThreadDel(self):
        self.regLock.acquire(1);
        self.upMsgThreadNum = self.upMsgThreadNum - 1;
        self.regLock.release();
    def newDeviceThreadDel(self):
        self.newLock.acquire(1);
        self.newDeviceThreadNum = self.newDeviceThreadNum - 1;
        self.newLock.release();

threadManage_t = threadManage();
sqlitDb = sqlite3Db("devinfo","dev.db");

class msgPacket:
    def __init__(self):
        self.type = "";
        self.sn = "";
        self.token ="";
        self.model = "";
        self.lanip = "";
        self.password = "";
        self.imsi = "";
        self.signal = "";
        self.slot = "";
        self.pstype = "";
        self.lon = "";
        self.lat = "";
        self.cid = "";
        self.lac = "";
        self.bid = "";
        self.sid = "";
        self.nid = "";
        self.boottime = "";
        self.cpuusage = "";
        self.memusage = "";
        self.onlinetime = "";
        self.rx = "";
        self.tx = "";

class messageUp(threading.Thread):
    def __init__(self,conf,queue,main):
        threading.Thread.__init__(self);
        self.conf = conf;
        self.regQueue = queue;
        self.main = main;
    def run(self):
        #deviceStatus:deviceId:token:phone:imsi:coolingTime:baseTime:startUpTime:sn:lac:cid:ip:netPoint:rx:tx:phone:protol
        while True:
            if self.main == False:#
                global threadManage_t;
                deviceNum = self.regQueue.getQueueNum();
                num = self.conf.threadManageDeviceNum * threadManage_t.getUpNum();
                if num > deviceNum:
                    threadManage_t.upThreadDel();
                    break; 
            devData = self.regQueue.get();
            dataList = devData.split(":");
            netPoint = dataList[12];
            protol = dataList[16];
            e3gPrint("INFO",netPoint+"("+protol+") : ---------Device running-----------");
            baseTime = dataList[6];
            coolingTime = dataList[5];
            coolingTime = string.atoi(coolingTime);
            diff,newTime = timeDiff(baseTime.split("-"));
            if diff >= coolingTime:
                msg,rx,tx = fillStatisMsg(dataList,self.conf,baseTime);
                e3gPacket = getStatisMsg(msg);
                cli = createClient(self.conf.e3gIp,string.atoi(self.conf.e3gPort),dataList[11],protol);
                if cli == -1:
                    time.sleep(1);
                    continue;
                e3gPrint("INFO",netPoint+"("+protol+") : Statistics send->"+e3gPacket);
                pLen = len(e3gPacket);
                e3gPacket = enCrypt(e3gPacket);
                cli.send(e3gPacket,pLen);
                devData = setNewBaseTime(devData,newTime,rx,tx);
                time.sleep(0.1);
                cli.close();
            else:
                time.sleep(1);
            
            self.regQueue.put(devData);
            e3gPrint("INFO",netPoint+"("+protol+") : ---------Device running done--------");

def setNewBaseTime(devData,newTime,rx,tx):
    dataList = devData.split(":");
    data = "%s:%s:%s:%s:%s:%s:%s:%s:%s:%s:%s:%s:%s:%s:%s:%s:%s"%(dataList[0],dataList[1],dataList[2],dataList[3],\
                                               dataList[4],dataList[5],newTime,dataList[7],\
                                               dataList[8],dataList[9],dataList[10],dataList[11],dataList[12],rx,\
                                                              tx,dataList[15],dataList[16]);
    return data;

def enCrypt(data):
    data = enCrypto(data);
    return data;

def fillStatisMsg(dataList,conf,lastTime):
    msg = msgPacket();
    startUpTime = dataList[7];
    upTime,pppTime = getUpAndPppTime(startUpTime,lastTime);
    msg.type = "0005";
    msg.sn = dataList[8];
    msg.token = dataList[2];
    msg.model = conf.model;
    msg.boottime = upTime;
    msg.cpuusage = getCpu();
    msg.memusage = getMem();
    msg.imsi = dataList[4];
    msg.signal = getSignal();
    msg.pstype = conf.pstype;
    msg.lac = dataList[9];
    msg.cid = dataList[10];
    msg.onlinetime = pppTime;
    msg.rx = getRx();
    rx = msg.rx + string.atoi(dataList[13]);
    msg.tx = getTx();
    tx = msg.tx + string.atoi(dataList[14]);
    setDevRx(dataList[15],rx);#phone
    setDevTx(dataList[15],tx);
    return msg,rx,tx;

def checkDeviceActiv(conf,regDeviceQueue,newQueue):
    global threadManage_t;

    deviceNum = regDeviceQueue.getQueueNum();
    while True:
        threadNum = threadManage_t.getUpNum() - 1;
        num = conf.threadManageDeviceNum * threadNum;
        if num < deviceNum:
            messageUp_t = messageUp(conf,regDeviceQueue,False);
            messageUp_t.start();
            threadManage_t.upThreadAdd();
        else:
            break;
    deviceNum = newQueue.getQueueNum();
    while True:
        threadNum = threadManage_t.getNewNum() - 1;
        num = conf.threadManageDeviceNum * threadNum;
        if num < deviceNum:
            thread.start_new_thread(deviceCheck,(newQueue,regDeviceQueue,conf,False));
            threadManage_t.newDeviceThreadAdd();
        else:
            break;
    checkThread = threading.Timer(0.5,checkDeviceActiv,[conf,regDeviceQueue,newQueue]);
    checkThread.start();

def checkprogram(conf,regDeviceQueue,newQueue):
    global threadManage_t;

    deviceNum = regDeviceQueue.getQueueNum();
    num = conf.threadManageDeviceNum * threadManage_t.getUpNum();
    DebugFillTheFile("reg:Can deal device num=%s,threadNum = %s,a thread can deal device num=%s device in reg queue=%s\n"\
                         %(num,threadManage_t.getUpNum(),conf.threadManageDeviceNum,deviceNum));
    deviceNum = newQueue.getQueueNum();
    num = conf.threadManageDeviceNum * threadManage_t.getNewNum();
    DebugFillTheFile("new:Can deal device num=%s,threadNum = %s,a thread can deal device num=%s device in new queue=%s\n"\
                         %(num,threadManage_t.getNewNum(),conf.threadManageDeviceNum,deviceNum));
    threading.Timer(60,checkprogram,[conf,regDeviceQueue,newQueue]).start();
    
def device(conf,newDeviceQueue,regDeviceQueue):
    e3gPrint("INFO","Device running");
    messageUp_t = messageUp(conf,regDeviceQueue,True);
    messageUp_t.start();
    checkThread = threading.Timer(0.1,checkDeviceActiv,[conf,regDeviceQueue,newDeviceQueue]);
    checkThread.start();
    #----checkSelf = threading.Timer(1,checkprogram,[conf,regDeviceQueue,newDeviceQueue]);
    #----checkSelf.start();
    deviceCheck(newDeviceQueue,regDeviceQueue,conf,True);
    
def getUpAndPppTime(baseTime,lastTime):
    upTime,nowTime = timeDiff(baseTime.split("-"));
    pppTime,nowTime = timeDiff(lastTime.split("-"));
    if pppTime < 0:
        pppTime = 0;
    return upTime,pppTime;

def getCpu():
    cpu = random.randint(5,100);
    return cpu;

def getTx():
    tx = random.randint(10000,50000);
    return tx;

def getRx():
    rx = random.randint(10000,50000);
    return rx;

def getCid(phone):
    global sqlitDb;
    cid = sqlitDb.select("cid","phone",phone);
    return cid[0][0];

def getLac(phone):
    global sqlitDb;
    lac = sqlitDb.select("lac","phone",phone);
    return lac[0][0];

def getSignal():
    signal = random.randint(1,33);
    if signal == 32:
        signal = 99;
    return signal;

def getMem():
    mem = random.randint(5,100);
    return mem;

def getDescr(phone):
    global sqlitDb;
    descr = sqlitDb.select("descr","phone",phone);
    return descr[0][0];

def getImsi(phone):
    global sqlitDb;
    imsi = sqlitDb.select("imsi","phone",phone);
    return imsi[0][0];

def getSn(phone):
    global sqlitDb;
    sn = sqlitDb.select("sn","phone",phone);
    return sn[0][0];

def getIp(phone):
    global sqlitDb;
    ip = sqlitDb.select("ip","phone",phone);
    return ip[0][0];

def getMask(phone):
    global sqlitDb;
    mask = sqlitDb.select("mask","phone",phone);
    return mask[0][0];

def getNetPoint(phone):
    global sqlitDb;
    netPoint = sqlitDb.select("descr","phone",phone);
    return netPoint[0][0];

def setDevReg(phone,regValue):
    global sqlitDb;
    sqlitDb.update("reg","phone",regValue,phone);

def setDevRx(phone,value):
    global sqlitDb;
    sqlitDb.update("rx","phone",value,phone);

def setDevTx(phone,value):
    global sqlitDb;
    sqlitDb.update("tx","phone",value,phone);
    
def timeDiff(baseTime):
    newTime = time.localtime();
    t1 = datetime.datetime(string.atoi(baseTime[0]),string.atoi(baseTime[1]),\
                           string.atoi(baseTime[2]),string.atoi(baseTime[3]),\
                           string.atoi(baseTime[4]),string.atoi(baseTime[5]));

    t2 = datetime.datetime(newTime[0],newTime[1],newTime[2],newTime[3],newTime[4],\
                           newTime[5]);
    diff = (t2 - t1).seconds;
    newTime = "%s-%s-%s-%s-%s-%s"%(newTime[0],newTime[1],newTime[2],newTime[3],newTime[4],newTime[5]);
    return diff,newTime;

def fillRegisterMsg(dataList,conf):
    msg = msgPacket();
    msg.type = "0002";
    phone = dataList[3];
    msg.sn = getSn(phone);
    msg.token = dataList[2];
    msg.model = conf.model;
    msg.lanip = getIp(phone);
    msg.password = conf.password;
    msg.imsi = dataList[4];
    msg.signal = getSignal();
    msg.pstype = conf.pstype;
    msg.lac = getLac(phone);
    msg.lac = "%X"%(string.atoi(msg.lac));
    msg.cid = getCid(phone);
    msg.cid = "%X"%(string.atoi(msg.cid));
    return msg;
        
def deviceCheck(newQueue,regQueue,conf,main):
    while True:
        if main == False:
            global threadManage_t;
            deviceNum = newQueue.getQueueNum();
            num = conf.threadManageDeviceNum * threadManage_t.getNewNum();
            if num > deviceNum:
               	threadManage_t.newDeviceThreadDel();
		break; 
        devData = newQueue.get();
        #deviceStatus:deviceId:token:phone:imsi:coolingTime:baseTime:startUpTime:netPoint
        dataList = devData.split(":");
        coolingTime = dataList[5];
        baseTime = dataList[6];
        diff,nowTime = timeDiff(baseTime.split("-"));
        coolingTime = string.atoi(coolingTime);
        if diff < coolingTime:
            newQueue.put(devData);
            time.sleep(1);
            continue;
        deviceStatus = dataList[0];
        deviceId = dataList[1];
        netPoint = dataList[8];
        phone = dataList[3];
        protol = dataList[9];
        startUpTime = dataList[7];
        msg = fillRegisterMsg(dataList,conf);
        cli = createClient(conf.e3gIp,string.atoi(conf.e3gPort),getIp(phone),protol);
        if cli == -1:
            newQueue.put(devData);
            print "Continue ,because can't connect to the server"
            time.sleep(1);
            continue;
        if deviceStatus == "0":
            #conf.ipPool = conf.ipPool+":"+getIp(phone);
            #conf.maskPool = conf.maskPool + ":" + getMask(phone); 
            #addIpAddress(conf.ipPool,conf.maskPool);
            setDevReg(phone,"0");
            e3gPacket = getReplyMsg("1001",msg.sn,msg.token,msg.model,"0");
            pLen = len(e3gPacket);
            e3gPrint("INFO",netPoint+"("+protol+") :Dialing packet->"+e3gPacket);
            e3gPacket = enCrypt(e3gPacket);
            cli.send(e3gPacket,pLen);
            devData = "1:%s:%s:%s:%s:%s:%s:%s:%s:%s"%(deviceId,msg.token,phone,\
                                             msg.imsi,conf.downloadTime,nowTime,startUpTime,netPoint,protol);
            e3gPrint("INFO",netPoint+"("+protol+") : Download....................");
            newQueue.put(devData);
        elif deviceStatus == "1":#
            e3gPacket = getReplyMsg("1002",msg.sn,msg.token,msg.model,"0");
            pLen = len(e3gPacket);
            e3gPrint("INFO",netPoint+"("+protol+") :Download packet->"+e3gPacket);
            e3gPacket = enCrypt(e3gPacket);
            cli.send(e3gPacket,pLen);
            devData = "2:%s:%s:%s:%s:%s:%s:%s:%s:%s"%(deviceId,msg.token,phone,msg.imsi,\
                                             conf.dealingTime,nowTime,startUpTime,netPoint,protol);
            e3gPrint("INFO",netPoint+"("+protol+") : Dealing.....................");
            newQueue.put(devData);
        elif deviceStatus == "2":
            e3gPacket = getReplyMsg("1003",msg.sn,msg.token,msg.model,"0");
            pLen = len(e3gPacket);
            e3gPrint("INFO",netPoint+"("+protol+") :Reboot packet->"+e3gPacket);
            e3gPacket = enCrypt(e3gPacket);
            cli.send(e3gPacket,pLen);
            devData = "3:%s:%s:%s:%s:%s:%s:%s:%s:%s"%(deviceId,msg.token,phone,msg.imsi,\
                                             conf.rebootTime,nowTime,startUpTime,netPoint,protol);
            newQueue.put(devData);
            e3gPrint("INFO",netPoint+"("+protol+") : Reboot.......................");
        elif deviceStatus == "3": 
            e3gPacket = getRegisterMsg(msg);
            pLen = len(e3gPacket);
            e3gPrint("INFO",netPoint+"("+protol+") :Register packet->"+e3gPacket);
            e3gPacket = enCrypt(e3gPacket);
            cli.send(e3gPacket,pLen);
            #deviceStatus:deviceId:token:phone:imsi:coolingTime:baseTime:startUpTime:sn:lac:cid:ip:netPoint:rx:tx:phone:protol
            devData = "3:%s:%s:%s:%s:%s:%s:%s:%s:%s:%s:%s:%s:0:0:%s:%s"%(deviceId,msg.token,phone,msg.imsi,\
                                             conf.keepAliveTime,nowTime,startUpTime,msg.sn,msg.lac,\
                                                         msg.cid,getIp(phone),netPoint,phone,protol);
            e3gPrint("INFO",netPoint+"("+protol+") : Runging.......................");
            setDevReg(phone,"1");
            regQueue.put(devData);
        else:
            debug("Error device Status");
        time.sleep(0.1);
        cli.close();

def getRegisterMsg(msg):
    data = '''{type:"%s",sn:"%s",token:"%s",model:"%s",lanip:"%s",\
password:"%s",sims:[{imsi:"%s",signal:"%s",slot:"%s",locations:\
[{pstype:"%s",lon:"%s",lat:"%s",cid:"%s",lac:"%s",bid:"%s",sid:"%s",\
nid:"%s"}]}]}'''%(msg.type,msg.sn,msg.token,msg.model,msg.lanip,msg.password,msg.imsi,\
                  msg.signal,msg.slot,msg.pstype,msg.lon,msg.lat,msg.cid,msg.lac,msg.bid,\
                  msg.sid,msg.nid);
    return data;

def getStatisMsg(msg):
    data = '''{type:"%s",sn:"%s",token:"%s",model:"%s",boottime:"%s",cpuusage:"%s",\
memusage:"%s",sims:[{imsi:"%s",signal:"%s",slot:"%s",locations:[{pstype:"%s",lon:"%s",\
lat:"%s",cid:"%s",lac:"%s",bid:"%s",sid:"%s",nid:"%s"}],onlinetime:"%s",rx:"%s",\
tx:"%s"}]}'''%(msg.type,msg.sn,msg.token,msg.model,msg.boottime,msg.cpuusage,msg.memusage,\
               msg.imsi,msg.signal,msg.slot,msg.pstype,msg.lon,msg.lat,msg.cid,msg.lac,msg.bid,\
                  msg.sid,msg.nid,msg.onlinetime,msg.rx,msg.tx);
    return data;

def getReplyMsg(seq,sn,token,model,status):
    data='''{type:"%s",sn:"%s",token:"%s",model:"%s",status:"%s"}'''%(seq,sn,token,\
                                                                      model,status);
    return data;


def addIpAddress(ipPool,maskPool):
    return 0;
