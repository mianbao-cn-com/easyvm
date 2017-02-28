#-*- coding:utf-8 -*-

'''
@Created on 2016年5月9日
 
@author: MianBao

@author_web: Mianbao.cn.com

@系统设置
'''
import pysphere
import sys
import time
import os

from pysphere.resources import VimService_services as VI
from pysphere import VIException, VIApiException, FaultTypes
from pysphere import VITask, VIProperty, VIMor, MORTypes
from pysphere.vi_snapshot import VISnapshot


class mianbao(pysphere.vi_virtual_machine.VIVirtualMachine):
    
    def clone(self, name, sync_run=True, folder=None, resourcepool=None, 
              datastore=None, host=None, power_on=True, template=False, 
              snapshot=None, linked=False,customize=None, data=None):
        """Clones this Virtual Machine
        @name: name of the new virtual machine
        @sync_run: if True (default) waits for the task to finish, and returns
            a VIVirtualMachine instance with the new VM (raises an exception if 
        the task didn't succeed). If sync_run is set to False the task is 
        started and a VITask instance is returned
        @folder: name of the folder that will contain the new VM, if not set
            the vm will be added to the folder the original VM belongs to
        @resourcepool: MOR of the resourcepool to be used for the new vm. 
            If not set, it uses the same resourcepool than the original vm.
        @datastore: MOR of the datastore where the virtual machine
            should be located. If not specified, the current datastore is used.
        @host: MOR of the host where the virtual machine should be registered.
            IF not specified:
              * if resourcepool is not specified, current host is used.
              * if resourcepool is specified, and the target pool represents a
                stand-alone host, the host is used.
              * if resourcepool is specified, and the target pool represents a
                DRS-enabled cluster, a host selected by DRS is used.
              * if resource pool is specified and the target pool represents a 
                cluster without DRS enabled, an InvalidArgument exception be
                thrown.
        @power_on: If the new VM will be powered on after being created. If
            template is set to True, this parameter is ignored.
        @template: Specifies whether or not the new virtual machine should be 
            marked as a template.         
        @snapshot: Snaphot MOR, or VISnaphost object, or snapshot name (if a
            name is given, then the first matching occurrence will be used). 
            Is the snapshot reference from which to base the clone. If this 
            parameter is set, the clone is based off of the snapshot point. This 
            means that the newly created virtual machine will have the same 
            configuration as the virtual machine at the time the snapshot was 
            taken. If this parameter is not set then the clone is based off of 
            the virtual machine's current configuration.
        @linked: If True (requires @snapshot to be set) creates a new child disk
            backing on the destination datastore. None of the virtual disk's 
            existing files should be moved from their current locations.
            Note that in the case of a clone operation, this means that the 
            original virtual machine's disks are now all being shared. This is
            only safe if the clone was taken from a snapshot point, because 
            snapshot points are always read-only. Thus for a clone this option 
            is only valid when cloning from a snapshot
        """
        try:
            #get the folder to create the VM
            folders = self._server._retrieve_properties_traversal(
                                         property_names=['name', 'childEntity'],
                                         obj_type=MORTypes.Folder)
            folder_mor = None
            for f in folders:
                fname = ""
                children = []
                for prop in f.PropSet:
                    if prop.Name == "name":
                        fname = prop.Val
                    elif prop.Name == "childEntity":
                        children = prop.Val.ManagedObjectReference
                if folder == fname or (not folder and self._mor in children):
                    folder_mor = f.Obj
                    break
            if not folder_mor and folder:
                raise VIException("Couldn't find folder %s" % folder,
                                  FaultTypes.OBJECT_NOT_FOUND)
            elif not folder_mor:
                raise VIException("Error locating current VM folder",
                                  FaultTypes.OBJECT_NOT_FOUND)
    
            request = VI.CloneVM_TaskRequestMsg()
            _this = request.new__this(self._mor)
            _this.set_attribute_type(self._mor.get_attribute_type())
            request.set_element__this(_this)
            request.set_element_folder(folder_mor)
            request.set_element_name(name)
            spec = request.new_spec()
            if template:
                spec.set_element_powerOn(False)
            else:
                spec.set_element_powerOn(power_on)
            location = spec.new_location()
            if resourcepool:
                if not VIMor.is_mor(resourcepool):
                    resourcepool = VIMor(resourcepool, MORTypes.ResourcePool)
                pool = location.new_pool(resourcepool)
                pool.set_attribute_type(resourcepool.get_attribute_type())
                location.set_element_pool(pool)
            if datastore:
                if not VIMor.is_mor(datastore):
                    datastore = VIMor(datastore, MORTypes.Datastore)
                ds = location.new_datastore(datastore)
                ds.set_attribute_type(datastore.get_attribute_type())
                location.set_element_datastore(ds)
            if host:
                if not VIMor.is_mor(host):
                    host = VIMor(host, MORTypes.HostSystem)
                hs = location.new_host(host)
                hs.set_attribute_type(host.get_attribute_type())
                location.set_element_host(hs)
            if snapshot:
                sn_mor = None
                if VIMor.is_mor(snapshot):
                    sn_mor = snapshot
                elif isinstance(snapshot, VISnapshot):
                    sn_mor = snapshot._mor
                elif isinstance(snapshot, basestring):
                    for sn in self.get_snapshots():
                        if sn.get_name() == snapshot:
                            sn_mor = sn._mor
                            break
                if not sn_mor:
                    raise VIException("Could not find snapshot '%s'" % snapshot,
                                      FaultTypes.OBJECT_NOT_FOUND) 
                snapshot = spec.new_snapshot(sn_mor)
                snapshot.set_attribute_type(sn_mor.get_attribute_type())
                spec.set_element_snapshot(snapshot)
            
            if linked and snapshot:
                location.set_element_diskMoveType("createNewChildDiskBacking")

            if not template and customize:
                if data is None:
                    raise VIApiException("Cannot use Customization without data")

                customization = spec.new_customization()
                spec.set_element_customization(customization)

                globalIPSettings = customization.new_globalIPSettings()
                customization.set_element_globalIPSettings(globalIPSettings)


                # nicSettingMap
                nicSetting = customization.new_nicSettingMap()
                adapter = nicSetting.new_adapter()
                nicSetting.set_element_adapter(adapter)
                
                ipAddress = data.get('ip')
                netmask = data.get('netmask')
                gateway = data.get('gateway')
                
                fixedip = VI.ns0.CustomizationFixedIp_Def("ipAddress").pyclass()
                fixedip.set_element_ipAddress(ipAddress)
                
                
                
                #dhcp = VI.ns0.CustomizationDhcpIpGenerator_Def("ip").pyclass()
                adapter.set_element_ip(fixedip)
                adapter.set_element_subnetMask(netmask)
                #help(adapter.set_element_gateway([gateway,]))
                adapter.set_element_gateway([gateway,])

                nicSetting.set_element_adapter(adapter)
                customization.set_element_nicSettingMap([nicSetting,])

                if customize == "SYSPREP":
                    # here starts windows
                    identity = VI.ns0.CustomizationSysprep_Def("identity").pyclass()
                    customization.set_element_identity(identity)

                    guiUnattended = identity.new_guiUnattended()
                    guiUnattended.set_element_autoLogon(True)
                    guiUnattended.set_element_autoLogonCount(1)

                    passw = guiUnattended.new_password()
                    guiUnattended.set_element_password(passw)
                    passw.set_element_value( data["adminpw"] )
                    passw.set_element_plainText(True)

                    # http://msdn.microsoft.com/en-us/library/ms912391(v=winembedded.11).aspx
                    # 85 is GMT Standard Time
                    timeZone = data.get("timezone", 85)
                    guiUnattended.set_element_timeZone(timeZone)
                    identity.set_element_guiUnattended(guiUnattended)

                    userData = identity.new_userData()
                    userData.set_element_fullName( data.get("fullName", "PyShere"))
                    userData.set_element_orgName( data.get("orgName", "PySphere") )
                    userData.set_element_productId("")
                    computerName = VI.ns0.CustomizationFixedName_Def("computerName").pyclass()
                    computerName.set_element_name(name.replace("_", ""))
                    userData.set_element_computerName( computerName )
                    identity.set_element_userData(userData)

                    identification = identity.new_identification()

                    if data.get("joinDomain", False):
                        # join the domain
                        identification.set_element_domainAdmin( data["domainAdmin"] )
                        domainAdminPassword = identification.new_domainAdminPassword()
                        domainAdminPassword.set_element_plainText(True)
                        domainAdminPassword.set_element_value( data["domainAdminPassword"] )
                        identification.set_element_domainAdminPassword(domainAdminPassword)
                        identification.set_element_joinDomain( data["joinDomain"] )
                        identity.set_element_identification(identification)
                elif customize == "SYSPREPTEXT":
                    identity = VI.ns0.CustomizationSysprepText_Def("identity").pyclass()
                    customization.set_element_identity(identity)
                    identity.set_element_value(data["value"])

                elif customize == "LINUX":
                    identity = VI.ns0.CustomizationLinuxPrep_Def("identity").pyclass()
                    customization.set_element_identity(identity)
                    identity.set_element_domain( data["domain"])
                    hostName = VI.ns0.CustomizationFixedName_Def("hostName").pyclass()
                    hostName.set_element_name(name.replace("_", ""))
                    identity.set_element_hostName(hostName)

            spec.set_element_location(location)    
            spec.set_element_template(template)
            request.set_element_spec(spec)
            task = self._server._proxy.CloneVM_Task(request)._returnval
            vi_task = VITask(task, self._server)
            if sync_run:
                status = vi_task.wait_for_state([vi_task.STATE_SUCCESS,
                                                 vi_task.STATE_ERROR])
                if status == vi_task.STATE_ERROR:
                    raise VIException(vi_task.get_error_message(),
                                      FaultTypes.TASK_ERROR)
                return mianbao(self._server, vi_task.get_result()._obj) 
                
            return vi_task

        except (VI.ZSI.FaultException), e:
            raise VIApiException(e)