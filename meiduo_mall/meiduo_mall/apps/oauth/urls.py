from django.urls import path
from . import views

urlpatterns = [
    # 提供QQ登录扫码页面
    path('qq/login/', views.QQAuthURLView.as_view()),
    # 处理QQ登录回调
    path('oauth_callback/', views.QQAuthUserView.as_view()),
]