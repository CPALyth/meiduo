from rest_framework.generics import ListAPIView

from users.models import User
from ..serializer.users import UserSerializer
from ..utils import MyPagination


class UserView(ListAPIView):
    """获取用户数据"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = MyPagination