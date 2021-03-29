import os

from alipay import AliPay
from django import http
from django.conf import settings
from django.shortcuts import render, redirect

# Create your views here.
from django.views import View

from Time_mall.utils.view import MyLoginRequiredMixin

from Time_mall.utils.response_code import RETCODE
from orders.models import OrderInfo
from payments.models import Payment
from payments.utils import createAlipay,generate_alipay_link
'''
商家帐号
ywtcep5487@sandbox.com
买家帐号
tnjguu3290@sandbox.com
'''
class PayView(MyLoginRequiredMixin,View):
    def get(self,request,orderId):
        user = request.user
        try:
            order = OrderInfo.objects.get(order_id=orderId, user=user, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden('订单信息错误')
        alipay = createAlipay()
        alipay_url = generate_alipay_link(order,orderId,alipay)
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'alipay_url': alipay_url})
class PaymentStatusView(View):
    def get(self,request):
        # 获取前端传入的请求参数
        query_dict = request.GET
        data = query_dict.dict()
        # 获取并从请求参数中剔除signature
        signature = data.pop('sign')
        # 通知验证
        # 创建支付宝支付对象
        alipay = createAlipay()
        # 校验这个重定向是否是alipay重定向过来的
        success = alipay.verify(data, signature)
        if success:
            # 读取order_id
            order_id = data.get('out_trade_no')
            # 读取支付宝流水号
            trade_id = data.get('trade_no')
            # 保存Payment模型类数据
            try:
                Payment.objects.create(
                    order_id=order_id,
                    trade_id=trade_id
                )
                # 修改订单状态为待评价
                OrderInfo.objects.filter(order_id=order_id, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']).update(
                    status=OrderInfo.ORDER_STATUS_ENUM["UNCOMMENT"])
                # 响应trade_id
                context = {
                    'trade_id': trade_id
                }
                return render(request, 'payment.html', context)
            except Exception as e:
                # 订单重复保存则跳转订单页面
                return redirect('/user/order/1/')
        else:
            # 订单支付失败，重定向到我的订单
            return redirect('/user/order/1/')