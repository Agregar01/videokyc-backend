from rest_framework import generics
from rest_framework.exceptions import NotFound

from authentication.models import User
from common.services import generate_otp, send_user_otp
from rest_framework.response import Response


class ResendOTP(generics.GenericAPIView):

    def post(self, *args, **kwargs):
        user_id = self.request.parser_context.get("kwargs").get("user_id")
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise NotFound("User not found")
        pin = generate_otp(user.email)
        user_otp = send_user_otp(pin, user.email)
        return Response(user_otp)