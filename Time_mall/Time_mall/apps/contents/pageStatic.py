# 静态化首页
from collections import OrderedDict

from django.template import loader
import os
from django.conf import settings

from contents.utils import get_category,get_contents
from contents.models import ContentCategory

def get_static_page():
    #获取分类
    categories = get_category()
    contents = get_contents({})
    # 构造上下文
    context = {
        'categories': categories,
        'contents': contents
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