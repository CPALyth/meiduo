from django.urls import path
from . import views

urlpatterns = [
    # 省市区三级联动
    path('areas/', views.AreasView.as_view()),
]