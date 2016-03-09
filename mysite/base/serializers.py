from django.contrib.auth.models import User
from rest_framework import serializers
from mysite.base import models


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']
