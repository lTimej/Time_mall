import json,logging
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.db import transaction


from django import http
from django.conf import settings
from django.shortcuts import render, redirect
from django.views import View
from django_redis import get_redis_connection
# Create your views here.
from response_code import RETCODE

from goods import constants
from goods.models import Sku
from goods.utils import get_pagination_data
from orders.utils import get_carts, get_addr
from users.models import Address
from orders.models import OrderInfo,OrderGoods

#日志器
logger = logging.getLogger('django')
class OrderListView(View):
    def get(self,request):
        user = request.user
        if not user.is_authenticated:
            return http.HttpResponseForbidden("未登录")

        cart_list,cartLen = get_carts(user)
        address_dict_list,default_address_id = get_addr(user)
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
        #立即购买是商品信息
        sku_id = int(data_dict.get("sku_id"))
        count = int(data_dict.get("count"))
        specs = data_dict.get("specs")
        buy_id = data_dict.get('id')
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
                skus_id = [int(sku_id) for sku_id in selected if sku_id in skus]

                if buy_id:
                    skus_id = list()
                    skus_id.append(sku_id)
                #初始化商品总数和商品总价格
                total_num = 0
                total_price = 0
                freight = Decimal('0.00')
                order_id = timezone.localtime().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)
                order = OrderInfo.objects.create(#新增订单信息
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=total_num,
                    total_amount=total_price,
                    freight=freight,
                    pay_method=pay_method,
                    #判断支付方式，如果为货到付款则修改为代发货状态
                    status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'] if pay_method == OrderInfo.PAY_METHODS_ENUM[
                        'ALIPAY'] else
                    OrderInfo.ORDER_STATUS_ENUM['UNSEND']
                )
                for sku_id in skus_id:#查询被勾选的商品
                    while True:
                        # 获取商品属性
                        try:
                            if not buy_id:
                                spec = redis_conn.hget("spec_user_%s" % user.id, sku_id).decode()
                                count = int(skus.get(str(sku_id).encode()))
                            else:
                                spec = specs
                                count = int(count)
                        except:
                            spec = specs
                            count = int(count)
                        # 获取商品数量
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
                #订单成功提交显示sku标题和数量
                sku_id = sku_id
                sku_count = int(count)
            except Exception as e:
                logger.error(e)
                transaction.savepoint_rollback(save_id)
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '下单失败'})
            #订单提交成功，提交一次事务
            transaction.savepoint_commit(save_id)
        #执行
        if not buy_id:
            try:
                # 订单提交清空购物车商品
                pipeline = redis_conn.pipeline()
                pipeline.hdel("cart_user_%s" % user.id, *selected)
                pipeline.srem("cart_selected_%s" % user.id, *selected)
                pipeline.hdel("spec_user_%s" % user.id, *selected)
                pipeline.execute()
            except Exception:
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '数据错误'})
        return http.JsonResponse({"code":RETCODE.OK,'errmsg':"提交成功","order_id":order.order_id,"sku_id":int(sku_id),"sku_count":int(sku_count)})
class CommitOrderView(View):
    def get(self,request):
        #获取参数
        order_id = request.GET.get("order_id")
        pay_method = request.GET.get("pay_method")
        total_price = request.GET.get("payment_amount")
        mv = request.GET.get("mv")
        mv = mv.split('_')
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
        return render(request,'summit_order.html',context)
#用户订单列表
class UserOrderView(LoginRequiredMixin,View):
    def get(self,request,page):
        user = request.user
        orderInfo_query = OrderInfo.objects.filter(is_deleted=False,user=user)
        #构造前端数据/home/time/app_public_key.pem
        orders = list()
        for orderInfo_obj in orderInfo_query:
            #查找订单信息
            orders_dict = dict()
            orders_list = list()
            order_id = orderInfo_obj.order_id
            createTime = str(orderInfo_obj.create_time)[0:str(orderInfo_obj.create_time).find('.')]
            status = OrderInfo.ORDER_STATUS_CHOICES[orderInfo_obj.status-1][1]
            freight =str( orderInfo_obj.freight)
            orders_dict['orderId'] = order_id
            orders_dict['createTime'] = createTime
            total_price = 0
            orderGoods_query = orderInfo_obj.skus.all()
            #查找sku信息
            for orderGoods_obj in orderGoods_query:
                d = dict()
                sku_count = orderGoods_obj.count
                sku_id = orderGoods_obj.sku_id
                sku_obj = Sku.objects.get(id=sku_id)
                spu_id = sku_obj.spu_id
                sku_title = sku_obj.title
                sku_price = sku_obj.price
                sku_now_price = sku_obj.now_price
                total_price += sku_count * sku_now_price
                sku_img = settings.HTT + str(sku_obj.skuimage_set.first().image)
                sku_specs = eval(orderGoods_obj.specs)
                d['title'] = sku_title
                d["count"] = sku_count
                d['price'] = str(sku_price)
                d['now_price'] = str(sku_now_price)
                d['image'] = sku_img
                d["specs"] = sku_specs
                d["spu_id"] = spu_id
                orders_list.append(d)
            orders_list[0]['total_price'] = str(total_price)
            orders_list[0]['freight'] = str(freight)
            orders_list[0]['status'] = status
            orders_dict['orders'] = orders_list
            orders.append(orders_dict)
        #每页显示订单数
        per_page_num = constants.ORDER_LIST_LIMIT
        #如果用户随意输入的页数不符合，则跳转第一页
        if len(orders)%2 == 0:
            total_page = len(orders) // per_page_num
        else:
            total_page = len(orders) // per_page_num +1
        if int(page) > total_page or int(page) <1:
            page = 1
        #分页后数据
        order_dict, total_page = get_pagination_data(orders, page, per_page_num)
        #上下文
        context = {
            "page_num": int(page),
            "total_page": total_page,
            "orders":order_dict
        }
        #响应
        return render(request,'user_order.html',context)
#删除订单
class DelOrderView(View):
    def get(self,request,order_id):
        order_id = order_id[0:-1]
        page = order_id[-1]
        try:
            OrderInfo.objects.filter(order_id=order_id).update(
                is_deleted=True
            )
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden("订单不存在")
        return redirect('/user/order/1/')
#订单详情
class OrderDetailView(View):
    def get(self,request,order_id):
        # order_id = request.GET.get("orderId")

        orderInfo_obj = OrderInfo.objects.get(order_id=order_id)
        order_status = OrderInfo.ORDER_STATUS_CHOICES[orderInfo_obj.status-1][1]
        order_time = str(orderInfo_obj.create_time)[0:str(orderInfo_obj.create_time).find('.')]
        order = {
            "order_id":order_id,
            "order_status":order_status,
            "order_time":order_time
        }
        address_obj = orderInfo_obj.address
        receiver = address_obj.receiver
        addr = address_obj.province.name + address_obj.city.name + address_obj.district.name + address_obj.place
        email = address_obj.email
        phone = address_obj.mobile
        address = {
            "receiver":receiver,
            "addr":addr,
            "enail":email or '',
            "phone":phone
        }
        ordergoods_query = orderInfo_obj.skus.all()
        skus = []
        for og_obj in ordergoods_query:
            sku_obj = og_obj.sku
            sku = {
                'sku_title' : sku_obj.title,
                'sku_img' : settings.HTT + str(sku_obj.skuimage_set.first().image),
                'sku_price' :str(sku_obj.price),
                'sku_now_price' : str(sku_obj.now_price),
                'sku_spec' : eval(og_obj.specs),
                'sku_cout' : og_obj.count,
                'spu_id':str(sku_obj.spu_id)
            }
            skus.append(sku)
        skus[0]['total_price'] = str(orderInfo_obj.total_amount)
        skus[0]["sku_status"] = OrderInfo.ORDER_STATUS_CHOICES[orderInfo_obj.status-1][1]
        skus[0]["yh"] = "每满100元减10元：省¥7.47满2件减2元"
        context = {
            "order":order,
            "address":address,
            "sku":skus,
        }
        print(context)
        return render(request,'order_detail.html',context)