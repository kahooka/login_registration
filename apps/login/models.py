from __future__ import unicode_literals
from django.db import models
import re
import bcrypt

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')
NAME_REGEX = re.compile(r'^[A-Za-z]\w+$')

class UserManager(models.Manager):
    def validate_login(self, post_data):
        errors = []
        # check DB for post_data['email']
        if len(self.filter(email=post_data['email'])) > 0:
            # check this user's password
            user = self.filter(email=post_data['email'])[0]
            if not bcrypt.checkpw(post_data['password'].encode(), user.password.encode()):
                errors.append("Your email or password is incorrect.")
        else:
            errors.append("Your email or password is incorrect.")
        if errors:
            return errors
        return user

    def validate_registration(self, post_data):
        errors = []
        # VALIDATION: names gotta be 2+ characters
        if len(post_data['first_name']) < 2 or len(post_data['last_name']) < 2:
            errors.append("Name fields must be 2+ characters.")
        # VALIDATION: password gotta be 8+ characters
        if len(post_data['password']) < 8:
            errors.append("Your password must be 8+ characters.")
        # VALIDATION: name fields be letters only           
        if not re.match(NAME_REGEX, post_data['first_name']) or not re.match(NAME_REGEX, post_data['last_name']):
            errors.append("Name fields should consist of letters only.")
        # VALIDATION: check if email be valid
        if not re.match(EMAIL_REGEX, post_data['email']):
            errors.append("Email is invalid.")
        # VALIDATION: email gotta be a snowflake
        if len(User.objects.filter(email=post_data['email'])) > 0:
            errors.append("This email address is already in use.")
        # VALIDATION: password matches password_confirm
        if post_data['password'] != post_data['password_confirm']:
            errors.append("Passwords do not match.")
        if not errors:
            hashed = bcrypt.hashpw((post_data['password'].encode()), bcrypt.gensalt(5))
            user=self.create(
                first_name = post_data['first_name'],
                last_name = post_data['last_name'],
                email = post_data['email'].lower(),
                password = hashed)
            return user
        return errors

class User(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    objects = UserManager()