from django.db import models

from mongoengine import Document, StringField, FloatField, DateTimeField

class CryptoMarket(Document):
    symbol = StringField(required=True, unique=True)
    price = FloatField(required=True)
    volume = FloatField()
    last_updated = DateTimeField()
