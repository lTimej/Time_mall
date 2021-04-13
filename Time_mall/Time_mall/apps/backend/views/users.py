import json
import datetime

from django import http
from django.conf import settings
from django.views import View
from django.shortcuts import render
from django.contrib.auth import authenticate, login

from rest_framework.views import APIView


from backend.utils import generate_jwt
from users.models import User
from response_code import RETCODE

class backendLoginView(View):
    def _generate_token(self,user_id):
        """
        生成token
        :param user_id: 用户id
        :return: token
        """
        # 颁发JWT
        now = datetime.datetime.utcnow()
        expiry = str(now + datetime.timedelta(days=settings.JWT_EXPIRATION_DELTA[0]))
        token = generate_jwt({'user_id': user_id}, expiry)
        return token
    def post(self,request):
        #获取参数
        json_data = request.body
        dict_data = json.loads(json_data.decode())
        username = dict_data.get("username")
        password = dict_data.get("password")
        #检验参数
        if not all([username,password]):
            return http.JsonResponse({"code":RETCODE.PARAMERR,"errmsg":"参数不足"})
        #用户验证
        user = authenticate(username=username, password=password)
        if not user:#不存在抛出异常
            return http.JsonResponse({"code":RETCODE.AUTHENTIC,"errmsg":"帐号或密码错误"})
        #生成token
        token = self._generate_token(user.id)
        context = {
            "code": RETCODE.OK,
            "token":token,
            "username":user.username,
            "user_id":user.id
        }
        #作出响应
        return http.JsonResponse(context)

