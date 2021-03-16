from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^cartlist/$',views.CartListView.as_view(),name='cartlist')
]