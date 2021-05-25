from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import Permission

from ..serializers.permissions import PermissionSerializer
from ..utils import MyPagination


class PermissionView(ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    pagination_class = MyPagination
    permission_classes = [IsAdminUser]
