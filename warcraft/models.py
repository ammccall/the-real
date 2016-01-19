from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractBaseUser
from simple_email_confirmation import SimpleEmailConfirmationUserMixin
from django.contrib.auth.models import UserManager
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.signals import user_logged_in, user_logged_out

# Create your models here.

'''class UserProfile(models.Model):
    user   = models.OneToOneField(User)
    picture = models.ImageField(upload_to="images")
    REQUIRED_FIELDS = ('user', 'email',)
    
    def __unicode__(self):
        return self.user.usernam'''
class Friends(models.Model):
    name = models.CharField(max_length=31, default = "")
    friends = models.ForeignKey('User', null = True, blank = True)


class LoggedUser(models.Model):
    user = models.ForeignKey('User')
    web = models.BooleanField(default=False)
    internal = models.BooleanField(default=False)

    def __unicode__(self):
        return self.user.userName

    def login_user(sender, request, user, **kwargs):
        try:
            e = LoggedUser.objects.get(user=user)
        except LoggedUser.DoesNotExist:
            LoggedUser(user=user, web=user.login_web, internal=user.login_internal).save()

    def logout_user(sender, request, user, **kwargs):
        try:
            u = LoggedUser.objects.get(user=user)
            u.delete()
        except LoggedUser.DoesNotExist:
            pass

    user_logged_in.connect(login_user)
    user_logged_out.connect(logout_user)



class CustomUserManager(BaseUserManager):

    def create_user(self, userName, password=None, **extra_fields):
        userName = userName
        user = self.model(userName=userName, is_staff=False, is_active=True, is_superuser=False, is_admin = False)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, userName, password, **extra_fields):
        userName = userName
        user = self.model(userName=userName, is_staff=False, is_active=True, is_superuser=True, is_admin = True)
        user.set_password(password)
        user.save(using=self._db)
        return user
        


        
class User(SimpleEmailConfirmationUserMixin, AbstractBaseUser):
        wins = models.PositiveIntegerField(default = 0)
        losses = models.PositiveIntegerField(default = 0)
        rating = models.FloatField(default = 1000)
        ranking = models.PositiveIntegerField(default = 1)
        userName = models.CharField(max_length=31, unique = True)
        picture =models.ImageField(upload_to="images")
        firstName = models.CharField(max_length=31)
        lastName = models.CharField(max_length=31)
        email = models.EmailField('email address')
        is_active = models.BooleanField(default = False)
        is_admin = models.BooleanField(default = False)
        is_online = models.BooleanField(default = False)
        login_internal = models.BooleanField(default = False)
        login_web = models.BooleanField(default = False)
        USERNAME_FIELD = 'userName'
        REQUIRED_FIELDS = []
        emailEvery= models.IntegerField(default = 0)
        has_messages = models.BooleanField(default = False)
        
        objects = CustomUserManager()

        def __unicode__(self):
            return self.userName
        
        @property
        def is_superuser(self):
            return self.is_admin

        @property
        def is_staff(self):
            return self.is_admin

        def has_perm(self, perm, obj=None):
            return self.is_admin

        def has_module_perms(self, app_label):
            return self.is_admin
        
        def get_short_name(self):
            return self.userName
            
        def get_email(self):
            return self.email
        
        def get_wins(self):
            return self.wins

        def get_losses(self):
            return self.losses

        def get_rating(self):
            return self.rating

        def get_ranking(self):
            return self.ranking

        def get_my_friends_as_list(self):
            return ', '.join(self.friends_set.values_list('name', flat=True))