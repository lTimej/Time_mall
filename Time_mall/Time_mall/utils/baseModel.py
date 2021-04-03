from django.db import models

class BaseModel(models.Model):
    """基类模型：为模型类补充字段"""
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    class Meta:
        #抽象模型类：不创建basemodel表
        abstract = True