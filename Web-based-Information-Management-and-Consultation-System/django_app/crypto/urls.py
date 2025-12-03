from django.urls import path
from . import views

# Importamos explícitamente las vistas para mayor claridad
from .views import (
    main_dashboard, 
    crypto_market_overview, 
    binance_market_data, 
    wazirx_market_data, 
    api_market_overview,  # <--- IMPORTANTE: La nueva vista API
    crypto_list,
    crypto_create,
    crypto_edit,
    crypto_delete
)

urlpatterns = [
    # --- NUEVA RUTA API (Para conectar tu futuro React/Next.js) ---
    path('api/market-overview/', views.api_market_overview, name='api_market_overview'),
    path('api/binance/', views.api_binance_data, name='api_binance_data'),
    path('api/wazirx/', views.api_wazirx_data, name='api_wazirx_data'),

    # -------------------------------------------------------------

    # Rutas originales (Legacy - Para que no se rompa tu dashboard actual)
    path('', views.crypto_market_overview, name='crypto_market_overview'),
    path('binance/', views.binance_market_data, name='binance_market_data'),
    path('wazirx/', views.wazirx_market_data, name='wazirx_market_data'),
    path('dashboard/', views.main_dashboard, name='main_dashboard'),

    # Panel admin custom (CRUD)
    path('admin/cryptomarket/', views.crypto_list, name='crypto_list'),
    path('admin/cryptomarket/add/', views.crypto_create, name='crypto_create'),
    path('admin/cryptomarket/edit/<str:pk>/', views.crypto_edit, name='crypto_edit'),
    path('admin/cryptomarket/delete/<str:pk>/', views.crypto_delete, name='crypto_delete'),
]