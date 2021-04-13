from django.conf.urls import url
from django.contrib import admin
from .views import users

urlpatterns = [
    #后台登录
    url(r'^login/$',users.backendLoginView.as_view(),name='adminLogin'),
]
