from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^imgCode/(?P<uuid>.*)/', views.ImgCodeView.as_view(),name='imgCode'),


]