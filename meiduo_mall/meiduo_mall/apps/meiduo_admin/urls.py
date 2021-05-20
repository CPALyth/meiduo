from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.routers import DefaultRouter

from .views import statistical
from .views import users, specs

urlpatterns = [
    # ---------------- 后台登录 ----------------
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
    # 月增用户
    path('statistical/month_increment/', statistical.UserMonthIncrementView.as_view()),
    # 日分类商品
    path('statistical/goods_day_views/', statistical.UserGoodsCountView.as_view()),

    # ---------------- 用户管理 ----------------
    # 查询用户, 新增用户
    path('users/', users.UserView.as_view()),

]

router = DefaultRouter()
router.register('goods/specs', specs.SpecsView, basename='specs')
print(router.urls)
urlpatterns += router.urls