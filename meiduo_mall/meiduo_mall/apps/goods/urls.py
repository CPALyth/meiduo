from django.urls import path
from . import views

app_name = 'goods'
urlpatterns = [
    # 商品列表页
    path('list/<int:category_id>/<int:page_num>/', views.ListView.as_view(), name='list'),

]