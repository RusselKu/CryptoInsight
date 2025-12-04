from django.urls import path, include
from django.contrib import admin
from . import views
from .views import main_dashboard, crypto_market_overview, binance_market_data, wazirx_market_data

urlpatterns = [
    path('', views.crypto_market_overview, name='crypto_market_overview'),
    path('binance/', views.binance_market_data, name='binance_market_data'),
    path('wazirx/', views.wazirx_market_data, name='wazirx_market_data'),
    path('dashboard/', views.main_dashboard, name='main_dashboard'),

    # Panel admin custom (CRUD)
    path('cryptomarket/', views.crypto_list, name='crypto_list'),
    path('cryptomarket/add/', views.crypto_create, name='crypto_create'),
    path('cryptomarket/edit/<str:pk>/', views.crypto_edit, name='crypto_edit'),
    path('cryptomarket/delete/<str:pk>/', views.crypto_delete, name='crypto_delete'),
]
