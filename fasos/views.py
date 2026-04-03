from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import MedicalFacility
from .serializers import MedicalFacilitySerializer

# Create your views here.
class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role == 'admin' or obj.operator == request.user

class MedicalFacilityViewSet(viewsets.ModelViewSet):
    serializer_class = MedicalFacilitySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return MedicalFacility.objects.all()
        if hasattr(user, 'opd') and user.opd:
            return MedicalFacility.objects.filter(operator__opd=user.opd)
        return MedicalFacility.objects.filter(operator=user)