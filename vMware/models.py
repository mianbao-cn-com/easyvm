#-*- coding:utf-8 -*-

'''
@Created on 2016年5月24日
 
@author: MianBao

@author_web: Mianbao.cn.com

@User
'''
from django.db import models
from User.models import user
from django.template.defaultfilters import title



'''
@about VC connection info
'''
  
class vcenter(models.Model):
    host = models.GenericIPAddressField()
    user = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    status = models.IntegerField() #0：正常可用 ，1禁用 ，10000：删除状态
    alias = models.CharField(max_length=50,default=0)

class vc_error(models.Model):
    vc = models.ForeignKey(vcenter)
    key = models.CharField(max_length=50)
    val = models.TextField(null=True)
    status = models.IntegerField()
'''
@about VM info
'''

class network(models.Model):
    ip = models.CharField(max_length=50)
    mac = models.CharField(max_length=50)
    uplink = models.CharField(max_length=50)
    connect = models.IntegerField()
    status = models.IntegerField()#0现在的状态，1历史
    times = models.CharField(max_length=50)
    
class disk(models.Model):
    total = models.IntegerField()
    used = models.IntegerField()
    status = models.IntegerField()
    solts = models.IntegerField()
    times = models.CharField(max_length=50)
    
class memorys(models.Model):
    memory = models.IntegerField()
    cpu = models.IntegerField()
    status = models.IntegerField()
    times = models.CharField(max_length=50)
    
class agentlog(models.Model):
    time = models.CharField(max_length=50)
    why = models.TextField()
    vmsid = models.IntegerField()
    type = models.IntegerField()
    
class run(models.Model):
    power = models.CharField(max_length=50)
    ptime = models.CharField(max_length=50)
    runhost = models.CharField(max_length=50)
    folder = models.CharField(max_length=50)
    status = models.IntegerField()
    times = models.CharField(max_length=50)
    
class vms(models.Model):
    Core = models.IntegerField()
    hz = models.IntegerField()
    memory = models.IntegerField()
    '''
    GENDER_CHOICE = (
        (u'M', u'Male'),
        (u'F', u'Female'),
    )
    '''
    vmtools = models.CharField(max_length=50)
    dnsname = models.CharField(max_length=50)
    systemversion = models.CharField(max_length=50)
    type = models.IntegerField()#1:模板，0虚拟机
    name = models.CharField(max_length=50)
    ctime = models.CharField(max_length=50)
    vmsid = models.CharField(max_length=50)
    status = models.IntegerField()
    vms_network = models.ManyToManyField(network)
    vms_disk = models.ManyToManyField(disk)
    vms_memorys = models.ManyToManyField(memorys)
    vms_run = models.ManyToManyField(run)
    times = models.CharField(max_length=50)
    vc = models.ForeignKey(vcenter)

class t_hash(models.Model):
    vmsid = models.CharField(max_length=50)
    hash_type = models.CharField(max_length=50)
    hash = models.CharField(max_length=50)
    vc = models.ForeignKey(vcenter)

'''
@about node info
'''
class datacenter(models.Model):
    name = models.CharField(max_length=50)
    datacenter_id = models.CharField(max_length=50)
    conn = models.ForeignKey(vcenter)
    
class cluster(models.Model):
    name = models.CharField(max_length=50)
    dc = models.ForeignKey(datacenter)
    cluster_id = models.CharField(max_length=50)
    conn = models.ForeignKey(vcenter)
    
class node(models.Model):
    name = models.CharField(max_length=50)
    node_id = models.CharField(max_length=50)
    domain_id = models.CharField(max_length=50)
    resource_id = models.CharField(max_length=50)
    resource_val = models.CharField(max_length=50)
    dc = models.ForeignKey(datacenter,null=True)
    cluster = models.ForeignKey(cluster,null=True)
    conn = models.ForeignKey(vcenter,null=True)
    assign = models.IntegerField()#1为建议值

class node_disk(models.Model):
    datastore_id = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    total = models.CharField(max_length=50)
    free = models.CharField(max_length=50)
    assign = models.IntegerField()
    node = models.ForeignKey(node,null=True)
    conn = models.ForeignKey(vcenter,null=True)

class node_network(models.Model):
    name = models.CharField(max_length=50)
    vswitch = models.CharField(max_length=50)
    vlan = models.IntegerField()
    type = models.IntegerField() #0:本地虚拟交换机，1：dvs
    node = models.ForeignKey(node,null=True)
    times = models.CharField(max_length=50)
    conn = models.ForeignKey(vcenter,null=True)
    todc = models.ForeignKey(datacenter,null=True)
    portkey = models.CharField(max_length=50,default=0)
    
class ippool(models.Model):
    pooladd = models.CharField(max_length=50)
    start = models.IntegerField()
    end = models.IntegerField()
    netmask = models.CharField(max_length=50)
    gateway = models.CharField(max_length=50)
    dns1 = models.CharField(max_length=50)
    dns2 = models.CharField(max_length=50)
    vlan = models.IntegerField()
    alia = models.CharField(max_length=50,null=True)
    remark = models.TextField(null=True)
    
class custome(models.Model):
    adminpw = models.CharField(max_length=50)
    timezone = models.CharField(max_length=50)
    fullName = models.CharField(max_length=50)
    orgName = models.CharField(max_length=50)
    joinDomain = models.CharField(max_length=50)
    domainAdmin = models.CharField(max_length=50)
    domainAdminPassword = models.CharField(max_length=50)
    joinDomain = models.CharField(max_length=50)
    value = models.CharField(max_length=50)
    domain = models.CharField(max_length=50)

class vmtype(models.Model):
    type_name = models.CharField(max_length=50,null=False)
    template = models.ForeignKey(vms)
    application = models.CharField(max_length=50,null=False)
    remark = models.TextField(null=True)
    status = models.IntegerField()

class resource(models.Model):
    name = models.CharField(max_length=50,null=False)
    vc = models.ForeignKey(vcenter)
    node = models.ForeignKey(node,null=True)
    data = models.ForeignKey(node_disk,null=True)
    type = models.IntegerField()#0自动开通，1手动开通
    status = models.IntegerField()
    
class order(models.Model):
    num = models.IntegerField()
    resource = models.ForeignKey(resource,null=True)
    project = models.TextField(null=True)
    endtime = models.CharField(max_length=50,null=False)
    uid = models.ForeignKey(user,null=True)
    template = models.ForeignKey(vmtype,null=True)
    applytime = models.CharField(max_length=50,null=False)
    status = models.IntegerField()#0:申请提交，1审核通过,3开通中,4排队，5,开通中，7,分析中，6：交付发送邮件，9:邮件发送失败，2，手动开通配置生成完成，100,开通失败,200：审核驳回;5000:回收

class order_remark(models.Model):
    remark = models.TextField(null=True)
    
class order_flow(models.Model):
    order = models.ForeignKey(order,null=True)
    key = models.CharField(max_length=50,null=False)
    rs = models.IntegerField()
    remark = models.ForeignKey(order_remark,null=True)
    ippool = models.ForeignKey(ippool,null=True)
    uid = models.ForeignKey(user,null=True)
    time = models.CharField(max_length=50,null=False)
    
class order_resource(models.Model):
    order = models.ForeignKey(order,null=True)
    key = models.CharField(max_length=50,null=False)
    val = models.CharField(max_length=50,null=False)

class ip_ping_doubt(models.Model):
    ip = models.CharField(max_length=50,null=False)

class vm_name(models.Model):
    prefix = models.CharField(max_length=50,null=False)
    suffix = models.IntegerField()
    pointer = models.IntegerField()
    recover = models.CharField(max_length=50,null=False)
    vc = models.ForeignKey(vcenter)

class order_error(models.Model):
    order = models.ForeignKey(order,null=True)
    time = models.CharField(max_length=50,null=False)
    item = models.CharField(max_length=50,null=False)
    detail = models.TextField(null=True)
    key = models.CharField(max_length=50,null=False)
    status = models.IntegerField(null=True,default=0)
    try_num = models.IntegerField(null=True,default=0)
    
class order_vm_open_log(models.Model):
    order = models.ForeignKey(order,null=True)
    name = models.CharField(max_length=50,null=False)
    rs = models.IntegerField()
    ip = models.CharField(max_length=50,null=False)
    time = models.CharField(max_length=50,null=False)

class bulletin_site(models.Model):
    name = models.CharField(max_length=50,null=False)
     
class bulletin(models.Model):
    title = models.CharField(max_length=50,null=False)
    content = models.TextField(null=True)
    site = models.ForeignKey(bulletin_site,null=True)
    uid = models.ForeignKey(user,null=True)
    endtime = models.CharField(max_length=50,null=False)
    status = models.IntegerField()

class message(models.Model):        
    key = models.CharField(max_length=50,null=False)
    val = models.TextField(null=True)
    
    