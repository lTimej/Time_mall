from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    #支付
    url(r'^payment/(?P<orderId>\d+)/$',views.PayView.as_view(),name="payment"),
    #支付状态
    url(r'^payment/status/$',views.PaymentStatusView.as_view(),name="paystatus")

]