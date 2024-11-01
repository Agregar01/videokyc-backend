from django.urls import path
from common.views import ResendOTP

urlpatterns = [
    path("user/<uuid:user_id>/resend-otp/", ResendOTP.as_view(), name="resend-otp"),
]
