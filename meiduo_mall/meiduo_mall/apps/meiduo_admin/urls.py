from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.routers import DefaultRouter

from .views import statistical, users, specs, images, skus, orders, permissions

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

    # ---------------- 商品管理 ----------------
    # 规格管理
    path('goods/simple/', specs.SpecsView.as_view({'get': 'simple'})),
    # 图片管理
    path('skus/simple/', images.ImagesView.as_view({'get': 'simple'})),
    # SKU管理
    path('goods/<int:pk>/specs/', skus.SKUView.as_view({'get': 'specs'})),
]

# ---------------- 商品管理 ----------------
# 规格管理
router = DefaultRouter()
router.register('goods/specs', specs.SpecsView, basename='specs')
urlpatterns += router.urls

# 图片管理
router = DefaultRouter()
router.register('skus/images', images.ImagesView, basename='images')
urlpatterns += router.urls

# SKU管理
router = DefaultRouter()
router.register('skus', skus.SKUView, basename='skus')
urlpatterns += router.urls

# 订单管理
router = DefaultRouter()
router.register('orders', orders.OrderView, basename='orders')
urlpatterns += router.urls

# 权限管理
router = DefaultRouter()
router.register('permissions/perms', permissions.PermissionView, basename='perms')
urlpatterns += router.urls
