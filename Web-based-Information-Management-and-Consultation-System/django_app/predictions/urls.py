from django.urls import path
from . import views

urlpatterns = [
    path('crypto-predictions/', views.predict, name='crypto_predictions'),
]
