from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    #QQ登录
    url(r'^qq/login/$', views.QQLoginView.as_view(), name='qqLogin'),
    #QQ回调地址
    url(r'^oauth_callback/$', views.QQcallBackView.as_view(), name='qqcallback'),

]