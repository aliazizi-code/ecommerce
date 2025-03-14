from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.otp import delete_otp, generate_otp
from accounts.tasks import send_otp_to_phone_tasks
from accounts.models import User
from accounts.serializers import (
    RequestOTPSerializer,
    VerifyOTPRequestSerializer,
    EmailLoginSerializer,
    NumberLoginSerializer,
)


class BaseLoginView(APIView):
    serializer_class = None

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']
            delete_otp(user.id)
            return Response(data=self._handle_login(user), status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _handle_login(self, user):
        refresh = RefreshToken.for_user(user)
        created = False

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'created': created
        }


class GenerateOTPView(APIView):
    serializer_class = RequestOTPSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            user, created = User.objects.get_or_create(number=data['number'])

            otp = generate_otp(user.id)
            send_otp_to_phone_tasks.delay(otp)

            return self._generate_response(created)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def _generate_response(self, created):
            status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
            return Response(data={'message': 'OTP sent successfully'}, status=status_code)


class VerifyOTPView(BaseLoginView):
    serializer_class = VerifyOTPRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            user = get_object_or_404(User, number=data['number'])

            user.is_active = True
            user.save()
            delete_otp(user.id)
            return Response(data=self._handle_login(user), status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailLoginView(BaseLoginView):
    serializer_class = EmailLoginSerializer


class NumberLoginView(BaseLoginView):
    serializer_class = NumberLoginSerializer
