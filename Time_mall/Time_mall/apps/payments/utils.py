import os

from alipay import AliPay, AliPayConfig
from django.conf import settings
# 创建支付宝支付对象
'''
出现钓鱼页面，关闭浏览器，崇打开

'''
def createAlipay():
    # 创建对接支付宝接口的SDK对象
    app_private_key_string = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem")).read()
    alipay_public_key_string = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/alipay_public_key.pem")).read()
    alipay = AliPay(  # 传入公共参数（对接任何接口都要传递的）
        appid=settings.ALIPAY_APPID,  # 应用ID
        app_notify_url=None,  # 默认回调url，如果采用同步通知就不传
        # 应用的私钥和支付宝公钥的路径
        app_private_key_string=app_private_key_string,
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2",  # 加密标准
        debug=settings.ALIPAY_DEBUG  # 指定是否是开发环境
    )
    return alipay

def generate_alipay_link(order,order_id,alipay):
    subject = "Time商城%s"%order_id
    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no = order_id,
        total_amount = str(order.total_amount),
        subject = subject,
        return_url = settings.ALIPAY_RETURN_URL,
        notify_url = "http://192.168.1.132:8081/payment/notify/"  # 可选, 不填则使用默认notify url
    )
    # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
    alipay_url = settings.ALIPAY_URL + "?" + order_string
    return alipay_url