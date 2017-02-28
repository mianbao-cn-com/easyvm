#-*- coding:utf-8 -*-
'''
@Created on 2016年5月20日
 
@author: MianBao

@author_web: Mianbao.cn.com

@系统设置
'''
from models import *
from public_fun import ReportError
from pysphere import VIServer



class con:
    
    def __init__(self,id=None,order_id=None):
        self.__vcid = id
        self.__order_id = order_id
        self.server = None
    
    def GetVcenterInfo(self):
        if self.__vcid:
            vc_info = vcenter.objects.get(id=self.__vcid)
            vc_info = vc_info.__dict__
            if vc_info['status'] == 0:
                del vc_info['id']
                del vc_info['status']
                del vc_info['_state']
                del vc_info['alias']
                return vc_info
            else:
                self.VCErrorReport('此VC已被禁用！')
                return 1
        
    def StartConnect(self):
        vc_info = self.GetVcenterInfo()
        if vc_info != 1:
            Server = VIServer()
            try:
                Server.connect(**vc_info)
                self.server = Server
            except Exception,e:
                self.VCErrorReport(e.message)
            return Server if Server.is_connected() else  1
    
    def Discon(self):
        self.server.disconnect()
    
    def VCErrorReport(self,mes):
        item = 'VC连接失败'
        detail = mes
        key = 'VC'
        ReportError(self.__order_id,item,detail,key)
        
   
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        