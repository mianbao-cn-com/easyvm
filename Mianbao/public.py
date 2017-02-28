#-*- coding:utf-8 -*-

'''
@Created on 2016年5月10日
 
@author: MianBao

@author_web: Mianbao.cn.com

@ Public function
'''
from websettings import websetting
from django.shortcuts import render,render_to_response,redirect,HttpResponse
from email.mime.multipart import MIMEMultipart  
from email.mime.text import MIMEText  
from email.mime.image import MIMEImage 
from email.utils import COMMASPACE,formatdate 
import smtplib
from models import *
import md5
import sys
from django.template.loader import get_template
from django.template import Context
import time
from django.template.defaultfilters import linebreaksbr

websets = websetting()

def public(request,set_class,where,site):
    ret = {'set_class':set_class,'where':where,'site':site}
    ret['name'] = request.session.get('name',None)
    ret['uid'] = request.session.get('uid',None)
    ret['title'] = websets.Gettitle()
    ret['logintime'] = request.session.get('logintime',None)
    ret['mail_add'] = websets.GetMailAdd()
    ret['permission'] = request.session.get('permission',None)
    ret['dpname'] = request.session.get('dpname',None)
    return ret

def GetFormPost(request,FormId):
    new = dict()
    for x in FormId:
        new[x] = request.POST.get(x)
    return new

def CheckPermission(ret,name):
    try:
        rs = ret['permission'].get(name,None)
        return True if isinstance(rs,int) else False
    except Exception,e:
        return False

def cper(val):
    def deco(func):
        def _deco(request, *args, **kwargs):
            rs = request.session.get('permission',None)
            check_rs = False
            if rs:
                check_rs = True if isinstance(rs.get(val,None),int) else False
            if check_rs:
                ret = func(request,*args, **kwargs)
            else:
                ret = HttpResponse('404 Fobbidn')
            return ret
        return _deco
    return deco


def Md5s(str):
        m = md5.new()
        m.update(str)
        rs = m.hexdigest()
        return rs

def sendmail(receiver, subject, html,att=None,att_name = None):
    # Create message container - the correct MIME type is multipart/alternative.  
    msg = MIMEMultipart('alternative')
    
    #解决邮件弹出通知框乱码问题
    if not isinstance(subject,unicode):
        subject = unicode(subject)
        msg['Subject'] = subject
    else:
        msg['Subject'] = subject
    
    mails = system.objects.get(id=1) 
    msg['From'] = mails.mail_user
    msg['To'] = COMMASPACE.join(receiver)
    msg['Date'] = formatdate(localtime=True)     
    # Create the body of the message (a plain-text and an HTML version).
    htmls = get_template('mail.txt')
    html = htmls.render(html)
    # Record the MIME types of both parts - text/plain and text/html.   
    part2 = MIMEText(html, 'html' ,'utf-8')  
      
    # Attach parts into message container.  
    # According to RFC 2046, the last part of a multipart message, in this case  
    # the HTML message, is best and preferred.    
    msg.attach(part2)  
    #构造附件  
    if att is not None:
        att = MIMEText(open(att, 'rb').read(), 'base64', 'utf-8')  
        att["Content-Type"] = 'application/octet-stream'  
        att["Content-Disposition"] = 'attachment; filename="%s"' % att_name
        msg.attach(att)
    smtp = smtplib.SMTP()  
    smtp.connect(mails.mail_smtp)
    smtp.login(mails.mail_user, mails.mail_pwd)
    try:
        smtp.sendmail(mails.mail_user, receiver, msg.as_string())  
        smtp.quit()
        return 0
    except Exception,e:
        return e.message

def unit_convert(v1,start=0):
    v1 = int(v1)
    li = ['bytes','Kb','M','G','T','P']
    a = start
    while v1 > 1024:
        v1 = v1/1024
        a += 1
    return str(round(v1,1))+str(li[a])

def GenerateAtoZ(exclude=None):
    abc = map(chr,range(97,123))
    if exclude:
        [abc.remove(x.lower()) for x in exclude]
    return abc

def DateConvertStamp(str):
    list_str = str.split('-')
    stamp = list()
    for x in list_str:
        tuple_str = time.strptime(x.strip(),'%m/%d/%Y')
        stamp_str = time.mktime(tuple_str)
        stamp.append(stamp_str)
    return tuple(stamp)








