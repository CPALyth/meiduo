from django.urls import path
from . import views

app_name = 'users'  # 指定namespace
urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),

]