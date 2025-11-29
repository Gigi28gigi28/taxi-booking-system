from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager, Group
)
from django.utils import timezone

# USER MANAGER
class CompteManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(email, password, **extra_fields)


# CUSTOM USER MODEL
class Compte(AbstractBaseUser, PermissionsMixin):

    ROLE_CHOICES = (
        ('passager', 'Passager'),
        ('chauffeur', 'Chauffeur'),
    )

    email = models.EmailField(unique=True)
    nom = models.CharField(max_length=150, blank=True)
    prenom = models.CharField(max_length=150, blank=True)

    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='passager')

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CompteManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  

    def __str__(self):
        return f"{self.email} ({self.role})"

    def save(self, *args, **kwargs):
     if self.email:
        self.email = self.email.lower().strip()
        super().save(*args, **kwargs)


        try:
            Group.objects.get_or_create(name=self.role)

            user_group = Group.objects.get(name=self.role)

            if user_group not in self.groups.all():
                self.groups.add(user_group)

        except Exception:
            pass
