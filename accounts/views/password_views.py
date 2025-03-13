from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions
from accounts.serializers.password_serializers import *
from accounts.otp import *
from accounts.models import User
from accounts.tasks import send_otp_to_email_tasks, send_otp_to_phone_tasks



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
                if user.number == data['number']:
                    otp = generate_otp_pass(user.id)
                    send_otp_to_phone_tasks.delay(otp)

                    return Response({"detail": "OTP sent successfully."}, status=status.HTTP_200_OK)
                return Response({"detail": "New number must be different from the current number."}, status=status.HTTP_400_BAD_REQUEST)
            
            if email:
                user = get_object_or_404(User, email=email)
                if user.email != data['email']:
                    otp = generate_otp_pass(user.id)
                    send_otp_to_email_tasks.delay(otp)

                    return Response({"detail": "OTP sent successfully."}, status=status.HTTP_200_OK)
                return Response({"detail": "New email must be different from the current email."}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordVerifyView(APIView):
    serializer_class = ForgotPasswordVerifySerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            number = data.get('number')
            email = data.get('email')
            otp = data['otp']
            new_password = data['password']

            if number:
                user = get_object_or_404(User, number=number)
                if user.number == data['number']:
                    if verify_otp_pass(user.id, otp):
                        user.set_password(new_password)
                        user.save()
                        return Response({"detail": "Password reset successfully."}, status=status.HTTP_200_OK)
                    return Response({"detail": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
                return Response({"detail": "New number must be different from the current number."}, status=status.HTTP_400_BAD_REQUEST)
            
            if email:
                user = get_object_or_404(User, email=email)
                if user.email != data['email']:
                    if verify_otp_pass(user.id, otp):
                        user.set_password(new_password)
                        user.save()
                        return Response({"detail": "Password reset successfully."}, status=status.HTTP_200_OK)
                    return Response({"detail": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
                return Response({"detail": "New email must be different from the current email."}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        user = request.user

        if serializer.is_valid():
            data = serializer.validated_data
            old_password = data['old_password']
            new_password = data['password']

            if user.check_password(old_password):
                user.set_password(new_password)
                user.save()
                return Response({"detail": "Password changed successfully."}, status=status.HTTP_200_OK)
            return Response({"detail": "Invalid password."}, status=status.HTTP_400_BAD_REQUEST)
