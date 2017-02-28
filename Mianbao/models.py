#-*- coding:utf-8 -*-

'''
@Created on 2016年5月9日
 
@author: MianBao

@author_web: Mianbao.cn.com

@系统设置
'''
from django.db import models



class system(models.Model):
    md5_add = models.CharField(max_length=50,null=False)
    mail_add = models.CharField(max_length=50,null=True)
    mail_smtp = models.CharField(max_length=50,null=True)
    mail_user = models.CharField(max_length=50,null=True)
    mail_pwd = models.CharField(max_length=50,null=True)
    
class webset(models.Model):
    title = models.CharField(max_length=50,null=False)
    name = models.CharField(max_length=50,null=False)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    