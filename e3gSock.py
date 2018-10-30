#!/usr/bin/python
# -*- coding: utf8 -*-

import socket
import select
from common import *

socketFailed = failedMessage();

class tcpServer:
    def __init__(self,ip,port,backlog):
        self.ip = ip;
        self.stat = True;
        self.port = port;
        self.backlog = backlog;
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM);
        try:
            self.socket.bind((self.ip,self.port));
        except:
            e3gPrint("ERR","Port are aready bind");
            self.stat = False;
        try:
            self.socket.listen(self.backlog);
        except:
            e3gPrint("ERR","Can't listen");
            self.stat = False;
    def __del__(self):
        self.socket.close();
    def acceptClient(self):
        if self.stat == False:
            return -2;
        self.infds,self.outfds,self.errfds = select.select([self.socket],[],[],5);
        if len(self.infds) != 0:
            e3gPrint("INFO","Accept the client connect");
            self.conn,self.cliAddr = self.socket.accept();
            return self.conn;
        else:
            return -1;
    def send(self,data):
	global socketFailed;
        status=self.sock.sendall(buffer(data));
	if status != None:
	    e3gPrint("ERR","send Failed !!!");
	    socketFailed.put("socket send","%s"%(time.localtime())); 
        time.sleep(0.2);   
    def recv(self,bufSiz):
        data = self.conn.recv(bufSiz);
        return data;
    def close(self):
        self.conn.close();
        
class tcpClient:
    def __init__(self,ip,port,localIp):
        self.ip = ip;
        self.port = port;
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        try:
            self.sock.bind((localIp,0));
        except:
            e3gPrint("ERR","Local ip are in use");
    def tcpConnect(self):
	global socketFailed;
        try:
            self.sock.connect((self.ip,self.port));
            status = 0;
        except:
            e3gPrint("ERR","Connect to device timeout");
	    socketFailed.put("socket send","%s"%(time.localtime())); 
            status = -1;
        return status;
    def send(self,data,pLen):
	global socketFailed;
        status=self.sock.sendall(buffer(data));
	if status != None:
	    e3gPrint("ERR","send Failed !!!");
	    socketFailed.put("socket send","%s"%(time.localtime())); 
        time.sleep(0.2);   
    def recv(self,bufSiz):
        data = self.sock.recv(bufSiz);
        return data;
    def close(self):
        self.sock.close();
        
class udpClient:
    def __init__(self,ip,port,localIp):
        self.ip = ip;
        self.port = port;
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);
        try:
            self.sock.bind((localIp,0));
        except:
            e3gPrint("ERR","Local ip are in use");
    def send(self,data,pLen):
        try:
            length = self.sock.sendto(data,(self.ip,self.port));
        except:
            e3gPrint("INFO","Socket is not connected,maybe disconnect by peer");
            return -1;
        time.sleep(0.5);   
    def close(self):
        self.sock.close();

def createClient(ip,port,dst,protol):
    if protol == "UDP":
        sock = udpClient(ip,port,dst);
    else:
        sock = tcpClient(ip,port,dst);
        status = sock.tcpConnect();
        if status == -1:
            return -1;
    return sock;

def getProtol():
    socketType = random.randint(0,10);
    if socketType % 2 == 0:
	socketType = "TCP";
    else:
	socketType = "UDP";
    return socketType;

if __name__ == "__main__":
    import sys;
    cli = createClient(sys.argv[1],string.atoi(sys.argv[2]),'','UDP');
    data = raw_input("Please input data to test send:");
    cli.send(data);
