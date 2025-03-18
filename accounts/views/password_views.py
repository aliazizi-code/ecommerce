from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions
from accounts.models import User
from accounts.tasks import send_otp_to_email_tasks, send_otp_to_phone_tasks
from accounts.otp import generate_otp_pass, delete_otp_pass, OTP_TIMEOUT
from utils import CacheManager
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
                CacheManager.set_new_value(user.id, 'number', 'type_forget_pass', OTP_TIMEOUT)
                return self._generate_response(user, 'number')
                
            
            if email:
                user = get_object_or_404(User, email=email)
                otp = generate_otp_pass(user.id)
                send_otp_to_email_tasks.delay(otp)
                CacheManager.set_new_value(user.id, 'email', 'type_forget_pass', OTP_TIMEOUT)
                return self._generate_response(user, 'email')
        
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _generate_response(self, user, otp_type):
            return Response(data={
                "detail": "OTP sent successfully.",
                "user_id": user.id,
                "otp_type": otp_type
        }, status=status.HTTP_200_OK)
    
    


class ForgotPasswordVerifyView(APIView):
    serializer_class = ForgotPasswordVerifySerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            new_password = data['password']
            user_id = data.get('user_id')
            email = data.get('email')
            number = data.get('number')
            otp_type = CacheManager.get_value(user_id, 'type_forget_pass')

            if otp_type == 'email' and email:
                return self._reset_password(user_id, new_password, email, 'email')

            if otp_type == 'number' and number:
                return self._reset_password(user_id, new_password, number, 'number')
            
            
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _generate_response(self):
            return Response(data={"detail": "Password reset successfully."}, status=status.HTTP_200_OK)
    
    def _reset_password(self, user_id, new_password, identifier, identifier_type):
        if identifier_type == 'email':
            user = get_object_or_404(User, email=identifier, id=user_id)
        else:
            user = get_object_or_404(User, number=identifier, id=user_id)
        
        user.set_password(new_password)
        user.save()
        CacheManager.delete_value(user.id, 'type_forget_pass')
        delete_otp_pass(user.id)
        return self._generate_response()


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
            
