from celery import Celery
from django.conf import settings

# 创建实例前, 为celery使用django配置文件进行设置
import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'

# 创建Celery实例
celery_app = Celery('meiduo', broker='redis://{}/10'.format(settings.SERVER_IP))

# 注册任务
celery_app.autodiscover_tasks([
    'celery_tasks.sms',
    'celery_tasks.email',
    'celery_tasks.static',
])