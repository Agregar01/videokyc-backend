from django.urls import path
from videokyc.views import GetVerificationsDetail, GetVerificationsStatistics, SendEmail, VerifyClient, GetVerifications


urlpatterns = [
    path("trigger-email/", SendEmail.as_view(), name = "trigger-email"),
    path("complete-verification/client/", VerifyClient.as_view(), name = "complete-verification"),
    path("verifications/<str:client_id>/", GetVerifications.as_view(), name = "verifications"),
    path("verifications/statistics/<str:client_id>/", GetVerificationsStatistics.as_view(), name = "verifications-statistics"),
    path("verification-detail/<str:reference_id>/", GetVerificationsDetail.as_view(), name = "verification-detail"),
]
