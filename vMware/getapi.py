#-*- coding:utf-8 -*-

'''
@Created on 2016年5月20日
 
@author: MianBao

@author_web: Mianbao.cn.com

@系统设置
'''
from connect import con
from Mianbao.public import *

import time
import json
import pprint
from pysphere import MORTypes


class api:
    
    def __init__(self,Server=None):
        self.__Server = Server
        self.__tools = None
        self.__props = None
        self.__properties_name = None
        self.__vm_properties = None
    
    def ApiKeyList(self):
        update_name_dict = {"summary.runtime.maxCpuUsage":"hz","guest.toolsStatus":"vmtools","config.template":"type","summary.vm":"vmsid",}
        return update_name_dict
    
    def ApiMemorysDict(self):
        memory_key_dict = {"summary.quickStats.hostMemoryUsage":"memory","summary.quickStats.overallCpuUsage":"cpu"}
        return memory_key_dict
    
    def ApiRunDict(self):
        run_key_dict = {"summary.runtime.powerState":"power","summary.runtime.bootTime":"ptime","summary.runtime.host":"runhost"}
        return run_key_dict
        
    def PropertiesParameter(self):
        ls = ['summary.vm','summary.config.numEthernetCards','summary.config.annotation','summary.config.numVirtualDisks','summary.quickStats.overallCpuUsage','summary.quickStats.hostMemoryUsage','summary.runtime.bootTime','summary.runtime.powerState','summary.runtime.host','summary.runtime.maxCpuUsage','guest.toolsStatus','guest.guestFullName','guest.guestState','guest.hostName','name','config.template','config.hardware.numCPU','config.hardware.memoryMB',]
        return ls
    
    def ToolsStatusCheck(self):
        #guest_tools_status_error = ['guestToolsNotInstalled','guestToolsSupportedNew','guestToolsUnmanaged']
        guest_tools_status_ok = ['toolsOk','guestToolsCurrent', 'guestToolsNeedUpgrade', 'guestToolsSupportedOld', 'guestToolsTooNew', 'guestToolsTooOld']
        return True if self.__tools in guest_tools_status_ok else False
        
    def GetVmsFromApi(self):
        Parameter = self.PropertiesParameter()
        type_par = 'VirtualMachine'
        self.__props = self.__Server._retrieve_properties_traversal(property_names=Parameter,obj_type=type_par)
    
    def GetVmsFromApiDict(self):
        vms_key_dict = {'summary.runtime.maxCpuUsage':'hz','guest.toolsStatus':'vmtools','config.template':'type','summary.vm':'vmsid'}
        return vms_key_dict
        
    def PropsConvertDict(self):
        allvms = list()
        needs = self.ApiKeyList()
        for prop in self.__props:
            allvms = self.ApiDataProcess(prop, needs, allvms)
        return allvms
    
    def ApiDataProcess(self,prop,needs,allvms):
        vm = dict()
        memory = dict()
        run = dict()
        for m in prop.PropSet:
            '''
            @vms api
            '''
            needs_name = needs.get(m.Name,None)
            if needs_name:
                vm[needs_name] =  m.Val
            
            '''
            @获取虚拟机的tools
            '''
            if m.Name == "guest.toolsStatus":
                self.__tools = m.Val
            
            '''
            @获取虚拟机名称，传递给getpoweronvmproperties
            '''
            if m.Name == 'name':
                self.__properties_name=m.Val
            
            '''
            @生成Api run
            '''
            run_key_dict = self.ApiRunDict()
            needs_run = run_key_dict.get(m.Name,None)
            if needs_run:
                run[needs_run] = time.mktime(m.Val) if needs_run == 'ptime' else m.Val
            
            '''
            @生成Api memory
            '''
            
            memory_key_dict = self.ApiMemorysDict()
            needs_memory = memory_key_dict.get(m.Name,None)
            if needs_memory:
                memory[needs_memory] = m.Val
            
        vms_properties = self.GetPoweronVmProperties() if self.ToolsStatusCheck() else self.GetPoweroffVmProperties()
        
        '''
        @合并API和properties的vms
        '''
        vms_properties['vms'] = dict(vms_properties['vms'],**vm)
        
        '''
        @run 合并
        '''
        vms_properties['run'] = dict(vms_properties['run'],**run)
        
        '''
        @memory 合并
        '''
        vms_properties['memorys'] = memory
        
        vms_properties = self.GenerateHash(vms_properties)
        vms_properties['vmsid'] = vms_properties['vms']['vmsid']
        allvms.append(vms_properties)
        return allvms
    
    def GenerateHash(self,dicts):
        hash_dict = dict()
        for x,y in dicts.items():
            hash_dict[str(x)] = Md5s(str(json.dumps(y)))
        dicts['hash'] = hash_dict
        return dicts
    
    def VmsGetKeyDict(self):
        vms_key_list = {'num_cpu':'Core','memory_mb':'memory','hostname':'dnsname','guest_full_name':'systemversion','name':'name'}
        return vms_key_list
    
    def NetworkGetKeyDict(self):
        network_key_list = {'ip_addresses':'ip','mac_address':'mac','network':'uplink','connected':'connect'}
        return network_key_list
    
    def DiskGetKeyDict(self):
        disk_key_list = {'capacity':'total','committed':'used','unitNumber':'solts'}
        return disk_key_list
    
    def GetVmProperties(self):
        vm = self.__Server.get_vm_by_name(self.__properties_name)
        self.__vm_properties = vm.get_properties()
        allvms = dict()
        
        '''
        @run dict
        '''
        vm_folder = vm.properties.parent.name
        allvms['run'] = {'folder':vm_folder}
        
        '''
        @属性部分值获取
        '''
        vms = dict()
        vms_key_dict = self.VmsGetKeyDict()
        for key,val in vms_key_dict.items():
            vm_get = self.__vm_properties.get(key,None)
            vms[val] = vm_get if vm_get is not None else '0000000000'
        allvms['vms'] = vms
        
        '''
        @硬盘信息获取
        '''
        disk = list()
        disks = self.__vm_properties.get('disks',None)
        disk_key_dict = self.DiskGetKeyDict()
        for z in disks:
            disk_dict = dict()
            for m,n in disk_key_dict.items():
                disk_dict[n] = z.get('device').get(m,None) if m == 'unitNumber' else z.get(m,None)
            disk.append(disk_dict)
        allvms['disk'] = disk
        return allvms
        
    def GetPoweronVmProperties(self):
        allvms = self.GetVmProperties()
        net = list()
        nets = self.__vm_properties.get('net')
        net_key_dict = self.NetworkGetKeyDict()
        if len(nets) > 0: 
            for x in nets:
                net_dict = dict()
                for m,n in net_key_dict.items():
                    if m == 'ip_addresses':
                        #屏蔽网卡没连接的报错
                        if x.get('connected') == False:
                            net_dict[n] = 0
                        else:
                            ip_list = x.get(m,'00000')
                            net_dict[n] = ip_list[0] if len(ip_list) > 0 else '0.0.0.0'
                    else:
                        x.get(m,'00000')   
                net.append(net_dict)
        allvms['network'] = net
        return allvms  

    def GetPoweroffVmProperties(self):
        allvms = self.GetVmProperties()
        net = list()
        net_value_dict = self.__vm_properties.get('devices')
        for m in net_value_dict.keys():
            if int(m) >= 4000 and int(m) < 4999:
                if net_value_dict.get(m).get('type') in self.network_type_list():
                    nets_dict = dict()
                    nets_dict['mac'] = net_value_dict.get(m).get('macAddress',None)
                    nets_dict['uplink'] = net_value_dict.get(m).get('summary',None)
                    nets_dict['ip'] = 0
                    nets_dict['connect'] = 0
                    nets_dict['status'] = 0
                    net.append(nets_dict)
        allvms['network'] = net
        return allvms
                
    def network_type_list(self):
        net_list = ["VirtualE1000", "VirtualE1000e", "VirtualPCNet32", "VirtualVmxnet", "VirtualVmxnet3"]
        return net_list
    
    
    
    
    
    

