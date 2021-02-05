import logging

from celery import Celery
from celery_tasks.main import app
from celery_tasks.sms_code.yuntongxun.ccp_sms import CCP

from . import constants

#日志信息
logger = logging.getLogger('django')

# bind：保证task对象会作为第一个参数自动传入
# name：异步任务别名,每个任务必须具有唯一的名称。
# retry_backoff：异常自动重试的时间间隔 第n次(retry_backoff×2^(n-1))s
# max_retries：异常自动重试次数的上限
@app.task(bind=True,name="send_sms_code",retry_backoff=3)
def send_sms_code(self,phone,sms_code):
    '''
    :param phone: 注册手机号
    :param sms_code: 短信验证码
    :return: 状态码
    '''
    # 容联云通讯发送短信
    try:# to用户  datas[验证码内容,终止时间]，tempId模板id
        res = CCP().send_template_sms(to=phone, datas=[sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60],
                                tempId=constants.SEND_SMS_TEMPLATE_ID)
    except Exception as e:
        #
        logger.error(e)
        # 有异常自动重试三次
        raise self.retry(exc=e, max_retries=3)
    if res != 0:
        # 有异常自动重试三次
        raise self.retry(exc=Exception('发送短信失败'), max_retries=3)
    #正常返回
    return res