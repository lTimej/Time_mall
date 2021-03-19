from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    #购物车
    url(r'^cartlist/$',views.CartListView.as_view(),name='cartlist'),
    #购物车全选------待优化
    url(r'^cartlist/selected/$',views.CartSelectedView.as_view()),
    #快捷购物车功能
    url(r'^carts/$',views.ShortCutCartView.as_view(),name='carts'),
]