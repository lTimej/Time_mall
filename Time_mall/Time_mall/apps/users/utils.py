import re

from users.models import User

from django.contrib.auth.backends import ModelBackend
'''
重写ModelBackend的authenticate函数，来判断用户帐号是手机号登录还是用户名登录
'''
def get_user(user):
    '''
    :param user: 用户登录帐号
    :return: 判断用户是手机号登录还是用户名登录
    '''
    try:#用户存在返回
        if re.match("^1[3-9]\d{9}$",user):#手机号登录
            user = User.objects.get(phone=user)
        else:#用户名登录
            user = User.objects.get(username=user)
    except User.DoesNotExist:#不存在返回None
        return None

    return user


class MyAuthenticate(ModelBackend):
    """
    Authenticates against settings.AUTH_USER_MODEL.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        '''
        重写authenticate用户认证
        :param request:
        :param username: 登录帐号
        :param password: 密码
        :param kwargs:
        :return: 用户对象
        '''
        #判断帐号是用户名or手机号
        user = get_user(username)
        #校验密码和帐号
        if user.check_password(password) and user:
            #用户对象
            return user