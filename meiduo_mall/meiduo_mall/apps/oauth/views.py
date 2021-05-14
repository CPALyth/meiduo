import logging
import re

from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.conf import settings  # 代表启动模块对应的配置文件(manage对应dev)
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseServerError
from django_redis import get_redis_connection
from QQLoginTool.QQtool import OAuthQQ

from meiduo_mall.utils.response_code import RETCODE
from users.models import User
from .models import OAuthQQUser
from .utils import generate_access_token, check_access_token
from carts.utils import merge_cart_cookie_redis

logger = logging.getLogger('django')

class QQAuthURLView(View):
    """提供QQ登录扫码页面"""
    def get(self, request):
        # 接收next
        next = request.GET.get('next')
        # 创建工具对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI, state=next)
        # 生成QQ登录扫码链接地址
        login_url = oauth.get_qq_url()
        # 响应
        return JsonResponse({'code': RETCODE.OK, 'errmsg':'OK', 'login_url':login_url})



class QQAuthUserView(View):
    """处理QQ登录回调"""
    def get(self, request):
        """处理QQ登录回调的业务逻辑"""
        # 获取code
        code = request.GET.get('code')
        if not code:
            return HttpResponseForbidden('获取code失败')
        # 创建工具对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI)
        try:
            # 使用code获取access_token
            access_token = oauth.get_access_token(code)
            # 获取openid
            openid = oauth.get_open_id(access_token)
        except Exception as e:
            logger.error(e)
            return HttpResponseServerError('OAuth2.0认证失败')
        # 使用openid判断该QQ是否绑定美多账号
        try:
            oauth_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:  # opendid未绑定美多用户
            # 序列化openid
            access_token_openid = generate_access_token(openid)
            context = {'access_token_openid': access_token_openid}
            # 展示绑定页面
            return render(request, 'oauth_callback.html', context)
        else:  # openid已绑定
            # 获取美多用户
            user = oauth_user.user
            # 状态保持
            login(request, user)
            # 响应重定向到首页
            response = redirect(reverse('contents:index'))
            # 将用户名写入到cookie中
            response.set_cookie('username', user.username, max_age=3600 * 24 * 14)
            # 用户登录成功, 把cookie购物车合并到redis购物车
            response = merge_cart_cookie_redis(request, user, response)
            return response

    def post(self, request):
        """美多商城用户绑定到openid"""
        # 接收参数
        mobile = request.POST.get('mobile')
        pwd = request.POST.get('password')
        sms_code_client = request.POST.get('sms_code')
        access_token_openid = request.POST.get('access_token_openid')

        # 校验参数
        # 判断参数是否齐全
        if not all([mobile, pwd, sms_code_client]):
            return HttpResponseForbidden('缺少必传参数')
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseForbidden('请输入正确的手机号码')
        # 判断密码是否合格
        if not re.match(r'^[0-9A-Za-z]{8,20}$', pwd):
            return HttpResponseForbidden('请输入8-20位的密码')
        # 判断短信验证码是否一致
        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        if sms_code_server is None:
            return render(request, 'oauth_callback.html', {'sms_code_errmsg': '无效的短信验证码'})
        if sms_code_client != sms_code_server.decode():
            return render(request, 'oauth_callback.html', {'sms_code_errmsg': '输入短信验证码有误'})
        # 判断openid是否有效：错误提示放在sms_code_errmsg位置
        openid = check_access_token(access_token_openid)
        if not openid:
            return render(request, 'oauth_callback.html', {'openid_errmsg': 'openid已失效'})
        # 使用手机号查询对应的用户是否存在
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 如果用户不存在, 新建用户
            user = User.objects.create_user(username=mobile, password=pwd, mobile=mobile)
        else:
            # 如果用户存在, 需要校验密码
            if not user.check_password(pwd):
                # 密码错误, 刷新页面
                return render(request, 'oauth_callback.html', {'account_errmsg': '用户名或密码错误'})
        # 将 新建用户 或 已存在用户 绑定到openid
        try:
            oauth_qq_user = OAuthQQUser.objects.create(user=user, openid=openid)
        except Exception as e:
            logger.error(e)
            return render(request, 'oauth_callback.html', {'qq_login_errmsg': 'qq登录失败'})
        # 实现状态保持
        login(request, user)
        # 重定向到state
        next = request.GET.get('state')
        response = redirect(next)
        # 登录时用户名写入到cookie, 有效期2week
        response.set_cookie('username', user.username, max_age=3600 * 24 * 14)
        # 用户登录成功, 把cookie购物车合并到redis购物车
        response = merge_cart_cookie_redis(request, user, response)
        # 响应QQ登录结果
        return response
