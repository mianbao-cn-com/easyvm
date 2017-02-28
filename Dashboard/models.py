#-*- coding:utf-8 -*-

'''
@Created on 2016年5月11日
 
@author: MianBao

@author_web: Mianbao.cn.com

@User
'''

from django.db import models

class group(models.Model):
    name = models.CharField(max_length=30)

class permission(models.Model):
    permission_num = models.IntegerField()
    name = models.CharField(max_length=30)
    
    permission_group = models.ManyToManyField(group)

class user(models.Model):
    name = models.CharField(max_length=30)
    tel = models.CharField(max_length=30)
    password = models.CharField(max_length=100)
    createdate = models.CharField(max_length=30)
    register_time = models.CharField(max_length=30)
    last_login = models.CharField(max_length=30)
    mail = models.EmailField()
    active = models.IntegerField()
    
    user_group = models.ManyToManyField(group)
    user_permission = models.ManyToManyField(permission)










