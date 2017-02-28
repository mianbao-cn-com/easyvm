#-*- coding:utf-8 -*-

'''
@Created on 2016年5月9日
 
@author: MianBao

@author_web: Mianbao.cn.com

@系统设置
'''
from django.db import models



class Public_Log(models.Model):
    ctime = models.CharField(max_length = 100,null=False)
    douser = models.IntegerField(null=False)
    todo = models.CharField(max_length = 100,null=False)
    touser = models.IntegerField(null=False)
    result = models.IntegerField(null=False)
    type = models.IntegerField(null=False)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    