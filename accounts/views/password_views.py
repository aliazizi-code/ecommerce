from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions
from accounts.models import User
from accounts.tasks import send_otp_to_email_tasks, send_otp_to_phone_tasks
from accounts.otp import generate_otp_pass
from accounts.serializers import (
    ForgotPasswordRequestSerializer,
    ForgotPasswordVerifySerializer,
    ChangePasswordSerializer
)


class ForgotPasswordRequestView(APIView):
    serializer_class = ForgotPasswordRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            number = data.get('number')
            email = data.get('email')

            if number:
                user = get_object_or_404(User, number=number)
                otp = generate_otp_pass(user.id)
                send_otp_to_phone_tasks.delay(otp)
                return Response({"detail": "OTP sent successfully."}, status=status.HTTP_200_OK)
                
            
            if email:
                user = get_object_or_404(User, email=email)
                otp = generate_otp_pass(user.id)
                send_otp_to_email_tasks.delay(otp)
                return Response({"detail": "OTP sent successfully."}, status=status.HTTP_200_OK)
                
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordVerifyView(APIView):
    serializer_class = ForgotPasswordVerifySerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            number = data.get('number')
            email = data.get('email')
            new_password = data['password']

            if number:
                user = get_object_or_404(User, number=number)
                user.set_password(new_password)
                user.is_active = True
                user.save()
                return Response({"detail": "Password reset successfully."}, status=status.HTTP_200_OK)
            
            if email:
                user = get_object_or_404(User, email=email)
                user.set_password(new_password)
                user.is_active = True
                user.save()
                return Response({"detail": "Password reset successfully."}, status=status.HTTP_200_OK) 
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        user = request.user

        if serializer.is_valid():
            data = serializer.validated_data
            new_password = data['password']

            user.set_password(new_password)
            user.save()
            return Response({"detail": "Password changed successfully."}, status=status.HTTP_200_OK)
            
