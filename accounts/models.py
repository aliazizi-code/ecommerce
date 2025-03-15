from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation.trans_null import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from .managers import UserManager
from utils.validators import validate_image_dimensions, validate_image_size


def get_upload_to(instance, filename):
        return f'users/avatar/{instance}/{filename}'


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, blank=True, null=True)
    number = PhoneNumberField(unique=True, region='IR')
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)

    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_new = models.BooleanField(default=True)
    permissions = models.CharField(max_length=255, default='', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'number'
    REQUIRED_FIELDS = ['email']

    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name.capitalize()} {self.last_name.capitalize()}"
        return ""

    def mask_number(self):
        return f"+98{str(self.number)[2:4]}{'*' * 5}{str(self.number)[-2:]}"
    
    def mask_email(self):
        email = self.email
        return f"{email[:3]}{'*' * 4}@{'*' * 3}"

    def mask_contact_info(self):
        if self.full_name():
            return self.full_name()
        if self.email:
            return self.mask_email()
        if self.number:
            return self.mask_number()
        return "unknown"
        


    def __str__(self):
        full_name = self.full_name()
        return f"{full_name.strip()} ({self.number or self.email})".strip()

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        """Is the user a member of staff?"""
        # Simplest possible answer: All admins are staff
        return self.is_admin


class UserProfile(models.Model):
    class Gender(models.TextChoices):
        male = 'M', _('Male')
        female = 'F', _('Female')
        other = 'O', _('Other')

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to=get_upload_to, validators=[validate_image_size, validate_image_dimensions])
    avatar_thumbnail = ImageSpecField(source='avatar',
                                      processors=[ResizeToFill(120, 120)],
                                      format='JPEG',
                                      options={'quality': 80})
    age = models.PositiveSmallIntegerField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=Gender.choices, default=Gender.other)

    def __str__(self):
        return str(self.user)
