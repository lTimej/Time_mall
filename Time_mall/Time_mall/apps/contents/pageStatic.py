# 静态化首页
from collections import OrderedDict

from django.template import loader
import os
from django.conf import settings

from contents.utils import get_category, get_contents, get_data
from contents.models import ContentCategory, AdCategory


def get_static_page():
    #获取分类
    goods = get_category()
    obj = ContentCategory.objects.all()
    contents = {}
    for cc in obj:  # 一级标题
        ct_obj = cc.content_set.all()
        for content_obj in ct_obj:  # 二级标题
            cc_title = cc.title
            title = content_obj.title
            price = content_obj.price
            discountprice = content_obj.discountprice
            image = content_obj.image
            ad_id = cc.adCategory_id
            ad_obj = AdCategory.objects.get(id=ad_id)
            ad_title = ad_obj.title
            get_data(cc_title, title, price, discountprice, image)
    # 获取广告商品信息
    get_contents(contents)
    # 上下文
    print(goods,contents)
    context = {
        'goods': goods,
        "contents": contents
    }

    # 渲染模板
    # 先获取模板文件
    template = loader.get_template('index.html')
    # 在使用上下文渲染模板文件
    html_text = template.render(context)

    # 将模板文件写入到静态路径
    file_path = os.path.join(settings.STATICFILES_DIRS[0], 'index.html')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_text)