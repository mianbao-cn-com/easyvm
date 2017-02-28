#-*- coding:utf-8 -*-

'''
@Created on 2017年1月12日
 
@author: MianBao

@author_web: Mianbao.cn.com

@公共参数设置
'''

from vMware.models import message



def GetSendMail(str):
    mess = message.objects.filter(key=str)
    if mess.count() == 1 and len(mess[0].val) != 0:
        mess_list = mess[0].val.split(',')
        return mess_list
    else:
        return list()
#['order_apply','order_pay','wechat_secret','wechat_id','wechat_corp']    
def GetWechatSecret():
    mess = message.objects.filter(key='wechat_secret')
    if mess.count() == 1:
        return mess[0].val
    else:
        return None
    
def GetWechatID():
    mess = message.objects.filter(key='wechat_id')
    if mess.count() == 1:
        return mess[0].val
    else:
        return None

def GetWechatCorp():
    mess = message.objects.filter(key='wechat_corp')
    if mess.count() == 1:
        return mess[0].val
    else:
        return None




