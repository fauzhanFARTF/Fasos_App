from rest_framework import permissions

class IsOPDModelAllowed(permissions.BasePermission):
    ALLOWED_MAP = {
        'DINKES': ['MedicalFacility'],
        'DISKOMINFO': ['CCTVFacility'],
        'SETDA': ['DistrictOfficeFacility']
    }

    def has_permission(self, request, view):
        if not request.user.is_authenticated or not request.user.opd:
            return False

        # Admin superuser boleh akses semua
        if request.user.is_superuser:
            return True

        model_name = view.model_class.__name__
        allowed_models = self.ALLOWED_MAP.get(request.user.opd.kode, [])

        # Read-only boleh untuk semua viewer/editor
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write access hanya untuk OPD yang diizinkan
        return model_name in allowed_models