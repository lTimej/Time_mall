import json
import base64
import pickle
from decimal import Decimal

from django.shortcuts import render
from django import http
from django.views import View
from django.contrib.auth import authenticate
# Create your views here.
from django_redis import get_redis_connection
from django.conf import settings

from Time_mall.utils.response_code import RETCODE

from cart.utils import combine_carts
from goods import constants
from goods.models import Sku
from goods.utils import get_pagination_data

from django.contrib.auth.mixins import LoginRequiredMixin

class CartListView(View):
    def get(self,request):
        #判断用户是否登录
        user = request.user
        if  user.is_authenticated:#已登录，获取redis数据
            #链接resdis数据库
            redis_conn = get_redis_connection("carts")
            skus = redis_conn.hgetall('cart_user_%s'%user.id)
            selected = redis_conn.smembers("cart_selected_%s"%user.id)
            #构建购物车数据结构
            carts = {}
            for sku_id,count in skus.items():
                # 商品属性
                spec = redis_conn.hget("spec_user_%s" % user.id, int(sku_id))
                spec = eval(spec.decode())
                carts[int(sku_id)] = {
                    "count":int(count),
                    "selected":sku_id in selected,
                    "spec":spec
                }
        else:#未登录，获取cookies数据
            carts_str = request.COOKIES.get("carts")
            if carts_str:
                carts = pickle.loads(base64.b64decode(carts_str.encode()))
            else:
                carts = {}
        #查询sku信息

        cart_list = list()
        for sku_id in carts.keys():
            sku_obj = Sku.objects.get(id=sku_id)
            sku_id = sku_obj.id
            spu_id = sku_obj.spu_id
            title = sku_obj.title
            price = str(sku_obj.price)
            now_price = str(sku_obj.now_price)
            img = settings.HTT + str(sku_obj.skuimage_set.first().image)
            count = carts[sku_id].get("count")
            sku_specs = carts[sku_id].get("spec")
            selected = carts[sku_id].get("selected")
            #保留两位小数
            sku_amount_price = str(eval(now_price) *int(count))
            sku_amount_price = str(Decimal(sku_amount_price).quantize(Decimal("0.00")))
            sku_dict = {
                'sku_id':sku_id,
                'title':title,
                'price':price,
                'now_price':now_price,
                'img':img,
                'count':count,
                'selected':str(selected),
                'sku_specs':sku_specs,
                "spu_id":spu_id,
                "sku_amount_price":sku_amount_price
            }
            cart_list.append(sku_dict)
        cartLen = len(cart_list)
        context = {
            'carts':cart_list,
            "cartLen":cartLen,
        }
        return render(request,'cart.html',context)
    def post(self,request):
        #获取参数
        json_data = request.body.decode()
        data = json.loads(json_data)
        sku_id = data.get("sku_id")
        sku_count = data.get("count")
        selected = data.get("selected",True)
        specs = data.get("specs")
        spec = [key+':' + value for key,value in specs.items()]
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
            pipeline.hset("spec_user_%s" % user.id, sku_id, str(spec))
            # pipeline.set("cart_spec_%s" % sku_id, str(spec))
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
                # carts_dict[sku_id]['selected'] = selected
                # carts_dict[sku_id]['selected'] = selected
            else:#不存在则添加sku
                carts_dict[sku_id] = {
                    "count":sku_count,
                    "selected":selected,
                    "spec":spec
                }
                #将字典转换成base64的字符串
            carts = base64.b64encode(pickle.dumps(carts_dict)).decode()
            #构造响应
            response = http.JsonResponse({'code':'ok','errmsg':"添加购物车成功"})
            response.set_cookie('carts', carts, max_age=constants.CARTS_COOKIE_EXPIRES)
            return response
    def put(self,request):
        # 获取参数
        json_data = request.body.decode()
        data = json.loads(json_data)
        sku_id = data.get("sku_id")
        sku_count = data.get("count")
        sku_price = data.get("price")
        sku_amount_price = str(float(sku_price) * int(sku_count))
        sku_amount_price = str(Decimal(sku_amount_price).quantize(Decimal("0.00")))
        selected = data.get("selected",True)
        if not all([sku_id,sku_count]):
            return http.HttpResponseForbidden("参数不全")
        # 判断sku是否存在
        try:
            Sku.objects.get(id=sku_id)
        except Sku.DoesNotExist:
            return http.HttpResponseForbidden("商品不存在")
        user = request.user
        # 判断用户是否登录
        if user.is_authenticated:  # 已登录加入redis4号库
            redis_conn = get_redis_connection("carts")
            pipeline = redis_conn.pipeline()
            #直接覆盖当前用户sku的数量
            pipeline.hset("cart_user_%s" % user.id, sku_id, sku_count)
            if selected:#如果选中，添加
                pipeline.sadd("cart_selected_%s" % user.id, sku_id)
            else:#没选中，删除
                pipeline.srem("cart_selected_%s" % user.id, sku_id)
            pipeline.execute()
            # 响应结果
            cart_sku = {
                "sku_id": sku_id,
                "count": sku_count,
                "selected": selected,
                "sku_amount_price":sku_amount_price
            }
            return http.JsonResponse({'code':RETCODE.OK, 'errmsg':'修改购物车成功', 'cart_sku':cart_sku})
        else:  # 未登录加入cookies中
            # 获取carts的cookies值
            carts_str = request.COOKIES.get("carts")
            if carts_str:  # 存在把cookie值转换为字典
                carts_dict = pickle.loads(base64.b64decode(carts_str.encode()))
            else:  # 不存在设置cart_dict为空
                carts_dict = {}
            # 从购物车中获取sku
            cart_sku = carts_dict.get(sku_id)
            if cart_sku:  # 购物车存在这sku则将覆盖
                carts_dict[sku_id]['count'] = sku_count
                carts_dict[sku_id]['selected'] = selected
            else:  # 不存在则添加sku
                carts_dict[sku_id] = {
                    "count": sku_count,
                    "selected": selected,
                }
                # 将字典转换成base64的字符串
            carts = base64.b64encode(pickle.dumps(carts_dict)).decode()

            # 构造响应数据
            cart_sku = {
                "sku_id": sku_id,
                "count": sku_count,
                "selected": selected,
                "sku_amount_price":sku_amount_price
            }
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '修改购物车成功', 'cart_sku': cart_sku})
            response.set_cookie('carts', carts, max_age=constants.CARTS_COOKIE_EXPIRES)
            return response
    def delete(self,request):
        # 获取参数
        json_data = request.body.decode()
        data = json.loads(json_data)
        sku_id = data.get("sku_id")
        # 判断sku是否存在
        try:
            Sku.objects.get(id=sku_id)
        except Sku.DoesNotExist:
            return http.HttpResponseForbidden("商品不存在")
        user = request.user
        # 判断用户是否登录
        if user.is_authenticated:  # 已登录加入redis4号库
            redis_conn = get_redis_connection("carts")
            pipeline = redis_conn.pipeline()
            pipeline.hdel("cart_user_%s" % user.id, sku_id)
            pipeline.srem("cart_selected_%s" % user.id, sku_id)
            pipeline.execute()
            # 响应结果
            cart_sku = {
                "sku_id": sku_id,
            }
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '修改购物车成功', 'cart_sku': cart_sku})
        else:  # 未登录加入cookies中
            # 获取carts的cookies值
            carts_str = request.COOKIES.get("carts")
            if carts_str:  # 存在把cookie值转换为字典
                carts_dict = pickle.loads(base64.b64decode(carts_str.encode()))
            else:  # 不存在设置cart_dict为空
                carts_dict = {}
            # 从购物车中获取sku
            cart_sku = carts_dict.get(sku_id)
            if cart_sku:
                del carts_dict[sku_id]
                # 将字典转换成base64的字符串
            carts = base64.b64encode(pickle.dumps(carts_dict)).decode()
            # 构造响应数据
            cart_sku = {
                "sku_id": sku_id,
            }
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '修改购物车成功', 'cart_sku': cart_sku})
            response.set_cookie('carts', carts, max_age=constants.CARTS_COOKIE_EXPIRES)
            return response
class CartSelectedView(View):
    def put(self,request):
        # 获取参数
        json_data = request.body.decode()
        data = json.loads(json_data)
        selected = data.get("selected", True)
        user = request.user
        # 判断用户是否登录
        if user.is_authenticated:  # 已登录加入redis4号库
            redis_conn = get_redis_connection("carts")
            redis_cart = redis_conn.hgetall("cart_user_%s" % user.id)
            key = redis_cart.keys()
            if selected:#全勾选，sku_id全添加
                redis_conn.sadd("cart_selected_%s"%user.id,*key)
            else:#全取消，则删除
                redis_conn.srem("cart_selected_%s"%user.id,*key)
            # 响应结果
            cart_sku = {
                "selected": selected,
            }
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '修改购物车成功', 'cart_sku': cart_sku})
        else:  # 未登录加入cookies中
            # 获取carts的cookies值
            carts_str = request.COOKIES.get("carts")
            if carts_str:  # 存在把cookie值转换为字典
                carts_dict = pickle.loads(base64.b64decode(carts_str.encode()))
            else:  # 不存在设置cart_dict为空
                carts_dict = {}
            if  selected:#全选，将sku设置True
                for carts in carts_dict.values():
                    carts['selected'] = True
            else:#全取消，将sku取消
                for carts in carts_dict.values():
                    carts['selected'] = False
                # 将字典转换成base64的字符串
            carts = base64.b64encode(pickle.dumps(carts_dict)).decode()
            # 构造响应数据
            cart_sku = {
                "selected": selected,
            }
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '修改购物车成功', 'cart_sku': cart_sku})
            response.set_cookie('carts', carts, max_age=constants.CARTS_COOKIE_EXPIRES)
            return response
class ShortCutCartView(View):
    def get(self,request):
        #获取用户
        user = request.user
        if user.is_authenticated:#已登录，获取redis值
            redis_conn = get_redis_connection('carts')
            skus = redis_conn.hgetall('cart_user_%s'%user.id)
            carts = {}
            for sku_id, count in skus.items():
                carts[int(sku_id)] = {
                    "count": int(count),
                }
        else:#未登录，获取cookies
            carts_str = request.COOKIES.get("carts")
            if carts_str:
                carts = pickle.loads(base64.b64decode(carts_str.encode()))
            else:
                carts = {}
        # 查询sku信息
        cart_list = list()
        #构造sku商品信息
        for sku_id in carts.keys():
            sku_obj = Sku.objects.get(id=sku_id)
            sku_id = sku_obj.id
            spu_id = sku_obj.spu_id
            title = sku_obj.title
            img = settings.HTT + str(sku_obj.skuimage_set.first().image)
            count = carts[sku_id].get("count")
            sku_dict = {
                'sku_id': sku_id,
                'title': title,
                'img': img,
                'count': count,
                "spu_id": spu_id,
            }
            cart_list.append(sku_dict)
        cartLen = len(cart_list)
        context = {
            "code":"ok",
            'carts': cart_list[0:3],#快捷栏只显示三天购物车信息
            "cartLen":cartLen
        }
        return http.JsonResponse(context)