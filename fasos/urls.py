from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MedicalFacilityViewSet

router = DefaultRouter()
router.register(r'medical-facilities', MedicalFacilityViewSet, basename='facility')

urlpatterns = [
    path('', include(router.urls)),
]