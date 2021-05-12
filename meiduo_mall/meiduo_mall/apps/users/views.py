import re, json, logging

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from django import http
from django.urls import reverse
from django_redis import get_redis_connection

from meiduo_mall.utils.views import LoginRequiredJsonMixin
from .models import User, Address
from .utils import generate_verify_email_url, check_verify_email_token
from meiduo_mall.utils.response_code import RETCODE
from celery_tasks.email.tasks import send_virify_email
from . import constants

logger = logging.getLogger('django')


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


class EmailView(View):
    """添加邮箱"""
    def put(self, request):
        user = request.user
        # 接收参数
        json_dict = json.loads(request.body.decode())
        email = json_dict.get('email')
        # 校验参数
        pat = r'^[a-zA-Z0-9]+[a-zA-Z0-9_-]+@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$'
        if not re.match(pat, email):
            return http.JsonResponse({'code': RETCODE.EMAILERR, 'errmsg': '参数email有误'})
        # 保存邮箱到数据库
        try:
            user.email = email
            user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '添加邮箱失败'})
        # 发送验证邮件到邮箱
        verify_url = generate_verify_email_url(user)
        send_virify_email.delay(email, verify_url)
        # 响应结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})


class VerifyEmailView(View):
    """验证邮箱"""
    def get(self, request):
        # 接收参数
        token = request.GET.get('token')
        # 校验参数
        if not token:
            return http.HttpResponseForbidden('缺少token')
        # 从token获取user
        user = check_verify_email_token(token)
        if not user:
            return http.HttpResponseForbidden('无效的token')
        # 将email_active字段设置为True
        try:
            user.email_active = True
            user.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('激活邮箱失败')
        # 响应结果: 重定向到用户中心
        return redirect(reverse('users:info'))


class AddressView(LoginRequiredMixin, View):
    """用户收货地址"""
    def get(self, request):
        return render(request, 'user_center_site.html')


class AddressCreateView(LoginRequiredJsonMixin, View):
    """新增收货地址"""
    def post(self, request):
        """实现新增地址逻辑"""
        user = request.user
        count = user.addresses.count()
        if count > constants.USER_ADDRESS_COUNTS_LIMIT:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '超出用户地址上限'})

        # 接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '缺少必传参数'})
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.JsonResponse({'code': RETCODE.MOBILEERR, 'errmsg': '参数mobile有误'})
        if tel and not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
            return http.JsonResponse({'code': RETCODE.TELERR, 'errmsg': '参数tel有误'})
        if email and not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.JsonResponse({'code': RETCODE.EMAILERR, 'errmsg': '参数email有误'})

        # 保存用户传入的地址信息
        try:
            address = Address.objects.create(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
            # 如果当前登录用户没有默认地址, 则新地址就设为默认地址
            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '新增地址失败'})

        # 将新增的地址响应给前端实现局部刷新
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        # 响应保存结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '新增地址成功', 'address': address_dict})


class AddressView(View):
    """用户收货地址"""
    def get(self, request):
        # 获取当前登录用户的收货地址列表
        user = request.user
        addresses = Address.objects.filter(user=user, is_deleted=False)
        address_list = []
        for address in addresses:
            address_list.append({
                'id': address.id,
                'title': address.title,
                'receiver': address.receiver,
                'province': address.province.name,
                'city': address.city.name,
                'district': address.district.name,
                'place': address.place,
                'mobile': address.mobile,
                'tel': address.tel,
                'email': address.email,
            })
        # 构造上下文
        context = {
            'default_address_id': user.default_address_id,
            'addresses': address_list,
        }
        return render(request, 'user_center_site.html', context)


class UpdateDestroyAddressView(View):
    """更新和删除地址"""
    def put(self, request, address_id):
        """更新地址"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')
        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '缺少必传参数'})
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.JsonResponse({'code': RETCODE.MOBILEERR, 'errmsg': '参数mobile有误'})
        if tel and not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
            return http.JsonResponse({'code': RETCODE.TELERR, 'errmsg': '参数tel有误'})
        if email and not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.JsonResponse({'code': RETCODE.EMAILERR, 'errmsg': '参数email有误'})
        # 使用最新的地址信息覆盖指定旧的地址信息
        try:
            Address.objects.filter(id=address_id).update(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '修改地址失败'})
        # 响应新的地址信息给前端渲染
        address = Address.objects.get(id=address_id)
        address_dict = {
            'id': address.id,
            'title': address.title,
            'receiver': address.receiver,
            'province': address.province.name,
            'city': address.city.name,
            'district': address.district.name,
            'place': address.place,
            'mobile': address.mobile,
            'tel': address.tel,
            'email': address.email
        }
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '修改地址成功', 'address': address_dict})

    def delete(self, request, address_id):
        """删除地址"""
        try:
            Address.objects.filter(id=address_id).update(is_deleted=True)
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '删除地址失败'})
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除地址成功'})


class DefaultAddressView(View):
    """设置默认地址"""
    def put(self, request, address_id):
        try:
            address = Address.objects.get(id=address_id)
            user = request.user
            user.default_address = address
            user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '设置默认地址失败'})
        # 响应结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '设置默认地址成功'})

class UpdateTitleAddressView(View):
    """更改地址标题"""

    def put(self, request, address_id):
        """实现更新地址标题"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        title = json_dict.get('title')
        # 校验参数
        if not title:
            return http.JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '缺少title'})
        try:
            # 查询当前要更新标题的地址
            address = Address.objects.get(id=address_id)
            # 将新的地址标题覆盖地址标题
            address.title = title
            address.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '更新标题失败'})
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '更新标题成功'})