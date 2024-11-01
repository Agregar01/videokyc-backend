from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# from apikeys.models import APIKeys
from apikey.models import APIKey
from authentication import validators
# from authentication.models import BusinessDocuments
# from authentication.tokens import CustomRefreshToken
# from business.serializers import BusinessDocumentsSerializer
from authentication.models import OTP, Business, User
# from common.services import email_notification, generate_otp, send_user_otp
from rest_framework.response import Response
from urllib.parse import urljoin
# from django.conf import settings
from django.db import transaction

from common.services import email_notification
from team.models import Team, TeamMember

class SendOTPSerializer(serializers.Serializer):
    email=serializers.EmailField(required=True)
    class Meta:
        fields = ["email"]

        
class UserSerializer(serializers.ModelSerializer):
    is_email_verified = serializers.ReadOnlyField()
    firstname = serializers.CharField(
        max_length=100,
        required=True,
        validators=[validators.firstname_validation],
    )
    lastname = serializers.CharField(
        max_length=100,
        required=True,
        validators=[validators.lastname_validation],
    )
    password = serializers.CharField(
        write_only=True, required=True, validators=[validators.password_validator]
    )

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "phone",
            "firstname",
            "lastname",
            "is_email_verified",
            "business_name",
            "business_type",
            "password"
        )

    @transaction.atomic
    def create(self, validated_data):
        otp = OTP.objects.filter(email=validated_data.get("email"), is_verified=True).first()
        if not otp:
            raise serializers.ValidationError("Email not verified. Kindly verify your email")

        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        business = Business.objects.create(
            user=user,
            business_name=user.business_name,
            business_type=user.business_type
        )
        team = Team.objects.create(
            business=business, name=f"{business.business_name} Team"
        )
        TeamMember.objects.create(
            team=team, email=user.email, is_active=True
        )
        APIKey.objects.create(name="First API Key", business=business)
        return user
    

class BusinessSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Business
        fields = "__all__"


class VerifyOTPSerializer(serializers.Serializer):
    email=serializers.EmailField(required=True)
    otp = serializers.CharField(
        max_length=8,
        required=True,
        error_messages={
            "blank": "Provide OTP",
            "required": "OTP is required",
        },
    )

    class Meta:
        fields = ["email", "otp"]


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if user is None:
                raise serializers.ValidationError("Invalid login credentials.")
            
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled.")

            data['user'] = user
        else:
            raise serializers.ValidationError("Both email and password are required.")

        return data

    def save(self, **kwargs):
        return self.validated_data['user']


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    class Meta:
        model = Business
        fields = [
            "refresh",
        ]

    def validate(self, attrs):
        try:
            token = RefreshToken(attrs["refresh"])
            token.blacklist()
        except TokenError:
            raise ValidationError({"message": "Invalid refresh token"})
        return {}


class UpdateBusinessSerializer(serializers.ModelSerializer):
    id_image_director_1 = serializers.FileField(required=False)
    id_image_director_2 = serializers.FileField(required=False)
    logo = serializers.FileField(required=False)
    registration_documents = serializers.FileField(required=False)

    class Meta:
        model = Business
        fields = [
            "address",
            "id_image_director_1",
            "id_image_director_2",
            "logo",
            "registration_documents",
            "tax_identification"
        ]


class PasswordResetNonLoggedInSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ["email"]

class PasswordChangeSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(
        write_only=True, required=True, validators=[validators.password_validator]
    )
    confirm_new_password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs.get("new_password") != attrs.get("confirm_new_password"):
            raise ValidationError("Passowrds do not match")
        return attrs

    def save(self, **kwargs):
        request: Request = self.context.get("request")
        user_id = request.parser_context.get("kwargs").get("user_id")
        user = Business.objects.filter()
        password = self.validated_data["password"]
        new_password = self.validated_data["new_password"]

        if not user.check_password(password):
            raise serializers.ValidationError("Current password is incorrect")
        user.set_password(new_password)
        user.save()
        email_data = {
            "subject": "Password Change",
            "message": "Your password has been changed successfully",
        }
        email_notification(email_data["subject"], email_data["message"], user.email)
        return user




class PasswordResetVerifyOTPSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["email", "otp"]


class CompletePasswordResetSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    otp = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["email", "otp", "password"]



