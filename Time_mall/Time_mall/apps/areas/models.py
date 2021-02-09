from django.db import models

# Create your models here.

#地区模型类
class Areas(models.Model):
    name = models.CharField(verbose_name="地区名称",max_length=20)
    #上级删除时就设置为空  related_name='sub'指明父级查询子级数据的语法
    parent = models.ForeignKey(to='self',on_delete=models.SET_NULL,related_name='subs',blank=True,null=True,verbose_name="上级行政区")
    class Meta:
        db_table = 'tb_areas'
        verbose_name = "省市区"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name