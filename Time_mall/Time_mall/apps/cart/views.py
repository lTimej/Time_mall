import json
import base64
import pickle

from django.shortcuts import render
from django import http
from django.views import View
from django.contrib.auth import authenticate
# Create your views here.
from django_redis import get_redis_connection

from goods import constants
from goods.models import Sku


class CartListView(View):
    def get(self,request):
        return render(request,'cart.html')
    def post(self,request):
        #获取参数
        json_data = request.body.decode()
        data = json.loads(json_data)
        sku_id = data.get("sku_id")
        sku_count = data.get("count")
        selected = data.get("selected",True)
        #验证参数
        #判断参数是否齐全
        if not all([sku_id,sku_count]):
            return http.HttpResponseForbidden("参数不全")
        #判断sku是否存在
        try:
            Sku.objects.get(id=sku_id)
        except Sku.DoesNotExist:
            return http.HttpResponseForbidden("商品不存在")
        #判断selected是否为bool
        if selected:
            if not isinstance(selected,bool):
                return http.HttpResponseForbidden("参数有误")
        print(sku_id,sku_count)
        user = request.user
        #判断用户是否登录
        if user.is_authenticated:#已登录加入redis4号库
            '''
                user_id:{
                    sku_id1:{
                        count:0,
                    }
                    sku_id2:{
                        count:0,
                    }
                }
                selected:[sku_id1,sku_id2]
            '''
            redis_conn = get_redis_connection("carts")
            pipeline = redis_conn.pipeline()
            pipeline.hincrby("cart_user_%s"%user.id,sku_id,sku_count)
            if selected:
                pipeline.sadd("cart_selected_%s"%user.id,sku_id)
            pipeline.execute()
            # 响应结果
            return http.JsonResponse({'code': 'ok', 'errmsg': '添加购物车成功'})
        else:#未登录加入cookies中
            '''
                {
                    sku_id1:{
                        count:1,
                        selected:True
                    },
                    sku_id2:{
                        count:1,
                        selected:True
                    }
                }
            '''
            #获取carts的cookies值
            carts_str = request.COOKIES.get("carts")
            if  carts_str:#存在把cookie值转换为字典
                carts_dict = pickle.loads(base64.b64decode(carts_str.encode()))
            else:#不存在设置cart_dict为空
                carts_dict = {}
            #从购物车中获取sku
            cart_sku = carts_dict.get(sku_id)
            if cart_sku:#购物车存在这sku则将加数量
                carts_dict[sku_id]['count'] += sku_count
                carts_dict[sku_id]['selected'] = selected
            else:#不存在则添加sku
                carts_dict[sku_id] = {
                    "count":sku_count,
                    "selected":selected
                }
                #将字典转换成base64的字符串
            carts = base64.b64encode(pickle.dumps(carts_dict)).decode()
            #构造响应
            response = http.JsonResponse({'code':'ok','errmsg':"添加购物车成功"})
            response.set_cookie('carts', carts, max_age=constants.CARTS_COOKIE_EXPIRES)
            return response