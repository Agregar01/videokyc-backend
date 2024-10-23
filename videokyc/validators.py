from rest_framework import serializers

class Validators:


    @staticmethod
    def phone_validation(value):
        if not value.isdigit() and len(value) not in range(7, 20):
            raise serializers.ValidationError("Invalid phone number")