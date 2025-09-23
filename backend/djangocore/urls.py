"""
URL configuration for djangocore project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from users.views import SocialLoginCallbackView, CustomRegisterView, CustomLoginView
from .views import health_check

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('api/v1/auth/login/', CustomLoginView.as_view(), name='custom_login'),
    path('api/v1/auth/registration/', CustomRegisterView.as_view(), name='custom_registration'),
    path('api/v1/accounts/', include('allauth.urls')),
    path('api/v1/users/', include('users.urls')),
    path('api/v1/games/', include('games.urls')),
    path('api/v1/zawomons/', include('zawomons.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    # Możesz dodać kolejne endpointy API tutaj
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    path('api/v1/accounts/social/callback/', SocialLoginCallbackView.as_view(), name='social_callback'),
]
