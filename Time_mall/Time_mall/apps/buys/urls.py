from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    #立即购买
    url(r'^buy/$',views.BuyView.as_view(),name='buy'),
]