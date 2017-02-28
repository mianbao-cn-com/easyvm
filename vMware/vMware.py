#-*- coding:utf-8 -*-

'''
@Created on 2016年5月20日
 
@author: MianBao

@author_web: Mianbao.cn.com

@系统设置
'''
from django.db import transaction
from django.db.models import Avg, Max, Min, Count,Sum

from connect import *
from getapi import *
from getvms import DATA_PROCESS,GETNODE
from django.http.response import HttpResponse
from Mianbao.public import public,GetFormPost,CheckPermission,cper,GenerateAtoZ
from manage import MANAGE,OrderInfoGenerate,VM_Create
from public_fun import *
from django.db import connection
from crontab import GetVmsInfo,GetNetworkInfo,CrontabErrorMailSend,Network_check
from Public.wechat import send_msg
from pysphere.vi_property import VIProperty
from Public.public import GetWechatSecret,GetWechatID,GetWechatCorp

from agent import CreateVM


'''
@vmware manager
'''
def vmware_test(request):
    print 'start....'
    #Network_check()
    print 'end.....'
    CreateVM()
    return HttpResponse('OK123')
    '''
    
    vc_id_list = vcenter.objects.filter(status=0).values('id')
    for vc_dict in vc_id_list:
        for vc_id in vc_dict.values():
            vc = con(int(vc_id))
            server = vc.StartConnect()
            if not isinstance(server,int):
                GetVmsInfo(server,vc_id)
                vc.Discon()
            else:
                mail_title = u'VC连接出错'
                mail_dict = {'title':u'VC连接出错'}
                mail_dict['content'] = u'可能是由于不能连通VC导致的！'
                CrontabErrorMailSend(mail_title,mail_dict)
    
    return HttpResponse('OK123')
    '''
    '''
    vc_id_list = vcenter.objects.filter(status=0).values('id')
    for vc_dict in vc_id_list:
        for vc_id in vc_dict.values():
            vc = con(int(vc_id))
            server = vc.StartConnect()
            vms = api(server)
            vms.GetVmsFromApi()
            all_vms = vms.PropsConvertDict()
            for x in all_vms:
                print x
                handle_vms = DATA_PROCESS(x,vc_id)
                handle_vms.MainCycle()
    
    
    return HttpResponse('OK123')
    '''
'''
def Manage(request):
    ret = public(request,'vmware-manage','虚拟化','管理')
    ret['bodycss'] = 'sidebar-collapse'
    ret['nodes'] = node.objects.filter()
    if request.method == 'POST':
        form_key = ['node','datastore']
        form_value = GetFormPost(request,form_key)
        vmware = MANAGE()
        nodes_rs = vmware.AssignNode(form_value.get('node'))
        data_rs = vmware.AssignData(form_value.get('datastore'))
        if not (nodes_rs and data_rs):
            vMwareNodeAndDataSetError(ret)
            return render_to_response('public/message.html',ret)
        else:
            return redirect('/vMware/manage/')
    else:
        node_rs = node.objects.filter(assign=1)
        ret['node'] = CheckMysqlRsNum(node_rs)[0]
        node_disk_rs = node_disk.objects.filter(assign=1)
        ret['data'] = CheckMysqlRsNum(node_disk_rs)[0]
        ret['orders'] = order.objects.filter(status__lt=10)
        return render_to_response('vmware/manage/virtual_manage.html',ret)
'''

def Manage(request):
    ret = public(request,'vmware-manage','虚拟化','管理')
    ret['bodycss'] = 'sidebar-collapse'
    ret['resources'] = resource.objects.filter().count()
    ret['orders'] = order.objects.filter(status__lt=9)
    ret['wait_start'] = order.objects.filter(status__lt=9).values('num').aggregate(Sum('num')).get('num__sum',0)
    ret['over'] = order.objects.filter(status=100).values('num').aggregate(Sum('num')).get('num__sum',0)
    ret['type'] = vmtype.objects.filter(status__lt=100).count()
    ret['ippools'] = ippool.objects.all()
    return render_to_response('vmware/manage/virtual_manage.html',ret)
    
def Network(request):
    ret = public(request,'vmware-manage','网络','设置')
    node_list = node_network.objects.filter().values('name','vswitch','vlan','type','conn','times')
    node_list.query.group_by = ['name','vswitch','conn']
    ret['node_networks'] = node_list
    ret['nowtime'] = time.time() - 650
    return render_to_response('vmware/manage/network_list.html',ret)

def NetworkEdit(request,id,dvs_name):
    ret = public(request,'vmware-manage','分布式网络','编辑')
    if request.method == 'POST':
        form_key = ['name','vlan','vc']
        form_value = GetFormPost(request,form_key)
        network_vlan = MANAGE()
        rs = network_vlan.UpdateDvsVlan(form_value)
        if not rs:
            vMwareNodeDvsUpdateError(ret)
            return render_to_response('public/message.html',ret)
        else:
            return redirect('/vMware/network/')
    else:
        networks = node_network.objects.filter(conn=id,name=dvs_name)
        ret['network'] = networks.first()
        networks.query.group_by = ['name']
        ret['hosts'] = networks
        return render_to_response('vmware/manage/network_edit.html',ret)

def NetworkDel(request,id,dvs_name,dvs_vswitch):
    ret = public(request,'vmware-manage','分布式网络','删除')
    network = MANAGE()
    del_network = {'name':dvs_name,'vswitch':dvs_vswitch}
    del_network['conn'] = network.GetVCFromId(id)
    rs = network.DelDvs(del_network)
    vMwareNodeDvsDelRight(ret) if rs else vMwareNodeDvsDelError(ret)
    return render_to_response('public/message.html',ret)

def IPPool(request):
    ret = public(request,'vmware-manage','IP地址池','管理')
    ret['bodycss'] = 'sidebar-collapse'
    if request.method == 'POST':
        form_key = ['pooladd','netmask','gateway','dns1','dns2','vlan','alia','remark']
        form_value = GetFormPost(request,form_key)
        ip_pool = MANAGE()
        rs = ip_pool.IpPoolCreate(form_value)
        if not rs:
            vMwareIpPoolCreateError(ret)
            return render_to_response('public/message.html',ret)
        else:
            return redirect('/vMware/ippool/')
    else:
        ret['ippools'] = ippool.objects.filter()
        return render_to_response('vmware/manage/ip_pool.html',ret)

def IPPoolDatial(request,id):
    ret = public(request,'vmware-manage','IP地址池','管理')
    ret['pools'] = ippool.objects.get(id=id)
    return render_to_response('vmware/manage/pool_detial.html',ret)

def IPPoolEdit(request,id):
    ret = public(request,'vmware-manage','IP地址池','管理')
    if request.method == 'POST':
        form_key = ['pooladd','netmask','gateway','dns1','dns2','vlan','alia','remark']
        form_value = GetFormPost(request,form_key)
        ip_pool = MANAGE()
        rs = ip_pool.IpPoolCreate(form_value,id=id)
        if not rs:
            vMwareIpPoolCreateError(ret)
            return render_to_response('public/message.html',ret)
        else:
            return redirect('/vMware/ippool/')
    else:
        ret['pools'] = ippool.objects.get(id=id)
    return render_to_response('vmware/manage/pool_edit.html',ret)
    
def IPPoolDel(request,id):
    ret = public(request,'vmware-manage','IP地址池','管理')
    rs = ippool.objects.filter(id=id).delete()
    vMwareIpPoolDelRight(ret) if rs else vMwareIpPoolDelError(ret)
    return render_to_response('public/message.html',ret)
    
def Custom(request):
    ret = public(request,'vmware-manage','虚拟机命名规则','列表')
    ret['names'] = vm_name.objects.filter(recover=0)
    return render_to_response('vmware/manage/custome.html',ret)

def CustomAdd(request):
    ret = public(request,'vmware-manage','虚拟机命名规则','新增')
    if request.method == 'POST':
        form_key = ['prefix','suffix','pointer','vc',]
        form_value = GetFormPost(request,form_key)
        cust_name = MANAGE()
        rs = cust_name.SaveName(form_value)
        if not rs:
            ret['message_url'] = '/vMware/customization/'
            ret['status'] = 'error'
            ret['message_title'] = '新增失败'
            ret['message_content'] = '每个VC下面只能有一个命名规则，而此VC下已有命名规则！'
        return render_to_response('public/message.html',ret)
    else:
        ret['vcs'] = vcenter.objects.filter(status=0).values('id','host','alias')
        return render_to_response('vmware/manage/custome_add.html',ret)

def CustomEdit(request,id):
    ret = public(request,'vmware-manage','虚拟机命名规则','新增')
    if request.method == 'POST':
        form_key = ['prefix','suffix','pointer']
        form_value = GetFormPost(request,form_key)
        vm_name.objects.filter(id=id).update(**form_value)
        return redirect('/vMware/customization/')
    else:
        ret['vcs'] = vcenter.objects.filter(status=0).values('id','host','alias')
        ret['name'] = vm_name.objects.get(id=id)
        return render_to_response('vmware/manage/custome_edit.html',ret)

def CustomDel(request,id):
    ret = public(request,'vmware-manage','虚拟机命名规则','删除')
    vm_name.objects.get(id=id).delete()
    return redirect('/vMware/customization/')
        
def VMTypes(request):
    ret = public(request,'vmware-manage','虚拟机类型','列表')
    ret['types'] = vmtype.objects.filter(status__lt=100)
    return render_to_response('vmware/manage/virtual_type.html',ret)

def VMTypesAdd(request):
    ret = public(request,'vmware-manage','虚拟机类型','新增')
    if request.method == 'POST':
        form_key = ['type_name','template','application','remark']
        form_value = GetFormPost(request,form_key)
        typesadd = MANAGE()
        typesadd.VmTypesAdd(form_value)
        return redirect('/vMware/virtual_type/')
    else:
        exclude_abc = vmtype.objects.filter(status=0).values_list().values('type_name')
        abc = list()
        for x in exclude_abc:
            abc.append(x.get('type_name'))
        ret['abc'] = GenerateAtoZ(abc)
        ret['templates'] = vms.objects.filter(type=1,status=0).values('id','name','vc')
        print ret['templates'].query
        return render_to_response('vmware/manage/virtual_type_add.html',ret)
    
def VMTypesDel(request,id):
    ret = public(request,'vmware-manage','虚拟机类型','删除')
    try:
        vmtype.objects.filter(id=id).update(status=100)
    except Exception,e:
        pass
    return redirect('/vMware/virtual_type/')

def VMTypesDisable(request,id):
    ret = public(request,'vmware-manage','虚拟机类型','禁用')
    vmtype.objects.filter(id=id).update(status=2)
    return redirect('/vMware/virtual_type/')

def VMTypesEnable(request,id):
    ret = public(request,'vmware-manage','虚拟机类型','启用')
    vmtype.objects.filter(id=id).update(status=0)
    return redirect('/vMware/virtual_type/')

def OrderDetail(request,id):
    ret = public(request,'vmware-detail','订单','详情')
    ret['bodycss'] = 'sidebar-collapse'
    ret['order'] = order.objects.get(id=id)
    ret['info'] = order_resource.objects.filter(order__id=id)
    ret['flow'] = order_resource.objects.filter(order__id=id)
    ret['errors'] = order_error.objects.filter(order__id=id,status=0)
    return render_to_response('vmware/manage/order_detail.html',ret)

def OrderPay(request,id):
    ret = public(request,'apply-apply','订单','交付')
    pay_order = order.objects.get(id=id)
    if pay_order.status == 6 or pay_order.status == 2:
        pay_order.status = 8
        pay_order.save()
        orders = MANAGE()
        try:
            rs = orders.OrderPaySendMail(id)
        except Exception,e:
            rs = 1
        if rs == 0:
            pay_order.status = 100
            pay_order.save()
            OrderFlowSave({'order':id,'key':'sendmail','rs':0,'uid':ret['uid']})
            return redirect('/vMware/manage/')
        else:
            pay_order.status = 9
            pay_order.save()
            OrderFlowSave({'order':id,'key':'sendmail','rs':1,'uid':ret['uid']})
            vMwareOrderSendMailError(ret)
            return render_to_response('public/message.html',ret)
    else:
        vMwareOrderStatusError(ret)
        return render_to_response('public/message.html',ret)

@transaction.atomic 
def OrderReject(request,id):
    ret = public(request,'apply-apply','订单','驳回')
    if request.method == 'POST':
        form_key = ['remark']
        form_value = GetFormPost(request,form_key)
        print form_value
        reject_order = order.objects.get(id=id)
        status = reject_order.status
        if status in [0,1]:
            rs = Regect0(reject_order,form_value,ret['uid'])
    return redirect('/vMware/manage/')
    
    
  
'''
@虚拟机申请部分
'''
def VMApply(request):
    ret = public(request,'apply-apply','虚拟机','申请')
    ret['type'] = vmtype.objects.filter(status=0)
    ret['bulletins'] = bulletin.objects.filter(status=0,endtime__gt=time.time(),site__id__in=[1,3])
    return render_to_response('vmware/new_virtual.html',ret)

def VMApplyOrder(request,types):
    ret = public(request,'apply-apply','虚拟机','申请')
    if request.method == 'POST':
        form_key = ['num','resource','project','endtime','template']
        form_value = GetFormPost(request,form_key)
        form_value['uid'] = ret['uid']
        order = MANAGE()
        rs = order.Save(form_value)
        vMwareOrderAddRight(ret) if rs else vMwareOrderAddError(ret)
        return render_to_response('public/message.html',ret)
    else:
        ret['num'] = range(1,10)
        ret['x'] = vmtype.objects.get(type_name=types,status=0)
        vmtypes = vmtype.objects.get(type_name=types,status=0)
        template_name = vmtypes.template.name
        vms_vc = vms.objects.filter(name=template_name,status=0).values_list('vc')
        vc_list = list()
        [ vc_list.append(int(x[0])) for x in vms_vc if len(x) > 0 ]
        ret['resoruce'] = resource.objects.filter(vc__id__in = vc_list).values('name','id','status')
        return render_to_response('vmware/order.html',ret)

@transaction.atomic 
def OrderCheck(request,id):
    ret = public(request,'apply-apply','订单','审核通过')
    if isinstance(int(id),int):
        order.objects.filter(id=id).update(status=1)
        OrderFlowSave({'order':id,'key':'check','rs':0,'uid':ret['uid']})
    return redirect('/vMware/manage/')

@transaction.atomic
def OrderOpened(request,id):
    ret = public(request,'apply-apply','订单','开通')
    if request.method == 'POST':
        form_key = ['ippools',]
        form_value = GetFormPost(request,form_key)
        order_rs = order_flow.objects.filter(order__id=id,key='opened_ippools')
        if len(order_rs) == 0:
            order.objects.filter(id=id).update(status=3)
            OrderFlowSave({'order':id,'key':'opened_ippools','rs':0,'uid':ret['uid'],'ippool':form_value.get('ippools',None)})
            return redirect('/vMware/manage/')
        else:
            vMwareOrderInfoError(ret)
            return render_to_response('public/message.html',ret)

def OrderOver(request):
    ret = public(request,'apply-apply','订单','已完成订单')
    ret['bodycss'] = 'sidebar-collapse'
    ret['over'] = order.objects.filter(status=100)
    return render_to_response('vmware/manage/order_over.html',ret)
    
'''
@资源池设置部分
'''
def Resource(request):
    ret = public(request,'vmware-manage','资源位置','列表')
    if request.method == 'POST':
        form_key = ['name','vc','type','node','data']
        form_value = GetFormPost(request,form_key)
        typesadd = MANAGE()
        typesadd.ResourceAdd(form_value)
        return redirect('/vMware/resource/')
    else:
        ret['resources'] = resource.objects.filter()
        ret['vcs'] = vcenter.objects.filter().values('host','id')
        return render_to_response('vmware/manage/resource.html',ret)

def ResourceDel(request,id):
    ret = public(request,'vmware-manage','资源位置','删除')
    resource.objects.get(id=id).delete()
    return redirect('/vMware/resource/')

def ResourceDisable(request,id):
    ret = public(request,'vmware-manage','资源位置','删除')
    resource.objects.filter(id=id).update(status=1)
    return redirect('/vMware/resource/')

def ResourceEnable(request,id):
    ret = public(request,'vmware-manage','资源位置','删除')
    resource.objects.filter(id=id).update(status=0)
    return redirect('/vMware/resource/')


'''
@about vm
'''

def Vm(request):
    ret = public(request,'vm','虚拟机','列表')
    ret['vms'] = vms.objects.filter(status=0,type=0)
    ret['num'] = ret['vms'].count()
    return render_to_response('vmware/vmware_list.html',ret)
    

'''
@user order
'''  

def MyOrder(request):
    ret = public(request,'order','订单','列表')
    ret['bodycss'] = 'sidebar-collapse'
    ret['orders'] = order.objects.filter(uid__id=ret['uid'])
    return render_to_response('vmware/my_order.html',ret)
    
    
'''
@bulletin 
'''

def Bulletin(request):
    ret = public(request,'vmware-manage','公告','列表')
    ret['bulletins'] = bulletin.objects.filter()
    return render_to_response('vmware/manage/bulletin.html',ret)
    
def BulletinAdd(request):
    ret = public(request,'vmware-manage','公告','新增')
    if request.method == 'POST':
        form_key = ['title','site','endtime','content',]
        form_value = GetFormPost(request,form_key)
        bulletin = MANAGE()
        bulletin.BulletinSave(form_value,ret)
        return redirect('/vMware/bulletin/')
    else:
        ret['sites'] = bulletin_site.objects.filter()
    return render_to_response('vmware/manage/bulletin_add.html',ret)

def BulletinEdit(request,id):
    ret = public(request,'vmware-manage','公告','编辑')
    if request.method == 'POST':
        form_key = ['title','site','endtime','content',]
        form_value = GetFormPost(request,form_key)
        bulletins = MANAGE()
        bulletins.BulletinUpdate(form_value,id)
        return redirect('/vMware/bulletin/')
    else:
        ret['sites'] = bulletin_site.objects.filter()
        ret['bulletin'] = bulletin.objects.get(id=id)
        ret['now'] = time.time()
        return render_to_response('vmware/manage/bulletin_edit.html',ret)
    
def BulletinDel(request,id):
    ret = public(request,'vmware-manage','公告','列表')
    bulletin.objects.get(id=id).delete()
    return redirect('/vMware/bulletin/')

def BulletinDisable(request,id):
    ret = public(request,'vmware-manage','公告','禁用')
    bulletin.objects.filter(id=id).update(status=1)
    return redirect('/vMware/bulletin/')
    
def BulletinEnable(request,id):
    ret = public(request,'vmware-manage','公告','启用')
    bulletin.objects.filter(id=id).update(status=0)
    return redirect('/vMware/bulletin/')

   
'''
@about vCenter Set
'''
def vCenter(request):
    ret = public(request,'vmware-manage','vCenter','列表')
    ret['vCenters'] = vcenter.objects.filter(status__lt=1000)
    return render_to_response('vmware/manage/vCenter.html',ret)

def vCenterAdd(request):
    ret = public(request,'vmware-manage','vCenter','新增')
    if request.method == 'POST':
        form_key = ['host','user','password','alias',]
        form_value = GetFormPost(request,form_key)
        form_value['status'] = 0
        vcenter(**form_value).save()
        return redirect('/vMware/vCenter/')
    else:
        return render_to_response('vmware/manage/vCenter_add.html',ret)

def vCenterEdit(request,id):
    ret = public(request,'vmware-manage','vCenter','编辑')
    if request.method == 'POST':
        form_key = ['host','user','password','alias',]
        form_value = GetFormPost(request,form_key)
        vcenter.objects.filter(id=id).update(**form_value)
        return redirect('/vMware/vCenter/')
    else:
        ret['vCenters'] = vcenter.objects.get(id=id)
    return render_to_response('vmware/manage/vCenter_edit.html',ret)

def vCenterDisable(request,id):
    ret = public(request,'vmware-manage','vCenter','禁用')
    ret['vCenters'] = vcenter.objects.filter(id=id).update(status=1)
    return redirect('/vMware/vCenter/')

def vCenterEnable(request,id):
    ret = public(request,'vmware-manage','vCenter','启用')
    ret['vCenters'] = vcenter.objects.filter(id=id).update(status=0)
    return redirect('/vMware/vCenter/')

def vCenterDel(request,id):
    ret = public(request,'vmware-manage','vCenter','删除')
    ret['vCenters'] = vcenter.objects.filter(id=id).update(status=1000)
    return redirect('/vMware/vCenter/')



'''
@about message send set
'''
def Message(request):
    ret = public(request,'vmware-manage','通知','配置')
    if request.method == 'POST':
        form_key = ['order_apply','order_pay','wechat_secret','wechat_id','wechat_corp']
        form_value = GetFormPost(request,form_key)
        new = dict()
        for x in form_key:
            new['key'] = x
            new['val'] = form_value.get(x)
            mess = message.objects.filter(key=x)
            if mess.count() == 0 :
                message(**new).save()
            else:
                mess.update(**new)
        return redirect('/vMware/message/')
    else:
        mes = message.objects.filter()
        messa = dict()
        for x in mes:
            messa[x.key] = x.val
        ret['messages'] = messa
        ret['num'] = mes.count()
    return render_to_response('vmware/manage/message.html',ret)

def MessageMail(request):
    ret = public(request,'vmware-manage','通知邮件','配置')
    if request.method == 'POST':
        form_key = ['mail_add','mail_smtp','mail_user','mail_pwd',]
        form_value = GetFormPost(request,form_key)
        system.objects.filter().update(**form_value)
        return redirect('/vMware/message/conf/')
    else:
        ret['sys'] = system.objects.filter().first()
        return render_to_response('vmware/manage/message_mail.html',ret)





