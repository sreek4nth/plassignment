from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import ProductViewSet, ReviewViewSet, RegisterView, CustomAuthToken

# DRF router for REST API endpoints
router = DefaultRouter()
router.register('products', ProductViewSet)
router.register('reviews', ReviewViewSet)

urlpatterns = [
    # Frontend views
    path('', views.homepage, name='home'),
    path('login/', views.login_options, name='login_options'),
    path('login/admin/', views.admin_login, name='admin_login'),
    path('login/user/', views.user_login, name='user_login'),
    path('register/', views.register_user, name='register_user'),
    path('product/<int:pk>/review/', views.review_product, name='review_product'),

    # Admin dashboard views (custom HTML forms)
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/product/add/', views.create_product, name='create_product'),
    path('dashboard/product/<int:pk>/edit/', views.update_product, name='update_product'),
    path('dashboard/product/<int:pk>/delete/', views.delete_product, name='delete_product'),

    # REST API endpoints
    path('api/', include(router.urls)),
    path('api/register/', RegisterView.as_view(), name='api_register'),
    path('api/login/', CustomAuthToken.as_view(), name='api_login'),
]
