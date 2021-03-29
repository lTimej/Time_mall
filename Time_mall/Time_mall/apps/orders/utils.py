from decimal import Decimal

from django.conf import settings
from django_redis import get_redis_connection

from goods.models import Sku
from users.models import Address


def get_carts(user):
    # 获取购物车信息
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
        if not selected:  # 选择勾选的商品
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
        youhui = str((eval(price) - eval(now_price)) * count)
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
            'youhui': youhui
        }
        cart_list.append(sku_dict)
    cartLen = len(cart_list)
    return cart_list,cartLen

def get_addr(user):
    # 获取地址
    try:
        addresses = Address.objects.filter(user_id=user.id, is_deleted=False)
    except:
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
            "email": address.email or ''
        }
        address_dict_list.append(address_dict)
    # 将默认地址放在最前面
    if default_address_id:
        address_dict_list.insert(0, default_addr)
    return address_dict_list,default_address_id