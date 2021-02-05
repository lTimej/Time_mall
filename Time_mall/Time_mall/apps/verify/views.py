import json,logging,random

from django.shortcuts import render
from django.views import View
from django import http

from .libs.captcha.captcha import captcha
from Time_mall.utils import constants,response_code
from .libs.yuntongxun.ccp_sms import CCP

from django_redis import get_redis_connection
logger = logging.getLogger('django')
# Create your views here.
class ImgCodeView(View):
    def get(self,request,uuid):
        '''
        :param request: 前端通过ajax请求传来uuid
        :param uuid: 将uuid存入redis中作为图片验证码的唯一标识
        :return: image
        '''
        #获取验证码和验证么图片
        text,code = captcha.generate_captcha()
        #链接redis数据库
        redis_conn = get_redis_connection('verify_code')
        #插入数据   setex(key,expire_time,value)
        redis_conn.setex('img_%s'%uuid,constants.IMAGE_CODE_REDIS_EXPIRES,text)
        #响应图片
        return http.HttpResponse(code,content_type='image/jpg')
    # def post(self,request,uuid):
    #     '''
    #     :param request: 前端通过ajax请求传来uuid,来验证图片验证码是否输入正确
    #     :param uuid: 通过uuid查找redis数据库图片验证码
    #     :return: info
    #     '''
    #     #获取前端数据并转化为字典形式
    #     code = request.body.decode()
    #     code = json.loads(code)
    #     img_code = code.get('code')
    #     #链接redis数据库
    #     redis_conn = get_redis_connection('verify_code')
    #     #获取验证码
    #
    #     cc = redis_conn.get('img_%s'%uuid)
    #     try:
    #         redis_conn.delete('img_%s'%uuid)
    #     except Exception as e:
    #         logger.error(e)
    #     redis_img_code = cc.decode()
    #     #将验证码转化为小写
    #     redis_img_code = redis_img_code.lower()
    #     #验证
    #     if img_code.lower() == redis_img_code:
    #         return http.JsonResponse({'code':0})
    #     else:
    #         return http.JsonResponse({'code': 1,'error_info':'验证码输入错误'})

class SmsCodeView(View):
    def get(self,request,phone):
        '''
        :param request:
        :param phone: 前端发过来的参数
        :return: 响应码
        '''
        #获取参数
        uuid = request.GET.get("uuid")
        img_code = request.GET.get("img_code")

        #验证参数
        if not all([uuid,img_code]):
            return http.JsonResponse({'code':response_code.RETCODE.IMAGECODEERR,"errmsg":"验证码不为空"})

        # 链接redis数据库
        redis_conn = get_redis_connection('verify_code')

        #如果Redis服务端需要同时处理多个请求，加上网络延迟，那么服务端利用率不高，效率降低。
        #获取验证码
        img_code_redis = redis_conn.get('img_%s'%uuid)

        #校验验证码是否存在
        if not img_code_redis:
            return http.JsonResponse({'code': response_code.RETCODE.IMAGECODEERR, "errmsg": "验证码失效"})

        try:#取出uuid后，删除对应的uuid验证码，防止用户恶意测试
            redis_conn.delete('img_%s'%uuid)
        except Exception as e:
            #删除失败存入日志  uuid不存在，删除失败
            logger.error(e)

        #bytes类型转化为字符串类型
        redis_img_code = img_code_redis.decode()

        #将验证码转化为小写
        redis_img_code = redis_img_code.lower()

        #验证
        if img_code.lower() != redis_img_code:
            return http.JsonResponse({'code': response_code.RETCODE.IMAGECODEERR, "errmsg": "验证码输入错误"})

        # 随机生成6位纯数字的短信验证码
        sms_code = "%06d" % (random.randint(0, 999999))
        logger.info("短信验证码：%s"% sms_code)

        # 保存至redis数据库 生命为60秒
        redis_conn.setex("sms_%s" % phone, constants.SMS_CODE_REDIS_EXPIRES, sms_code)

        # 容联云通讯发送短信
        # to用户  datas[验证码内容,终止时间]，tempId模板id
        CCP().send_template_sms(to=phone, datas=[sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60],
                              tempId=constants.SEND_SMS_TEMPLATE_ID)

        # 防止恶意用户不通过点击按钮发送短信，通过链接频繁发送短信
        #第一次发送sms_code_flag为空，然后将flag存入redis设置flag60秒,与前端时间同步，
        sms_code_flag = redis_conn.get('sms_code_flag_%s' % phone)

        #如果flag存在抛出错误
        if sms_code_flag:
            return http.JsonResponse({'code': response_code.RETCODE.THROTTLINGERR , "errmsg": "发送过于频繁"})

        #不存在就写入
        redis_conn.setex("sms_code_flag_%s"%phone,constants.SEND_SMS_CODE_INTERVAL,1)

        #响应正确
        return http.JsonResponse({'code': response_code.RETCODE.OK, "errmsg": "发送成功"})