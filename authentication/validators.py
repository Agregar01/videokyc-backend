from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
import re
from authentication.models import Business, User


def firstname_validation(value):
    character_pattern = r'[-_.A-Za-z\s]'
    for character in value:
        if not re.match(character_pattern, character):
            raise ValueError("Firstname contains illegal character(s).")
    return value

def lastname_validation(value):
    character_pattern = r'[-_.A-Za-z\s]'
    for character in value:
        if not re.match(character_pattern, character):
            raise serializers.ValidationError("lastname contain illegal character(s).")
    return value


 
def phone_validation(value):
    if not value.isdigit() and len(value) not in range(8, 13):
        raise serializers.ValidationError("Invalid phone number")
    try:
        user = User.objects.get(phone=value)
        if user:
            raise serializers.ValidationError("Phone number already in use")
    except User.DoesNotExist:
        pass
def businessname_validation(value):
    try:
        business_name = Business.objects.get(business_name__iexact=value)
        if business_name:
            raise serializers.ValidationError("Business name already in use")
    except Business.DoesNotExist:
        pass

def email_validation(value):
    try:
        email = User.objects.get(email__iexact=value)
        if email:
            raise serializers.ValidationError("A business with this email already exists")
    except User.DoesNotExist:
        pass
    
def password_validator(value):
    number_pattern = r'\d'
    capital_letter_pattern = r'[A-Z]'
    small_letter_pattern = r'[a-z]'
    password_errors = []
    special_character_pattern = r'[!@#$%^&*()-=_+`~[\]{}|;:,.<>?]'
    
    if not re.search(number_pattern, value):
        message = "The password must contain at least one number."
        password_errors.append(message)
        
    if len(value) < 8:
        message = "The password must be at least 8 characters long."
        password_errors.append(message)
        
    if len(value) > 100:
        message = "The password must be at most 100 characters long."
        password_errors.append(message)

    if not re.search(capital_letter_pattern, value):
        message = "The password must contain at least one capital letter."
        password_errors.append(message)

    if not re.search(small_letter_pattern, value):
        message = "The password must contain at least one lowercase letter."
        password_errors.append(message)
        
    if not re.search(special_character_pattern, value):
        message = "The password must contain at least one special character."
        password_errors.append(message)
        
    if password_errors:
        raise serializers.ValidationError(password_errors) 
    return None
