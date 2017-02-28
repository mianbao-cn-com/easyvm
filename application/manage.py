#-*- coding:utf-8 -*-
'''
@Created on 2016年5月20日
 
@author: MianBao

@author_web: Mianbao.cn.com

@application 管理处理主程序
'''
from User.User_Class import User
from User.models import department
from application.models import *

class Application:
    
    def __init__(self):
        pass
    
    def AssetSave(self,dic):
        if isinstance(dic,dict):
            dic = self._DicHandle(dic)
            asset_obj = asset(**dic)
            rs = asset_obj.save()
            
    def HostUpdate(self,id,dic):
        if isinstance(dic,dict):
            dic = self._DicHandle(dic)
            del dic['belongu']
            update_rs = asset.objects.filter(id=id).update(**dic)
        
    def _DicHandle(self,dic):
        
        #handle the user
        if dic.has_key('belongu'):
            user = User(dic['belongu'])
            dic['belongu'] = user.GetUser()
        
        #handle the env
        dic['toenv'] = env.objects.get(id=dic['toenv'])
        
        #handle the department
        dic['department'] = department.objects.get(id=dic['department'])
        
        #handle the where
        dic['towhere'] = where.objects.get(id=dic['towhere'])
        
        #handle the room
        dic['toroom'] = room.objects.get(id=dic['toroom'])
        
        return dic
    
    def ProjectSave(self,dic):
        if isinstance(dic,dict):
            
            #handle the user
            user = User(dic['belongu'])
            dic['belongu'] = user.GetUser()
            
            rs = project(**dic)
            id = rs.save()
            
    def ProjectUpdate(self,dic):
        if isinstance(dic,dict):
            user = User(dic['belongu'])
            dic['belongu'] = user.GetUser()
            id = dic['id']
            del dic['id']
            project.objects.filter(id=id).update(**dic)
            
    def ClusterSave(self,dic):
        if isinstance(dic,dict):
            
            #handle the env
            dic['types'] = env.objects.get(id=dic['types'])
            
            dic['toproject'] = project.objects.get(id=dic['toproject'])
            
            rs = cluster(**dic)
            id = rs.save()
            
    def ClusterUpdate(self,dic):
        if isinstance(dic,dict):
            dic['types'] = env.objects.get(id=dic['types'])
            id = dic['id']
            del dic['id']
            clusters = cluster.objects.filter(id=id)
            toprojects = clusters.first()
            clusters.update(**dic)
            return toprojects.toproject.id
            
            
            