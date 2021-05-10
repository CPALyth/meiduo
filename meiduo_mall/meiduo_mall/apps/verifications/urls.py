from django.urls import re_path
from . import views

app_name = 'verifications'
urlpatterns = [
    re_path(r'^image_codes/(?P<uuid>[\w-]+)/$', views.ImageCodeView.as_view()),
]