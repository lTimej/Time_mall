import jwt
from django.conf import settings


def generate_jwt(payload,expire,secret=None):
    '''
    生成token
    :param payload: user_id 和username
    :param secret:
    :return:
    '''
    #构建载体内容
    _payload = {"expire":expire}
    # 将用户id用户名存入_payload
    _payload.update(payload)
    #secret不存在从配置中获取
    if not secret:
        secret = settings.SECRET_KEY
    #生成token
    token = jwt.encode(_payload,secret,algorithm="HS256")
    return token.decode()

def verify_token(token,secret=None):
    '''
    验证token
    :param token:
    :param secret:
    :return:
    '''
    # secret不存在从settings配置中获取
    if not secret:
        secret = settings.SECRET_KEY
    try:
        payload = jwt.decode(token, secret, algorithm=['HS256'])
    except jwt.PyJWTError:
        payload = None

    return payload