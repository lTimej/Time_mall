import pickle,base64
from decimal import Decimal

from django.conf import settings
from django_redis import get_redis_connection

from goods.models import Sku

def combine_carts(request,user,response):
    carts_str = request.COOKIES.get("carts")
    if carts_str:#存在获取
        cart_dict = pickle.loads(base64.b64decode(carts_str.encode()))
    else:#不存在则返回
        return response
    redis_conn = get_redis_connection("carts")
    skus = redis_conn.hgetall('cart_user_%s'%user.id)
    selected = redis_conn.smembers("cart_selected_%s"%user.id)
    skus_dict = dict()
    for sku,count in skus.items():
        spec = redis_conn.hget("spec_user_%s" % user.id,sku).decode()
        skus_dict[int(sku)] = {
            "spec":spec,
            "selected":sku in selected,
            "count": int(count)
        }
    #整合
    for key,value in cart_dict.items():
        pipeline = redis_conn.pipeline()
        if not skus_dict.get(key):#不存在则新增
            pipeline.hincrby("cart_user_%s"%user.id,key,value.get("count"))
            pipeline.hset("spec_user_%s" % user.id, key, str(value.get("spec")))
            if value.get("selected"):
                pipeline.sadd("cart_selected_%s" % user.id, key)
        else:#存在则修改商品数量
            count = cart_dict.get(key).get("count") + value.get("count")
            pipeline.hset("cart_user_%s"%user.id,key,count)
        pipeline.execute()
    # 清除cookie
    response.delete_cookie('carts')
    return response


