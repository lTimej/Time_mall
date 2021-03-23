import json,logging
from decimal import Decimal
from django.utils import timezone
from django.db import transaction

from django import http
from django.conf import settings
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
# Create your views here.
from Time_mall.utils.response_code import RETCODE
from goods.models import Sku
from users.models import Address
from orders.models import OrderInfo,OrderGoods

#日志器
logger = logging.getLogger('django')
class OrderListView(View):
    def get(self,request):
        user = request.user
        if not user.is_authenticated:
            return http.HttpResponseForbidden("未登录")
        #获取购物车信息
        # 链接resdis数据库
        redis_conn = get_redis_connection("carts")
        skus = redis_conn.hgetall('cart_user_%s' % user.id)
        selected = redis_conn.smembers("cart_selected_%s" % user.id)
        # 构建购物车数据结构
        carts = {}
        for sku_id, count in skus.items():
            # 商品属性
            spec = redis_conn.hget("spec_user_%s" % user.id, int(sku_id))
            spec = eval(spec.decode())
            carts[int(sku_id)] = {
                "count": int(count),
                "selected": sku_id in selected,
                "spec": spec
            }
        cart_list = list()
        for sku_id in carts.keys():
            selected = carts[sku_id].get("selected")
            if not selected:#选择勾选的商品
                continue
            sku_obj = Sku.objects.get(id=sku_id)
            sku_id = sku_obj.id
            spu_id = sku_obj.spu_id
            title = sku_obj.title
            price = str(sku_obj.price)
            now_price = str(sku_obj.now_price)
            img = settings.HTT + str(sku_obj.skuimage_set.first().image)
            count = carts[sku_id].get("count")
            sku_specs = carts[sku_id].get("spec")
            # 保留两位小数
            sku_amount_price = str(eval(now_price) * int(count))
            sku_amount_price = str(Decimal(sku_amount_price).quantize(Decimal("0.00")))
            youhui = str((eval(price) - eval(now_price))*count)
            youhui = str(Decimal(youhui).quantize(Decimal("0.00")))
            sku_dict = {
                'sku_id': sku_id,
                'title': title,
                'price': price,
                'img': img,
                'count': count,
                'selected': str(selected),
                'sku_specs': sku_specs,
                "spu_id": spu_id,
                "sku_amount_price": sku_amount_price,
                'youhui':youhui
            }
            cart_list.append(sku_dict)
        cartLen = len(cart_list)

        #
        try:
            addresses = Address.objects.filter(user_id=user.id,is_deleted=False)
        except :
            addresses = None
        try:
            default_address_id = user.default_address_id
        except:
            default_address_id = None
        address_dict_list = []
        # 重构前端数据
        default_addr = {}
        for address in addresses:
            if address.id == default_address_id:
                default_addr = {
                    "id": address.id,
                    "receiver": address.receiver,
                    "province": address.province.name,
                    "city": address.city.name,
                    "district": address.district.name,
                    "province_id": address.province.id,
                    "city_id": address.city.id,
                    "district_id": address.district.id,
                    "place": address.place,
                    "mobile": address.mobile,
                }
                continue
            address_dict = {
                "id": address.id,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "province_id": address.province.id,
                "city_id": address.city.id,
                "district_id": address.district.id,
                "place": address.place,
                "mobile": address.mobile,
                "email":address.email or ''
            }
            address_dict_list.append(address_dict)
        #将默认地址放在最前面
        if default_address_id:
            address_dict_list.insert(0,default_addr)
        if not cart_list:
            context = {
                "code":0,
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
        return render(request,'order.html',context)
class OrderView(View):
    def post(self,request):
        #获取参数
        data_str = request.body.decode()
        data_dict = json.loads(data_str)
        address_id = data_dict.get('address_id')
        pay_method = data_dict.get("pay_method")
        #校验参数
        if not all([address_id,pay_method]):
            return http.HttpResponseForbidden("缺少必传参数")
        try:#校验地址是否存在
            address = Address.objects.get(id=address_id)
        except Exception:
            return http.HttpResponseForbidden("地址不存在")
        #判断支付方式是否存在
        if pay_method not in OrderInfo.PAY_METHODS_ENUM.values():
            return http.HttpResponseForbidden("付款方式有误")
        with transaction.atomic():
            #创建事物保存点
            save_id = transaction.savepoint()
            try:
                # 获取当前登录用户
                user = request.user
                if not user.is_authenticated:
                    return http.JsonResponse({"code":RETCODE.SESSIONERR,"errmsg":"未登录"})
                #获取redis被勾选的数据
                redis_conn = get_redis_connection("carts")
                skus = redis_conn.hgetall("cart_user_%s"%user.id)
                selected = redis_conn.smembers("cart_selected_%s"%user.id)
                skus_id = [sku_id for sku_id in selected if sku_id in skus]
                #初始化商品总数和商品总价格
                total_num = 0
                total_price = 0
                freight = Decimal('0.00')
                order_id = timezone.localtime().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=total_num,
                    total_amount=total_price,
                    freight=freight,
                    pay_method=pay_method,
                    status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'] if pay_method == OrderInfo.PAY_METHODS_ENUM[
                        'ALIPAY'] else
                    OrderInfo.ORDER_STATUS_ENUM['UNSEND']
                )
                for sku_id in skus_id:#查询被勾选的商品
                    while True:
                        # 获取商品属性
                        spec = redis_conn.hget("spec_user_%s" % user.id, int(sku_id)).decode()
                        # 获取商品数量
                        count = int(skus.get(sku_id))
                        sku_obj = Sku.objects.get(id=int(sku_id))
                        price = Decimal(sku_obj.now_price).quantize(Decimal("0.00"))
                        total_num += count
                        total_price += count * price
                        # 查询商品库存量
                        start_stock = sku_obj.stock
                        start_sales = sku_obj.sales
                        if count > start_stock:  # 库存不足报错
                            sku = {  # 响应响应库存不足的商品
                                "sku_title": sku_obj.title,
                                "specs": spec
                            }
                            transaction.savepoint_rollback(save_id)  # 回滚到保存点
                            return http.JsonResponse({'code': RETCODE.STOCKERR, 'errmsg': '库存不足', "sku": sku})
                        now_stock = start_stock - count
                        now_sales = start_sales + count
                        # 增加sku的销售了减少库存量
                        res = Sku.objects.filter(id=sku_id,stock=start_stock).update(
                            stock=now_stock,
                            sales=now_sales
                        )
                        if res == 0:
                            continue
                        # 增加spu的销售
                        sku_obj.spu.sales += count
                        sku_obj.spu.save()
                        #保存订单信息
                        OrderGoods.objects.create(
                            order=order,
                            sku=sku_obj,
                            count=count,
                            price=price,
                            specs=spec
                        )
                        break
                order.total_count = total_num
                order.total_amount = total_price + freight
                order.save()
                sku_id = skus_id[0]
                sku_count = int(skus.get(sku_id))
            except Exception as e:
                logger.error(e)
                transaction.savepoint_rollback(save_id)
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '下单失败'})
            #订单提交成功，提交一次事务
            transaction.savepoint_commit(save_id)
        #订单提交清空购物车商品
        pipeline = redis_conn.pipeline()
        pipeline.hdel("cart_user_%s"%user.id,*selected)
        pipeline.srem("cart_selected_%s"%user.id,*selected)
        pipeline.hdel("spec_user_%s"%user.id,*selected)
        #执行
        try:
            pipeline.execute()
        except Exception:
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '数据错误'})
        print(address_id,pay_method,type(address_id),type(pay_method))
        return http.JsonResponse({"code":RETCODE.OK,'errmsg':"提交成功","order_id":order.order_id,"sku_id":int(sku_id),"sku_count":int(sku_count)})
class CommitOrderView(View):
    def get(self,request):
        #获取参数
        order_id = request.GET.get("order_id")
        pay_method = request.GET.get("pay_method")
        total_price = request.GET.get("payment_amount")
        mv = request.GET.get("mv")
        mv = mv.split('_')
        print(mv)
        sku_id = int(mv[0])
        sku_count = int(mv[1])
        try:
            sku_obj= Sku.objects.get(id=sku_id)
            sku_title = sku_obj.title
        except Exception:
            return http.HttpResponseForbidden("商品不存在")
        #校验参数
        if not all([order_id,pay_method,total_price]):
            return http.HttpResponseForbidden("参数不足")
        try:
            order_obj = OrderInfo.objects.get(order_id=order_id)
        except Exception:
            return http.HttpResponseForbidden("订单不存在在")
        orders = {
            "order_id": order_id,
            "pay_method": pay_method,
            "total_price": total_price,
            "sku_title":sku_title,
            "sku_count":sku_count
        }
        context = {
            "orders":orders
        }
        print(context)
        return render(request,'summit_order.html',context)
class UserOrderView(View):
    def get(self,request,page):
        orderInfo_query = OrderInfo.objects.all()
        orders = list()
        for orderInfo_obj in orderInfo_query:
            orders_dict = dict()
            order_id = orderInfo_obj.order_id
            orderGoods_query = orderInfo_obj.skus.all()
            for orderGoods_obj in orderGoods_query:
                sku_count = orderGoods_obj.count
                sku_id = orderGoods_obj.sku_id
                sku_obj = Sku.objects.get(id=sku_id)
                sku_title = sku_obj.title
                sku_price = sku_obj.price
                sku_now_price = sku_obj.now_price
                sku_img = sku_obj.skuimage_set.first().image
                sku_specs = eval(orderGoods_obj.specs)
                orders_dict['title'] = sku_title
                print(sku_title,sku_count,sku_price,sku_now_price,sku_specs,sku_img)
        return render(request,'user_order.html')