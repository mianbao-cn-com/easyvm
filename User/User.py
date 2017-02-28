#-*- coding:utf-8 -*-

'''
@Created on 2016年5月10日
 
@author: MianBao

@author_web: Mianbao.cn.com

@ The User Class
'''
from django.shortcuts import render_to_response,redirect
from django.http.response import HttpResponse
from Mianbao.public import public,GetFormPost,CheckPermission,cper
from User_Class import User
from public_fun import *
from Public.publiclog import *
from django.db.models import Q
from Mianbao.middle import CheckSession
from vMware.models import bulletin


'''
@common
'''
#check login and write session
def Login(request):
    ret = public(request,'User-Register','用户','注册')
    if request.method == 'POST':
        form_key = ['name','password']
        form_value = GetFormPost(request,form_key)
        login_check = User()
        login_rs = login_check.CheckLogin(form_value)
        if login_rs:
            writsession(request,login_rs)
            UpdateLoginTime(request)
            PublicLog(login_rs.id,u'登录',1).Create
            jump_url = request.session.get('history_url','/Dashboard/')
            return redirect(jump_url)
        else:
            ret['message']='The Password or Username error!'
            return render_to_response('login.html',ret)
    else:
        ret['bulletins'] = bulletin.objects.filter(status=0,endtime__gt=time.time(),site__id__in=[1,2])
        login_redirect = CheckSession(request)
        return render_to_response('login.html',ret) if login_redirect.CheckLogin() else redirect('/Dashboard/')
            
#the register
def Register(request):
    ret = public(request,'User-Register','用户','注册')
    if request.method == 'POST':
        form_key = ['name','password','password2','tel','department']
        form_value = GetFormPost(request,form_key)
        form_value['register_time'] = time.time()
        form_value['last_login'] = time.time()
        form_value['mail'] = str(form_value['name']) + str(ret['mail_add'])
        form_value['active'] = 1 #the mail no active
        users = User()
        rs = users.Add(form_value)
        if rs:
            PublicLog(rs,u'用户注册',2).Create
            UserRegisterActive(request,rs,form_value['name'],form_value['register_time'])
            UserRegisterRight(ret)
        else:
            UserRegisterError(ret)
        return render_to_response('public/message.html',ret)
    else:
        ret['departments'] = GetGroup()
        return render_to_response('register.html',ret)

#logout,and destroy session and history url
def Logout(request):
    ret = public(request,'User-Logout','用户','退出')
    PublicLog(ret['uid'],u'退出登录',4).Create
    del request.session['logintime']
    del request.session['uid']
    del request.session['mail']
    del request.session['name']
    del request.session['dpid']
    del request.session['dpname']
    del request.session['permission']
    request.session['history_url'] = '/Dashboard/'
    return redirect('/login/')

def MailActive(request):
    ret = public(request,'User-Logout','用户','邮件激活')
    if request.method == 'POST':
        register_time = user.objects.get(id=ret['uid']).register_time
        UserRegisterActive(request,ret['uid'],ret['name'],register_time)
        ret['message'] = '=-=-=-=-=-=-=激活邮件已发送，请查收！=-=-=-=-=-=-='
        return render_to_response('user/mail_active_tip.html',ret)
    else:
        return render_to_response('user/mail_active_tip.html',ret)

     
'''
@ User manage
'''
@cper(u'user_list')
def List(request):
    ret = public(request,'User-List','用户','注册')
    ret['users'] = user.objects.filter(active__lt=9999)
    ret['bodycss'] = 'sidebar-collapse'
    return render_to_response('user/list.html',ret)

@cper(u'user_update')
def UserEdit(request,id):
    ret = public(request,'User-List','用户','编辑')
    users = User(id)
    if request.method == 'POST':
        if str(id) != str(ret['uid']) or ret['uid'] == 1:
            form_value = dict()
            form_value['group'] = request.POST.getlist('group')
            form_value['ownpe'] = request.POST.getlist('ownpe')
            users.UserGroupUpdate(form_value)
            PublicLog(ret['uid'],u'编辑用户 %s 的信息' % users.GetUser().name,5).Create
            return redirect('/User/')
        else:
            ret = UserEditError(ret)
            PublicLog(ret['uid'],u'编辑用户 %s 的信息' % users.GetUser().name,5,result = 1).Create
            return render_to_response('public/message.html',ret)
    else:
        ret['user'] = users.GetUser()
        ret['ingroup'] = users.GetUserGroup()
        ret['othergroup'] = users.GetUserOtherGroup()
        ret['inpermission'] = users.GetUserPermission()
        ret['otherpermission'] = users.GetUserOtherPermission()
        return render_to_response('user/edit.html',ret)

def Active(request,id,username,rtime):
    ret = public(request,'User-Active','用户','激活')
    id = int(id)/(1024*1024*1024*715)
    users = user.objects.filter(id = id,active = 1)
    if len(users) == 1:
        if username == Md5s(users[0].name) and Md5s(str(users[0].register_time)) == rtime:
            users[0].active = 0
            users[0].save()
            ret = UserActiveRight(ret)
            PublicLog(id,u'激活',6).Create
    else:
        ret = UserActiveError(ret)
        PublicLog(id,u'激活',6,result=1).Create
    return render_to_response('public/message.html',ret)

@cper(u'user_del')
def UserDel(request,id):
    ret = public(request,'User-Del','用户','删除')
    users = user.objects.get(id = id)
    if users.active == 1:
        users.user_group.remove()
        users.user_department.remove()
        users.delete()
        PublicLog(ret['uid'],u'删除用户 %s' % users.name,3).Create
    else:
        users.active = 10000
        users.save()
        PublicLog(ret['uid'],u'删除用户 %s' % users.name,3).Create
    return redirect('/User/')

@cper(u'user_update')
def PasswdRest(request,id):
    ret = public(request,'User-PasswdRest','User','PasswdRest')
    users = User(id)
    rs,name = users.ResetPwd()
    if rs:
        PublicLog(ret['uid'],u'重置 %s 密码' % name,4,id).Create
        UserResetPwd(request,rs,name)
        return redirect('/User/')
    else:
        ret = UserResetPwdError(ret)
        PublicLog(ret['uid'],u'重置 %s 密码' % name,4,id,1).Create
        return render_to_response('public/message.html',ret)

def PasswdUpdate(request):
    ret = public(request,'User-PasswdUpdate','用户','更改密码')
    if request.method == 'POST':
        form_key = ['nowPwd','newPwd','confirmPwd']
        form_value = GetFormPost(request,form_key)
        if form_value['newPwd'] == form_value['confirmPwd']:
            user_class = User(int(ret['uid']))
            rs = user_class.UpdatePasswd(form_value['nowPwd'],form_value['newPwd'])
            ret = UserUpdatePwdRight(ret) if rs else UserUpdatePwdError(ret)
            rs_status = 0 if ret['status'] == 'right' else 1
            PublicLog(ret['uid'],u'修改密码',5,result=rs_status).Create
            return render_to_response('public/message.html',ret)
    else:
        return render_to_response('user/MustRestPwd.html',ret)



'''
@ Group manage
'''
@cper(u'group_list')
def GroupList(request):
    ret = public(request,'User-Group','组','列表')
    if request.method == 'POST':
        form_key = ['name','remark']
        form_value = GetFormPost(request,form_key)
        groups = Group()
        rs = groups.Add(form_value)
        if rs:
            PublicLog(ret['uid'],u'新增 %s 组' % form_value['name'],9).Create
            return redirect('/User/group/')
        else:
            ret = GroupAddError(ret)
            PublicLog(ret['uid'],u'新增 %s 组' % form_value['name'],9,result=1).Create
            return render_to_response('public/message.html',ret)
    else:
        ret['groups'] = group.objects.filter(active__lt=9999)
        return render_to_response('user/group/list.html',ret)

@cper(u'group_del') 
def GroupDel(request,id): 
    ret = public(request,'User-Group','组','删除')
    group_name = group.objects.get(id=id).name
    groups = Group(id)
    rs = groups.Del()
    if not rs:
        ret = GroupDelError(ret)
        PublicLog(ret['uid'],u'删除 %s 组' % group_name,7,result=1).Create
        return render_to_response('public/message.html',ret)
    else:
        PublicLog(ret['uid'],u'删除 %s 组' % group_name,7).Create
        return redirect('/User/group/')
    
@cper(u'group_update')
def GroupEdit(request,id):
    ret = public(request,'User-Group','组','编辑')
    groups = Group(id)
    if request.method == 'POST':
        form_key = ['name','remark']
        form_value = GetFormPost(request,form_key)
        form_value['ownpe'] = request.POST.getlist('ownpe')
        groups.UpdateGroup(form_value)
        PublicLog(ret['uid'],u'编辑 %s 组' % form_value['name'],8).Create
        return redirect('/User/group/edit/%s/' % id)
    else:
        ret['users'] = groups.GetGroupUser()
        ret['group'] = groups.GetGroup()
        ret['ownpes'] = groups.GetGroupPermission()
        ret['otherpes'] = groups.GetGroupOtherPermission()
        ret['buttom'] = '确认修改'
        return render_to_response('user/group/edit.html',ret)

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    










