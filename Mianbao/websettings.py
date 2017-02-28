#-*- coding:utf-8 -*-

'''
@Created on 2016年5月10日
 
@author: MianBao

@author_web: Mianbao.cn.com

@ Public function
'''

from models import webset,system


class websetting:
    
    def __init__(self):
        self.__websets = webset.objects.filter()
    
    def Gettitle(self):
        if len(self.__websets) == 1:
            return self.__websets[0].title
        else:
            return u'面包CMDB资产管理v2.0'
        
    def GetMd5Add(self):
        '''
        @获取密码杂项
        '''
        try:
            pwd_add = system.objects.get(id=1).md5_add
            return pwd_add
        except Exception,e:
            return 1
        
    def GetMailAdd(self):
        '''
        @获取邮箱后缀
        '''
        try:
            mail_add = system.objects.get(id=1).mail_add
            return mail_add if mail_add else '@mianbao.cn.com'
        except Exception,e:
            return 1
        
        
        