#-*- coding:utf-8 -*-

'''
@Created on 2016年5月10日
 
@author: MianBao

@author_web: Mianbao.cn.com

@ The User Class
'''

from models import *
from Mianbao.websettings import websetting
from django.db.models import Q

import md5
import time
import string
from random import choice



class User:
    
    def __init__(self,uid=None):
        self.__uid = uid
        self.__passwd = None
        pwd_adds = websetting()
        self.__pwd_add = pwd_adds.GetMd5Add()
        
    def UpdateLoginTime(self):
        user.objects.filter(id=self.__uid).update(last_login = time.time())
        
    def Del(self):
        user.objects.filter(id = self.__uid).update(Active = 1000)
        return 0
    
    def UpdatePasswd(self,oldpwd,passwd):
        self.__passwd = oldpwd
        oldpasswd = self.Md5s()
        mysql_user = user.objects.get(id=self.__uid)
        if oldpasswd == mysql_user.password:
            self.__passwd = passwd
            passwd = self.Md5s()
            mysql_user.password = passwd
            if str(mysql_user.active) == u'3':
                mysql_user.active = 0
            mysql_user.save()
            return True
        else:
            return False
    
    def Md5s(self):
        m = md5.new()
        m.update(self.__passwd + self.__pwd_add)
        rs = m.hexdigest()
        return rs
        
    def CheckLogin(self,userlist):
        self.__passwd = userlist['password']
        md5pwd = self.Md5s()
        userlist['password'] = md5pwd
        userlist['active__lt'] = 3
        rs = user.objects.filter(**userlist)
        return rs[0] if len(rs) == 1 else False
    
    def GenPassword(self,length=8,chars=string.ascii_letters+string.digits):
        '''
        @生成随机密码
        '''
        return ''.join([choice(chars) for i in range(length)])
    
    def Add(self,add_dict):
        if all(tuple(add_dict.values())):
            names = user.objects.filter(name=add_dict['name'],active__lt=9999)
            if len(names) == 0:
                if add_dict['password'] == add_dict['password2']:
                    self.__passwd = add_dict['password']
                    add_dict['password'] = self.Md5s()
                    dpid = add_dict['department']
                    del add_dict['department']
                    del add_dict['password2']
                    rs = user.objects.create(**add_dict)
                    rs.user_group.add(group.objects.get(name=u'普通用户'))
                    rs.user_department.add(department.objects.get(id=dpid))
                    rs.save()
                    return rs.id
    
    def ResetPwd(self):
        self.__passwd = self.GenPassword()
        md5_pwd = self.Md5s()
        userinfo = user.objects.get(id = self.__uid)
        userinfo.password = md5_pwd
        userinfo.save()
        return self.__passwd, userinfo.name
    
    def GetUser(self):
        rs = user.objects.filter(id=self.__uid)
        return rs[0] if len(rs) == 1 else False
    
    def GetUserList(self):
        rs = user.objects.filter(active=0).values('id','name')
        return rs
        
    def GetUserGroup(self):
        rs = group.objects.filter(user__id = self.__uid)
        return rs
            
    def GetUserOtherGroup(self):
        rs = group.objects.exclude(user__id = self.__uid)
        return rs
    
    def GetUserPermission(self):
        rs = permission.objects.filter(user__id = self.__uid)
        return rs
    
    def GetUserOtherPermission(self):
        rs = permission.objects.exclude(user__id = self.__uid)
        return rs
    
    def UserGroupUpdate(self,dicts):
        groups = dicts.get('group')
        ownpe = dicts.get('ownpe')
        
        user.objects.get(id=self.__uid).user_group.clear()
        user.objects.get(id=self.__uid).user_permission.clear()
        
        try:
            for x in groups:
                user.objects.get(id=self.__uid).user_group.add(group.objects.get(id=x))
                
            for y in ownpe:
                user.objects.get(id=self.__uid).user_permission.add(permission.objects.get(id=y))
                
            return True

        except Exception,e:
            return False

    def UserNum(self):
        user_num = user.objects.all().count()
        return user_num
    
    def ActiveMianbao(self):
        user.objects.filter(name=u'mianbao').update(active=0)
        return True
    
    def GetUserId(self,name):
        uid = user.objects.filter(name=name).first().id
        return uid
    
class Group:
    
    def __init__(self,gid=None):
        self.__gid = gid
    
    def Check(self):
        rs = group.objects.filter(name = self.__name,active__lt=9999)
        return False if len(rs) > 0 else True
        
    def Add(self,dicts):
        self.__name = dicts.get('name',None)
        if self.Check():
            dicts['active'] = 0
            rs = group(**dicts)
            rs.save()
            return True
        else:
            return False
    
    def Del(self):
        rs = user.objects.filter(active__lt = 9999 ,user_group__id = self.__gid).count()
        if rs == 0:
            gs = group.objects.get(id = self.__gid).delete()
            return True
        else:
            return False
        
    def GetGroupUser(self):
        rs = user.objects.filter(user_group = self.__gid)
        return rs
    
    def GetGroup(self):
        if self.__gid:
            rs = group.objects.get(id=self.__gid)
        else:
            rs = group.objects.filter()
        return rs
    
    def GetGroupPermission(self):
        rs = permission.objects.filter(permission_group__id = self.__gid)
        return rs
    
    def GetGroupOtherPermission(self):
        #rs = permission.objects.filter(Q(permission_group__id__lt = self.__gid)|Q(permission_group__id__gt = self.__gid))
        rs = permission.objects.exclude(permission_group = group.objects.get(id=self.__gid))
        return rs
    
    def UpdateGroup(self,dicts):
        group_pers = dicts.get('ownpe',[])
        del dicts['ownpe']
        group.objects.filter(id=self.__gid).update(**dicts)
        group.objects.get(id=self.__gid).permission_set.clear()
        try:
            if len(group_pers) > 0:
                for x in group_pers:
                    permission.objects.get(id=int(x)).permission_group.add(group.objects.get(id=self.__gid))
            return True
        except Exception,e:
            return False
    
    def GroupNum(self):
        group_num = group.objects.all().count()
        return group_num
    
    def GetId(self,name):
        group_id = group.objects.filter(name=name).first().id
        return group_id
    
    
        
class Permission():
    
    def __init__(self):
        pass
    
    def Add(self,dic):
        permission_num = permission.objects.filter(name=dic.get('name',None)).count()
        if permission_num == 0:
            dic['active'] = 0
            rs = permission(**dic)
            rs.save()
        
    def PermissionNum(self):
        permission_num = permission.objects.all().count()
        return permission_num
        
    def GetId(self,name):
        power_id = permission.objects.filter(name=name).first().id
        return power_id
    
    def GetAllId(self):
        id_list = list()
        id_lists = permission.objects.filter().values_list('id')
        [ id_list.append(x[0]) for x in id_lists if len(x) == 1 ]
        print id_list,'id_list'
        return id_list
    
class Department():
    
    def __init__(self):
        pass
    
    def Add(self,dic):
        department_num = department.objects.filter(name=dic.get('name',None)).count()
        if department_num == 0:
            dic['active'] = 0
            rs = department(**dic)
            rs.save()
    
    def Num(self):
        department_num = department.objects.all().count()
        return department_num
    
    def GetId(self,name):
        id = department.objects.filter(name=name).first().id
        return id
    




