from rest_framework import serializers
from .auth_serializers import PhoneNumberField
from django.core.validators import RegexValidator
from accounts.models import User
from django.shortcuts import get_object_or_404
from accounts.otp import verify_otp_pass


class PasswordField(serializers.CharField):
    default_validators = [
        RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[!@#$%^&*()_+{}":;\']).{8,}$',
            message="Password must be at least 8 characters long and include at least one uppercase letter, one lowercase letter, one digit, and one special character."
        )
    ]

    def __init__(self, *args, **kwargs):
        super(PasswordField, self).__init__(required=True, write_only=True, *args, **kwargs)


class PhoneEmailBaseSerializer(serializers.Serializer):
    number = PhoneNumberField(max_length=13, required=False)
    email = serializers.EmailField(required=False)

    # Validate phone number or email
    def validate(self, attrs):
        number = attrs.get('number', None)
        email = attrs.get('email', None)

        if not number and not email or number and email:
            raise serializers.ValidationError("Please provide either a phone number or an email address.")

        return attrs


class BasePasswordSerializer(serializers.Serializer):
    password = PasswordField()
    confirm_password = PasswordField()
    
    # Validate password match
    def validate(self, attrs):
        super().validate(attrs)


        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("The two password fields didn't match. Please try again. 🔒")
        return attrs


class ForgotPasswordRequestSerializer(PhoneEmailBaseSerializer):
    def validate_number(self, value):
        get_object_or_404(User, number=value)
        return value
    
    def validate_email(self, value):
        get_object_or_404(User, email=value)
        return value
    

class ForgotPasswordVerifySerializer(PhoneEmailBaseSerializer, BasePasswordSerializer):
    otp = serializers.IntegerField(required=True)

    def validate_number(self, value):
        get_object_or_404(User, number=value)
        return value
    
    def validate_email(self, value):
        get_object_or_404(User, email=value)
        return value
    
    def validate_otp(self, value):
        email = self.initial_data.get('email')
        number = self.initial_data.get('number')
        
        if email:
            user = get_object_or_404(User, email=email)
        elif number:
            user = get_object_or_404(User, number=number)
        else:
            raise serializers.ValidationError("Either email or number must be provided.")
        
        if not verify_otp_pass(user.id, value):
            raise serializers.ValidationError("Invalid OTP provided. Please try again.")
        return value


class ChangePasswordSerializer(BasePasswordSerializer):
    old_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context["request"].user

        if not user.check_password(value):
            raise serializers.ValidationError("Invalid password.")
        return value
    
    def validate(self, attrs):
        super().validate(attrs)

        if attrs['password'] == attrs['old_password']:
            raise serializers.ValidationError("")
        return attrs
