from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.contrib.auth.models import Group, Permission

from ..serializers.groups import GroupSerializer
from ..serializers.permissions import PermissionSerializer
from ..utils import MyPagination


class GroupView(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    pagination_class = MyPagination
    permission_classes = [IsAdminUser]

    def simple(self, request):
        perms = Permission.objects.all()
        ser = PermissionSerializer(perms, many=True)
        return Response(ser.data)
