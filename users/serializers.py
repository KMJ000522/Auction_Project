# users/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True) # 비밀번호는 응답에 포함 X

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'nickname')

    def create(self, validated_data):
        # [Level 3] 비밀번호 해싱(암호화) 처리 필수
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            nickname=validated_data.get('nickname', '')
        )
        return user

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('credit_score', 'phone_number')