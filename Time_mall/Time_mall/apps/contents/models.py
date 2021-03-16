from django.db import models
from Time_mall.utils.baseModel import BaseModel
# Create your models here.
class AdCategory(BaseModel):
    title = models.CharField(max_length=32, verbose_name="广告类别")
    class Meta:
        db_table = "tb_ad_category"
        verbose_name = '广告类别'
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.title

class ContentCategory(BaseModel):
    cid = models.CharField(max_length=12,verbose_name='内容id')
    title = models.CharField(max_length=64,verbose_name="内容标题")
    adCategory = models.ForeignKey(to=AdCategory,on_delete=models.PROTECT,verbose_name='广告类别')
    class Meta:
        db_table = "tb_content_category"
        verbose_name = '内容类别'
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.title

class Content(BaseModel):
    """广告内容"""
    category = models.ForeignKey(ContentCategory, on_delete=models.PROTECT, verbose_name='类别')
    title = models.CharField(max_length=256, verbose_name='标题')
    url = models.CharField(max_length=256, verbose_name='内容链接')
    image = models.ImageField(null=True, blank=True, verbose_name='图片')
    text = models.TextField(null=True, blank=True, verbose_name='内容')
    price = models.DecimalField(null=True, blank=True,max_digits=10, decimal_places=2, verbose_name='价格')
    discountprice = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2, verbose_name='折后价格')
    sequence = models.IntegerField(verbose_name='排序')
    status = models.BooleanField(default=True, verbose_name='是否展示')

    class Meta:
        db_table = 'tb_content'
        verbose_name = '广告内容'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.category.title + ': ' + self.title
