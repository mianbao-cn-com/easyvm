#-*- coding:utf-8 -*-

'''
@Created on 2016年5月10日
 
@author: MianBao

@author_web: Mianbao.cn.com

@ The User Class
'''

import os
from django.conf.urls import url, include, patterns
from django.contrib import admin
from django.conf import settings
from django.conf.urls import handler404, handler500

from User.User import Login,Register
from User.User import Logout
import Mianbao


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

handler404 = Mianbao.PageNotFound

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


if settings.DEBUG is False:
    urlpatterns += patterns('',url(r'^static/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.STATICFILES_DIRS[0],}),)

[ urlpatterns.append(url(r'^%s/' % y, include(y + '.urls'))) for y in Apps ]















