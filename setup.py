from distutils.core import setup
import py2exe

setup(console=['e3gTest.py','common.py','conf.py',\
               'deviceAction.py','e3gReqMsg.py',\
               'e3gSock.py','smsNet.py'],\
      data_files=['dev.db','e3g.conf','openssl','openssl\*']);
