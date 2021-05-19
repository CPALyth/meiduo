from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token
from .views import statistical

urlpatterns = [
    # 后台登录
    path('authorizations/', obtain_jwt_token),
    # ---------------- 数据统计 ----------------
    path('statistical/total_count/', statistical.UserTotalCountView.as_view()),
]