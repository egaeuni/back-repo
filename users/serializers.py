from .models import Profile
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    
    class Meta:
        model = Profile
        fields = ('email', 'password', 'nickname', 'name', 'major', 'student_id', 'cp_number', 'is_manager')
        extra_kwargs = {'email': {'required': True}}

    def validate_email(self, value):
        if Profile.objects.filter(email=value).exists():
            raise serializers.ValidationError("이미 존재하는 이메일 주소입니다.")
        return value

    def create(self, validated_data):
        user = Profile.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            nickname=validated_data['nickname'],
            name=validated_data['name'],
            major=validated_data['major'],
            student_id=validated_data['student_id'],
            cp_number=validated_data['cp_number'],
            is_manager=validated_data['is_manager']
        )
        user.save()
        token = Token.objects.create(user=user)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, data):
        user = authenticate(**data)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            if not created:
                token.delete()
                token = Token.objects.create(user=user)
            return token
        raise serializers.ValidationError(
            {
                "error":"잘못된 이메일 또는 비밀번호입니다."
            }
        )


# 프로필 정보 확인
class ProfileSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Profile
        fields = ('image', 'nickname', 'student_id', 'major', 'created_at')

    # 닉네임 중복 검사
    def validate_nickname(self, value):
        request_user = self.instance
        
        # 다른 사용자의 닉네임과 중복되는지 확인
        if Profile.objects.filter(nickname=value).exclude(id=request_user.id).exists():
            raise serializers.ValidationError("이미 존재하는 닉네임입니다.")
        
        return value

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.nickname = validated_data.get('nickname', instance.nickname)
        instance.image = validated_data.get('image', instance.image)
        instance.student_id = validated_data.get('student_id', instance.student_id)
        instance.major = validated_data.get('major', instance.major)
        instance.email = validated_data.get('email', instance.email)
        instance.is_manager = validated_data.get('is_manager', instance.is_manager)
        instance.created_at = validated_data.get("created_at", instance.created_at)
        instance.save()
        return instance