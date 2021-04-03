from django.db import models
from baseModel import BaseModel
# Create your models here.

#商品类别id
class ProductId(BaseModel):
    pid = models.CharField(max_length=32,verbose_name='商品编号')
    class Meta:
        db_table = 'tb_product_id'
        verbose_name = '商品编号'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.pid
#商品分类
class GoodsCategory(BaseModel):
    name = models.CharField(max_length=125,verbose_name='类名')
    parent = models.ForeignKey(to='self',related_name='subs',on_delete=models.CASCADE,verbose_name='目录',null=True,blank=True)
    class Meta:
        db_table = 'tb_goods_category'
        verbose_name = '商品类别'
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.name
#商品列表
class GoodsList(BaseModel):
    pid = models.ForeignKey(ProductId,verbose_name='商品pid')
    category = models.ForeignKey(GoodsCategory,verbose_name='商品类别',on_delete=models.CASCADE)
    url = models.CharField(max_length=256,verbose_name='商品url')
    sequeue = models.IntegerField(verbose_name='顺序')
    class Meta:
        db_table = 'tb_goods_list'
        verbose_name = '商品列表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.category.name
class Spu(BaseModel):
    name = models.CharField(max_length=64, verbose_name='名称')
    category1 = models.ForeignKey(GoodsCategory, on_delete=models.PROTECT, related_name='cat1_spu', verbose_name='一级类别')
    category2 = models.ForeignKey(GoodsCategory, on_delete=models.PROTECT, related_name='cat2_spu', verbose_name='二级类别')
    sales = models.IntegerField(default=0, verbose_name='销量')
    cfavs = models.IntegerField(default=0, verbose_name='收藏数')
    class Meta:
        db_table = 'tb_spu'
        verbose_name = '商品SPU'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
class Sku(BaseModel):
    title = models.CharField(max_length=64, verbose_name='名称')
    spu = models.ForeignKey(Spu, on_delete=models.CASCADE, verbose_name='商品')
    category = models.ForeignKey(GoodsCategory, on_delete=models.PROTECT, verbose_name='从属类别')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='单价')
    now_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='进价')
    stock = models.IntegerField(default=0, verbose_name='库存')
    sales = models.IntegerField(default=0, verbose_name='销量')
    comments = models.IntegerField(default=0, verbose_name='评价数')
    is_launched = models.BooleanField(default=True, verbose_name='是否上架销售')
    default_image = models.ImageField(verbose_name='默认图片')

    class Meta:
        db_table = 'tb_sku'
        verbose_name = '商品SKU'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s: %s' % (self.spu.id, self.title)
class SkuImage(BaseModel):
    sku = models.ForeignKey(Sku, on_delete=models.CASCADE, verbose_name='sku')
    image = models.ImageField(verbose_name='图片')

    class Meta:
        db_table = 'tb_sku_image'
        verbose_name = 'SKU图片'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s %s' % (self.sku.title, self.sku.id)
class SpuDescs(BaseModel):
    spu = models.ForeignKey(Spu, on_delete=models.CASCADE, verbose_name='spu_descs')
    detail_info = models.CharField(max_length=888,verbose_name='商品详情')
    desc_image = models.ImageField(verbose_name='图片')

    class Meta:
        db_table = 'tb_spu_desc'
        verbose_name = 'Spu详情'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s %s' % (self.sku.name, self.sku.id)
class SpuSpecification(BaseModel):
    """商品SPU规格"""
    spu = models.ForeignKey(Spu, on_delete=models.CASCADE, related_name='specs', verbose_name='商品SPU')
    name = models.CharField(max_length=20, verbose_name='规格名称')

    class Meta:
        db_table = 'tb_spu_specification'
        verbose_name = '商品Spu规格'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s: %s' % (self.spu.name, self.name)
class SpecificationOption(BaseModel):
    """规格选项"""
    spec = models.ForeignKey(SpuSpecification, related_name='options', on_delete=models.CASCADE, verbose_name='规格')
    value = models.CharField(max_length=20, verbose_name='选项值')

    class Meta:
        db_table = 'tb_specification_option'
        verbose_name = '规格选项'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s - %s' % (self.spec, self.value)
class SkuSpecification(BaseModel):
    """SKU具体规格"""
    sku = models.ForeignKey(Sku, related_name='specs', on_delete=models.CASCADE, verbose_name='sku')
    spec = models.ForeignKey(SpuSpecification, on_delete=models.PROTECT, verbose_name='规格名称')
    option = models.ForeignKey(SpecificationOption, on_delete=models.PROTECT, verbose_name='规格值')

    class Meta:
        db_table = 'tb_sku_specification'
        verbose_name = 'Sku规格'
        verbose_name_plural = verbose_name
