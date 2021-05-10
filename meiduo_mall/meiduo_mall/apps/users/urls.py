from django.urls import path, re_path
from . import views

app_name = 'users'  # 指定namespace
urlpatterns = [
    # 用户注册
    path('register/', views.RegisterView.as_view(), name='register'),
    # 判断用户名是否重复
    re_path(r'^username/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.UsernameCountView.as_view()),
]