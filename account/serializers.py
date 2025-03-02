from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import OTP
from django.contrib.auth import authenticate

User = get_user_model()

# User registration serializer (for creating a user with OTP verification)
class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'name', 'password', 'phone', 'description']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

# OTP Serializer for email verification
class OTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6)

# Serializer to return user data with roles (Admin/User)
class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'name', 'is_staff', 'is_active', 'phone', 'description']

# Login Serializer (for obtaining JWT tokens)
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        # Validate the user and password (You can use Django's `authenticate` method)
        user = authenticate(email=email, password=password)
        # print("111111111111",user)
        if not user:
            raise serializers.ValidationError("Invalid credentials")

        # Create JWT token
        refresh = RefreshToken.for_user(user)
        return {'refresh': str(refresh), 'access': str(refresh.access_token)}
