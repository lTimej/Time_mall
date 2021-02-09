from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    phone = models.CharField(max_length=11,unique=True,verbose_name='手机号')
    email_active = models.BooleanField(default=False,verbose_name="邮箱验证状态")
    class Meta:
        db_table = 'tb_users'#数据库表名
        verbose_name = '用户'# 在admin站点中显示的名称
        verbose_name_plural = verbose_name
    def __str__(self):
        """定义每个数据对象的显示信息"""
        return self.username