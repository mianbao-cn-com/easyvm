#-*- coding:utf-8 -*-

'''
@Created on 2017年2月8日
 
@author: MianBao

@author_web: Mianbao.cn.com

@主要针对应用运维的资产管理
'''
from django.db import transaction
from django.db.models import Avg, Max, Min, Count,Sum
from django.http.response import HttpResponse
from django.shortcuts import render_to_response,redirect

from models import *
from User.models import department
from Mianbao.public import public,GetFormPost
from manage import Application
from User.User_Class import User



'''
@ about Host
'''
def AssetList(request):
    ret = public(request,'app-asset','主机','列表')
    ret['bodycss'] = 'sidebar-collapse'
    ret['asset'] = asset.objects.filter()
    return render_to_response('application/asset_list.html',ret)

def AssetAdd(request):
    ret = public(request,'app-asset','主机','新增')
    if request.method == 'POST':
        form_key = ['ip','name','towhere','toroom','toenv','belongu','remark','department']
        form_value = GetFormPost(request,form_key)
        form_value['belongu'] = ret['uid']
        app = Application()
        app.AssetSave(form_value)
        return redirect('/application/asset_add/')
    else:
        ret['department'] = department.objects.filter(active=0)
        ret['wheres'] = where.objects.filter()
        ret['room'] = room.objects.filter()
        ret['env'] = env.objects.filter()
        return render_to_response('application/asset_add.html',ret)

def AssetBatchAdd(request):
    ret = public(request,'app-asset','主机','新增')
    if request.method == 'POST':
        batch_content = str(request.POST.get('batch_add'))
        batch_list = batch_content.rstrip().split("\n")
        form_key = ['name','ip','towhere','toroom','toenv','department','remark']
        for x in batch_list:
            x_list = x.split(',')
            if len(x_list) == len(form_key):
                tmp = zip(x_list, form_key)
                dic = dict((y, x) for x, y in tmp)
                dic['belongu'] = ret['uid']
                dic['towhere'] = where.objects.filter(name=dic['towhere']).first().id
                dic['toroom'] = room.objects.filter(name=dic['toroom']).first().id
                dic['toenv'] = env.objects.filter(name=dic['toenv']).first().id
                dic['department'] = department.objects.filter(name=dic['department']).first().id
                app = Application()
                app.AssetSave(dic)
        return redirect('/application/list/')
    
def AssetEdit(request,id):
    ret = public(request,'app-asset','主机','修改')
    if request.method == 'POST':
        form_key = ['ip','name','towhere','toroom','toenv','belongu','remark','department']
        form_value = GetFormPost(request,form_key)
        app = Application()
        app.HostUpdate(id, form_value)
        return redirect('/application/list/')
    else:
        ret['host'] = asset.objects.get(id=id)
        ret['department'] = department.objects.filter(active=0)
        ret['wheres'] = where.objects.filter()
        ret['room'] = room.objects.filter()
        ret['env'] = env.objects.filter()
        return render_to_response('application/asset_edit.html',ret)

'''
@about project
'''
def ProjectList(request):
    ret = public(request,'app-pro','应用','列表')
    ret['bodycss'] = 'sidebar-collapse'
    ret['projects'] = project.objects.filter()
    return render_to_response('application/project_list.html',ret)

def ProjectAdd(request):
    ret = public(request,'app-pro','应用','新增')
    if request.method == 'POST':
        form_key = ['name','belongu','devu','examu','remark']
        form_value = GetFormPost(request,form_key)
        app = Application()
        app.ProjectSave(form_value)
        return redirect('/application/app/list/')
    else:
        users = User()
        ret['users'] = users.GetUserList()
        return render_to_response('application/project_add.html',ret)

def ProjectEdit(request,projectid):
    ret = public(request,'app-pro','应用','编辑')
    if request.method == 'POST':
        form_key = ['name','belongu','devu','examu','remark']
        form_value = GetFormPost(request,form_key)
        form_value['id'] = projectid
        app = Application()
        app.ProjectUpdate(form_value)
        return redirect('/application/app/list/')
    else:
        users = User()
        ret['users'] = users.GetUserList()
        ret['project'] = project.objects.get(id=projectid)
        return render_to_response('application/project_edit.html',ret)
       
def ProjectCluster(request,id):
    ret = public(request,'app-pro','集群','列表')
    ret['bodycss'] = 'sidebar-collapse'
    ret['clusters'] = cluster.objects.filter(toproject__id=id)
    ret['id'] = id
    ret['project'] = project.objects.get(id=id)
    return render_to_response('application/cluster_list.html',ret)
    
def ClusterAdd(request,id):
    ret = public(request,'app-pro','集群','列表')
    if request.method == 'POST':
        form_key = ['name','types','port','sadd','remark']
        form_value = GetFormPost(request,form_key)
        form_value['toproject'] = id
        app = Application()
        app.ClusterSave(form_value)
        return redirect('/application/app/%s/' % id)
    else:
        ret['env'] = env.objects.filter()
        return render_to_response('application/cluster_add.html',ret)

def ClusterEdit(request,id):
    ret = public(request,'app-pro','集群','编辑')
    if request.method == 'POST':
        form_key = ['name','types','port','sadd','remark']
        form_value = GetFormPost(request,form_key)
        form_value['id'] = id
        app = Application()
        toproject = app.ClusterUpdate(form_value)
        return redirect('/application/app/%s/' % toproject)
    else:
        ret['env'] = env.objects.filter()
        ret['cluster'] = cluster.objects.get(id=id)
        return render_to_response('application/cluster_edit.html',ret)
    
def ClusterHostList(request,id):
    ret = public(request,'app-pro','集群主机','列表')
    ret['bodycss'] = 'sidebar-collapse'
    if request.method == 'POST':
        host_lists = request.POST.getlist('hostselect')
        for x in host_lists:
            cluster.objects.get(id=id).host.add(asset.objects.get(id=x))
        return redirect('/application/cluster/host/%s/' % id)
    else:
        ret['host'] = asset.objects.filter(cluster__id=id)
        ret['id'] = id
        ret['assets'] = asset.objects.filter()
        ret['cluster'] = cluster.objects.get(id=id)
        return render_to_response('application/host_list.html',ret)
    
def ClusterHostDel(request,clusterid,hostid):
    ret = public(request,'app-pro','集群主机','移除主机')
    cluster.objects.get(id=clusterid).host.remove(asset.objects.get(id=hostid))
    return redirect('/application/cluster/host/%s/' % clusterid)
    
def ClusterDel(request,clusterid,projectid):
    ret = public(request,'app-pro','集群主机','移除群集')
    if clusterid:
        asset_num = asset.objects.filter(cluster__id=clusterid).count()
        print asset_num
        if asset_num == 0:
            cluster.objects.get(id=clusterid).delete()
            return redirect('/application/app/%s/' % projectid)
        else:
            ret['message_url'] = '/application/app/%s/' % clusterid
            ret['status'] = 'error'
            ret['message_title'] = '删除失败'
            ret['message_content'] = '请移除属于集群的节点之后再进行集群的删除！'
            return render_to_response('public/message.html',ret)
    
def ProjectDel(request,projectid):
    ret = public(request,'app-pro','集群主机','删除应用')
    if projectid:
        cluster_num = cluster.objects.filter(toproject__id=projectid).count()
        if cluster_num == 0:
            project.objects.get(id=projectid).delete()
            return redirect('/application/app/list/')
        else:
            ret['message_url'] = '/application/app/list/'
            ret['status'] = 'error'
            ret['message_title'] = '删除失败'
            ret['message_content'] = '请移除属于此应用的集群之后再进行应用的删除！'
            return render_to_response('public/message.html',ret)
    
def AssetDel(request,id):
    ret = public(request,'app-pro','主机','删除主机')
    if id:
        cluster_num = cluster.objects.filter(host__id=id).count()
        if cluster_num == 0:
            asset.objects.get(id=id).delete()
            return redirect('/application/list/')
        else:
            ret['message_url'] = '/application/list/'
            ret['status'] = 'error'
            ret['message_title'] = '删除失败'
            ret['message_content'] = '此主机仍归属于集群，请解除主机与群集的关系后再进行删除！'
            return render_to_response('public/message.html',ret)
    
    
    
    
    
    
    
    
    
    
    
    
    
    

