from django.urls import path
from . import views

app_name = 'carts'
urlpatterns = [
    # 购物车
    path('carts/', views.CartsView.as_view(), name='info'),
    # 全选
    path('carts/selection/', views.CartsSelectAllView.as_view()),
]