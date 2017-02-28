#-*- coding:utf-8 -*-

'''
@Created on 2016年5月9日
 
@author: MianBao

@author_web: Mianbao.cn.com

@User
'''
from django.db import models



class group(models.Model):
    name = models.CharField(max_length=30)
    remark = models.TextField(null=True)
    active = models.IntegerField()
    
class permission(models.Model):
    name = models.CharField(max_length=30)
    introduction = models.CharField(max_length=30)
    permission_group = models.ManyToManyField(group)
    active = models.IntegerField()
    
class department(models.Model):
    name = name = models.CharField(max_length=30)
    active = models.IntegerField()
    
class user(models.Model):
    name = models.CharField(max_length=30)
    tel = models.CharField(max_length=30)
    password = models.CharField(max_length=100)
    register_time = models.CharField(max_length=30)
    last_login = models.CharField(max_length=30)
    mail = models.EmailField()
    active = models.IntegerField()
    
    user_group = models.ManyToManyField(group)
    user_permission = models.ManyToManyField(permission)
    user_department = models.ManyToManyField(department)









