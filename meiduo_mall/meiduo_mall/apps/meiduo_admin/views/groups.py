from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import Group

from ..serializers.groups import GroupSerializer
from ..utils import MyPagination


class GroupView(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    pagination_class = MyPagination
