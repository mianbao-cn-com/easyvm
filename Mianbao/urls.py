#-*- coding:utf-8 -*-

'''
@Created on 2016年5月10日
 
@author: MianBao

@author_web: Mianbao.cn.com

@ The User Class
'''

import os
from django.conf.urls import url, include
from django.contrib import admin
from User.User import Login,Register
from User.User import Logout

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


path_app = os.listdir(BASE_DIR)
Apps = list()
white_list = [u'Mianbao',u'static',u'template']
path_app = list(set(path_app)-(set(white_list)))
[Apps.append(x) for x in path_app if u'.' not in x ]


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/', Login),
    url(r'^register/', Register),
    url(r'^logout/', Logout),
]

[ urlpatterns.append(url(r'^%s/' % y, include(y + '.urls'))) for y in Apps ]















