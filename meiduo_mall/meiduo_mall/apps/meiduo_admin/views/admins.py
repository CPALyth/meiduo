from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.contrib.auth.models import Group

from users.models import User
from ..serializers.admins import AdminSerializer
from ..serializers.groups import GroupSerializer
from ..utils import MyPagination


class AdminView(ModelViewSet):
    queryset = User.objects.filter(is_staff=True)
    serializer_class = AdminSerializer
    pagination_class = MyPagination
    permission_classes = [IsAdminUser]
