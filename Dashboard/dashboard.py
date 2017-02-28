#-*- coding:utf-8 -*-

'''
@Created on 2016年5月11日
 
@author: MianBao

@author_web: Mianbao.cn.com

@User
'''
from Mianbao.public import public
from django.http.response import HttpResponse
from django.shortcuts import render_to_response,redirect

'''
@test
'''
from User.models import *



def index(request):
    ret = public(request,'Dashboard-index','仪表盘','首页')
    return render_to_response('dashboard/index.html',ret)










