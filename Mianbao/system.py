#-*- coding:utf-8 -*-

'''
@Created on 2016年5月10日
 
@author: MianBao

@author_web: Mianbao.cn.com

@ The system default setting.
'''
import time
import string
from random import choice

from models import system,webset
from User.User_Class import User,Group,Permission,Department
from websettings import websetting


class System():
    
    def __init__(self):
        self.titles = webset.objects.filter()
        self.__uid = None
    
    def Init(self):
        self.InitPasswordAdd()
        self.InitGroup()
        self.InitPower()
        self.InitDepartment()
        self.InitCreateUser()
        self.InitUserPowerLink()
        
    def Check(self):
        try:
            md5_add = system.objects.get(id=1).md5_add
            return False if md5_add else True
        except Exception,e:
            return True
    
    def InitPasswordAdd(self):
        '''
        @check the passwd add,if None add
        '''
        if self.Check():
            new = dict()
            new['md5_add'] = self.GenPasswordAdd()
            rs = system(**new)
            rs.save()
        '''
        @check title and name , if None add
        '''
        
    def GenPasswordAdd(self,length=8,chars=string.ascii_letters+string.digits):
        '''
        @生成随机密码
        '''
        return ''.join([choice(chars) for i in range(length)])
    
    def InitGroup(self):
        group = Group()
        if group.GroupNum() == 0:
            group_dict = [
                {'name':u'超级管理员','remark':u'超级管理员'},
                {'name':u'普通用户','remark':u'普通注册用户所属用户组'},
                {'name':u'vMware_Wechat','remark':u'微信通知专用组'},
                {'name':u'VMware管理','remark':u'VMware平台管理'},   
            ]
            
            for x in group_dict:
                print x
                group.Add(x)

    def InitPower(self):
        power = Permission()
        if power.PermissionNum() == 0:
            power_list = [
                {'name':u'user_list','introduction':u'列出现有用户列表'},
                {'name':u'user_add','introduction':u'新增系统用户'},
                {'name':u'group_add','introduction':u'新增用户组'},
                {'name':u'group_update','introduction':u'更新用户组'},
                {'name':u'user_del','introduction':u'删除系统用户'},
                {'name':u'user_update','introduction':u'更新用户信息'},
                {'name':u'group_list','introduction':u'列出用户组'},
                {'name':u'group_del','introduction':u'删除用户组'},
                {'name':u'vmware_manage','introduction':u'虚拟化管理'},
                {'name':u'vmware_network','introduction':u'虚拟化网络信息管理'},
                {'name':u'vmware_ip','introduction':u'虚拟化IP地址池管理'},
                {'name':u'vmware_resource','introduction':u'虚拟化资源池管理'},
                {'name':u'vmware_customize','introduction':u'虚拟化自定义规范'},
                {'name':u'vmware_vc','introduction':u'虚拟化VC设置'},
                {'name':u'vm_manage','introduction':u'虚拟机管理'},
                ]
            
            for x in power_list:
                power.Add(x)
    
    def InitDepartment(self):
        depart = Department()
        if depart.Num() == 0:
            depart_list= [
                    {'name':u'运维部'}
                ]
             
            for x in depart_list:
                depart.Add(x)
         
    def InitCreateUser(self):
        '''
        @生成默认用户及密码
        '''
        users = User()
        depart = Department()
        webconfig = websetting()
        if users.UserNum() == 0:
            form_value = {'name':u'mianbao',
                          'password':u'mianbao.cn.com',
                          'password2':u'mianbao.cn.com',
                          'tel':u'18888888888',
                          'department':u'%s' % depart.GetId(u'运维部')}
            form_value['register_time'] = time.time()
            form_value['last_login'] = time.time()
            form_value['mail'] = str(form_value['name']) + str(webconfig.GetMailAdd())
            form_value['active'] = u'0' #the mail no active
            self.__uid = users.Add(form_value)
            users.ActiveMianbao()
            
    def InitUserPowerLink(self):
        gp = Group()
        power = Permission()
        user = User(self.__uid)
        if (user.GetUserPermission().count() == 0 or user.GetUserGroup().count() == 0 ) and self.__uid:
            link_dict = {
                'group':[gp.GetId(u'超级管理员')],
                'ownpe':power.GetAllId()
                }
            user.UserGroupUpdate(link_dict)
        
        
        
        
        
        
        
        
        