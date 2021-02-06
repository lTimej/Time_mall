from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    #注册
    url(r'^register/$', views.RegisterView.as_view(),name='register'),
    #用户名重复验证
    url(r'userUnique/(?P<username>\w*)/',views.UsernameRepetition.as_view()),
    #手机号重复验证
    url(r'phone/(?P<phone>\w*)/', views.PhoneRepetition.as_view()),
    #用户登录
    url(r'^login/$',views.LoginView.as_view(),name="login"),
    #退出登录
    url(r"^logout/$",views.LogoutView.as_view(),name="logout")

]
