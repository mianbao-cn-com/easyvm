#-*- coding:utf-8 -*-

'''
@Created on 2016年5月10日
 
@author: MianBao

@author_web: Mianbao.cn.com

@ The User Class
'''
import time
from Mianbao.public import *
from User_Class import *
from models import *




def writsession(request,user_info):
    request.session['uid'] = user_info.id
    request.session['logintime'] = time.time()
    request.session['mail'] = user_info.mail
    request.session['name'] = user_info.name
    request.session['permission'] = GetPermission(user_info.id)
    request.session['dpid'],request.session['dpname'] = GetUserGroup(user_info.id)
    
def UpdateLoginTime(request):
    uid = request.session.get('uid',None)
    updates = User(uid)
    updates.UpdateLoginTime()
   
def GetPermission(uid):
    rs = user.objects.get(id=uid).user_permission.all()
    permission_list = dict()
    for x in rs:
        permission_list[x.name] = x.id
    
    group_rs = user.objects.get(id=uid).user_group.all()
    group_id_list = list()
    for y in group_rs:
        group_id_list.append(y.id)
    
    for m in group_id_list:
        g_permission = group.objects.get(id=m).permission_set.all()
        for n in g_permission:
            permission_list[n.name] = n.id
    
    return permission_list
    
def GetUserGroup(uid):
    rs = user.objects.get(id=uid).user_department.all()
    return rs[0].id,rs[0].name
    
def GetGroup():
    departments = department.objects.all()
    return departments



'''
@about user jump html
'''  
def UserRegisterRight(ret):
    ret['message_url'] = '/login/'
    ret['status'] = 'info'
    ret['message_title'] = '注册成功！'
    ret['message_content'] = '恭喜您已注册成功，系统已自动向您邮箱发送了一封激活邮件，请尽快登录邮箱进行激活！'
    return ret
    
def UserRegisterError(ret):
    ret['message_url'] = '/login/'
    ret['status'] = 'error'
    ret['message_title'] = '注册失败'
    ret['message_content'] = '注册失败，请联系管理员询问原因'
    return ret

def UserActiveRight(ret):
    ret['message_url'] = '/login/'
    ret['status'] = 'right'
    ret['message_title'] = '激活成功！'
    ret['message_content'] = '恭喜您，您的帐号已激活成功，请妥善保管您的密码，谢谢！'
    return ret

def UserActiveError(ret):
    ret['message_url'] = '/login/'
    ret['status'] = 'error'
    ret['message_title'] = '激活失败'
    ret['message_content'] = '此帐号不存在或已经激活！'
    return ret

def UserResetPwdError(ret):
    ret['message_url'] = '/User/'
    ret['status'] = 'error'
    ret['message_title'] = '密码重置失败'
    ret['message_content'] = '由于未知原因，密码重置失败，请稍后再试，或至mianbao.cn.com寻求解决方法！'
    return ret

def UserUpdatePwdRight(ret):
    ret['message_url'] = '/logout/'
    ret['status'] = 'right'
    ret['message_title'] = '密码修改成功'
    ret['message_content'] = '恭喜您，你的密码已修改成功！'
    return ret

def UserUpdatePwdError(ret):
    ret['message_url'] = '/User/UpdatePwd/'
    ret['status'] = 'error'
    ret['message_title'] = '密码修改失败'
    ret['message_content'] = '由于未知原因，您的密码重置失败，请稍后再试，或联系管理员解决！'
    return ret

def GroupAddError(ret):
    ret['message_url'] = '/User/group/'
    ret['status'] = 'error'
    ret['message_title'] = '组新增失败'
    ret['message_content'] = '此用组名已存在，请更换组名再新增！'
    return ret

def GroupDelError(ret):
    ret['message_url'] = '/User/group/'
    ret['status'] = 'error'
    ret['message_title'] = '用户组删除失败'
    ret['message_content'] = '此用户组中还有用户，请先移除用户才能删除此组！'
    return ret

def UserEditError(ret):
    ret['message_url'] = '/User/'
    ret['status'] = 'error'
    ret['message_title'] = '用户编辑失败'
    ret['message_content'] = '您不能编辑自己的权限和所属的用户组！'
    return ret

'''
@about User Send Mail
'''
def UserRegisterActive(request,id,username,register_time):
    domain_url  = request.META.get('HTTP_HOST')
    http_url = 'http://%s/User/Active/' % domain_url
    md5_str = '%s/%s/%s/'  % (str(id*1024*1024*1024*715), Md5s(username) ,Md5s(str(register_time)))
    send_url = http_url + md5_str
    mail_title = u'激活您的账户'
    mail_dict = {'title':u'激活您的账户'}
    mail_dict['content'] = u'请点击下面的“激活”按钮，激活您%s的账户。如您未在%s进行过注册，请忽略此邮件。' % (websets.Gettitle(),websets.Gettitle())
    mail_dict['value'] = u'激活'
    mail_dict['url'] = send_url
    sendmail([str(username) + str(systems.GetMailAdd()),],mail_title,mail_dict)
    
def UserResetPwd(request,passwd,mail):
    domain_url  = request.META.get('HTTP_HOST')
    mail_title = u'【通知】密码已重置'
    mail_dict = {'title':u'【通知】密码已重置'}
    mail_dict['content'] = u'您的%s账户密码已重置为： %s ,请尽快至平台使用新密码进行密码修改！' % (websets.Gettitle(),passwd)
    mail_dict['value'] = u'修改密码'
    mail_dict['url'] = 'http://%s/User/passwd/update/' % domain_url
    sendmail([mail + str(systems.GetMailAdd())],mail_title,mail_dict)
    
    
    
    
    
    
    
    
    
    
    
    
    
    





 