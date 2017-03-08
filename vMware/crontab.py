#-*- coding:utf-8 -*-

'''
@Created on 2016年5月20日
 
@author: MianBao

@author_web: Mianbao.cn.com

@系统设置
'''
import json
import traceback
from connect import *
from getapi import *
from getvms import DATA_PROCESS
from getvms import DATA_PROCESS,GETNODE
from Public.publiclog import logs
from Mianbao.websettings import websetting
from django.db import transaction
from public_fun import VcErrorReoprt,VcStatusUpdate

''' 
def Vms_check():
    vc_id_list = vcenter.objects.filter(status=0).values('id')
    for vc_dict in vc_id_list:
        for vc_id in vc_dict.values():
            vc = con(int(vc_id))
            server = vc.StartConnect()
            if not isinstance(server,int):
                GetVmsInfo(server,vc_id)
                vc.Discon()

def GetVmsInfo(server,vc_id):
    vms = api(server)
    vms.GetVmsFromApi()
    all_vms = vms.PropsConvertDict()
    for x in all_vms:
        handle_vms = DATA_PROCESS(x,vc_id)
        handle_vms.MainCycle()
'''
def Vms_check():
    error_vcid = ''
    try:
        vc_id_list = vcenter.objects.filter(status=0).values('id')
        for vc_dict in vc_id_list:
            for vc_id in vc_dict.values():
                error_vcid = vc_id
                vc = con(int(vc_id))
                server = vc.StartConnect()
                if not isinstance(server,int):
                    GetVmsInfo(server,vc_id)
                    vc.Discon()
                    VcStatusUpdate(error_vcid)
                else:
                    VcErrorReoprt(vc_id,'VC连接错误','与VC的连接失败，请检查网络')
    except Exception,e:
        VcErrorReoprt(error_vcid,'错误',e.message)
        


def GetVmsInfo(server,vc_id):
    try:
        vms = api(server)
        vms.GetVmsFromApi()
        all_vms = vms.PropsConvertDict()
        for x in all_vms:
            handle_vms = DATA_PROCESS(x,vc_id)
            handle_vms.MainCycle()
    except Exception:
        pass
    
def Network_check():
    try:
        vc_id_list = vcenter.objects.filter(status=0).values('id')
        for vc_dict in vc_id_list:
            for vc_id in vc_dict.values():
                vc = con(int(vc_id))
                server = vc.StartConnect()
                if not isinstance(server,int):
                    GetNetworkInfo(server,vc_id)
                    vc.Discon()
    except Exception,e:
        mail_title = u'【vmware crontab】定时任务执行出错'
        mail_dict = {'title':u'VMware 定时任务执行错误'}
        mail_dict['content'] = u'错误信息如下：%s' % e.message
        CrontabErrorMailSend(mail_title,mail_dict)
                  
      
                           
def GetNetworkInfo(server,vc_id):   
    try:
        nodes = GETNODE(server,int(vc_id))
        nodes.MainCycle()
    except Exception,e:
        mail_title = u'【VM Network agent 错误】抓取错误'
        mail_dict = {'title':u'VMware 网络抓取错误'}
        mail_dict['content'] = u'错误信息如下：%s' % e.message
        CrontabErrorMailSend(mail_title,mail_dict)
           
def CrontabErrorMailSend(mail_title,mail_dict):
    system = websetting()
    pass
    #sendmail(['huifei.han' + str(system.GetMailAdd())],mail_title,mail_dict)  
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
                