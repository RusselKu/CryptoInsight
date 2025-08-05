from django.urls import path
from . import views
from .views import main_dashboard
from .views import crypto_market_overview, binance_market_data, wazirx_market_data, main_dashboard



urlpatterns = [
    path('', views.crypto_market_overview, name='crypto_market_overview'),
    path('binance/', views.binance_market_data, name='binance_market_data'),
    path('wazirx/', views.wazirx_market_data, name='wazirx_market_data'),
    path('dashboard/', main_dashboard, name='main_dashboard'),
]

