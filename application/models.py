#-*- coding:utf-8 -*-

'''
@Created on 2016年5月24日
 
@author: MianBao

@author_web: Mianbao.cn.com

@User
'''
from django.db import models
from User.models import user,department



class where(models.Model):        
    name = models.CharField(max_length=50,null=False)

class room(models.Model):        
    name = models.CharField(max_length=50,null=False)
    
class env(models.Model):        
    name = models.CharField(max_length=50,null=False)
    
class asset(models.Model):        
    ip = models.CharField(max_length=50,null=False)
    name = models.CharField(max_length=50,null=True)
    towhere = models.ForeignKey(where)
    toroom = models.ForeignKey(room)
    toenv = models.ForeignKey(env)
    belongu = models.ForeignKey(user,null=False)
    remark = models.TextField(null=True)
    department = models.ForeignKey(department)

class project(models.Model):
    name = models.CharField(max_length=50,null=True)
    belongu = models.ForeignKey(user,null=False)
    devu = models.CharField(max_length=50,null=False)
    examu = models.CharField(max_length=50,null=False)
    remark = models.TextField(null=True)
    
class cluster(models.Model):
    name = models.CharField(max_length=50,null=True)
    types = models.ForeignKey(env)
    port = models.CharField(max_length=50,null=True)
    sadd = models.CharField(max_length=50,null=True)
    remark = models.TextField(null=True)
    toproject = models.ForeignKey(project,null=False,default=1)
    host = models.ManyToManyField(asset)

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    