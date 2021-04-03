import logging

from celery import Celery
from django.conf import settings

from Time_mall.utils import constants
from celery_tasks.main import app

from django.core.mail import send_mail

#日志信息
logger = logging.getLogger('django')

# bind：保证task对象会作为第一个参数自动传入
# name：异步任务别名,每个任务必须具有唯一的名称。
# retry_backoff：异常自动重试的时间间隔 第n次(retry_backoff×2^(n-1))s
# max_retries：异常自动重试次数的上限
@app.task(bind=True,name="send_verify_email",retry_backoff=3)
def send_verify_email(self,to_email, verify_url):
    '''
    邮箱验证
    :param to_email: 接收者
    :param verify_url: 验证链接
    :return:
    '''
    subject = "Time购物商城邮箱"
    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用Time购物商城。</p>' \
                   '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱,请在%d分钟内完成验证：</p>' \
                   '<p><a href="%s">%s<a></p>' % (to_email, constants.VERIFY_EMAIL_TOKEN_EXPIRES//60,verify_url, verify_url)
    try:# to用户  datas[验证码内容,终止时间]，tempId模板id
        send_mail(subject, '', settings.EMAIL_FROM, [to_email], html_message=html_message)
        print("发送成功")
    except Exception as e:
        #
        logger.error(e)
        print("发送失败")
        # 有异常自动重试三次
        raise self.retry(exc=e, max_retries=3)


