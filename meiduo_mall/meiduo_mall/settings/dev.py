"""
Django settings for meiduo_mall project.

Generated by 'django-admin startproject' using Django 3.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
import datetime
from pathlib import Path

SERVER_IP = '192.168.3.67'

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
print(BASE_DIR)  # /Users/ws/PycharmProjects/meiduo/meiduo_mall/meiduo_mall

import sys
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))
print(sys.path)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-hy04&&ogujj*dkj!a#851-t%54w_-grjuabrg6adi+i-bj=58%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'www.meiduo.site',
    '127.0.0.1',
    SERVER_IP,
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',  # 用户
    'contents',  # 内容(广告)
    'verifications',  # 验证码
    'oauth',  # 开放验证, 第三方登录
    'areas',  # 地区
    'goods',  # 商品
    'haystack',  # 全文检索
    'carts',  # 购物车
    'orders',  # 订单
    'payment',  # 支付
    'django_crontab', # 定时任务
    'meiduo_admin',  # 美多后台
    'corsheaders',  # 跨域访问
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'meiduo_mall.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'environment': 'meiduo_mall.utils.jinja2_env.jinja2_environment',
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'meiduo_mall.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': SERVER_IP,
        'PORT': 3306, # 数据库端口
        'USER': 'ws', # 数据库用户名
        'PASSWORD': '123456', # 数据库用户密码
        'NAME': 'meiduo' # 数据库名字
    },
    'slave': {  # 读(从机)
        'ENGINE': 'django.db.backends.mysql', # 数据库引擎
        'HOST': SERVER_IP, # 数据库主机
        'PORT': 8306, # 数据库端口
        'USER': 'root', # 数据库用户名
        'PASSWORD': '123456', # 数据库用户密码
        'NAME': 'meiduo' # 数据库名字
    }
}

# 配置Redis
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://{}:6379/0".format(SERVER_IP),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "session": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://{}:6379/1".format(SERVER_IP),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "verify_code": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://{}:6379/2".format(SERVER_IP),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "history": { # 用户浏览记录
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://{}:6379/3".format(SERVER_IP),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "carts": {  # 购物车
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://{}:6379/4".format(SERVER_IP),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
}
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "session"

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# 配置静态文件的加载路径
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 项目日志
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # 是否禁用已经存在的日志器
    'formatters': {  # 日志信息显示的格式
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(lineno)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(module)s %(lineno)d %(message)s'
        },
    },
    'filters': {  # 对日志进行过滤
        'require_debug_true': {  # django在debug模式下才输出日志
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {  # 日志处理方法
        'console': {  # 向终端中输出日志
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {  # 向文件中输出日志
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(os.path.dirname(BASE_DIR), 'logs/meiduo.log'),  # 日志文件的位置
            'maxBytes': 300 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose'
        },
    },
    'loggers': {  # 日志器
        'django': {  # 定义了一个名为django的日志器
            'handlers': ['console', 'file'],  # 可以同时向终端与文件中输出日志
            'propagate': True,  # 是否继续传递日志信息
            'level': 'INFO',  # 日志器接收的最低日志级别
        },
    }
}

# 指定自定义的用户模型类, 语法： '子应用.用户模型类'
AUTH_USER_MODEL = 'users.User'

# 指定自定义的用户认证后端
AUTHENTICATION_BACKENDS = ['users.utils.UsernameMobileBackend']

# 未登录时重定向的路由
LOGIN_URL = '/login/'

# QQ登录
QQ_CLIENT_ID = '101518219'
QQ_CLIENT_SECRET = '418d84ebdc7241efb79536886ae95224'
QQ_REDIRECT_URI = 'http://www.meiduo.site:8000/oauth_callback'

# 发送电子邮件
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' # 指定邮件后端
EMAIL_HOST = 'smtp.163.com' # 发邮件主机
EMAIL_PORT = 25 # 发邮件端口
EMAIL_HOST_USER = 'ws156858@163.com' # 授权的邮箱
EMAIL_HOST_PASSWORD = 'JBWENNUTHKKLFFBG' # 邮箱授权时获得的密码，非注册登录密码
EMAIL_FROM = '美多商城<ws156858@163.com>' # 发件人抬头
# 邮箱验证链接
EMAIL_VERIFY_URL = 'http://www.meiduo.site:8000/emails/verification/'

# 指定自定义的Django文件存储类
DEFAULT_FILE_STORAGE = 'meiduo_mall.utils.fastdfs.storage.FastDFSStorage'

# FastDFS相关参数
FDFS_BASE_URL = 'http://image.meiduo.site:8888/'
FDFS_CLIENT_PATH = os.path.join(BASE_DIR, 'utils/fastdfs/client.conf')


# Haystack
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://{}:9200/'.format(SERVER_IP), # Elasticsearch服务器ip地址，端口号固定为9200
        'INDEX_NAME': 'meiduo_mall', # Elasticsearch建立的索引库的名称
    },
}
# 当添加、修改、删除数据时，自动生成索引
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'
# 每页显示五条数据
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 5

# 支付宝SDK配置参数
ALIPAY_APPID = '2021000117647974'
ALIPAY_DEBUG = True
ALIPAY_URL = 'https://openapi.alipaydev.com/gateway.do'
ALIPAY_RETURN_URL = 'http://www.meiduo.site:8000/payment/status/'

# 定时任务
CRONJOBS = [
    # 每1分钟生成一次首页静态文件
    ('*/1 * * * *', 'contents.crons.gen_static_index_html', '>> ' + os.path.join(os.path.dirname(BASE_DIR), 'logs/crontab.log')),
]
# 避免提示中文字符异常错误
CRONTAB_COMMAND_PREFIX = 'LANG_ALL=zh_cn.UTF-8'

# MySQL读写分离路由
DATABASES_ROUTERS = ['meiduo_mall.utils.db_router.MasterSlaveDBRouter']

# CORS
CORS_ORIGIN_WHITELIST = (
    'http://127.0.0.1:8000',
    'http://127.0.0.1:8080',
    'http://www.meiduo.site:8080',
    'http://api.meiduo.site:8000',
    'http://{}:8000'.format(SERVER_IP),
    'http://{}:8080'.format(SERVER_IP),
)
CORS_ALLOW_CREDENTIALS = True  # 允许携带cookie

# REST框架配置
REST_FRAMEWORK = {
    # 指定认证方式
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
}
# 指定JWT的配置
JWT_AUTH = {
    # 指定token的有效期
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=1),
    # 指定返回结果方法
    'JWT_RESPONSE_PAYLOAD_HANDLER': 'meiduo_admin.utils.jwt_response_payload_handler',
}