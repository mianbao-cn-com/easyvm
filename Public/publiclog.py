#-*- coding:utf-8 -*-

'''
@Created on 2016年5月11日
 
@author: MianBao

@author_web: Mianbao.cn.com

@网站日志
'''

import os
import time
import logging
from django.db.models import Q
from .models import Public_Log


class PublicLog():
    
    def __init__(self,douser=None,todo=None,types=None,touser=None,result=0):
        #types: motify pawd 1
        self.todo = todo
        if touser is None:
            self.touser = douser
        else:
            self.touser = touser
        self.result = result
        self.types = types #1,login 2,register
        self.douser = douser
    
    @property
    def Create(self):
        new = dict()
        new['ctime'] = time.time()
        new['douser'] = self.douser
        new['todo'] = self.todo
        new['touser'] = self.touser
        new['result'] = self.result
        new['type'] = self.types
        
        rs = Public_Log(**new)
        rs.save()
        
    def GetUidLog(self,id):
        print id
        User_Log = Public_Log.objects.filter(Q(douser = id)|Q(touser = id))
        return User_Log
    
    @staticmethod
    def GetAllLog():
        User_Log = Public_Log.objects.all()
        return User_Log

def logs(where,log): 
        log_name = os.path.join(os.path.dirname(__file__),'vm_agent.log')
        logger = logging.getLogger(where)
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(log_name)
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s' )
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        logger.debug(log)
















