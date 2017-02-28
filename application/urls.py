#-*- coding:utf-8 -*-

'''
@Created on 2016年5月9日
 
@author: MianBao

@author_web: Mianbao.cn.com

@系统设置
'''

from django.conf.urls import url

from assets import *



urlpatterns = [
               
    url('app/(?P<id>\d*)/$', ProjectCluster),
    url('app/list/$', ProjectList),
    url('app/add/$', ProjectAdd),
    url('app/edit/(?P<projectid>\d*)/$', ProjectEdit),
    url('app/del/(?P<projectid>\d*)/$', ProjectDel),
    
    url('cluster/add/(?P<id>\d*)/$', ClusterAdd),
    url('cluster/edit/(?P<id>\d*)/$', ClusterEdit),
    url('cluster/host/(?P<id>\d*)/$', ClusterHostList),
    url('cluster/host/del/(?P<clusterid>\d*)/(?P<hostid>\d*)/$', ClusterHostDel),
    url('cluster/del/(?P<clusterid>\d*)/(?P<projectid>\d*)/$', ClusterDel),
    
    
    
    url('list/$', AssetList),
    url('asset_add/$', AssetAdd),
    url('asset_batch_add/$', AssetBatchAdd),
    url('host/edit/(?P<id>\d*)/$', AssetEdit),
    url('host/del/(?P<id>\d*)/$', AssetDel),
    
    
]