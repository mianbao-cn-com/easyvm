#-*- coding:utf-8 -*-

'''
@Created on 2016年5月20日
 
@author: MianBao

@author_web: Mianbao.cn.com

@系统设置
'''

from django.shortcuts import render_to_response,redirect


def PageNotFound(request):
    return redirect('/login/')