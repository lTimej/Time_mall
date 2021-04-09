from django import http
from django.shortcuts import render
from django.views import View
# Create your views here.
class backendLoginView(View):
    def post(self,request):
        json_data = request.body
        print(json_data)
        return http.JsonResponse({"code":"ok"})