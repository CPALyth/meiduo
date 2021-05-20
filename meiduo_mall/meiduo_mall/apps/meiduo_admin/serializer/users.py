import re

from rest_framework import serializers

from users.models import User

class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email', 'password')  # id默认是read_only
        extra_kwargs = {
            'password': {
                'write_only': True,
                'max_length': 20,
                'min_length': 8,
            },
            'username': {
                'max_length': 20,
                'min_length': 5,
            }
        }

    def validate_mobile(self, value):
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def validate_email(self, value):
        pat = r'^[a-zA-Z0-9]+[a-zA-Z0-9_-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$'
        if not re.match(pat, value):
            raise serializers.ValidationError('电子邮箱格式错误')
        return value

    def create(self, validated_data):
        # # 法一
        # user = super().create(validated_data)
        # password = validated_data['password']
        # user.set_password(password)
        # user.save()

        # 法二
        user = User.objects.create_user(**validated_data)
        return user