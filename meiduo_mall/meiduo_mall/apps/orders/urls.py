from django.urls import path
from . import views

app_name = 'orders'
urlpatterns = [
    path('orders/settlement/', views.OrderSettlementView.as_view(), name='settlement')
]