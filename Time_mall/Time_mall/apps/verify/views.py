import json

from django.shortcuts import render
from django.views import View
from django import http

from .libs.captcha.captcha import captcha
from Time_mall.utils import constants

from django_redis import get_redis_connection

# Create your views here.
class ImgCodeView(View):
    def get(self,request,uuid):
        text,code = captcha.generate_captcha()
        redis_conn = get_redis_connection('verify_code')
        redis_conn.setex('img_%s'%uuid,constants.IMAGE_CODE_REDIS_EXPIRES,text)
        return http.HttpResponse(code,content_type='image/jpg')
    def post(self,request,uuid):
        code = request.body.decode()
        code = json.loads(code)
        img_code = code.get('code')
        redis_conn = get_redis_connection('verify_code')
        cc = redis_conn.get('img_%s'%uuid)
        redis_img_code = cc.decode()
        redis_img_code = redis_img_code.lower()
        if img_code == redis_img_code:
            return http.JsonResponse({'code':0})
        else:
            return http.JsonResponse({'code': 1,'error_info':'验证码输入错误'})