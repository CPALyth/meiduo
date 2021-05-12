from django.urls import path, re_path
from . import views

app_name = 'users'  # 指定namespace
urlpatterns = [
    # 用户注册
    path('register/', views.RegisterView.as_view(), name='register'),
    # 判断用户名是否重复
    re_path(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.UsernameCountView.as_view()),
    # 判断手机号是否重复
    re_path(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
    # 用户登录
    path('login/', views.LoginView.as_view(), name='login'),
    # 退出登录
    path('logout/', views.LogoutView.as_view(), name='logout'),
    # 用户中心
    path('info/', views.UserInfoView.as_view(), name='info'),
    # 添加邮箱
    path('emails/', views.EmailView.as_view()),
    # 验证邮箱
    path('emails/verification/', views.VerifyEmailView.as_view()),
    # 展示用户地址
    path('addresses/', views.AddressView.as_view(), name='address'),
    # 新增用户地址
    path('addresses/create/', views.AddressCreateView.as_view()),
    # 修改/删除用户地址
    path('addresses/<int:address_id>/', views.UpdateDestroyAddressView.as_view()),
    # 设置默认地址
    path('addresses/<int:address_id>/default/', views.DefaultAddressView.as_view()),
    # 更新地址标题
    path('addresses/<int:address_id>/title/', views.UpdateTitleAddressView.as_view()),
]