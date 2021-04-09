from django import http
from django.shortcuts import render
from django.views import View
# Create your views here.
class backendLoginView(View):
    def get(self,request):
        return http.JsonResponse({"code":"ok"})