
import json
from decimal import Decimal

from django import http
from django.conf import settings
from django.shortcuts import render

# Create your views here.
from django.views import View

from Time_mall.utils.response_code import RETCODE
from django_redis import get_redis_connection

from goods.models import Sku
from orders.utils import get_carts, get_addr


class BuyView(View):
    def get(self,request):
        cart_list = []
        user = request.user
        if not user.is_authenticated:
            return http.HttpResponseForbidden("未登录")
        #获取参数
        sku_id = request.GET.get("sku_id")
        count = request.GET.get("count")
        specs = request.GET.get("specs")
        #校验参数
        if not all([sku_id,count,specs]):
            return http.HttpResponseForbidden("参数不足")
        try:
            sku_obj = Sku.objects.get(id=sku_id)
        except:
            return http.HttpResponseForbidden("商品不存在")
        sku_dict = {
            'id':'buy',
            'sku_id': sku_id,
            'title': sku_obj.title,
            'price': str(sku_obj.price),
            'img': settings.HTT + str(sku_obj.skuimage_set.first().image),
            'count': count,
            'selected': '',
            'sku_specs': eval(specs),
            "spu_id": sku_obj.spu_id,
            "sku_amount_price": str(Decimal(str(sku_obj.now_price * int(count))).quantize(Decimal("0.00"))),
            'youhui': str(Decimal(str((sku_obj.price - sku_obj.now_price) * int(count))).quantize(Decimal("0.00")))
        }
        cart_list.append(sku_dict)
        cartLen = len(cart_list)
        address_dict_list, default_address_id = get_addr(user)
        if not cart_list:
            context = {
                "code": 0,
                'carts': cart_list,
                "cartLen": cartLen,
                "addresses": address_dict_list,
                "default_address": default_address_id,
            }
        else:
            context = {
                "code": 1,
                'carts': cart_list,
                "cartLen": cartLen,
                "addresses": address_dict_list,
                "default_address": default_address_id,
            }
        return render(request, 'order.html', context)
    def post(self, request):
        # 获取参数
        json_data = request.body.decode()
        data = json.loads(json_data)
        specs = data.get("specs")
        spec = [key + ':' + value for key, value in specs.items()]
        # 响应结果
        return http.JsonResponse({'code': 'ok', 'errmsg': '购买成功',"specs":str(spec)})