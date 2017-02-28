#-*- coding:utf-8 -*-

'''
@Created on 2016年5月9日
 
@author: MianBao

@author_web: Mianbao.cn.com

@系统设置
'''
import json
from models import *
from django.shortcuts import HttpResponse
from Mianbao.public import unit_convert



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
    
    def nodedata(self):
        rs = node_disk.objects.filter(node__id=self.__value).values_list('id','name','free')
        return list(rs)
    
    def templateinfo(self):
        rs = vms.objects.filter(id=self.__value).values_list('Core','memory','systemversion')[0]
        rs = list(rs)
        rs_disk = disk.objects.filter(vms__id=self.__value,status=0).values_list('total')
        disk_list = ''
        for x in range(len(rs_disk)):
            disk_list += 'disk%s Total:%s' % (x,unit_convert(rs_disk[x][0]*1024))
        
        rs_net = network.objects.filter(vms__id=self.__value,status=0).count()
        
        rs.insert(2,disk_list)
        rs.insert(3,rs_net)
        return rs
    
    def vcnode(self):
        rs = node.objects.filter(conn__id = self.__value).values_list('id','name')
        return list(rs)
    
    
    
    
    
    
    
    