import json,re,logging

from django import http
from django.views import View
from django.urls import reverse
from django.db import DatabaseError
from django.shortcuts import render,redirect
from django_redis import get_redis_connection
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login,authenticate,logout

from cart.utils import combine_carts
from users.models import User,Address
from Time_mall.utils import constants,response_code
from Time_mall.utils.view import MyLoginRequiredMixin
from celery_tasks.email.tasks import send_verify_email
from users.utils import generate_email_token, get_email_info

'''
                     用户相关操作：logging logout register username_verify mobile_verify email address
'''

#日志器
logger = logging.getLogger('django')
#用户名重复校验
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
#手机号重复校验
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
#用户登录
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
        #重定向首页
        next = request.GET.get("next")
        # 指定未登录用户重定向的地址
        # 登录时next参数的作用是为了方便用户从哪里进入到登录页面，登录成功后就回到哪里。
        if next:#不为空，则重定向到指定的页面
            response = redirect(next)
        else:#重定向到首页
            response = redirect(reverse("contents:index"))
        # 将用户名存入cookies中
        response.set_cookie("username", user.username, max_age=constants.COOKIE_VALUE_EXPIERS)
        #购物车整合
        response = combine_carts(request,user,response)

        return response
#退出登录
class LogoutView(LoginRequiredMixin,View):
    def get(self,request):
        '''
        退出登录
        :param request:
        :return:
        '''
        #清理session
        logout(request)
        #重定向至首页

        next = request.GET.get("next")
        #next存在重定向到指定页面
        if next:
            response = redirect(next)
        else:
            response = redirect(reverse("contents:index"))
        #删除cookie
        response.delete_cookie("username")
        #返回
        return response
#用户信息
class UserInfoView(LoginRequiredMixin,View):
    def get(self,request):
        '''
        用户信息
        :param request:
        :return:
        '''
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
#添加邮箱
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
#邮箱验证
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
#收货地址
class AddressView(View):
    def get(self,request):
        '''
        收货地址
        :param request:
        :return: 响应收货地址页面
        '''
        #获取当前登录用户
        curr_user_obj = request.user
        #获取当前用户收货地址
        addresses = Address.objects.filter(user_id=curr_user_obj.id,is_deleted=False)
        address_dict_list = []
        #重构前端数据
        for address in addresses:
            address_dict = {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "province_id": address.province.id,
                "city_id": address.city.id,
                "district_id": address.district.id,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel or '',
                "email": address.email or ''
            }
            address_dict_list.append(address_dict)
            #上下文
        context = {
            'addresses': address_dict_list,
            'default_address_id':curr_user_obj.default_address_id or '0'
        }
        #响应页面
        return render(request,'user_address.html',context)
#新增收获地址
class NewAddAddressView(View):
    def post(self,request):
        '''
        新增地址
        :param request: 获取前端参数
        :return: 响应json数据
        '''
        #获取参数
        count = Address.objects.filter(user=request.user,is_deleted=False).count()
        if count >= 5:
            return http.JsonResponse({'code':response_code.RETCODE.THROTTLINGERR,'errmsg':'地址添加过多'})
        data_json = json.loads(request.body.decode())
        receiver = data_json.get('receiver')
        place = data_json.get('place')
        mobile = data_json.get('mobile')
        tel = data_json.get('tel')
        email = data_json.get('email')
        province_id = data_json.get('province_id')
        city_id = data_json.get('city_id')
        district_id = data_json.get('district_id')
        #校验参数
        if not all([receiver,place,mobile]):
            return http.HttpResponseForbidden("缺少必要参数")
        #校验手机格式
        if not re.match('^1[3-9]\d{9}$',mobile):
            return http.HttpResponseForbidden("手机号格式有误")

        #校验固定电话
        if tel:
            if not re.match('^\d{7}$',tel):
                return http.HttpResponseForbidden("固定电话格式有误")
        #校验邮箱
        if email:
            if not re.match('^[0-9a-zA-Z]{1,16}@(qq||yeah||126||163)\.(net||cn||com)$',email):
                return http.HttpResponseForbidden("邮箱格式有误")
        #保存数据库
        try:
            address_obj = Address.objects.create(
                user=request.user,#当前用户
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
            if not request.user.default_address:
                request.user.default_address = address_obj
                request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code':response_code.RETCODE.DBERR,'errmsg':'新增错误'})
        #地址详细信息
        address = {
            'receiver': receiver,
            'title':address_obj.title,
            'province': address_obj.province.name,
            'city': address_obj.city.name,
            'district': address_obj.district.name,
            'place': place,
            'mobile': mobile,
            'tel': tel or '',
            'email': email or '',
        }
        #响应数据
        return http.JsonResponse({'code':response_code.RETCODE.OK,'errmsg':'添加成功','address_dict':address})
#修改地址
class UpdateAddressView(View):
    def put(self,request,iid):
        '''
        修改地址
        :param request: 获取前端参数
        :return: 响应json数据
        '''
        # 获取参数
        data_json = json.loads(request.body.decode())
        receiver = data_json.get('receiver')
        place = data_json.get('place')
        mobile = data_json.get('mobile')
        tel = data_json.get('tel')
        email = data_json.get('email')
        province_id = data_json.get('province_id')
        city_id = data_json.get('city_id')
        district_id = data_json.get('district_id')
        # 校验参数
        if not all([receiver, place, mobile]):
            return http.HttpResponseForbidden("缺少必要参数")
        # 校验手机格式
        if not re.match('^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden("手机号格式有误")

        # 校验固定电话
        if tel:
            if not re.match('^\d{7}$', tel):
                return http.HttpResponseForbidden("固定电话格式有误")

        # 校验邮箱
        if email:
            if not re.match('^[0-9a-zA-Z]{1,16}@(qq||yeah||126||163)\.(net||cn||com)$', email):
                return http.HttpResponseForbidden("邮箱格式有误")
        # 保存数据库
        try:
            Address.objects.filter(id=iid).update(
                user=request.user,  # 当前用户
                receiver=receiver,
                # title=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': response_code.RETCODE.DBERR, 'errmsg': '修改错误'})

        # 地址详细信息
        address_obj = Address.objects.get(id=iid)
        address = {
            'receiver': receiver,
            'title': address_obj.title,
            'province': address_obj.province.name,
            'city': address_obj.city.name,
            'district': address_obj.district.name,
            'place': place,
            'mobile': mobile,
            'tel': tel,
            'email': email,
        }
        # 响应数据
        return http.JsonResponse({'code': response_code.RETCODE.OK, 'errmsg': '添加成功', 'address_dict': address})
#修改地址标题
class UpdateTitleView(View):
    def put(self,request,iid):
        '''
        修改地址标题
        :param request: 接受新标题
        :return:
        '''
        #接受参数
        new_title_dict = json.loads(request.body.decode())
        new_title = new_title_dict.get('new_title')
        #校验参数
        if not new_title:
            return http.HttpResponseForbidden("标题不为空")
        #保存数据库
        try:
            Address.objects.filter(id=iid).update(title=new_title)
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code':response_code.RETCODE.DBERR,'errmsg':'保存失败'})
        #响应数据
        return http.JsonResponse({'code':response_code.RETCODE.OK,'errmsg':'ok'})
#删除地址
class DelAddressView(View):
    def delete(self,request,iid):
        '''
        删除地址
        :param request:
        :param iid: 地址id
        :return: 响应状态
        '''
        try:#id存在则将is_deleted修改为True
            Address.objects.filter(id=iid).update(is_deleted=True)
            #当前用户有没有设置默认地址，并且是否存在
            obj = Address.objects.filter(id=request.user.default_address_id,is_deleted=False)
            if not obj:
                request.user.default_address_id = ''
                request.user.save()
        except Exception as e:#不存在返回错误状态码
            logger.error(e)
            return http.JsonResponse({'code': response_code.RETCODE.DBERR, 'errmsg': '删除失败'})
        #响应正确状态码
        return http.JsonResponse({'code': response_code.RETCODE.OK, 'errmsg': 'ok'})
#设置默认地址
class SetDefaultAddressView(View):
    def put(self,request,iid):
        '''
        #设置默认地址
        :param request:
        :param iid:地址id
        :return:
        '''
        try:#修改默认地址id
            request.user.default_address_id = iid
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': response_code.RETCODE.DBERR, 'errmsg': '更改失败'})
        # 响应正确状态码
        return http.JsonResponse({'code': response_code.RETCODE.OK, 'errmsg': 'ok'})
#修改密码
class UpdatePasswordView(View):
    def get(self,request):
        '''
        修改密码
        :param request:
        :return:
        '''
        return render(request,'update_password.html')