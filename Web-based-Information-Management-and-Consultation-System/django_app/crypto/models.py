from django.db import models
from mongoengine import Document, StringField, FloatField, DateTimeField

# Este modelo define la estructura de tus datos en MongoDB
# Se usa principalmente para el CRUD del panel de administración
class CryptoMarket(Document):
    symbol = StringField(required=True, unique=True)
    price = FloatField(required=True)
    volume = FloatField()
    last_updated = DateTimeField()

    # (Opcional) Esto ayuda a que se vea mejor en logs o debug
    def __str__(self):
        return f"{self.symbol} - ${self.price}"