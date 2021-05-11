import re,json

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from django import http
from django.urls import reverse
from django_redis import get_redis_connection

from .models import User
from meiduo_mall.utils.response_code import RETCODE

class EmailView(View):
    """添加邮箱"""
    def put(self, request):
        # 接收参数
        json_dict = json.loads(request.body.decode())
        email = json_dict.get('email')
        # 校验参数
        pat = r'^[a-zA-Z0-9]+[a-zA-Z0-9_-]+@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$'
        if not re.match(pat, email):
            return http.HttpResponseForbidden('参数email有误')




class UserInfoView(LoginRequiredMixin, View):
    """用户中心"""
    def get(self, request):
        """提供个人信息页面"""
        user = request.user
        context = {
            'username': user.username,
            'mobile': user.mobile,
            'email': user.email,
            'email_active': user.email_active,
        }
        return render(request, 'user_center_info.html', context)


class LogoutView(View):
    """用户退出登录"""
    def get(self, request):
        """实现用户退出登录的逻辑"""
        # 清除状态保持信息, 会话结束
        logout(request)
        # 退出登录后重定向到首页
        response = redirect(reverse('contents:index'))
        # 清除cookies中的用户名
        response.delete_cookie('username')
        return response


class LoginView(View):
    """用户登录"""
    def get(self, request):
        """提供用户登录界面"""
        return render(request, 'login.html')

    def post(self, request):
        """实现用户登录逻辑"""
        # 接收参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')
        # 校验参数
        if not all([username, password]):
            return http.HttpResponseForbidden("缺少必传参数")
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden("请输入正确的用户名或手机号")
        if not re.match(r'^[0-9A-Za-z_-]{8,20}$', password):
            return http.HttpResponseForbidden("密码最少8位, 最长20位")
        # 认证用户: 使用账号查询用户是否存在, 如果用户存在, 再校验密码是否正确
        user = authenticate(username=username, password=password)
        if user is None:
            return render(request, 'login.html', {'account_errmsg': '账号或密码错误'})
        # 状态保持
        login(request, user)
        # 使用remembered确定状态保持周期(默认是两周)
        if remembered != 'on':
            request.session.set_expiry(0)  # 状态保持在浏览器会话结束就销毁
        # 响应结果, 先取出next
        next = request.GET.get('next')
        if next:
            response = redirect(next)
        else:
            response = redirect(reverse('contents:index'))
        # 设置cookie
        response.set_cookie('username', user.username, max_age=3600*24*14)
        # 重定向到首页
        return response


class MobileCountView(View):
    """判断手机号是否重复注册"""
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


class UsernameCountView(View):
    """判断用户名是否重复注册"""
    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


class RegisterView(View):
    """用户注册"""
    def get(self, request):
        """提供用户注册页面"""
        return render(request, "register.html")

    def post(self, request):
        """实现用户注册业务逻辑"""
        # 接收参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        sms_code_client = request.POST.get('sms_code')
        allow = request.POST.get('allow')
        # 校验参数： 避免恶意用户绕过前端逻辑， 要保证后端的安全
        # 判断参数是否齐全， all([列表])会去校验列表中的元素是否为空， 只要有一个为空， 返回false
        if not all([username, password, password2, mobile, allow]):
            return http.HttpResponseForbidden("缺少必传参数")
        # 判断用户名是否5-20个字符
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden("请输入5-20个字符的用户名")
        # 判断密码是否是8-20个数字
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20位的密码')
        # 判断两次密码是否一致
        if password != password2:
            return http.HttpResponseForbidden('两次输入的密码不一致')
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号码')
        # 判断是否勾选用户协议
        if allow != 'on':
            return http.HttpResponseForbidden('请勾选用户协议')
        # 判断短信验证码是否输对
        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_{}'.format(mobile))
        if sms_code_server is None:
            return render(request, 'register.html', {'error_sms_code_message': '短信验证码已失效'})
        if sms_code_client != sms_code_server.decode():
            return render(request, 'register.html', {'error_sms_code_message': '短信验证码输入有误'})

        # 保存注册数据: 是注册业务的核心
        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except:
            return render(request, 'register.html', {'register_errmsg': '注册失败'})

        # 实现状态保持
        login(request, user)

        # 响应结果
        response = redirect(reverse('contents:index'))
        # 设置cookie
        response.set_cookie('username', user.username, max_age=3600 * 24 * 14)
        # 重定向到首页
        return response

