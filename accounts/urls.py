from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import auth_views, password_views, user_update_views

urlpatterns = [
    # Authentication endpoints
    path('auth/otp/request/', auth_views.GenerateOTPView.as_view(), name='request-otp'),
    path('auth/otp/verify/', auth_views.VerifyOTPView.as_view(), name='verify-otp'),
    path('auth/login/email/', auth_views.EmailLoginView.as_view(), name='email-login'),
    path('auth/login/number/', auth_views.NumberLoginView.as_view(), name='number-login'),

    # User profile management
    path('user/profile/', user_update_views.UpdateUserProfileView.as_view(), name='user-profile'),
    path('user/email/change/request/', user_update_views.ChangeEmailRequestView.as_view(), name='set-email-request'),
    path('user/email/change/verify/', user_update_views.ChangeEmailVerifyView.as_view(), name='set-email-verify'),
    path('user/phone/change/request/', user_update_views.ChangeNumberRequestView.as_view(), name='change-number-request'),
    path('user/phone/change/verify/', user_update_views.ChangeNumberVerifyView.as_view(), name='change-number-verify'),

    # Password management
    path('password/reset/request/', password_views.ForgotPasswordRequestView.as_view(), name='forgot-password-request'),
    path('password/reset/verify/', password_views.ForgotPasswordVerifyView.as_view(), name='forgot-password-verify'),
    path('password/change/', password_views.ChangePasswordView.as_view(), name='change-password'),

    # Token management
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
