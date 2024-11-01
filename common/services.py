import random
from typing import Any
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from common.models import Country
from config import settings

from authentication.models import Business, OTP, User
from rest_framework.exceptions import NotFound
from background_task import background
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from enum import Enum
from team.models import Team, TeamMember
from rest_framework.response import Response
from rest_framework import status

class BearerTokenAuthentication(BaseAuthentication):
    keyword = 'Bearer'
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None
        auth_parts = auth_header.split()
        if len(auth_parts) != 2 or auth_parts[0].lower() != self.keyword.lower():
            raise AuthenticationFailed('Invalid authorization header format')
        return (None, auth_parts[1])


class CommonUserServices:
    
    @staticmethod
    def get_user_by_id(user_id: str)-> User:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise NotFound("User not found")
        return user

    @staticmethod
    def get_country_by_id(country_id: str)-> Country:
        try:
            country = Country.objects.get(id=country_id)
        except Country.DoesNotExist:
            raise NotFound("Country not found")
        return country
    
    @staticmethod
    def get_user_by_email(email: str) -> User:
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise NotFound("User not found")
        return user
    
    @staticmethod
    def get_business_by_email(email: str) -> Business:
        try:
            business = Business.objects.get(email=email)
        except Business.DoesNotExist:
            raise NotFound("Business not found")
        return business
    
    @staticmethod
    def get_team_member_by_email(email: str) -> TeamMember:
        try:
            team_member = TeamMember.objects.get(email=email)
        except TeamMember.DoesNotExist:
            return {"status": False, "error": "Team member not found."}
        return team_member
    
    
    
    @staticmethod
    def create_team(business: Business) -> Team:
        team = Team.objects.create(business=business, primary_email=business.email)
        team.save()
        return team
    
    @staticmethod
    def is_email_verified(user) -> dict:
        if not user.is_email_verified:
            print("not veri")
            otp = generate_otp(user.email)
            send = send_user_otp(otp, user.email)
            
            return send

@background(schedule=1)
def email_notification(subject, message, email):
    from_email = settings.EMAIL_HOST_FROM
    send_mail(subject, message, from_email, [email])

    
def generate_otp(email):
    try:
        user_otp = OTP.objects.get(email=email)
        user_otp.delete()
    except ObjectDoesNotExist:
        pass

    otp = str(random.randint(100000, 999999))
    new_otp = OTP.objects.create(email=email, otp=otp)
    new_otp.save()
    return otp

def send_user_otp(otp: str, email: str) -> Any:
    email_data = {
        "subject": "Agregartech OTP Verification Email",
        "message": f"Your one time password is {otp}",
    }
    email_notification(email_data["subject"], email_data["message"], email)
    message = {
        "status": True,
        "otp_sent": True,
        "message": "An OTP has been sent to your email. Kindly confirm",
        "email": email,
    }
    return message

class Statuses(Enum):
    PENDING_STATUS = "Pending"
    PENDING_MESSAGE = "Transaction is pending"
    SUCCESSFUL_STATUS = "Success"
    SUCCESSFUL_MESSAGE = "Transaction completed successfully"
    FAILED_STATUS = "Failed"
    FAILED_MESSAGE = "Transaction failed"
    ACTIVE = "Active"
    BLOCKED = "Blocked"
    SETTLED = "Settled"
    APPROVED = "Approved"
    CANCELLED = "Cancelled",
    LIVE = "Live",
    TEST = "Test"