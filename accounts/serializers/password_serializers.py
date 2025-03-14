from rest_framework import serializers
from .auth_serializers import PhoneNumberField
import re
from accounts.models import User
from django.shortcuts import get_object_or_404
from accounts.otp import verify_otp_pass


class PasswordField(serializers.CharField):
    def __init__(self, *args, **kwargs):
        super(PasswordField, self).__init__(required=True, write_only=True, min_length=8, *args, **kwargs)

        def validate(self, value):
            # Validate password length
            if len(value) < 8:
                raise serializers.ValidationError("Password must be at least 8 characters long.")
            
            # Validate password contains a uppercase letter
            if not re.search(r'[A-Z]', value):
                raise serializers.ValidationError("Password must contain at least one uppercase letter.")
            
            # Validate password contains a lowercase letter
            if not re.search(r'[a-z]', value):
                raise serializers.ValidationError("Password must contain at least one lowercase letter.")
            
            # Validate password contains a number
            if not re.search(r'[0-9]', value):
                raise serializers.ValidationError("Password must contain at least one number.")
            
            # Validate password contains a special character
            if not re.search(r'[!@#$%^&*()_+{}":;\']', value):
                raise serializers.ValidationError("Password must contain at least one special character.")


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
