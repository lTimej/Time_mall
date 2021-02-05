from celery import Celery
from celery_tasks.main import app
from celery_tasks.sms_code.yuntongxun.ccp_sms import CCP
from . import constants

# 每个任务必须具有唯一的名称。
@app.task(name="send_sms_code")
def send_sms_code(phone,sms_code):
    '''
    :param phone: 注册手机号
    :param sms_code: 短信验证码
    :return: 状态码
    '''
    # 容联云通讯发送短信
    # to用户  datas[验证码内容,终止时间]，tempId模板id
    return CCP().send_template_sms(to=phone, datas=[sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60],
                            tempId=constants.SEND_SMS_TEMPLATE_ID)