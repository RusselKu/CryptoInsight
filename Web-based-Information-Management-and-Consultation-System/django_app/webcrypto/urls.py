from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin nativo Django

    # Auth login/logout
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # Rutas app crypto
    path('', include('crypto.urls')),

    # Rutas app predictions
    path('predictions/', include('predictions.urls')),
]
