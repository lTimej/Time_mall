from django.db import models
from Time_mall.utils.baseModel import BaseModel
from users.models import User

# Create your models here.
class OauthModel(BaseModel):
    user = models.ForeignKey(to=User,on_delete=models.CASCADE,verbose_name="用户")
    openid = models.CharField(max_length=64,verbose_name="open_id",db_index=True)
    class Meta:
        db_table = "tb_oauth_QQ"
        verbose_name = "QQ登录用户"
        verbose_name_plural = verbose_name