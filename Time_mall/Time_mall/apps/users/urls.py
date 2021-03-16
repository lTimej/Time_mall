from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    #注册
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
    #用户名重复验证
    url(r'userUnique/(?P<username>\w*)/', views.UsernameRepetition.as_view()),
    #手机号重复验证
    url(r'phone/(?P<phone>\w*)/', views.PhoneRepetition.as_view()),
    #用户登录
    url(r'^login/$', views.LoginView.as_view(), name="login"),
    #退出登录
    url(r"^logout/$", views.LogoutView.as_view(), name="logout"),
    #用户信息
    url(r"^userinfo/$", views.UserInfoView.as_view(), name="userinfo"),
    #邮箱
    url(r"^email/$", views.EmailView.as_view(), name="email"),
    #邮箱验证
    url(r"^email/verify/$", views.EmailVerifyView.as_view(), name="emailverify"),
    #用户收获地址
    url(r"^address/$", views.AddressView.as_view(), name="address"),
    #新增收货地址
    url(r"^address/add/$", views.NewAddAddressView.as_view()),
    #修改收获地址
    url(r"^address/update/(?P<iid>\d+)/$", views.UpdateAddressView.as_view()),
    #修改标题
    url(r"^address/update/title/(?P<iid>\d+)/$", views.UpdateTitleView.as_view()),
    #删除地址
    url(r"^address/del/(?P<iid>\d+)/$", views.DelAddressView.as_view()),
    #设置默认地址
    url(r"^set/default/address/(?P<iid>\d+)/$", views.SetDefaultAddressView.as_view()),
    #修改密码
    url(r"^update/password/$", views.UpdatePasswordView.as_view(),name='upass'),

]
