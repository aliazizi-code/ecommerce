from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions

from accounts.models import UserProfile
from accounts.tasks import send_otp_to_phone_tasks, send_otp_to_email_tasks
from utils import CacheManager
from accounts.otp import (
    generate_otp_change_email,
    delete_otp_change_email,
    generate_otp_change_number,
    delete_otp_change_number,
    OTP_TIMEOUT
)
from accounts.serializers import (
    UpdateUserProfileSerializer,
    ChangeEmailRequestSerializer,
    ChangeEmailVerifySerializer,
    ChangeNumberRequestSerializer,
    ChangeNumberVerifySerializer
)


class UpdateUserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UpdateUserProfileSerializer

    def patch(self, request):
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = self.serializer_class(user_profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangeEmailRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangeEmailRequestSerializer

    def post(self, request):
        user=request.user
        serializer = self.serializer_class(user, data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            otp = generate_otp_change_email(user.id)
            send_otp_to_email_tasks.delay(otp)
            CacheManager.set_new_value(user.id, data['email'], 'new_email', OTP_TIMEOUT)

            return Response({"message": "OTP sent to your email."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangeEmailVerifyView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangeEmailVerifySerializer

    def post(self, request):
        user = request.user
        serializer = self.serializer_class(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            data = serializer.validated_data
            user.email = data['email']
            user.save()
            delete_otp_change_email(user.id)
            CacheManager.delete_value(user.id, "new_email")
            return Response({"message": "Email successfully updated."}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangeNumberRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangeNumberRequestSerializer

    def post(self, request):
        user=request.user
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            
            otp = generate_otp_change_number(user.id)
            send_otp_to_phone_tasks.delay(otp)
            CacheManager.set_new_value(user.id, data['number'], "new_number", OTP_TIMEOUT)
                    
            return Response({"detail": "OTP sent successfully."}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangeNumberVerifyView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangeNumberVerifySerializer

    def post(self, request):
        user = request.user
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            
            user.number = data["number"]
            user.save()
            delete_otp_change_number(user.id)
            CacheManager.delete_value(user.id, "new_number")
            return Response({"detail": "Number changed successfully."}, status=status.HTTP_200_OK)
             
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
