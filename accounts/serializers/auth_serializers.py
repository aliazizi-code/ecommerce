from django.core.validators import RegexValidator
from rest_framework import serializers

from accounts.models import User


class PhoneNumberField(serializers.CharField):
    default_validators = [
        RegexValidator(
            regex=r'^\+98[0-9]{10}$',
            message="Phone number must be entered in the format: '+9891234567890'. Exactly 12 digits allowed."
        )
    ]


class RequestOTPSerializer(serializers.Serializer):
    number = PhoneNumberField(max_length=13)

    def validate_number(self, value):
        user = self.context['request'].user

        if User.objects.filter(number=value).exists():
            raise serializers.ValidationError("This phone number is already in use.")
        
        return value


class VerifyOTPRequestSerializer(serializers.Serializer):
    number = PhoneNumberField(max_length=13)
    otp = serializers.IntegerField(required=True)


class EmailLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)


class NumberLoginSerializer(serializers.Serializer):
    number = PhoneNumberField(max_length=13)
    password = serializers.CharField(write_only=True)
