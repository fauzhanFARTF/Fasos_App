from rest_framework import permissions

class IsOPDModelAllowed(permissions.BasePermission):
    """
    Permission untuk API: mapping OPD ke model yang boleh diakses
    """
    ALLOWED_MAP = {
        'DINKES': ['MedicalFacility'],
        'DISKOMINFO': ['CCTVFacility'],
        'SETDA': ['DistrictOfficeFacility']
    }

    def has_permission(self, request, view):
        if not request.user.is_authenticated or not request.user.opd:
            return False
        
        if request.user.is_superuser:
            return True
            
        model_name = view.model_class.__name__
        allowed_models = self.ALLOWED_MAP.get(request.user.opd.kode, [])
        
        # Read-only untuk semua user login
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Write access hanya untuk OPD yang diizinkan
        return model_name in allowed_models

    def has_object_permission(self, request, view, obj):
        # Read-only untuk semua
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write/delete hanya untuk operator sendiri atau admin
        return obj.operator == request.user or request.user.role == 'admin'