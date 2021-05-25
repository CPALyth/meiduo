from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.contrib.auth.models import Permission, ContentType

from ..serializers.permissions import PermissionSerializer, ContentTypeSerializer
from ..utils import MyPagination


class PermissionView(ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    pagination_class = MyPagination
    permission_classes = [IsAdminUser]

    def content_types(self, request):
        content = ContentType.objects.all()
        ser = ContentTypeSerializer(content, many=True)
        return Response(ser.data)
