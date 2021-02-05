from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    #图片验证码
    url(r'^imgCode/(?P<uuid>.*)/', views.ImgCodeView.as_view(),name='imgCode'),
    #短信验证码
    url(r'^smsCode/(?P<phone>1[3-9]\d{9})/', views.SmsCodeView.as_view(),name='smsCode')

]