from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions
from django.core.cache import cache

from accounts.models import UserProfile
from accounts.otp import *
from accounts.serializers.user_update_serializers import *
from accounts.serializers.auth_serializers import RequestOTPSerializer, VerifyOTPRequestSerializer



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


class SetEmailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SetEmailSerializer

    def patch(self, request):
        user=request.user
        serializer = self.serializer_class(user, data=request.data, partial=True)

        if user.email is None and serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangeNumberRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RequestOTPSerializer

    def post(self, request):
        user=request.user
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            new_number = data['number']
            if user.number != new_number:

                delete_otp_change_number(user.id)
                cache.delete(f"new_number_{user.id}")
                otp = generate_otp_change_number(user.id)
                print(f'Your OTP is: {otp}')
                cache.set(f"new_number_{user.id}", new_number, timeout=OTP_TIMEOUT)
                return Response({"detail": "OTP sent successfully."}, status=status.HTTP_200_OK)
            return Response({"detail": "New number is same as old number."}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangeNumberVerifyView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VerifyOTPRequestSerializer

    def post(self, request):
        user=request.user
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            otp = data['otp']
            new_number = cache.get(f"new_number_{user.id}")

            if new_number is not None:
                if verify_otp_change_number(user.id, otp):
                    user.number = new_number
                    user.save()
                    delete_otp_change_number(user.id)
                    cache.delete(f"new_number_{user.id}")
                    return Response({"detail": "Number changed successfully."}, status=status.HTTP_200_OK)
                return Response({"detail": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"detail": "OTP expired."}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
