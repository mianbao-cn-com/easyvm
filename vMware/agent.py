#-*- coding:utf-8 -*-

'''
@Created on 2016年5月20日
 
@author: MianBao

@author_web: Mianbao.cn.com

@Agent用于开通虚拟机
'''

from models import *
from manage import OrderInfoGenerate,VM_Create
from connect import con
from django.db.models import Q



def CreateVM():
    try:
        order_rs = order.objects.filter(status=3)
        order_wait = order.objects.filter(status=4)
        order_run = order.objects.filter(status=5)
        order_fen = order.objects.filter(status=7)
        if order_run.count() == 0 and order_fen.count() == 0 and order_wait.count() == 0:
            if order_rs.count() > 0:
                for x in order_rs:
                    change = order_flow.objects.filter(id=x.id,key='change').count()
                    if x.resource.type == 0 or change == 1:
                        order.objects.filter(id=x.id).update(status=7)
                        CreateProgram(x.id)
                    else:
                        order.objects.filter(id=x.id).update(status=7)
                        orders = OrderInfoGenerate(x.id)
                        orders.Generate()
                        order.objects.filter(id=x.id).update(status=2)
    except Exception,e:
        pass

def CreateProgram(id):
    try:
        orders = OrderInfoGenerate(id)
        orders.Generate()
        
        error_list = ['Custome','Name','get_vm']
        check_error = order_error.objects.filter(order__id = id,status=0,try_num__lte=10,key__in=error_list)
        check_error_try_num = order_error.objects.filter(order__id = id,status=0,try_num__gte=10,key__in=error_list).count()
        rs = order.objects.get(id=id)
        vc = con(int(rs.resource.node.conn.id),id)
        server = vc.StartConnect()
        if server != 1:
            if check_error.count() + check_error_try_num == 0:
                orders = VM_Create(id,server)
                orders.Create()
                server.disconnect()
            elif check_error.count() > 0:
                for x in check_error:
                    try_re = TryRebuilding(id,server)
                    rs = getattr(try_re,x.key)
                    rs = rs()
    except Exception,e:
        rs.status = 3
        rs.save()

                                
class TryRebuilding():
    
    def __init__(self,id,server):
        self.__id = id
        self.__server = server
        self.__order = OrderInfoGenerate(id)
        
    def Custome(self):
        self.__order.CustomizationType()
    
    def Name(self):
        self.__order.SaveName()

            
            