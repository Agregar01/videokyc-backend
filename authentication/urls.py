from django.urls import path
from authentication.views import (

    CreateUser,
    # GetBusinessDetails,
    LoginUser,
    PasswordResetNonLoggedInUser,
    PasswordResetVerifyOTP,
    SendOTPToEmail,
    BusinessDetail,

    VerifyEmailOTP,

)


urlpatterns = [
    path("signup/", CreateUser.as_view(), name="signup"),
    path("login/", LoginUser.as_view(), name="login"),
    # path("logout/", LogoutUser.as_view(), name="logout"),
    path("send-email-otp/", SendOTPToEmail.as_view(), name="send-email-otp"),
    path("verify-email/", VerifyEmailOTP.as_view(), name="verify-email"),
    path("business/<uuid:pk>/", BusinessDetail.as_view(), name="business-update"),
    # path("user/<uuid:user_id>/change-password/logged-in-user/", PasswordChangeLoggedInUser.as_view(), name="change-password-loggedin"),
    path("user/reset-password", PasswordResetNonLoggedInUser.as_view(), name="reset-password"),
    path("user/reset-password/otp-verify", PasswordResetVerifyOTP.as_view(), name="reset-password-verify-otp"),
    # path("user/complete-reset-password/", CompletePasswordReset.as_view(), name="complete-reset-password"),
    # path(
    #     "user/<uuid:pk>/kyc-documents-upload/",
    #     UploadUserDocuments.as_view(),
    #     name="kyc-documents-upload",
    # ),
    # path(
    #     "user/<str:email>/get-user-by-email/",
    #     GetUserByEmail.as_view(),
    #     name="get-user-by-email",
    # ),
    # path("info/<str:id>/",GetNameOfUserOrBusinessByIDView.as_view(), name="info"),
]
