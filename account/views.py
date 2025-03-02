from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth import authenticate
from rest_framework import status, permissions, views
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import OTP, UserAccount
from .serializers import UserRegistrationSerializer, OTPSerializer, LoginSerializer, UserDetailSerializer
from .utils import generateOtp, sendOtpEmail  

class RegisterView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Generate and send OTP
            otp = generateOtp()
            otp_record = OTP.objects.create(user=user, otpCode=otp)
            sendOtpEmail(user.email, otp)
            return Response({"message": "User created. Check your email for OTP."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OTPVerifyView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = OTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otpCode = serializer.validated_data['otpCode']
            try:
                user = UserAccount.objects.get(email=email)
                otp_record = OTP.objects.get(user=user, otpCode=otpCode)

                if otp_record.is_expired():
                    return Response({"message": "OTP expired."}, status=status.HTTP_400_BAD_REQUEST)

                # Mark the user as verified (you can update fields like `is_active` if needed)
                user.is_active = True
                user.save()
                otp_record.delete()  # Optional: delete OTP after verification
                return Response({"message": "OTP verified successfully!"}, status=status.HTTP_200_OK)
            except OTP.DoesNotExist:
                return Response({"message": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)

class AdminAccessView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get(self, request):
        print("11111111111",request)
        return Response({"message": "Admin access granted."}, status=status.HTTP_200_OK)

