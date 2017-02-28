#-*- coding:utf-8 -*-

'''
@Created on 2016年5月9日
 
@author: MianBao

@author_web: Mianbao.cn.com

@系统设置
'''

from django.conf.urls import url
from Ajax import *
from User import *

urlpatterns = [
    
    url('UpdateReset/(?P<id>\d*)/$', PasswdRest),
    url('UpdatePwd/$', PasswdUpdate),
    url('group/$', GroupList),
    url('MailActive/$', MailActive),
    url('group/del/(?P<id>\d*)/$', GroupDel),
    url('group/edit/(?P<id>\d*)/$', GroupEdit),
    url('del/(?P<id>\d*)/$', UserDel),
    url('edit/(?P<id>\d*)/$', UserEdit),
    url('Active/(?P<id>\d*)/(?P<username>[A-Za-z0-9]*)/(?P<rtime>[A-Za-z0-9]*)/$', Active),
    url('Ajax/(?P<value>.*)/(?P<do>[A-Za-z]*)/$', Ajax_url),
    url('$', List),
]