from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^register/$', views.RegisterView.as_view(),name='register'),
    url(r'userUnique/(?P<username>\w*)/',views.UsernameRepetition.as_view()),
    url(r'phone/(?P<phone>\w*)/', views.PhoneRepetition.as_view()),

]
