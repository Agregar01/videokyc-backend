from rest_framework import generics, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from authentication.models import OTP, Business, User
from authentication.serializers import (
    BusinessSerializer,
    # CompletePasswordResetSerializer,
    # CompletePasswordResetSerializer,
    LoginSerializer,
    PasswordResetNonLoggedInSerializer,
    PasswordResetVerifyOTPSerializer,
    # PasswordResetVerifyOTPSerializer,
    # PasswordResetNonLoggedInSerializer,
    # PasswordChangeSerializer,
    # PasswordResetNonLoggedInSerializer,
    # PasswordResetVerifyOTPSerializer,
    SendOTPSerializer,
    UpdateBusinessSerializer,
    UserSerializer,
    VerifyOTPSerializer,

)
from common.services import CommonUserServices, generate_otp, send_user_otp
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken
from team.models import TeamMember

common = CommonUserServices


class SendOTPToEmail(generics.GenericAPIView):
    serializer_class = SendOTPSerializer

    def post(self, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        try:
            serializer.is_valid()
            email = serializer.validated_data["email"]
            otp = generate_otp(email)
            user_otp = send_user_otp(otp, email)
            return Response(user_otp)

        except Exception as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

class VerifyEmailOTP(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer

    def post(self, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        try:
            serializer.is_valid(raise_exception=True)
            email = serializer.validated_data["email"]
            otp = serializer.validated_data["otp"]
            user_otp = OTP.objects.filter(otp=otp, email__iexact=email).first()
            if not user_otp:
                return Response({
                    "status": False,
                    "message": "OTP or email not found. Kindly request a new OTP"
                }, status=status.HTTP_400_BAD_REQUEST,
                )
            user = User.objects.filter(email__iexact=email).first()
            if user and (not user.is_email_verified):
                user.is_email_verified = True
                user.save()
            user_otp.is_verified = True
            user_otp.save()
            message = {"status": True, "message": "Email verification successful"}
            return Response(message, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

class CreateUser(generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            if serializer.is_valid(raise_exception=True):
                user = serializer.save()
                message = {
                    "status": True,
                    "message": "User successfully created",
                    "id": user.id
                }
                return Response(message, status=status.HTTP_201_CREATED)
            return Response({"status": False, "message": serializer.errors}, status=400)
        except Exception as e:
            message = {"error": str(e)}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)


        
class LoginUser(generics.GenericAPIView):
    serializer_class = LoginSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            team_member = common.get_team_member_by_email(user.email)
            if isinstance(team_member, dict) and not team_member["status"]:
                return Response(team_member)
            refresh = RefreshToken.for_user(user)
            return Response({
                "status": True,
                "team_member_id": team_member.id,
                "user_id": team_member.user.id,
                "team_id": team_member.team.id,
                "email": team_member.email,
                "business_id": team_member.team.business.id,
                "access": str(refresh.access_token)
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BusinessDetail(generics.RetrieveUpdateAPIView):
    parser_classes = (FormParser, MultiPartParser)
    permission_classes = [IsAuthenticated,]
    lookup_field = "pk"
    queryset = Business.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return UpdateBusinessSerializer
        return BusinessSerializer

    def get(self, request, *args, **kwargs):
        instance = self.kwargs.get("pk")
        business = Business.objects.filter(id=instance).first()
        business_data = BusinessSerializer(business).data
        
        return Response({"status": True, "business": business_data, "account": business_data})

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        business_serializer = BusinessSerializer(instance)
        response = business_serializer.data
        return Response({"status": True, "business": response})


class PasswordResetNonLoggedInUser(generics.GenericAPIView):
    serializer_class = PasswordResetNonLoggedInSerializer

    def post(self, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        try:
            email = serializer.validated_data["email"]
            user = common.get_user_by_email(email)
            otp = generate_otp(user.email)
            print(otp)
            user_otp = send_user_otp(otp, user.email)
            return Response(user_otp)
        except Exception as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class PasswordResetVerifyOTP(generics.GenericAPIView):
    serializer_class = PasswordResetVerifyOTPSerializer

    def post(self, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]
        user = common.get_user_by_email(email)
        if not OTP.objects.filter(otp=otp, email=user.email).first():
            return Response({"message": "OTP invalid or expired"})
        return Response(
            {"status": True, "message": "OTP verification successful"}, status=status.HTTP_200_OK
        )


# class CompletePasswordReset(generics.GenericAPIView):
#     serializer_class = CompletePasswordResetSerializer

#     def post(self, *args, **kwargs):
#         serializer = self.get_serializer(data=self.request.data)
#         serializer.is_valid(raise_exception=True)
#         email = serializer.validated_data["email"]
#         otp = serializer.validated_data["otp"]
#         password = serializer.validated_data["password"]
#         user = common_user_services.get_user_by_email(email)
#         if not UserOTP.objects.filter(otp=otp, user=user).first():
#             return Response({"message": "OTP invalid or expired"})
#         user.set_password(password)
#         user.save()
#         email_data = {
#             "subject": "Password Reset Successful",
#             "message": "Your password has been reset successfully",
#         }
#         # dependencies.send_email(user.email, email_data)
#         email_notification(email_data["subject"], email_data["message"], user.email)
#         return Response(
#             {"message": "Password updated successfully"}, status=status.HTTP_200_OK
#         )


from django.shortcuts import render

def custom_404(request, exception):
    return render(request, '404.html', status=404)