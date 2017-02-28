#-*- coding:utf-8 -*-

'''
@Created on 2016年5月20日
 
@author: MianBao

@author_web: Mianbao.cn.com

@系统设置
'''
from models import *
from django.db.models import Q

import time
from pysphere import VIProperty


class DATA_PROCESS:
    
    def __init__(self,dicts_one,vc_id):
        self.__data = dicts_one
        self.__vmsid = dicts_one.get('vmsid')
        self.__ctime = None
        self.__vc_id = vc_id
        self.__vc = vcenter.objects.get(id=vc_id)
    
    def MainCycle(self):
        update_list = self.HandleSingleDict(self.__data)
        self.ExecuteUpdateFun(update_list)
        
    def HandleSingleDict(self,singledict):
        update_dict = dict()
        for key,val in singledict.get('hash').items():
            select_hash = t_hash.objects.filter(vmsid = self.__vmsid,hash_type=key,vc=self.__vc)
            if len(select_hash) == 1:
                if select_hash[0].hash != val:
                    ctimes = vms.objects.filter(vmsid=self.__vmsid,vc=self.__vc).values('ctime')
                    self.__ctime = ctimes[0].get('ctime',time.time()) if ctimes.count() > 1 else time.time()
                    update_dict[key] = singledict.get(key)
                    select_hash[0].hash = val
                    select_hash[0].save()
            else:
                t_hash.objects.create(vmsid=self.__vmsid,hash_type=key,hash=val,vc=self.__vc)
                self.__ctime = time.time()
                update_dict[key] = singledict.get(key)
        return update_dict
    
    def VmsLinkToOther(self):
        vms_old_id_dict = dict()
        vms_rs = vms.objects.filter(vmsid=self.__vmsid,status=0)
        vms_old_id_dict['vms'] = vms_rs[0].id if vms_rs.count() > 0 else ''
        
        run_rs = run.objects.filter(vms__vmsid=self.__vmsid,status=0)
        vms_old_id_dict['run'] = run_rs[0].id if len(run_rs) > 0 else ''
        
        networks = network.objects.filter(vms__vmsid=self.__vmsid,status=0)
        networks_list = list()
        if networks.count() > 0:
            for x in networks:
                networks_list.append(x.id)
            vms_old_id_dict['network'] = networks_list
        else:
            vms_old_id_dict['network'] = ''
        
        memorys_rs = memorys.objects.filter(vms__vmsid=self.__vmsid,status=0)
        vms_old_id_dict['memorys'] = memorys_rs[0].id if len(memorys_rs) > 0 else ''
        
        disk_rs = disk.objects.filter(vms__vmsid=self.__vmsid,status=0)
        disk_list = list()
        if disk_rs.count() > 0:
            for y in disk_rs:
                disk_list.append(y.id)
            vms_old_id_dict['disk'] = disk_list
        else:
            vms_old_id_dict['disk'] = ''

        return vms_old_id_dict
        
    def ExecuteUpdateFun(self,update_dict):
        if len(update_dict) > 0:
            vms_link_other = self.VmsLinkToOther()
            for key,val in update_dict.items():
                fun = getattr(self, key)
                vms_link_other[key] = fun(val)
            self.RebuildLink(vms_link_other)
    
    def RebuildLink(self,link_list):
        vmsid = link_list.get('vms',self.__vmsid)
        vm = vms.objects.get(id=vmsid)
        '''
        @rebuild run
        '''
        vm.vms_run.add(run.objects.get(id=link_list.get('run',0)))
        
        '''
        @rebuild network
        '''
        for n in link_list.get('network',0):
            vm.vms_network.add(network.objects.get(id=n))
        
        '''
        @rebuild memorys
        '''
        vm.vms_memorys.add(memorys.objects.get(id=link_list.get('memorys',0)))
        
        '''
        @rebuild disk
        '''
        for m in link_list.get('disk'):
            vm.vms_disk.add(disk.objects.get(id=m))
            
        vm.save()
    
    def vms(self,val):
        vms.objects.filter(vmsid=self.__vmsid,status=0).update(status=1)
        val['ctime'] = self.__ctime
        val['status'] = 0
        val['times'] = time.time()
        val['vc'] = vcenter.objects.get(id=self.__vc_id)
        if not val.get('hz'):
            val['hz'] = 0
        vm_rs= vms(**val)
        vm_rs.save()
        
        '''
        #获取改变的信息
        old_dict_rs = vms.objects.get(vmsid=self.__vmsid,status=0).values()
        diff_dict = dict(set(old_dict_rs.items())^set(val.items()))
        
        #保存日志
        key_to_mean = self.VmsMysqlKeyToMean()
        '''
        
        return vm_rs.id
        
    def run(self,val):
        run.objects.filter(vms__vmsid=self.__vmsid,status=0).update(status=1)
        val['status'] = 0
        val['times'] = time.time()
        run_rs = run(**val)
        run_rs.save()
        return run_rs.id
        
    def network(self,val):
        network.objects.filter(vms__vmsid=self.__vmsid,status=0).update(status=1)
        network_id_list = list()
        for x in val:
            x['times'] = time.time()
            x['status'] = 0
            if not x.get('connect',False):
                x['connect'] = 1
            network_rs = network(**x)
            network_rs.save()
            network_id_list.append(network_rs.id)
        return network_id_list
        
    def memorys(self,val):
        memorys.objects.filter(vms__vmsid=self.__vmsid,status=0).update(status=1)
        val['status'] = 0
        val['times'] = time.time()
        memorys_rs = memorys(**val)
        memorys_rs.save()
        return memorys_rs.id
        
    def disk(self,val):
        disk.objects.filter(vms__vmsid=self.__vmsid,status=0).update(status=1)
        disk_id_list = list()
        for y in val:
            y['status'] = 0
            y['times'] = time.time()
            disk_rs = disk(**y)
            disk_rs.save()
            disk_id_list.append(disk_rs.id)
        return disk_id_list
        
    def VmsMysqlKeyToMean(self):
        key_to_mean = {
                       "Core":"核心数",
                        "hz":"hz数",
                        "memory":"内存总数",
                        "vmtools":"tools状态",
                        "dnsname":"系统域名",
                        "power":"电源状态",
                        "systemversion":"系统版本",
                        "type":"类型",
                        "name":"虚拟机名",
                        "ctime":"创建时间",
                        "vmsid":"vmid",
                        "status":"状态",
        }
        return key_to_mean
        
        
class GETNODE:
    
    def __init__(self,server,vc_id):
        self.__server = server
        self.__vc_id = vcenter.objects.get(id=vc_id)
    
    def GetDatacenter(self):
        '''
        @获取VC下面的DC
        '''
        dcs = self.__server.get_datacenters()
        if len(dcs) > 0:
            for key,val in dcs.items():
                val_check = datacenter.objects.filter(datacenter_id=key,conn=self.__vc_id)
                if val_check.count() == 0:
                    rs = datacenter(name=val,datacenter_id=key,conn=self.__vc_id)
                    rs.save()
                else:
                    if val_check[0].name != val:
                        val_check[0].name = val
                        val_check[0].save()
        return dcs
        
    def GetCluster(self,dc_mors):
        '''
        @根据DC获取Cluster，并生成相应格式的字典返回
        '''
        nodes_belong = dict()
        for dc_mor,dc_name in dc_mors.items():
            clusters = self.__server.get_clusters(from_mor=dc_mor)
            for key,val in clusters.items():
                val_check = cluster.objects.filter(cluster_id=key,conn=self.__vc_id)
                if val_check.count() == 0:
                    val_dc = datacenter.objects.get(datacenter_id=dc_mor,conn=self.__vc_id)
                    new = {'name':val,'cluster_id':key,'dc':val_dc,'conn':self.__vc_id}
                    rs = cluster(**new)
                    rs.save()
                else:
                    if val_check[0].name != val:
                        val_check[0].name = val
                        val_check[0].save()
                cluster_host = self.__server.get_hosts(from_mor=key)
                for node_id,node_name in cluster_host.items():
                    nodes_belong[node_id] = {'name':node_name,'dc':dc_mor,'cluster':key}
        return nodes_belong
    
    def GetHost(self,dcs):
        for x,y in dcs.items():
            hosts = self.__server.get_hosts(from_mor=x)
            for key,val in hosts.items():
                node_check = node.objects.filter(node_id=key,conn=self.__vc_id)
                if node_check.count() == 0:
                    new = dict()
                    new['name'] = val
                    new['node_id'] = key
                    new['domain_id'] = 0
                    new['resource_id'] = 0
                    new['resource_val'] = 0
                    new['assign'] = 0
                    new['dc'] = datacenter.objects.get(datacenter_id=x,conn=self.__vc_id)
                    new['conn'] = self.__vc_id
                    rs = node(**new)
                    rs.save()
                else:
                    node_check[0].name = val
                    node_check[0].dc = datacenter.objects.get(datacenter_id=x,conn=self.__vc_id)
                    node_check[0].conn = self.__vc_id
                    node_check[0].save()
                    rs = node.objects.get(node_id=key,conn=self.__vc_id)
                    rs.dc = datacenter.objects.get(datacenter_id=x,conn=self.__vc_id)
                    rs.save()
        
    def UpdateHost(self,nodes_belong):
        node.objects.filter().update(cluster='')
        for key,val in nodes_belong.items():
            nodes = node.objects.get(node_id=key,conn =self.__vc_id)
            nodes.domain_id = val.get('cluster')
            nodes.dc = datacenter.objects.get(datacenter_id=val.get('dc'),conn=self.__vc_id)
            nodes.cluster = cluster.objects.get(cluster_id=val.get('cluster'))
            nodes.save()
            
    def UpdateResource(self):
        compute_resources = self.__server._get_managed_objects("ComputeResource")
        for x,y in compute_resources.items():
            nodes = node.objects.filter(Q(name=y)|Q(domain_id=x),Q(conn=self.__vc_id))
            nodes_resource = self.__server.get_resource_pools(x)
            #nodes.resource_id = nodes_resource.keys()[0]
            #nodes.resource_val = nodes_resource.values()[0]
            nodes.update(resource_id=nodes_resource.keys()[0],resource_val=nodes_resource.values()[0])
            
    
    def GetNodeDisk(self):
        disks = self.__server.get_hosts()
        for disk_mor,disk_name in disks.items():
            nodes = node.objects.filter(node_id=disk_mor,conn=self.__vc_id)
            if nodes.count() > 0:
                p = VIProperty(self.__server, disk_mor)
                for ds in p.datastore:
                    disk_rs = node_disk.objects.filter(datastore_id = ds._obj,conn=self.__vc_id)
                    if disk_rs.count() == 0:
                        new = dict()
                        new['datastore_id'] = ds._obj
                        new['name'] = 0
                        new['total'] = 0
                        new['free'] = 0
                        new['assign'] = 0
                        new['node'] = nodes[0]
                        new['conn'] = self.__vc_id
                        node_disk(**new).save()
    
    def UpdateNodeDisk(self):
        for ds_mor, name in self.__server.get_datastores().items():
            props = VIProperty(self.__server, ds_mor)
            new=dict()
            new['name'] = name
            new['total'] = props.summary.capacity
            new['free'] = props.summary.freeSpace
            node_disk.objects.filter(datastore_id=ds_mor).update(**new)
            
    def GetNodeNetwork(self):
        try:
            host = self.__server.get_hosts()
            for y,z in host.items():
                node_rs = node.objects.filter(node_id=y,name=z,conn=self.__vc_id)
                if node_rs.count() == 1:
                    prop = VIProperty(self.__server, y)
                    for pg in prop.configManager.networkSystem.networkInfo.portgroup:
                        new = {'node':node_rs[0]}
                    #print pg.spec.name 虚拟端口组名,'----',pg.spec.vswitchName所在交换机名,pg.spec.vlanId vlanid
                        new['name'] = pg.spec.name
                        new['vswitch'] = pg.spec.vswitchName
                        new['vlan'] = pg.spec.vlanId
                        new['type'] = 0
                        new['conn'] = self.__vc_id
                        check_rs = node_network.objects.filter(**new)
                        new['times'] = str(int(time.time()))
                        node_network(**new).save() if check_rs.count() == 0 else check_rs.update(times=str(int(time.time())))
        except Exception,e:
            pass
    
    def GetDVS(self):
        try:
            s = self.__server
            for x, y in s.get_datacenters().items():
                dcprops = VIProperty(s, x)
                dc = datacenter.objects.get(conn=self.__vc_id,name=y)
                hfmor = dcprops.networkFolder._obj
                dvpg_mors = s._retrieve_properties_traversal(property_names=['name','portgroup','summary.hostMember'],
                                                    from_node=hfmor, obj_type='DistributedVirtualSwitch')
                for item in dvpg_mors:
                    DVS = dict()
                    for p in item.PropSet:
                        if p.Name == 'name':
                            DVS['name'] = p.Val
                        if p.Name == 'portgroup':
                            portgroup = list()
                            pg_mors = p.Val.ManagedObjectReference
                            for pg_mor in pg_mors:
                                key_mor = s._get_object_properties(pg_mor, property_names=['config.name'])
                                for key in key_mor.PropSet:
                                    portgroup.append(key.Val)
                            DVS['portgroup'] = portgroup
                        if p.Name == 'summary.hostMember':
                            host = list()
                            pg_mors = p.Val.ManagedObjectReference
                            for pg_mor in pg_mors:
                                key_mor = s._get_object_properties(pg_mor, property_names=['name'])
                                for key in key_mor.PropSet:
                                    host.append(key.Val)
                            DVS['host'] = host
                    
                    mysql_dvs = {'type':1,'conn':self.__vc_id}
                    mysql_dvs['vswitch'] = DVS['name']
                    for q in DVS['portgroup']:
                        mysql_dvs['name'] = q
                        for w in DVS['host']:
                            mysql_dvs['node'] = node.objects.get(name=str(w),conn=self.__vc_id)
                            rs = node_network.objects.filter(**mysql_dvs)
                            if rs.count() == 0:
                                mysql_dvs['times'] = str(int(time.time()))
                                mysql_dvs['vlan'] = 0
                                mysql_dvs['todc'] = dc
                                node_network(**mysql_dvs).save()
                                del mysql_dvs['times']
                                del mysql_dvs['vlan']
                            else:
                                rs.update(times = str(int(time.time())))
        except Exception,e:
            pass
        
    def GetDvsKey(self):
        dc_dict = dict()
        for x, y in self.__server.get_datacenters().items():
            dcprops = VIProperty(self.__server, x)
            nfmor = dcprops.networkFolder._obj
            dvpg_mors = self.__server._retrieve_properties_traversal(property_names=['name','key'],
                                            from_node=nfmor, obj_type='DistributedVirtualPortgroup')
            if dvpg_mors:
                dvs_dict = dict()
                for dvpg in dvpg_mors:
                    for p in dvpg.PropSet:
                        if p.Name == "name":
                            dvs = p.Val
                        if p.Name == "key":
                            portgroupKey = p.Val
                    if all((dvs,portgroupKey)):
                        dvs_dict[dvs] = portgroupKey
                dc_dict[y] = dvs_dict
        return dc_dict
            
    
    def SaveDvsKey(self,dc_dict):
        for x,y in dc_dict.items():
            if all((x,y)):
                dc = datacenter.objects.get(conn=self.__vc_id,name=x)
                dc_nodes = node.objects.filter(dc=dc).values_list('id')
                dc_node_list = list()
                [ dc_node_list.append(int(x[0])) for x in dc_nodes if len(x) > 0]
                for m,n in y.items():
                    rs = node_network.objects.filter(name=m,node__id__in=dc_node_list).update(portkey=n)
            
            
            
    def MainCycle(self):
        dcs = self.GetDatacenter()
        nodes_belong = self.GetCluster(dcs)
        self.GetHost(dcs)
        self.UpdateHost(nodes_belong)
        self.UpdateResource()
        self.GetNodeDisk()
        self.UpdateNodeDisk()
        self.GetNodeNetwork()
        self.GetDVS()
        dvs_rs = self.GetDvsKey()
        self.SaveDvsKey(dvs_rs)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

