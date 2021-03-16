from django.views import View
from django.shortcuts import render

from contents.utils import get_category, get_data, get_contents
from goods.models import GoodsCategory,ProductId
from contents.models import Content,ContentCategory,AdCategory

from collections import OrderedDict

class IndexView(View):
    def get(self,request):
        '''
        首页
        :param request:
        :return:
        '''
        #获取商品分类
        goods = get_category()
        obj = ContentCategory.objects.all()
        contents = {}
        for cc in obj:#一级标题
            ct_obj = cc.content_set.all()
            for content_obj in ct_obj:#二级标题
                cc_title = cc.title
                title = content_obj.title
                price = content_obj.price
                discountprice = content_obj.discountprice
                image = content_obj.image
                ad_id = cc.adCategory_id
                ad_obj = AdCategory.objects.get(id=ad_id)
                ad_title = ad_obj.title
                get_data(cc_title, title, price, discountprice, image)
        #获取广告商品信息
        get_contents(contents)
        #上下文
        context = {
            'goods':goods,
            "contents":contents
        }
        #响应前端界面
        return render(request,'index.html',context)

class expectPage(View):
    def get(self,request):
        '''
        待开发提示页面
        :param request:
        :return:
        '''
        return render(request,'myTemplate.html')
