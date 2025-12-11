"""stockmgtr URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from stock import api_views
from stock import views

# Create a router and register our viewsets with it for the API.
router = DefaultRouter()
router.register(r'stock', api_views.StockViewSet)
router.register(r'suppliers', api_views.SupplierViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- 1. API URLS ---
    path('api/', include(router.urls)),

    # --- 2. AUTHENTICATION ---
    # Custom Logout (Must be defined BEFORE 'django.contrib.auth.urls' to override it)
    path('accounts/logout/', views.custom_logout, name='logout'),
    
    # Standard Django Auth (Login, Password Reset, etc.)
    path('accounts/', include('django.contrib.auth.urls')),

    # --- 3. ADVANCED FEATURES ---
    path('upload_csv/', views.upload_csv, name='upload_csv'),
    path('generate_pdf/<int:pk>/', views.generate_pdf, name='generate_pdf'),

    # --- 4. MAIN APP URLS ---
    # This includes all your standard views like view_stock, add_stock, etc.
    path('', include('stock.urls')),

    path('add_to_cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('view_cart/', views.view_cart, name='view_cart'),
    path('clear_cart/', views.clear_cart, name='clear_cart'),
    path('checkout/', views.checkout_cart, name='checkout'),
]