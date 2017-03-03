#-*- coding:utf-8 -*-
import sys 
from Public.public import GetSendMail
reload(sys)
sys.setdefaultencoding('utf-8')

'''
@Created on 2016年5月20日
 
@author: MianBao

@author_web: Mianbao.cn.com

@vmware的管理类
'''
from models import *
from Mianbao.public import DateConvertStamp, sendmail,unit_convert
import time
import platform
import os
from django.template.backends.django import Template
from models import ippool
from MySQLdb.constants.CR import IPSOCK_ERROR
from pysphere.resources import VimService_services as VI
from public_fun import OrderFlowSave
from Public.wechat import send_news_message
from User.User_Class import Group
from User.models import *
from pysphere.vi_task import VITask
from pysphere import VIProperty

from django.db.models import F
from django.db import transaction
from django.template.defaultfilters import linebreaksbr



class MANAGE:

    def __init__(self):
        pass
    
    def AssignNode(self,id):
        try:
            node.objects.filter(assign=1).update(assign=0)
            rs = node.objects.get(id=id)
            rs.assign = 1
            rs.save()
            return True
        except Exception,e:
            return False
    
    def AssignData(self,id):
        try:
            node_disk.objects.filter(assign=1).update(assign=0)
            rs = node_disk.objects.get(id=id)
            rs.assign = 1
            rs.save()
            return True
        except Exception,e:
            return False

    def GetVCFromHost(self,host):
        try:
            vc_id = vcenter.objects.get(host=host)
            return vc_id
        except Exception,e:
            return 0
    
    def GetVCFromId(self,id):
        try:
            vc_id = vcenter.objects.get(id=id)
            return vc_id
        except Exception,e:
            return 0
        
    def UpdateDvsVlan(self,vlan_dict):
        if isinstance(vlan_dict,dict):
            update_vlan_rs = node_network.objects.filter(name=vlan_dict.get('name',None),conn=self.GetVCFromHost(vlan_dict.get('vc',None)))
            update_vlan_rs.update(vlan=vlan_dict.get('vlan',0))
        return True
    
    def DelDvs(self,vlan_dict):
        if isinstance(vlan_dict,dict):
            node_network.objects.filter(**vlan_dict).delete()
            return True

    def CheckIpv4(self,str):
        str_list = str.split('.')
        ip_list = [ x for x in str_list if int(x) < 255]
        return ip_list if len(ip_list) == 4 else False
    
    def SplitIpPool(self,str):
        new = dict()
        if '-' in str:
            str_list = str.split('-')
            str_ip_list = self.CheckIpv4(str_list[0])
            if str_ip_list:
                new['start'] = int(str_ip_list[3])
                str_ip_list.pop()
                new['pooladd'] = '.'.join(str_ip_list)
                new['end'] = int(str_list[1])
        return new
        
    def IpPoolCreate(self,pool_dict,id=None):
        if isinstance(pool_dict,dict):
            default = '0.0.0.0'
            ip_pool = pool_dict.get('pooladd',default)
            pools_start_end = self.SplitIpPool(ip_pool)
            if pools_start_end:
                pool_dict = dict(pool_dict, **pools_start_end)
                pool_dict['vlan'] = int(pool_dict['vlan'])
                if id:
                    ippool.objects.filter(id=id).update(**pool_dict)
                else:
                    ippool(**pool_dict).save()
                return True
        else:
            return False
        
    def VmTypesAdd(self,val):
        if isinstance(val,dict):
            if val.get('template'):
                val['template'] = vms.objects.get(id=val.get('template'))
                val['status'] = 0
                vmtype(**val).save()
                return True
        else:
            return False
        
    def ResourceAdd(self,val):
        if isinstance(val,dict):
            if val.get('vc'):
                val['vc'] = vcenter.objects.get(id=val.get('vc'))
                val['node'] = node.objects.get(id=val.get('node'))
                val['data'] = node_disk.objects.get(id=val.get('data'))
                val['status'] = 0
                resource(**val).save()
                return True
        else:
            return False
        
    def Save(self,val):
        if isinstance(val,dict):
            val['applytime'] = time.time()
            val['resource'] = resource.objects.get(id=val.get('resource'))
            val['uid'] = user.objects.get(id=val.get('uid'))
            val['template'] = vmtype.objects.get(id=val.get('template'))
            val['endtime'] = DateConvertStamp(val.get('endtime'))[-1]
            val['status'] = 0
            order(**val).save()
            new_group = Group(group.objects.get(name='vMware_Wechat'))
            group_users = new_group.GetGroupUser()
            for x in group_users:
                send_news_message(x.tel,
                         "新虚拟机申请",
                         "资源位置：%s \n申请用户：%s \n使用模板：%s(%svCPU/%s) \n申请数量：%s 台\n申请用途：%s" % (val['resource'].name,val['uid'].name,val['template'].type_name,val['template'].template.Core,unit_convert(val['template'].template.memory,2),val['num'],val['project'])
                         )
            return True
        else:
            return False
    
    def OrderPaySendMail(self,order_id,html_add=u''):
        order_object = order.objects.get(id=order_id)
        order_log = order_vm_open_log.objects.filter(order__id = order_id)
        order_resource_gen = order_resource.objects.filter(order__id=order_id)
        mail_part = u"=" * 30
        mail_html = u"<br>资源位置：%s<br><br>申请用途：%s <br>" % (order_object.resource.name, order_object.project)
        br = u'<br>'
        mail_html = mail_html + html_add
        html_footer = u"*订单编号： %s *" % order_id
        change = order_flow.objects.filter(id=order_id,key='change').count()
        name_list = list()
        ip_list = list()
        if order_object.resource.type == 0 or change == 1:
            for x in order_log:
                mail_html = mail_html + mail_part + br
                mail_html = mail_html + u"&nbsp;&nbsp;主机名:" + str(x.name) + br
                mail_html = mail_html + u"&nbsp;&nbsp;IP地址:" + str(x.ip) + br
        else:
            for x in order_resource_gen:
                if x.key == 'name':
                    name_list.append(x.val)
                if x.key == 'ip':
                    ip_list.append(x.val)
            for y in range(len(name_list)):
                mail_html = mail_html + mail_part + br
                mail_html = mail_html + u"&nbsp;&nbsp;主机名:" + str(name_list[y]) + br
                mail_html = mail_html + u"&nbsp;&nbsp;IP地址:" + str(ip_list[y]) + br
        html = mail_html + mail_part + br*3 + html_footer
        mail_object = u"【通知】虚拟机开通"
        html_dict = {'title':u'虚拟机开通'}
        html_dict['content'] = html
        send_mail = GetSendMail('order_pay')
        send_mail.append(order_object.uid.mail)
        rs = sendmail(send_mail,mail_object,html_dict)
        return rs
    
    def BulletinSave(self,dicts,ret):
        if isinstance(dicts,dict):
            dicts['endtime'] = DateConvertStamp(dicts['endtime'])[1]
            dicts['site'] = bulletin_site.objects.get(id=dicts['site'])
            dicts['status'] = 0
            dicts['uid'] = user.objects.get(id=ret.get('uid'))
            bulletin(**dicts).save()
            return 0
    
    def BulletinUpdate(self,dicts,id):
        if isinstance(dicts,dict):
            dicts['endtime'] = DateConvertStamp(dicts['endtime'])[1]
            dicts['site'] = bulletin_site.objects.get(id=dicts['site'])
            bulletin.objects.filter(id=id).update(**dicts)
            return 0
    
    def SaveName(self,dic):
        dic['recover'] = 0
        dic['vc'] = vcenter.objects.get(id=dic['vc'])
        name_num = vm_name.objects.filter(vc=dic['vc']).count()
        if name_num == 0:
            rs = vm_name(**dic)
            rs.save()
            return rs.id
        else:
            return False
            
        
class OrderInfoGenerate:
    
    def __init__(self,order_id):
        self.__order = order.objects.get(id=order_id)
        self.__num = self.__order.num
        self.__ippools_id = order_flow.objects.get(key='opened_ippools',order__id=order_id).ippool.id
        self.__pools = None
        self.__pooladd = None
        self.__pools_start = None
        self.__pools_end = None
    
    def GenerateCollectRange(self):
        try:
            pools = ippool.objects.get(id=self.__ippools_id)
            self.__pools = pools
            self.__pooladd = pools.pooladd
            self.__pools_start = pools.start
            self.__pools_end = pools.end
            self.__pools_netmask = pools.netmask
            return True
        except Exception:
            return False
    
    def CollectOrderResource(self):
        rs = self.GenerateCollectRange()
        if rs:
            ips = order_resource.objects.filter(key='ip',val__contains=self.__pooladd,order__status__lt=5000).values('val')
            ip_list = list()
            [ ip_list.append(m.get('val')) for m in ips ] 
            return ip_list
        else:
            return 1
        
    def CollectNetwork(self):
        rs = self.GenerateCollectRange()
        if rs:
            ips = network.objects.filter(ip__contains=self.__pooladd,status=0).values('ip')
            ip_list = list()
            [ ip_list.append(m.get('val')) for m in ips ]
            return ip_list
        else:
            return 1
        
    def MergeIPList(self):
        resource = self.CollectOrderResource()
        network = self.CollectNetwork()
        if resource != 1 and network != 1:
            ip_list = list(set(list(resource)+list(network)))
            return ip_list
        else:
            return False
        
    def GenerateIP(self):
        use_ip_list = self.MergeIPList()
        ip_list = list()
        if all((self.__pools_start,self.__pools_end)):
            for suffix in range(self.__pools_start,self.__pools_end + 1):
                if suffix <= self.__pools_end + 1:
                    ip = str(self.__pooladd) + '.' + str(suffix)
                    if ip not in use_ip_list and len(ip_list) < int(self.__num):
                        ip_list.append(ip)
                    else:
                        rs = self.IPPingCheck(ip_list)
                        if rs:
                            if len(rs) == int(self.__num):
                                break
                else:
                    item = 'IP地址'
                    detail = 'IP地址池中可用IP不足'
                    key = 'IP'
                    self.ReportError(item,detail)
        return ip_list
    
    def IPPingCheck(self,ip_list):
        rs = False
        if 'inu' in platform.system():
            for ip in ip_list:
                cmd_rs = os.system('ping -c 2 %s' % ip)
                if cmd_rs == 0:
                    ip_list.remove(ip)
                    ip_ping_doubt(**{'ip':ip}).save()
            rs = ip_list
        return rs
        
    def SaveToOrderResource(self):
        ip_list = self.GenerateIP()
        if len(ip_list) == self.__num:
            new = {'order':self.__order}
            new['key'] = 'ip'
            for ip in ip_list:
                new['val'] = ip
                order_resource(**new).save()
            common = {'gateway':self.__pools.gateway}
            common['dns1'] = self.__pools.dns1
            common['dns2'] = self.__pools.dns2
            common['vlan'] = self.__pools.vlan
            node = self.__order.resource.node
            rs = node_network.objects.filter(node=node,vlan=self.__pools.vlan)
            if rs.count() == 1:
                order_resource(**{'order':self.__order,'key':'network','val':rs[0].name}).save()
            for key,val in common.items():
                order_resource(**{'order':self.__order,'key':key,'val':val}).save()
            return True
        else:
            return False
    
    def SaveAssignHost(self):
        node_id = self.__order.resource.node.node_id
        new = {'order':self.__order}
        new['key'] = 'host'
        new['val'] = node_id
        order_resource(**new).save()
        
    def SaveAssignResource(self):
        resource_ids = self.__order.resource.node.resource_id
        new={'order':self.__order}
        new['key'] = 'resourcepool'
        new['val'] = resource_ids
        order_resource(**new).save()
    
    def NameExistCheck(self,name):
        name_check_rs = vms.objects.filter(name=name)
        resource_name_check_rs = order_resource.objects.filter(key='name',val=name)
        return True if name_check_rs.count() == 0 and resource_name_check_rs.count() == 0 else False
        
    def NameRuleGenerate(self):
        names = vm_name.objects.filter(recover=0,vc=self.__order.resource.vc)
        rs = 0
        if names.count() > 0:
            name = names[0]
            name_suffix_change = name.pointer + 1
            max_name_suffix = '9'* name.suffix
            for x in range(self.__num):
                new={'order':self.__order,'key':'name'}
                while True:
                    if int(max_name_suffix) >= name_suffix_change:
                        new_name = name.prefix + '_' + '0'*(name.suffix-len(str(name_suffix_change))) +str(name_suffix_change)
                        if self.NameExistCheck(new_name):
                            new['val'] = new_name
                            order_resource(**new).save()
                            names.update(pointer=name_suffix_change)
                            break
                        names.update(pointer=name_suffix_change)
                        name_suffix_change = name_suffix_change + 1
                        rs = 0
                    else:
                        item = '虚拟机名字'
                        detail = '虚拟机名字生成规律中已没有可用的名字，请更新规则'
                        key = 'Name'
                        self.ReportError(item,detail,key)
                        rs = 1
        else:
            item = '名字生成规律'
            detail = '您还未设置虚拟机名字生成规律！'
            key = 'Name'
            self.ReportError(item,detail,key)
            self.__order.status = 3
            self.__order.save()
            rs = 1
        return rs
            
    def SaveName(self):
        names = vm_name.objects.filter(recover=0,vc=self.__order.resource.vc)
        recovery_names = vm_name.objects.filter(prefix=0,suffix=0,pointer=0,vc=self.__order.resource.vc)
        if recovery_names.count() < self.__num:
            rs = self.NameRuleGenerate()
        else:
            names = recovery_names[:self.__num]
            new={'order':self.__order}
            new['key'] = 'name'
            for x in names:
                if self.NameExistCheck(x.recover):
                    new['val'] = x.recover
                    order_resource(**new).save()
            names.delete()
            rs = 0
        if rs == 0:
            order_error.objects.filter(order=self.__order,key='Name').update(status=1)
            self.__order.status = 3
            self.__order.save()
    
    def SaveFloder(self):
        floder = self.__order.uid.name
        new = {'order':self.__order}
        new['key'] = 'folder'
        new['val'] = floder
        order_resource(**new).save()
    
    def CustomizationType(self):
        template_version = self.__order.template.template.systemversion
        types=0
        linux_list = ['CentOS','Red Hat','inux','entO','Red','SUSE','Debian','Sianu']
        windows_list = ['Windows','indow']
        linux_rs = [ True for x in linux_list if x in template_version]
        win_rs = [ True for x in windows_list if x in template_version]
        if linux_rs:
            types = 'LINUX'
        elif win_rs:
            types = 'SYSPREP'
        
        new = {'order':self.__order}
        new['key'] = 'customize'
        new['val'] = types
        
        check_cus = order_resource.objects.filter(order=self.__order,key='customize',val='0')
        check_cus_have = order_resource.objects.filter(order=self.__order,key='customize').count()
        
        if check_cus.count() > 0 and types != 0:
            check_cus.update(val=types)
            order_error.objects.filter(order=self.__order,key='Custome',status=0).update(status=1)
        elif check_cus_have == 0:
            order_resource(**new).save()
            if types == 0:
                item = '模板自定义规范调用失败'
                detail = 'VMware未能识别出系统的类型，无法调用相应的自定义规范'
                key = 'Custome'
                self.ReportError(item,detail,key)
                self.__order.status = 3
                self.__order.save()
        elif check_cus_have + check_cus.count() > 0:
            error = order_error.objects.filter(order=self.__order,status=0,try_num__lte=10,key='Custome').update(try_num = F('try_num') + 1)
            
    
    def SaveDatastore(self):
        data = self.__order.resource.data.datastore_id
        new = {'order':self.__order}
        new['key'] = 'datastore'
        new['val'] = data
        order_resource(**new).save()
        
    def SaveNetmask(self):
        new = {'order':self.__order}
        new['key'] = 'netmask'
        new['val'] = self.__pools_netmask
        order_resource(**new).save()
        
    def ReportError(self,item,detail,key):
        order_num = order_error.objects.filter(key=key,order=self.__order,status=0).count()
        if order_num == 0:
            error = {'order':self.__order}
            error['time'] = time.time()
            error['item'] = item
            error['detail'] = detail
            error['key'] = key
            error['status'] = 0
            order_error(**error).save()
    
    def Generate(self):
        check_resouce = order_resource.objects.filter(order=self.__order).count()
        try:
            if check_resouce == 0:
                with transaction.atomic():
                    self.SaveToOrderResource()
                    self.SaveAssignHost()
                    self.SaveAssignResource()
                    self.SaveName()
                    self.SaveFloder()
                    self.CustomizationType()
                    self.SaveDatastore()
                    self.SaveNetmask()
                    order_info = order_error.objects.filter(order=self.__order)
                    if order_info.count() > 0:
                        return False
                    else:
                        self.__order.status = 4
                        self.__order.save()
                        return True
            else:
                self.__order.status = 4
                self.__order.save()
        except Exception:
            raise Generate_error('The Generate have a error!')

class Generate_error():
    def __init__(self,info):
        self.args = info

class VM_Create:
    
    def __init__(self,order_id,s):
        self.__order = order.objects.get(id=order_id)
        self.__s = s
        
    def GetIPList(self):
        ips = order_resource.objects.filter(order=self.__order,key='ip')
        ip_list = list()
        for ip in ips:
            ip_list.append(ip.val)
        return ip_list
    
    def GetNameList(self):
        names = order_resource.objects.filter(order=self.__order,key='name')
        names_list = list()
        for name in names:
            names_list.append(name.val)
        return names_list
    
    def PublicList(self):
        orders = order_resource.objects.filter()
        public_list = dict()
        net_list = dict()
        for y in orders:
            if y.key not in ['ip','name','vlan','dns1','dns2','gateway','netmask']:
                public_list[y.key] = y.val
            if y.key in ['dns1','dns2','gateway','netmask','vlan']:
                net_list[y.key] = y.val
        return public_list,net_list
    
    def FloderCheck(self,folder_name,parent_folder_name='vm'):
        folders = self.__s._retrieve_properties_traversal(property_names=['name'], obj_type='Folder')
        folder = list()
        rs = None
        for f in folders:
            folder.append(f.PropSet[0].Val)
            if f.PropSet[0].Val == parent_folder_name:
                vm_folder = f.Obj
            if f.PropSet[0].Val == folder_name:
                rs = f.Obj
        if rs is None:
            request = VI.CreateFolderRequestMsg()
            _this = request.new__this(vm_folder)
            _this.set_attribute_type(vm_folder.get_attribute_type())
            request.set_element__this(_this)
            request.set_element_name(folder_name)
            rs = self.__s._proxy.CreateFolder(request)
        return rs 
    
    def GetDvsUuid(self,dc_name,portgroupKey):
        dcmor = [k for k,v in self.__s.get_datacenters().items() if v==dc_name][0]
        dcprops = VIProperty(self.__s, dcmor)
        nfmor = dcprops.networkFolder._obj
        
        # Grab the dvswitch uuid and portgroup properties
        dvswitch_mors = self.__s._retrieve_properties_traversal(property_names=['uuid','portgroup'],
                                            from_node=nfmor, obj_type='DistributedVirtualSwitch')
        
        
        dvswitch_mor = None
        # Get the appropriate dvswitches managed object
        for dvswitch in dvswitch_mors:
            if dvswitch_mor:
                break
            for p in dvswitch.PropSet:
                if p.Name == "portgroup":
                    pg_mors = p.Val.ManagedObjectReference
                    for pg_mor in pg_mors:
                        if dvswitch_mor:
                            break
                        key_mor = self.__s._get_object_properties(pg_mor, property_names=['key'])
                        for key in key_mor.PropSet:
                            if key.Val == portgroupKey:
                                dvswitch_mor = dvswitch
        
        # Get the switches uuid
        dvswitch_uuid = None
        for p in dvswitch_mor.PropSet:
            if p.Name == "uuid":
                dvswitch_uuid = p.Val
        return dvswitch_uuid
        
    def change_dvs_net(self, vm, pg_map, dc_name):
        """Takes a VIServer and VIVirtualMachine object and reconfigures
        dVS portgroups according to the mappings in the pg_map dict. The
        pg_map dict must contain the source portgroup as key and the
        destination portgroup as value"""
        # Find virtual NIC devices
        vm_obj = self.__s.get_vm_by_name(vm)
        uuid = self.GetDvsUuid(dc_name, pg_map)
        if vm_obj:
            net_device = []
            for dev in vm_obj.properties.config.hardware.device:
                if dev._type in ["VirtualE1000", "VirtualE1000e",
                                "VirtualPCNet32", "VirtualVmxnet",
                                "VirtualNmxnet2", "VirtualVmxnet3"]:
                    net_device.append(dev)
    
        # Throw an exception if there is no NIC found
        if len(net_device) == 0:
            raise Exception("The vm seems to lack a Virtual Nic")
        try:
            # Use pg_map to set the new Portgroups
            for dev in net_device:
                #old_portgroup = dev.backing.port.portgroupKey
                #if pg_map.has_key(old_portgroup):
                dev.backing.port._obj.set_element_portgroupKey(pg_map)
                dev.backing.port._obj.set_element_portKey('')
                dev.backing.port._obj.set_element_switchUuid(uuid)
        
            # Invoke ReconfigVM_Task
            request = VI.ReconfigVM_TaskRequestMsg()
            _this = request.new__this(vm_obj._mor)
            _this.set_attribute_type(vm_obj._mor.get_attribute_type())
            request.set_element__this(_this)
        
            # Build a list of device change spec objects
            devs_changed = []
            for dev in net_device:
                spec = request.new_spec()
                dev_change = spec.new_deviceChange()
                dev_change.set_element_device(dev._obj)
                dev_change.set_element_operation("edit")
                devs_changed.append(dev_change)
        
            # Submit the device change list
            spec.set_element_deviceChange(devs_changed)
            request.set_element_spec(spec)
            ret = self.__s._proxy.ReconfigVM_Task(request)._returnval
        
            # Wait for the task to finish
            task = VITask(ret, self.__s)
        
            #status = task.wait_for_state([task.STATE_SUCCESS, task.STATE_ERROR])
        except Exception,e:
            item = '虚拟机网络更改失败'
            detail = e.message
            key = 'change_network'
            self.ReportError(item,detail,key)
            pass
    
    def FromVlanGetNetwork(self,vlan,node_id,vm):
        nodes = node.objects.get(node_id=node_id)
        network_lists = node_network.objects.filter(node=nodes,vlan=vlan)
        if network_lists.count() == 1:
            pg_map =  network_lists[0].portkey
            dc_name = network_lists[0].todc.name
            try:
                self.change_dvs_net(vm,pg_map,dc_name)
            except Exception,e:
                item = '虚拟机网络更改失败'
                detail = e.message
                key = 'change_network'
                self.ReportError(item,detail,key)
                pass
        else:
            item = '虚拟机网络更改失败'
            detail = '此节点上没有相应的vlan网络'
            key = 'change_network'
            self.ReportError(item,detail,key)

    def Create(self):
        
        ip_list = self.GetIPList()
        name_list = self.GetNameList()
        pub_list,net_list =  self.PublicList()
        
        template_name = self.__order.template.template.name
        try:
            vm = self.__s.get_vm_by_name(template_name)
        except Exception,e:
            item = '在此资源域未发现相应模板'
            detail = e.message
            key = 'get_vm'
            self.ReportError(item,detail,key)
        
        if len(ip_list) == len(name_list) and vm:
            self.FloderCheck(pub_list.get('folder'))
            
            self.__order.status = 5
            self.__order.save()
            for xyz in range(len(ip_list)):
                pub_list['name'] = name_list[xyz]
                pub_list['sync_run'] = False
                net_list['domain'] = 'Mianbao.cn.com'
                net_list['ip'] = ip_list[xyz]
                pub_list['data'] = net_list
                pub_list['data']['adminpw'] = 'Howbuy1!'
                if pub_list.has_key('network'):
                    del pub_list['network']
                if pub_list.get('customize') == 'SYSPREP':
                    del pub_list['customize']
                vm_open_log = order_vm_open_log.objects.filter(ip=net_list['ip'],name=pub_list['name'],order=self.__order).count()
                if vm_open_log == 0:
                    try:
                        clone_rs = vm.clone(**pub_list)
                    except Exception,e:
                        clone_rs = 'error'
                    while True:
                        if clone_rs != 'error':
                            runing_status = clone_rs.get_state()
                        else:
                            runing_status = 'error'
                        if runing_status == 'success':
                            right_rs = {'order':self.__order}
                            right_rs['name'] = name_list[xyz]
                            right_rs['rs'] = 0
                            right_rs['time'] = time.time()
                            right_rs['ip'] = ip_list[xyz]
                            order_vm_open_log(**right_rs).save()
                            self.FromVlanGetNetwork(net_list['vlan'],pub_list['host'],pub_list['name'])
                            break
                        elif runing_status == 'error':
                            error_rs = {'order':self.__order}
                            error_rs['name'] = name_list[xyz]
                            error_rs['rs'] = 1
                            error_rs['time'] = time.time()
                            error_rs['ip'] = ip_list[xyz]
                            order_vm_open_log(**error_rs).save()
                            break
                        time.sleep(5)
                else:
                    pass
            
            self.__order.status = 6
            self.__order.save()
                            
        else:
            print ip_list,name_list
            print 'List No eq!'
        
    def ReportError(self,item,detail,key):
        order_num = order_error.objects.filter(key=key,order=self.__order,status=0).count()
        if order_num == 0:
            error = {'order':self.__order}
            error['time'] = time.time()
            error['item'] = item
            error['detail'] = detail
            error['key'] = key
            error['status'] = 0
            order_error(**error).save()
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    