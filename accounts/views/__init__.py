from accounts.views.auth_views import (
    GenerateOTPView,
    VerifyOTPView,
    EmailLoginView,
    NumberLoginView,
)

from accounts.views.password_views import (
    ChangePasswordView,
    ForgotPasswordVerifyView,
    ForgotPasswordRequestView
)

from accounts.views.user_update_views import (
    ChangeEmailVerifyView,
    UpdateUserProfileView,
    ChangeEmailRequestView,
    ChangeNumberVerifyView,
    ChangeNumberRequestView,
)