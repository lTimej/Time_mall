import json

from django import http
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render
from django_redis import get_redis_connection

from goods.models import Spu,Sku,SpuSpecification,SpecificationOption,SkuSpecification
from goods.utils import get_spu, get_goods_category, get_pagination_data, get_sku, get_sku_image, get_detail_image, \
    get_img

from contents.utils import get_category

from goods import constants

# Create your views here.
#商品列表
class GoodsListView(View):
    def get(self,request,category_id):
        page = request.GET.get('page')
        per_page_num = constants.GOODS_LIST_LIMIT
        if not page:
            page = 1
        sort = request.GET.get('sort', 'default')
        p_r = request.GET.get("p_r",'')
        #排序后数据
        skus_list = get_spu(category_id,sort,p_r)
        #面包屑
        breadcrums= get_goods_category(category_id)
        #分类器
        try:
            sku_dict,total_page = get_pagination_data(skus_list,page,per_page_num)
            content = {
                'spus_dict':sku_dict,
                'goods':get_category(),
                "breadcrums":breadcrums,
                "page_num":page,
                "total_page":total_page,
                "sort":sort,
                "category_id":category_id,
                "p_r":p_r
            }
        except:
            return http.HttpResponseForbidden("商品类别不存在")
        return render(request,"list.html",content)
#商品详情信息
class GoodsDetailView(View):
    def get(self,request,spu_id):
        user_id = request.user.id
        detail_image = get_sku_image(spu_id)
        desc_dict = get_detail_image(spu_id)
        goods_detail,sku_id = get_sku(spu_id,detail_image,desc_dict)
        #将浏览商品保存数据库
        redis_conn = get_redis_connection('history')
        pipeline = redis_conn.pipeline()
        pipeline.lrem('history_%s'%user_id,0,sku_id)
        pipeline.lpush('history_%s'%user_id,sku_id)
        pipeline.ltrim('history_%s'%user_id,0,4)
        pipeline.execute()
        context = {
            "goods_detail":goods_detail
        }
        return render(request,"detail.html",context)
#sku
class SkuView(View):
    def get(self,request):
        spec_title = request.GET.get("spec_title")
        spec_id = request.GET.get("spec_id")
        spec_label = request.GET.get("label")
        flag = int(request.GET.get("flag"))
        context = get_img(spec_title,spec_id,spec_label,flag)
        return http.JsonResponse(context)

#热销
class HotView(View):
    def get(self,request,category_id):
        print(category_id)
        sku_query = Sku.objects.order_by('-sales')[0:2]
        sku_hot = list()
        for sku_obj in sku_query:
            hot = dict()
            hot['title'] = sku_obj.title
            hot['price'] = str(sku_obj.price)
            hot['img'] = settings.HTT + str(sku_obj.skuimage_set.first().image)
            hot['spu_id'] = sku_obj.spu_id
            hot['sku_id'] = sku_obj.id
            sku_hot.append(hot)
        context = {
            'hots':sku_hot,
        }
        return http.JsonResponse({"code":'ok','hots':sku_hot})

