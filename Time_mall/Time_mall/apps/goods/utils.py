from django import http
from django.conf import settings
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage

from goods import constants
from goods.models import Spu, GoodsCategory, Sku, SpuSpecification, SpuDescs, SpecificationOption, SkuSpecification

htt = settings.HTT
htts = settings.HTTS
#spu商品列表
def get_spu(category_id,sort=None,p_r=None):
    skus_list = []
    sku_list = []
    #构造商品排列顺序
    if sort == "price":
        sort_sequence = "now_price"
    elif sort == "sales":
        sort_sequence = "sales"
    else:
        sort_sequence = "create_time"

    try:
        #过滤sku商品标题重复数据
        if p_r and p_r != '_':
            price_range = p_r.split('_')
            lp = price_range[0]
            rp = price_range[1]
            sku_title = Sku.objects.filter(Q(is_launched=True)&Q(now_price__lte=rp)&Q(now_price__gte=lp)).order_by(sort_sequence).values('title').distinct()
        else:
            sku_title = Sku.objects.filter(is_launched=True).order_by(sort_sequence).values('title').distinct()
        for sku in sku_title:
            if sku.get("title") not in sku_list:
                sku_list.append(sku.get("title"))
        #构造前端所需数据
        for sku_title in sku_list:
            sku_dict = {}
            #同类spu商品获取第一个sku商品
            if p_r and p_r != '_':
                price_range = p_r.split('_')
                lp = price_range[0]
                rp = price_range[1]
                skus_obj = Sku.objects.filter(Q(title=sku_title)&Q(now_price__lte=rp)&Q(now_price__gte=lp)&Q(category_id=category_id)).order_by(sort_sequence).first()
            else:
                skus_obj = Sku.objects.filter(title=sku_title,category_id=category_id).order_by(sort_sequence).first()
            try:
                title = skus_obj.title
                img = skus_obj.default_image
                price = skus_obj.price
                now_price = skus_obj.now_price
                spu_id = skus_obj.spu_id
                sku_dict['image'] = htt + str(img)
                sku_dict['title'] = title
                sku_dict['price'] = str(price)
                sku_dict['now_price'] = str(now_price)
                sku_dict['url'] = htts + 'detail/' + str(spu_id) +'/'
                skus_list.append(sku_dict)
            except:
                return http.HttpResponseNotFound('GoodsCategory does not exist')
    except Sku.DoesNotExist:
        return http.HttpResponseNotFound('GoodsCategory does not exist')
    return skus_list
#分页
def get_pagination_data(skus_dict,page,per_page_num):
    sku_dict = {}
    #分页器对象
    # Paginator(object_list, per_page_data)
    paginator = Paginator(skus_dict, per_page_num)
    try:#判断页表页是否存在
        # 获取列表页总页数
        total_page = paginator.num_pages
        #展示第几页数据
        page_skus = paginator.page(page)
    except:
        return http.HttpResponseNotFound('empty page')

    #转换成Vue能渲染的数据，不能识别QuerySet数据
    skus_list = []
    for skus in page_skus:
        skus_list.append(skus)
    sku_dict['goods'] = skus_list
    return sku_dict,total_page
#面包屑
def get_goods_category(category_id):
    breadcrums_dict = {}
    try:#成功
        obj = GoodsCategory.objects.get(id=category_id)
        #一级面包屑
        cat1 = "首页"
        # 二级面包屑
        cat2 = obj.parent.name
        # 三级面包屑
        cat3 = obj.name
        #构造面包屑字典数据
        breadcrums_dict['cat1'] = cat1
        breadcrums_dict['cat2'] = cat2
        breadcrums_dict['cat3'] = cat3
        return breadcrums_dict
    except Exception as e:#数据库查询失败返回空
        return breadcrums_dict
#sku商品信息
def get_sku(spu_id,detail_image,desc_dict):
    specs_query = SpuSpecification.objects.filter(spu_id=spu_id)
    sku_obj = Sku.objects.filter(spu_id=spu_id).first()
    goods_detail = dict()
    spec_dict = dict()
    d = {}
    specs_list = ['color','size']
    for index,specs_obj in enumerate(specs_query):
        specs_option_list = list()
        goods_specs = dict()
        name = specs_obj.name
        id = specs_obj.id
        specs_option_query = specs_obj.options.all()
        spec_id = 0
        for specs_option_obj in specs_option_query:
            value = specs_option_obj.value
            spec_id = specs_option_obj.spec_id
            if value not in specs_option_list:
                specs_option_list.append(value)
                spec_dict[name] = spec_id
        goods_specs[name] = specs_option_list
        d[specs_list[index]] = goods_specs
    title = sku_obj.title
    price = sku_obj.price
    now_price = sku_obj.now_price
    default_image = sku_obj.default_image
    goods_detail['title'] = title
    goods_detail['price'] = str(price)
    goods_detail['now_price'] = str(now_price)
    goods_detail['default_image'] = htt + str(default_image)
    goods_detail['goods_specs'] = d
    goods_detail['detail_image'] = detail_image
    goods_detail['desc_dict'] = desc_dict
    goods_detail['spec_dict'] = spec_dict
    goods_detail['spu_id'] = spu_id
    return goods_detail
#商品sku图
def get_sku_image(spu_id):
    sku_query= Sku.objects.filter(spu_id=spu_id)
    detail_image = list()
    for sku_obj in sku_query:
        sku_image_obj = sku_obj.skuimage_set.get()
        image = htt + str(sku_image_obj.image)
        detail_image.append(image)
    lens = len(detail_image)
    if lens < 5:
        return detail_image
    return detail_image[0:5]
#商品详情图
def get_detail_image(spu_id):
    desc_query = SpuDescs.objects.filter(spu_id=spu_id)
    desc_dict = dict()
    desc_img = list()
    for desc_obj in desc_query:
        desc_dict = dict()
        title = desc_obj.detail_info
        img = htt + str(desc_obj.desc_image)
        desc_img.append(img)
        desc_dict['title'] = title
    desc_dict['image'] = desc_img
    return desc_dict

def get_img(spec_title,spec_id,spec_label,flag):
    spec_option_obj = SpecificationOption.objects.filter(value=spec_title, spec_id=spec_id).first()
    spec_option_id = spec_option_obj.id
    sku_spec_obj = SkuSpecification.objects.filter(option_id=spec_option_id, spec_id=spec_id).first()
    sku_id = sku_spec_obj.id
    sku_obj = Sku.objects.get(id=sku_id)
    img = sku_obj.skuimage_set.first().image
    price = sku_obj.price
    now_price = sku_obj.now_price
    if flag == 0:
        context = {
            'sku_id':sku_id,
            'img': htt + str(img),
            'price':price,
            'now_price':now_price
        }
    else:
        context = {
            'img': htt + str(img),
            'price': price,
            'now_price': now_price
        }
    return context
