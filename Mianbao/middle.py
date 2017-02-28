#-*- coding:utf-8 -*-

'''
@Created on 2016年5月10日
 
@author: MianBao

@author_web: Mianbao.cn.com

@系统设置
'''

import time
from django.shortcuts import render,render_to_response,redirect,HttpResponse
from system import System
from User.models import user
from websettings import websetting

    
class Login_check(object):
    
    def process_request(self,request):
        '''
        @initial the default data
        '''
        initial_default = System()
        initial_default.Init()
        
        '''
        @Login Check and white list Check
        '''
        login = CheckSession(request)
        if not login.CheckWhite():
            rs = login.CheckLogin()
            websets = websetting()
            login.HistoryUrl()
            if rs:
                return redirect('/login/')
            else:
                rs_timeout = login.CheckSessionTimeout()
                if rs_timeout:
                    ret={'username':request.session.get('name',None),'title':websets.Gettitle()}
                    return render_to_response('lockscreen.html',ret)
                else:
                    request.session['logintime'] = time.time()
                    if login.CheckUserStatus():
                        if login.MustMailActive():
                            return redirect('/User/MailActive/')
                        else:
                            return redirect('/User/UpdatePwd/')
                
    def process_exception(self, request, exception):
        pass
    
    def process_response(self, request,response):
        pass
        return response
    

class CheckSession:
    
    def __init__(self,request):
        self.white_list = [u'/login/', u'/register/', u'/api/', u'/favicon.ico', u'/logout/']
        self.blurry_list = [u'Ajax',u'Active']
        self.white_url = [u'/login/', u'/register/', u'/api/', u'/favicon.ico', u'/logout/']
        self.blurry_white_list = [u'Active']
        self.request = request
        self.path = request.path
        self.uid = request.session.get('uid',None)
        self.mail = request.session.get('mail',None)
        self.logintime = request.session.get('logintime',None)
        
    def CheckWhite(self):
        rs = list()
        [ rs.append(y) for y in self.blurry_list if y in self.path ]
        white_rs = True if self.path in self.white_list else False
        return True if white_rs or len(rs) > 0 else False
    
    def CheckLogin(self):
        return False if all((self.uid,self.mail)) else True
    
    def HistoryUrl(self):
        history_url = self.request.META.get('PATH_INFO','/Dashboard/')
        history_url = '/Dashboard/' if history_url == '/' else history_url
        if history_url not in self.white_url:
            for x in self.blurry_white_list:
                if x not in history_url:
                    self.request.session['history_url'] = history_url
            
    def CheckSessionTimeout(self):
        now_time = time.time()
        return True if float(now_time) - float(self.logintime) > 3600 else False
        
    def CheckUserStatus(self):
        users = user.objects.get(id=self.uid).active
        self.__active = str(users)
        return True if str(users) in ['1','3',] and u'/User/UpdatePwd/' not in self.path else False
            
    def MustMailActive(self):
        return True if self.__active in ['1',] and u'/User/MailActive/' not in self.path else False
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    
    
