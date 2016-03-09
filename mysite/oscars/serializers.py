from mysite.oscars import models
from rest_framework import serializers


class OscarPoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OscarPool
        exclude = ['winner','identity','creation_date','oscar_ceremony','admin_note']
