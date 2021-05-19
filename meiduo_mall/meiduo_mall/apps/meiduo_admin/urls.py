from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token
from .views import statistical

urlpatterns = [
    # 后台登录
    path('authorizations/', obtain_jwt_token),
    # ---------------- 数据统计 ----------------
    # 用户总数
    path('statistical/total_count/', statistical.UserTotalCountView.as_view()),
    # 日增用户
    path('statistical/day_increment/', statistical.UserDayIncrementView.as_view()),
    # 日活用户
    path('statistical/day_active/', statistical.UserDayActiveView.as_view()),
    # 下单用户
    path('statistical/day_orders/', statistical.UserDayOrderView.as_view()),
]