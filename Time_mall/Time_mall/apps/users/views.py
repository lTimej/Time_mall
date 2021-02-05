import re

from django.db import DatabaseError
from django.shortcuts import render,redirect
from django.urls import reverse
from django.views import View
from django import http
from django_redis import get_redis_connection

from users.models import User
# Create your views here.
#用户名重复校验
class UsernameRepetition(View):
    def get(self,request,username):
        '''
        :param request:前端通过ajax请求后端用户名数据数据，返回用户名个数给前端
        :param username: 前端输入框的参数
        :return: json数据
        '''
        #返回用户名个数
        count = User.objects.filter(username=username).count()
        return http.JsonResponse({"count":count})
#手机号重复校验
class PhoneRepetition(View):
    def get(self,request,phone):
        '''
        :param request:
        :param username: 前端输入框的参数
        :return: json数据
                '''
        # 返回手机号个数
        count = User.objects.filter(phone=phone).count()
        #返回响应
        return http.JsonResponse({"count":count})

class RegisterView(View):
    def get(self,request):
        '''
        :param request:
        :return: 展示注册页面
        '''
        return render(request,'register.html')
    def post(self,request):
        '''
        :param request:前端参数
        :return:首页
        '''
        #1、接受参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        sms_code = request.POST.get('sms_code')
        allow = request.POST.get('allow')

        #2、校验参数  防止恶意访问网站 比如爬虫
            #参数是否都存在
        if not all([username,password,password2,mobile,allow]):
            return http.HttpResponseForbidden("缺少必传参数")

        #校验用户名4-16位
        if not re.match('^[0-9a-zA-Z-_]{4,16}',username):
            return http.HttpResponseForbidden("用户名必须为4-16个字符")

        #校验密码8-16位数字和字母
        if not re.match('^[0-9a-zA-Z]{8,16}$',password):
            return http.HttpResponseForbidden("密码必须为8-16个数字和字母")

        #确认密码
        if password2 != password:
            return http.HttpResponseForbidden("两次密码不一致")

        #手机号校验
        if not re.match('^1[3-9]\d{9}$',mobile):
            return http.HttpResponseForbidden("您输入的手机号格式不正确")

        #校验用户协议
        if allow != 'on':
            return http.HttpResponseForbidden("请勾选用户协议!")

        #3、保存至数据库
        try:
            User.objects.create_user(
                username=username,
                password=password,
                phone=mobile
            )
        #写入失败就抛出异常
        except DatabaseError:
            return render(request,'register.html',{"register_error":"注册失败"})

        #后端对短信验证码进行验证
        #链接redis数据库
        redis_conn = get_redis_connection('verify_code')

        #如果Redis服务端需要同时处理多个请求，加上网络延迟，那么服务端利用率不高，效率降低。
        #获取短信验证码
        redis_sms_code = redis_conn.get('sms_%s'%mobile)
        #校验验证码是否存在
        if not redis_sms_code:
            return render(request, 'register.html', {"register_error": "短信验证码失效"})
        #校验验证码是否正确
        if redis_sms_code.decode() != sms_code:
            return render(request, 'register.html', {"register_error": "短信输入错误"})

        #4、重定向页面
        return redirect(reverse('contents:index'))#reverse反向解析
        # return http.HttpResponse('注册成功，重定向到首页')

