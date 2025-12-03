from django.urls import path
from . import views

urlpatterns = [
    path('crypto-predictions/', views.predict, name='crypto_predictions'),
    path('binance/', views.predict_binance, name='binance_predictions'),
    path('wazirx/', views.predict_wazirx, name='wazirx_predictions'),
    path('binance/history/<str:symbol>/', views.historical_binance_data, name='historical_binance_data'),
    path('wazirx/history/<str:symbol>/', views.historical_wazirx_data, name='historical_wazirx_data'),
]
