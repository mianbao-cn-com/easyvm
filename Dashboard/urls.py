#-*- coding:utf-8 -*-

'''
@Created on 2016年5月11日
 
@author: MianBao

@author_web: Mianbao.cn.com

@系统设置
'''

from django.conf.urls import url

from .dashboard import *

urlpatterns = [
    url('$', index),
    #url('del/$', User_del),
    #url('add/$', User_del),
]