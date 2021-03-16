import json

from django import http
from django.views import View
from django.shortcuts import render

from goods.models import Spu,Sku,SpuSpecification,SpecificationOption,SkuSpecification
from goods.utils import get_spu, get_goods_category, get_pagination_data, get_sku, get_sku_image, get_detail_image, \
    get_img

from contents.utils import get_category

# Create your views here.
#商品列表
class GoodsListView(View):
    def get(self,request,category_id):
        page = request.GET.get('page')
        if not page:
            page = 1
        sort = request.GET.get('sort', 'default')
        p_r = request.GET.get("p_r",'')
        #排序后数据
        skus_list = get_spu(sort,p_r)
        #面包屑
        breadcrums= get_goods_category(category_id)
        #分类器
        sku_dict,total_page = get_pagination_data(skus_list,page)
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
        return render(request,"list.html",content)
#商品详情信息
class GoodsDetailView(View):
    def get(self,request,spu_id):
        detail_image = get_sku_image(spu_id)
        desc_dict = get_detail_image(spu_id)
        goods_detail = get_sku(spu_id,detail_image,desc_dict)
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
        print(spec_label,spec_title)
        context = get_img(spec_title,spec_id,spec_label,flag)
        return http.JsonResponse(context)

