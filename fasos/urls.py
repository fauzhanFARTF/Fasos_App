from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MedicalFacilityViewSet, DistrictOfficeFacilityViewSet, CCTVFacilityViewSet

router = DefaultRouter()
router.register(r'medical', MedicalFacilityViewSet, basename='medical')
router.register(r'district', DistrictOfficeFacilityViewSet, basename='district')
router.register(r'cctv', CCTVFacilityViewSet, basename='cctv')

urlpatterns = [path('', include(router.urls))]