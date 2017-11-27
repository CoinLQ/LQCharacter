from .settings import *

# mysql 数据库
import pymysql

pymysql.install_as_MySQLdb()
# DEBUG=False 不会用自带的 server 去 server js/css 等静态文件
# 需要用 nginx 之类的去做静态文件的 server.
DEBUG = True
INTERNAL_IPS = ['127.0.0.1']
ALLOWED_HOSTS += INTERNAL_IPS
ALLOWED_HOSTS.append('localhost')

PROJECT_ROOT = os.path.join(os.path.realpath(os.path.dirname(__file__)), os.pardir)
# 重置 setting 里的 STATIC_ROOT 配置
#执行collectstatic时打开, 并关闭STATICFILES_DIRS中的'static'
#STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static/')

# static 目录配置
# 如果 DEBUG 为 False 这里就会失效，需要用 NGIX 代理
STATICFILES_DIRS = [
    os.path.join(PROJECT_ROOT, 'static'),
    #os.path.join(PROJECT_ROOT, 'frontend/dist/static'),
]

# 开发环境开启跨域
CORS_ORIGIN_ALLOW_ALL = True

INSTALLED_APPS.append('debug_toolbar')
MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')

# 请按照你开发时本机的数据库名字，密码，端口填写
DATABASES = {
    # 'default': {
    #     'BACKEND': 'django_redis.cache.RedisCache',
    #     'LOCATION': '127.0.0.1:6379',
    #     "OPTIONS": {
    #         "CLIENT_CLASS": "django_redis.client.DefaultClient",
    #     },
    # },
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
}

AUTH_PASSWORD_VALIDATORS = [
]

#允许用户名和Email登录. 目前email没有唯一性, 暂不打开了.
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    #'accounts.backends.EmailBackend',
)