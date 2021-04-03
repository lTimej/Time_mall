import os

from celery import Celery

# celery配置默认的django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Time_mall.settings.dev")
#实例化对象
app = Celery('Time')
#加载配置环境
app.config_from_object('django.conf:settings', namespace='CELERY')
# 加载任务
app.autodiscover_tasks(['celery_tasks.sms_code','celery_tasks.send_verify_email'])

