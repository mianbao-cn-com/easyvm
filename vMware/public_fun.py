#-*- coding:utf-8 -*-

'''
@Created on 2016年5月30日
 
@author: MianBao

@author_web: Mianbao.cn.com

@系统设置
'''
from models import *
from User.models import user
import time
from Mianbao.public import DateConvertStamp, sendmail,unit_convert
from User.User_Class import User


'''
@about vmware jump html
'''  

def vMwareNodeAndDataSetError(ret):
    ret['message_url'] = '/vMware/manage/'
    ret['status'] = 'error'
    ret['message_title'] = '设置失败'
    ret['message_content'] = '由于未知原因您此次设置已失败，请确认后再次尝试！'
    return ret

def vMwareNodeDvsUpdateError(ret):
    ret['message_url'] = '/vMware/network/'
    ret['status'] = 'error'
    ret['message_title'] = '设置失败'
    ret['message_content'] = '由于未知原因您此次设置已失败，请确认后再次尝试！'
    return ret

def vMwareNodeDvsDelRight(ret):
    ret['message_url'] = '/vMware/network/'
    ret['status'] = 'right'
    ret['message_title'] = '删除成功'
    ret['message_content'] = '虚拟交换机已成功删除！'
    return ret

def vMwareNodeDvsDelError(ret):
    ret['message_url'] = '/vMware/network/'
    ret['status'] = 'error'
    ret['message_title'] = '虚拟交换机删除失败'
    ret['message_content'] = '由于未知原因您此次设置已失败，请确认后再次尝试！'
    return ret

def vMwareIpPoolCreateError(ret):
    ret['message_url'] = '/vMware/ippool/'
    ret['status'] = 'error'
    ret['message_title'] = '新增失败'
    ret['message_content'] = '由于未知原因您此次设置已失败，请确认后再次尝试！'
    return ret

def vMwareIpPoolDelRight(ret):
    ret['message_url'] = '/vMware/ippool/'
    ret['status'] = 'right'
    ret['message_title'] = '删除成功！'
    ret['message_content'] = 'IP资源池删除成功！'
    return ret

def vMwareIpPoolDelError(ret):
    ret['message_url'] = '/vMware/ippool/'
    ret['status'] = 'error'
    ret['message_title'] = '删除失败'
    ret['message_content'] = '由于未知原因您此次设置已失败，请确认后再次尝试！'
    return ret

def vMwareOrderAddRight(ret):
    ret['message_url'] = '/vMware/apply/'
    ret['status'] = 'right'
    ret['message_title'] = '添加成功！'
    ret['message_content'] = '您的订单已成功提交，请至任务进度处查看任务进展详情！'
    return ret

def vMwareOrderAddError(ret):
    ret['message_url'] = '/vMware/ippool/'
    ret['status'] = 'error'
    ret['message_title'] = '删除失败'
    ret['message_content'] = '由于未知原因您此次设置已失败，请确认后再次尝试！'
    return ret

def vMwareOrderInfoError(ret):
    ret['message_url'] = '/vMware/ippool/'
    ret['status'] = 'error'
    ret['message_title'] = '失败!'
    ret['message_content'] = '此订单的虚拟机开通信息已生成，不能再次生成！'
    return ret

def vMwareOrderSendMailError(ret):
    ret['message_url'] = '/vMware/manage/'
    ret['status'] = 'error'
    ret['message_title'] = '失败!'
    ret['message_content'] = '通知邮件发送失败！'
    return ret

def vMwareOrderStatusError(ret):
    ret['message_url'] = '/vMware/manage/'
    ret['status'] = 'error'
    ret['message_title'] = '失败!'
    ret['message_content'] = '邮件状态禁止交付！'
    return ret

'''
@about vmware public
'''
def CheckMysqlRsNum(rs):
    rss = ['0','0']
    return rss if len(rs) == 0 else rs
        
def OrderFlowSave(dic):
    if isinstance(dic,dict):
        flow_check = order_flow.objects.filter(key=dic['key'],order=dic['order']).count()
        if flow_check == 0: 
            if dic.get('uid',None):
                dic['uid'] = user.objects.get(id=dic['uid'])
            dic['order'] = order.objects.get(id=dic['order'])
            dic['time'] = time.time()
            if dic.get('ippool',None):
                dic['ippool'] = ippool.objects.get(id=dic.get('ippool'))
            order_flow(**dic).save()

'''
@about Order Regect
'''
def Regect0(reject,form_value,uid):
    save_reject_rs = order_remark(**form_value).save()
    users = User(uid)
    new  = dict()
    new['order'] = reject
    new['key'] = 'reject'
    new['rs'] = 0
    new['remark'] = save_reject_rs
    new['uid'] = users.GetUser()
    new['time'] = time.time()
    order_flow(**new).save()
    reject.status = 200
    reject.save()
    mail_object = u"【通知】虚拟申请被驳回"
    html_dict = {'title':u'驳回通知',
                 'content':u'驳回原因：%s <br><br><br><br>**订单详情： &nbsp;&nbsp;%s(单号)&nbsp;&nbsp; %s **<br>' % (form_value.get('remark',None),reject.id,reject.project)}
    rs = sendmail([reject.uid.mail],mail_object,html_dict)
    return True

def Regect1(reject,id):
    resource_reject = order_resource.objects.filter(order=reject)
    for x,y in resource_reject:
        if x == 'name':
            new = dict()
            new['prefix'] = 0
            new['suffix'] = 0
            new['pointer'] = 0
            new['recover'] = y
            vm_name.create(**new).save()
    return True

def ReportError(order_id,item,detail,key):
        error = {'order':order_id}
        error['time'] = time.time()
        error['item'] = item
        error['detail'] = detail
        error['key'] = key
        error['status'] = 0
        order_error(**error).save()














