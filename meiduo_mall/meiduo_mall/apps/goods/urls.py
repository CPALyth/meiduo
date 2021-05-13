from django.urls import path
from . import views

app_name = 'goods'
urlpatterns = [
    # 商品列表页
    path('list/<int:category_id>/<int:page_num>/', views.ListView.as_view(), name='list'),
    # 热销排行
    path('hot/<int:category_id>/', views.HotGoodsView.as_view()),
    # 商品详情
    path('detail/<int:sku_id>/', views.DetailView.as_view(), name='detail'),

]