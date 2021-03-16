from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(),name='index'),
    url(r'^expect$', views.expectPage.as_view(),name='expect'),
]