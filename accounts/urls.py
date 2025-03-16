from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    # Authentication endpoints
    path('auth/otp/request/', views.GenerateOTPView.as_view(), name='request-otp'),
    path('auth/otp/verify/', views.VerifyOTPView.as_view(), name='verify-otp'),
    path('auth/login/email/', views.EmailLoginView.as_view(), name='email-login'),
    path('auth/login/number/', views.NumberLoginView.as_view(), name='number-login'),

    # User profile management
    path('user/profile/', views.UpdateUserProfileView.as_view(), name='user-profile'),
    path('user/email/change/request/', views.ChangeEmailRequestView.as_view(), name='change-email-request'),
    path('user/email/change/verify/', views.ChangeEmailVerifyView.as_view(), name='change-email-verify'),
    path('user/phone/change/request/', views.ChangeNumberRequestView.as_view(), name='change-number-request'),
    path('user/phone/change/verify/', views.ChangeNumberVerifyView.as_view(), name='change-number-verify'),

    # Password management
    path('password/reset/request/', views.ForgotPasswordRequestView.as_view(), name='forgot-password-request'),
    path('password/reset/verify/', views.ForgotPasswordVerifyView.as_view(), name='forgot-password-verify'),
    path('password/change/', views.ChangePasswordView.as_view(), name='change-password'),

    # Token management
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
