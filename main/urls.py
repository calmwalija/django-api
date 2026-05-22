"""
URL configuration for main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path, include

from rest_framework import routers

from authenticator.views import AuthenticationCreateAPIView, CurrentUserAPIView
from patients import views
from patients.generic_views import PatientGenericView, PatientRetrieveView
from patients.view_set import PatientViewSet

from drf_spectacular.views import (
  SpectacularAPIView,
  SpectacularRedocView,
  SpectacularSwaggerView,
)

from rest_framework_simplejwt.views import (
  TokenObtainPairView,
  TokenRefreshView,
)

router = routers.DefaultRouter()
router.register("patient", PatientViewSet)

urlpatterns = [
  path("api/v1/patient/", views.patient_list),
  path("api/v1/patient/<int:id>/", views.patient_detail),

  path("api/v2/", include(router.urls)),

  path("api/v3/patient/", PatientGenericView.as_view()),
  path("api/v3/patient/<int:id>/", PatientRetrieveView.as_view()),

  path("api/auth/register/", AuthenticationCreateAPIView.as_view()),
  path("api/auth/me/", CurrentUserAPIView.as_view()),

  path("api/auth/login/", TokenObtainPairView.as_view()),
  path("api/auth/refresh/", TokenRefreshView.as_view()),

  path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
  path("api/docs/", SpectacularSwaggerView.as_view(), name="swagger-ui"),
  path("api/redoc/", SpectacularRedocView.as_view(), name="redoc"),
]
