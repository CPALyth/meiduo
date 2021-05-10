from django.urls import path
from . import views

app_name = 'contents'  # 指定namespace
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
]