import re

from django.shortcuts import render
from django.views import View
from django import http

from .models import User


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

        # 保存注册数据: 是注册业务的核心
        try:
            User.objects.create_user(username=username, password=password, mobile=mobile)
        except:
            return render(request, 'register.html', {'register_errmsg': '注册失败'})

        # 成功， 重定向到首页
        return http.HttpResponse('注册成功，重定向到首页')
