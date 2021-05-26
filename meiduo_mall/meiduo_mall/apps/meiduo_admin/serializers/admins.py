from rest_framework import serializers
from users.models import User


class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """父类的保存用户不会使之成为管理员, 密码也不会加密存储"""
        user = super().create(validated_data)
        user.is_staff = True
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        """父类的更新用户不会加密存储密码"""
        user = super().update(instance, validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
