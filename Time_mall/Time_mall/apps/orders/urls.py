from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    #订单列表
    url(r'^orderlist/$',views.OrderListView.as_view(),name='orderlist'),
    #结算订单页面
    url(r'^order/$',views.OrderView.as_view(),name='order'),
    #订单提交页面
    url(r'^order/commit/$',views.CommitOrderView.as_view(),name='Oscommit'),
    #订单提交页面
    url(r'^user/order/(?P<page>\d+)/$',views.UserOrderView.as_view(),name='userorder'),
]