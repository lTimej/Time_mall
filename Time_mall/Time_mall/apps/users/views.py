import json
import re,logging

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import login,authenticate,logout
from django.db import DatabaseError
from django.shortcuts import render,redirect
from django.urls import reverse
from django.views import View
from django import http
from django_redis import get_redis_connection
from django.contrib.auth.mixins import LoginRequiredMixin

from users.models import User
from Time_mall.utils import constants,response_code
from Time_mall.utils.view import MyLoginRequiredMixin
from celery_tasks.email.tasks import send_verify_email
from users.utils import generate_email_token, get_email_info

logger = logging.getLogger('django')

class UsernameRepetition(View):
    def get(self,request,username):
        '''
        用户名重复校验
        :param request:前端通过ajax请求后端用户名数据数据，返回用户名个数给前端
        :param username: 前端输入框的参数
        :return: json数据
        '''
        #返回用户名个数
        count = User.objects.filter(username=username).count()
        return http.JsonResponse({"count":count})

class PhoneRepetition(View):
    def get(self,request,phone):
        '''
        手机号重复校验
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
        用户注册
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

class LoginView(View):
    def get(self,request):
        '''
        用户登录
        :param request: get请求
        :return: 登录界面
        '''
        return render(request,"login.html")
    def post(self,request):
        '''
        :param request: post
        :return:
        '''
        #获取参数
        username = request.POST.get("username")
        password = request.POST.get("password")
        remembered = request.POST.get("remembered")
        #校验参数
        #判断参数是否齐全
        if not all([username,password]):
            return http.HttpResponseForbidden("参数不全")
        #用户名是否为4-16位
        if not re.match("^[0-9a-zA-Z]{4,16}$",username):
            return http.HttpResponseForbidden("用户名必须为4-16为")
        #密码是否为8-16位
        if not re.match("^[0-9A-Za-z]{8,16}$",password):
            return http.HttpResponseForbidden("密码必须为8-16为")
        #用户名和密码校验
        user = authenticate(username=username,password=password)
        #返回None，用户名或密码出错，重新返回到登录页面
        if not user:
            return render(request,"login.html",{"login_errmsg":"用户名或密码输入不正确"})
        #认证成功，实现状态保持,加入session
        login(request,user)
        #没有记住用户，设置session周期为0
        if not remembered:
            request.session.set_expiry(0)
        else:#默认周期为14天
            request.session.set_expiry(None)
        print(user)
        #重定向首页
        next = request.GET.get("next")
        # 指定未登录用户重定向的地址
        # 登录时next参数的作用是为了方便用户从哪里进入到登录页面，登录成功后就回到哪里。
        if next:#不为空，则重定向到指定的页面
            response = redirect(next)
        else:#重定向到首页
            response = redirect(reverse("contents:index"))
        #将用户名存入cookies中
        response.set_cookie("username",user.username,max_age=constants.COOKIE_VALUE_EXPIERS)
        return response
#退出登录
class LogoutView(View):
    def get(self,request):
        #清理session
        logout(request)
        #重定向至首页
        response = redirect(reverse("contents:index"))
        #删除cookie
        response.delete_cookie("username")
        #返回
        return response

#用户信息
class UserInfoView(LoginRequiredMixin,View):
    def get(self,request):
        # username = request.COOKIES.get("username")
        #获取前端所需要的参数
        username = request.user.username
        phone = request.user.phone
        email = request.user.email
        email_active = request.user.email_active
        context = {
            "username":username,
            "phone":phone,
            "email":email,
            "email_active":email_active
        }
        #将数据传到前端
        return render(request,'user_info.html',context)

class EmailView(MyLoginRequiredMixin,View):#用户登录才进行添加
    def put(self,request):
        '''
        添加邮箱
        :param request: put请求
        :return: 响应状态码
        '''
        #获取参数
        #获取邮箱，转换为字符类型
        email_string = request.body
        if not email_string:
            return http.HttpResponseForbidden("邮箱格式不为空")
        email_string = email_string.decode()
        #转换成字典，取出email
        email = json.loads(email_string).get("email")
        #校验参数
        if not re.match('^[0-9a-zA-Z]{1,16}@(qq|yeah|126|163)\.(net|cn|com)$',email):
            return http.HttpResponseForbidden("邮箱格式不正确")
        #保存数据库
        try:
            request.user.email = email
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': response_code.RETCODE.DBERR, 'errmsg': '添加邮箱失败'})
        #获取email验证url
        verify_url = generate_email_token(request.user)
        #异步发送
        print(verify_url)
        send_verify_email.delay(email,verify_url)
        print(9999999999999)
        #响应状态码
        return http.JsonResponse({"code":response_code.RETCODE.OK,'errmsg':"邮箱发送成功"})

class EmailVerifyView(View):
    def get(self,request):
        '''
        邮箱验证
        :param request:
        :return:重定向用户信息界面
        '''
        #获取链接参数
        token = request.GET.get("token")
        #校验
        if not token:
            return http.HttpResponseForbidden("验证失败")
        #解析链接参数
        user = get_email_info(token)
        #校验判断token是否过期
        if not user:
            return http.HttpResponseForbidden("验证已过期")
        try:#更新用户邮箱激活状态
            user.email_active = True
            user.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError("存储失败")
        #重定向userinfo
        return redirect(reverse('users:userinfo'))

class AddressView(View):
    def get(self,request):
        return render(request,'user_address.html')