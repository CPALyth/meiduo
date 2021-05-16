from django.urls import path
from . import views

app_name = 'orders'
urlpatterns = [
    # 结算订单
    path('orders/settlement/', views.OrderSettlementView.as_view(), name='settlement'),
    # 提交订单
    path('orders/commit/', views.OrderCommitView.as_view()),
    # 提交订单成功
    path('orders/success/', views.OrderSuccessView.as_view()),
    # 我的订单
    path('orders/info/<int:page_num>/', views.UserOrderInfoView.as_view(), name='info'),
    # 商品评价
    path('orders/comment/', views.OrderCommentView.as_view(), name='comment'),
]