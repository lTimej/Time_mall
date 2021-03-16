from django.db import models
from django.contrib.auth.models import AbstractUser

from Time_mall.utils.baseModel import BaseModel
'''
 null :参数仅影响数据库存储
 blank:参数影响表单中值
 DateField.auto_now:每次保存对象时自动将字段设置为现在,该字段仅在调用时自动更新Model.save()
 DateField.auto_now_add:首次创建对象时，将字段自动设置为现在----------auto_now_add，auto_now和default是互斥的
 CASCADE:级联删除。Django模拟ON DELETE CASCADE上SQL约束的行为，并删除包含ForeignKey的对象
 PROTECT:通过引发ProtectedError的子类来 防止删除引用的对象 django.db.IntegrityError。
 RESTRICT:通过引发RestrictedError（的子类 django.db.IntegrityError）防止删除引用的对象 。不同于PROTECT，如果引用的对象还引用了在同一操作中通过CASCADE 关系删除的另一个对象，则允许删除该对象。
'''

class User(AbstractUser):
    phone = models.CharField(max_length=11,unique=True,verbose_name='手机号')
    email_active = models.BooleanField(default=False,verbose_name="邮箱验证状态")
    default_address = models.ForeignKey('Address', related_name='users', null=True, blank=True,
                                        on_delete=models.SET_NULL, verbose_name='默认地址')
    class Meta:
        db_table = 'tb_users'#数据库表名
        verbose_name = '用户'# 在admin站点中显示的名称
        verbose_name_plural = verbose_name
    def __str__(self):
        """定义每个数据对象的显示信息"""
        return self.username

class Address(BaseModel):
    """用户地址"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='用户')
    title = models.CharField(max_length=20, verbose_name='地址名称')
    receiver = models.CharField(max_length=20, verbose_name='收货人')
    province = models.ForeignKey(to='areas.Areas', on_delete=models.PROTECT, related_name='province_addresses',
                                 verbose_name='省')
    city = models.ForeignKey(to='areas.Areas', on_delete=models.PROTECT, related_name='city_addresses', verbose_name='市')
    district = models.ForeignKey(to='areas.Areas', on_delete=models.PROTECT, related_name='district_addresses',
                                 verbose_name='区')
    place = models.CharField(max_length=50, verbose_name='地址')
    mobile = models.CharField(max_length=11, verbose_name='手机')
    tel = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='固定电话')
    email = models.CharField(max_length=30, null=True, blank=True, default='', verbose_name='电子邮箱')
    is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')

    class Meta:
        db_table = 'tb_address'
        verbose_name = '用户地址'
        verbose_name_plural = verbose_name
        ordering = ['-update_time']
