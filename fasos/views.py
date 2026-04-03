from rest_framework import viewsets
from .models import MedicalFacility, DistrictOfficeFacility, CCTVFacility
from .serializers import MedicalFacilitySerializer, DistrictOfficeFacilitySerializer, CCTVFacilitySerializer
from .permissions import IsOPDModelAllowed
from rest_framework.permissions import IsAuthenticated

class MedicalFacilityViewSet(viewsets.ModelViewSet):
    queryset = MedicalFacility.objects.all()
    serializer_class = MedicalFacilitySerializer
    permission_classes = [IsAuthenticated, IsOPDModelAllowed]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser: return MedicalFacility.objects.all()
        return MedicalFacility.objects.filter(operator__opd=user.opd)

class DistrictOfficeFacilityViewSet(viewsets.ModelViewSet):
    queryset = DistrictOfficeFacility.objects.all()
    serializer_class = DistrictOfficeFacilitySerializer
    permission_classes = [IsAuthenticated, IsOPDModelAllowed]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser: return DistrictOfficeFacility.objects.all()
        return DistrictOfficeFacility.objects.filter(operator__opd=user.opd)

class CCTVFacilityViewSet(viewsets.ModelViewSet):
    queryset = CCTVFacility.objects.all()
    serializer_class = CCTVFacilitySerializer
    permission_classes = [IsAuthenticated, IsOPDModelAllowed]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser: return CCTVFacility.objects.all()
        return CCTVFacility.objects.filter(operator__opd=user.opd)