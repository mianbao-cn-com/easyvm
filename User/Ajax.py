#-*- coding:utf-8 -*-

'''
@Created on 2016年5月10日
 
@author: MianBao

@author_web: Mianbao.cn.com

@ The User Class
'''
import json
from models import *
from django.shortcuts import HttpResponse



def Ajax_url(request,value,do):
    if request.method == 'POST':
        if all((value,do)):
            ajax = Ajax(value)
            rs = getattr(ajax,do)
            rs = rs()
            return HttpResponse(json.dumps(rs))
    else:
        return HttpResponse(json.dumps(1))
        
class Ajax:
    
    def __init__(self,value):
        self.__value = value
    
    def check(self):
        user_check = user.objects.filter(name = self.__value,active__lt=9999)
        rs = 0 if len(user_check) == 0 else 1
        return rs
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        