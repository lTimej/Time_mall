from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    #商品列表
    url(r'^goodslist/(?P<category_id>\d+)/$', views.GoodsListView.as_view(),name='goodslist'),
    #详情页
    url(r'^detail/(?P<spu_id>\d+)/$', views.GoodsDetailView.as_view(),name='detail'),
    #sku
    url(r'^sku/$', views.SkuView.as_view(),name='sku'),
    #热销
    url(r'^hot/(?P<category_id>\d+)/$',views.HotView.as_view(),name='hot'),
]