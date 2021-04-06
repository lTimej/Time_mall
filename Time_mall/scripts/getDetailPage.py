#!/usr/bin/env python
import os
import sys

from goods.utils import get_sku_image, get_detail_image, get_sku

sys.path.insert(0, '../')

import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'Time_mall.settings.dev'

import django
django.setup()

from django.template import loader
from django.conf import settings

from goods import models

def generate_static_sku_detail_html(spu_id):
    """
    生成静态商品详情页面
    :param sku_id: 商品sku id
    """
    # 获取当前sku的信息
    detail_image = get_sku_image(spu_id)
    desc_dict = get_detail_image(spu_id)
    goods_detail, sku_id = get_sku(spu_id, detail_image, desc_dict)
    context = {
        "goods_detail": goods_detail
    }

    template = loader.get_template('detail.html')
    html_text = template.render(context)
    file_path = os.path.join(settings.STATICFILES_DIRS[0], 'detail/'+str(sku_id)+'.html')
    with open(file_path, 'w') as f:
        f.write(html_text)

if __name__ == '__main__':
    spus = models.Spu.objects.all()
    for spu in spus:
        generate_static_sku_detail_html(spu.id)