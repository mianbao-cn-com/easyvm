#-*- coding:utf-8 -*-

'''
@Created on 2016年5月9日
 
@author: MianBao

@author_web: Mianbao.cn.com

@系统设置
'''

from django.conf.urls import url
#from Ajax import *
from vMware import *
from Ajax import Ajax_url

urlpatterns = [
    url('test/$', vmware_test),
    url('manage/$', Manage),
    url('network/$', Network),
    url('ippool/$', IPPool),
    url('customization/$', Custom),
    url('customization/add/$', CustomAdd),
    url('customization/edit/(?P<id>\d*)/$', CustomEdit),
    url('customization/del/(?P<id>\d*)/$', CustomDel),
    
    url('ippool/del/(?P<id>\d*)/$', IPPoolDel),
    url('ippool/detail/(?P<id>\d*)/$', IPPoolDatial),
    url('ippool/edit/(?P<id>\d*)/$', IPPoolEdit),
    
    url('network/edit/(?P<id>\d*)/(?P<dvs_name>.*)/$', NetworkEdit),
    url('network/del/(?P<id>\d*)/(?P<dvs_name>.*)/(?P<dvs_vswitch>.*)/$', NetworkDel),
    
    url('virtual_type/$', VMTypes),
    url('virtual_type/add/$', VMTypesAdd),
    url('virtual_type/del/(?P<id>\d*)/$', VMTypesDel),
    url('virtual_type/enable/(?P<id>\d*)/$', VMTypesEnable),
    url('virtual_type/disable/(?P<id>\d*)/$', VMTypesDisable),
    
    url('apply/$', VMApply),
    url('order/over/$', OrderOver),
    url('order/(?P<id>\d*)/$', OrderCheck),
    url('order/(?P<types>[A-Za-z]*)/$', VMApplyOrder),
    url('order/opened/(?P<id>\d*)/$', OrderOpened),
    url('order/pay/(?P<id>\d*)/$', OrderPay),
    url('order/detail/(?P<id>\d*)/$', OrderDetail),
    url('order/reject/(?P<id>\d*)/$', OrderReject),
    
    url('myorder/$', MyOrder),
    
    url('vm/$', Vm),
    
    url('message/$', Message),
    url('message/conf/$', MessageMail),
    
    url('vCenter/$', vCenter),
    url('vCenter/add/$', vCenterAdd),
    url('vCenter/edit/(?P<id>\d*)/$', vCenterEdit),
    url('vCenter/disable/(?P<id>\d*)/$', vCenterDisable),
    url('vCenter/enable/(?P<id>\d*)/$', vCenterEnable),
    url('vCenter/del/(?P<id>\d*)/$', vCenterDel),
    
    url('bulletin/$', Bulletin),
    url('bulletin/add/$', BulletinAdd),
    url('bulletin/edit/(?P<id>\d*)/$', BulletinEdit),
    url('bulletin/disable/(?P<id>\d*)/$', BulletinDisable),
    url('bulletin/enable/(?P<id>\d*)/$', BulletinEnable),
    url('bulletin/del/(?P<id>\d*)/$', BulletinDel),
    
    url('resource/$', Resource),
    url('resource/enable/(?P<id>\d*)/$', ResourceEnable),
    url('resource/disable/(?P<id>\d*)/$', ResourceDisable),
    url('resource/del/(?P<id>\d*)/$', ResourceDel),
    
    url('Ajax/(?P<value>.*)/(?P<do>[A-Za-z]*)/$', Ajax_url),
    #url('$', List),
]