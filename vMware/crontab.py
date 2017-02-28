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

from django.db import transaction


 
def Vms_check():
    try:
        vc_id_list = vcenter.objects.filter(status=0).values('id')
        for vc_dict in vc_id_list:
            for vc_id in vc_dict.values():
                vc = con(int(vc_id))
                server = vc.StartConnect()
                if not isinstance(server,int):
                    GetVmsInfo(server,vc_id)
                    vc.Discon()
                '''
                else:
                    mail_title = u'VC连接出错 %s ' % vc_id
                    mail_dict = {'title':u'VC连接出错'}
                    mail_dict['content'] = u'可能是由于不能连通VC导致的！'
                    CrontabErrorMailSend(mail_title,mail_dict)
                '''
    except Exception,e:
        mail_title = u'【vmware crontab】定时任务执行出错'
        mail_dict = {'title':u'VMware 定时任务执行错误'}
        mail_dict['content'] = u'错误信息如下：%s' % e.message
        CrontabErrorMailSend(mail_title,mail_dict)
     
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
                '''
                else:
                    mail_title = u'VC连接出错'
                    mail_dict = {'title':u'VC连接出错'}
                    mail_dict['content'] = u'可能是由于不能连通VC导致的！'
                    CrontabErrorMailSend(mail_title,mail_dict)
                '''
    except Exception,e:
        mail_title = u'【vmware crontab】定时任务执行出错'
        mail_dict = {'title':u'VMware 定时任务执行错误'}
        mail_dict['content'] = u'错误信息如下：%s' % e.message
        CrontabErrorMailSend(mail_title,mail_dict)
                  
def GetVmsInfo(server,vc_id):
    try:
        vms = api(server)
        vms.GetVmsFromApi()
        all_vms = vms.PropsConvertDict()
        for x in all_vms:
            handle_vms = DATA_PROCESS(x,vc_id)
            handle_vms.MainCycle()
    except Exception,e:
        mail_title = u'【VM agent 错误】VMware agent 抓取错误'
        mail_dict = {'title':u'VMware agent 抓取错误'}
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
    sendmail(['huifei.han' + str(systems.GetMailAdd())],mail_title,mail_dict)        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
                