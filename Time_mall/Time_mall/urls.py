"""Time_mall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    #用户
    url(r'^',include('users.urls',namespace='users')),
    #首页
    url(r'^',include('contents.urls',namespace='contents')),
    #验证码
    url(r'^',include('verify.urls',namespace='verify')),
    #第三方
    url(r'^',include('oauths.urls',namespace='oauths')),
    #收获地址
    url(r'^',include('areas.urls',namespace='areas')),
    #商品
    url(r'^',include('goods.urls',namespace='goods')),
    #购物车
    url(r'^',include('cart.urls',namespace='cart')),
    #订单
    url(r'^',include('orders.urls',namespace='orders')),
    #支付
    url(r'^',include('payments.urls',namespace='payments')),
    #立即购买
    url(r'^',include('buys.urls',namespace='buys')),
]