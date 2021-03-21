from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    #订单列表
    url(r'^orderlist/$',views.OrderListView.as_view(),name='orderlist')
]