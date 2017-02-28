#-*- coding:utf-8 -*-

'''
@Created on 2016年5月11日
 
@author: MianBao

@author_web: Mianbao.cn.com

@ The User Class
'''
from django import template
from django.template.base import resolve_variable, Node, TemplateSyntaxError
from User.models import *
import time
from vMware.models import vcenter, node_network, node,disk,network,\
    order_resource,run
from Mianbao.public import unit_convert
from application.models import cluster,project,asset


register = template.Library()


'''
@about css
'''
@register.simple_tag
def return_class(v1,v2):
    list = str(v1).split('-')
    if str(v2) in list:
        return 'active'

'''
@time convert
'''
@register.simple_tag
def second_convert(str):
    try:
        float_time = float(str)
        time_fomat = '%Y-%m-%d %H:%M:%S'
        rs = time.strftime(time_fomat,time.localtime(float_time))
        return rs
    except Exception,e:
        return 'paramater must is a float'

@register.simple_tag
def minute_convert(str):
    try:
        float_time = float(str)
        time_fomat = '%Y-%m-%d %H:%M'
        rs = time.strftime(time_fomat,time.localtime(float_time))
        return rs
    except Exception,e:
        return 'paramater must is a float'
    
@register.simple_tag
def date_convert(str):
    try:
        float_time = float(str)
        time_fomat = '%Y-%m-%d'
        rs = time.strftime(time_fomat,time.localtime(float_time))
        return rs
    except Exception,e:
        return 'paramater must is a float'
    
@register.simple_tag
def month_convert(str):
    try:
        float_time = float(str)
        time_fomat = '%Y-%m'
        rs = time.strftime(time_fomat,time.localtime(float_time))
        return rs
    except Exception,e:
        return 'paramater must is a float'


'''
@about User info Get
'''
@register.simple_tag
def GetUserDepartment(uid):
    rs = user.objects.get(id=uid).user_department.all()
    return rs[0].name

@register.simple_tag
def GetUserGroup(uid):
    rs = user.objects.get(id=uid).user_group.all()
    return rs[0].name


'''
@about Group
'''
@register.simple_tag
def GetGroupUser(uid):
    rs = user.objects.filter(active__lt = 9999 ,user_group = uid).count()
    return rs


'''
@about vMware
'''
@register.simple_tag
def Converttypes(num):
    convert = ['标准交换机','分布式交换机','未知类型的虚拟交换机']
    try:
        num = int(num)
    except Exception,e:
        num = 2
    return convert[num]

@register.simple_tag
def GetvCenter(num):
    try:
        vc = vcenter.objects.get(id=num).host
        return vc
    except Exception,e:
        return '未知的VC'

@register.simple_tag
def GetNode(id):
    try:
        vc = node.objects.filter(id=id)
        return vc[0].name
    except Exception,e:
        return '未知的VC'

@register.simple_tag
def Stringlowtoup(str):
    return str.upper()

@register.simple_tag
def GetTemplateFromId(id):
    rs_disk = disk.objects.filter(vms__id=id,status=0).values_list('total')
    disk_list = ''
    for x in range(len(rs_disk)):
        disk_list += '%s' % (unit_convert(rs_disk[x][0]*1024))
        disk_list += '/' if x < len(rs_disk) - 1 else ''
    return disk_list

@register.simple_tag
def GetNetworkFromId(id):
    rs_net = network.objects.filter(vms__id=id,status=0).count()
    return rs_net

@register.simple_tag
def Resourcestatus(id):
    id_status = ['自动开通','手动开通']
    return id_status[id]

@register.simple_tag
def OrderStatus(id):
    id_status = {0:'待审核',1:'待开通',3:'生成配置',4:'排队中',5:'开通中',7:'生成配置',6:'待交付',2:'配置完成',100:'已完成',200:'已驳回'}
    return id_status.get(id,'异常状态')

@register.simple_tag
def OrderSchedule(id):
    id_status = ['','','',20,35,60,20,35,60,20,35,60]
    return id_status[id]

@register.simple_tag
def FromOrderGetName(id):
    print id
    resources = order_resource.objects.filter(order__id=id)
    print resources.count()
    #name = list()
    name = [ x.val for x in resources if x.key == 'name' ]
    print name
    return ','.join(name)

@register.simple_tag
def FromOrderGet(id,str):
    resources = order_resource.objects.filter(order__id=id)
    name = [ x.val for x in resources if x.key == str ]
    print name
    return ','.join(name)
     
@register.simple_tag
def UnitConvert(v1,start):
    v1 = int(v1)
    li = ['bytes','Kb','M','G','T','P']
    a = start
    while v1 > 1024:
        v1 = v1/1024
        a += 1
    return str(v1)+str(li[a])

'''
@about vms
'''
@register.simple_tag
def FromVmGetIP(id):
    vm_ip = network.objects.filter(vms__id=id).order_by('-id')
    ip = vm_ip[0].ip if vm_ip.count() > 0 else '未配置IP'
    return ip

@register.simple_tag
def FromVmGetStatus(id):
    vm_run = run.objects.filter(vms__id=id).order_by('-id')
    ip = vm_run[0].power if vm_run.count() > 0 else '未配置IP'
    return ip
    

'''
@about select
'''
@register.simple_tag
def CheckSelect(id1,id2):
    return 'selected'if int(id1) == int(id2) else ''
        
'''
@about data input convert
'''
@register.simple_tag
def InputDataConvert(str):
    try:
        float_time = float(str)
        time_fomat = '%m/%d/%Y'
        rs = time.strftime(time_fomat,time.localtime(float_time))
        return rs
    except Exception,e:
        return 'paramater must is a float'

'''
@about content
'''
@register.simple_tag
def CheckContent(str):
    if len(str) == 0:
        return '暂无'
    else:
        return str

'''
@about asset Project
'''
@register.simple_tag
def FromIdGetHostNum(id):
    if id:
        cluster_num = cluster.objects.filter(toproject=id).count()
        return cluster_num
    else:
        return 'Null'

@register.simple_tag
def GetProjectHostNum(id):
    num = 0
    if id:
        clusters = cluster.objects.filter(toproject=id)
        for x in clusters:
            asset_num = asset.objects.filter(cluster__id=x.id).count()
            num += asset_num
    return num

@register.simple_tag
def GetClusterHostNum(id):
    if id:
        host_num = asset.objects.filter(cluster__id=id).count()
        return host_num
    else:
        return 'Null'

@register.simple_tag
def ReturnSpanClass(str):
    class_dict = {u'测试':'label-success',u'仿真':'label-warning',u'生产':'label-danger'}
    if class_dict.has_key(str):
        return class_dict.get(str)
    else:
        return 'Null'














