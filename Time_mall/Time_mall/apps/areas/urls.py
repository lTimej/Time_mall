from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    #用户收获地址
    url(r"^areas/$", views.AreasView.as_view(), name="areas"),


]
