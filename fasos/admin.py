# fasos/admin.py
from django.contrib.gis import admin
from leaflet.admin import LeafletGeoAdminMixin  # ✅ Import ini
from django.utils import timezone
from .models import OPD, CustomUser, MedicalFacility, CCTVFacility, DistrictOfficeFacility, BatasKecamatan


# ==========================================
# ACTIONS UNTUK SOFT DELETE
# ==========================================
def soft_delete_selected(modeladmin, request, queryset):
    queryset.update(is_deleted=True, deleted_at=timezone.now())
    modeladmin.message_user(request, f"{queryset.count()} record berhasil di-soft delete.")
soft_delete_selected.short_description = "🗑️ Soft Delete Selected"

def restore_selected(modeladmin, request, queryset):
    queryset.update(is_deleted=False, deleted_at=None)
    modeladmin.message_user(request, f"{queryset.count()} record berhasil di-restore.")
restore_selected.short_description = "♻️ Restore Selected"

def hard_delete_selected(modeladmin, request, queryset):
    count = queryset.count()
    queryset.hard_delete()
    modeladmin.message_user(request, f"{count} record dihapus permanen.")
hard_delete_selected.short_description = "⚠️ Hard Delete Permanent"


# ==========================================
# MIXIN: SOFT DELETE ADMIN
# ==========================================
class SoftDeleteAdminMixin:
    list_filter = ['is_deleted']
    actions = [soft_delete_selected, restore_selected, hard_delete_selected]

    def get_queryset(self, request):
        return self.model.objects.with_deleted()


# ==========================================
# MIXIN: OPD PERMISSION & MENU VISIBILITY
# ==========================================
class OPDPermissionMixin:
    ALLOWED_FACILITY_MODELS = {
        'DINKES': ['MedicalFacility'],
        'DISKOMINFO': ['CCTVFacility'],
        'SETDA': ['DistrictOfficeFacility'],
    }

    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True
        
        user = request.user
        if not user.is_authenticated or not hasattr(user, 'opd') or not user.opd:
            return False

        model_name = self.model.__name__

        if model_name in ['OPD', 'CustomUser']:
            return user.role == 'admin'

        allowed = self.ALLOWED_FACILITY_MODELS.get(user.opd.kode, [])
        return model_name in allowed

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.is_authenticated and request.user.opd:
            return qs.filter(operator__opd=request.user.opd)
        return qs.none()

    def save_model(self, request, obj, form, change):
        if not change:
            obj.operator = request.user
        super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        return request.user.is_superuser or (request.user.is_authenticated and request.user.role in ['admin', 'editor'])

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or (request.user.is_authenticated and request.user.role in ['admin', 'editor'])

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or (request.user.is_authenticated and request.user.role == 'admin')

    def has_view_permission(self, request, obj=None):
        return request.user.is_authenticated


# ==========================================
# 1. ADMIN OPD
# ==========================================
@admin.register(OPD)
class OPDAdmin(SoftDeleteAdminMixin, OPDPermissionMixin, admin.ModelAdmin):
    list_display = ['uuid', 'kode', 'nama', 'is_deleted', 'deleted_at']
    readonly_fields = ['uuid']
    search_fields = ['nama', 'kode']
    ordering = ['kode']

    def has_add_permission(self, request): return request.user.is_superuser
    def has_change_permission(self, request, obj=None): return request.user.is_superuser
    def has_delete_permission(self, request, obj=None): return request.user.is_superuser


# ==========================================
# 2. ADMIN CUSTOM USER
# ==========================================
@admin.register(CustomUser)
class OPDUserAdmin(SoftDeleteAdminMixin, OPDPermissionMixin, admin.ModelAdmin):  # ✅ Tidak perlu Leaflet untuk User
    model = CustomUser
    list_display = ['uuid', 'username', 'email', 'opd', 'role', 'is_staff', 'is_active', 'is_deleted']
    readonly_fields = ['uuid', 'last_login', 'date_joined', 'is_deleted', 'deleted_at']

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
        ('OPD & Role', {'fields': ('opd', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'opd', 'role'),
        }),
    )

    def get_queryset(self, request):
        qs = CustomUser.objects.with_deleted()
        if request.user.is_superuser: return qs
        if request.user.is_authenticated and request.user.opd:
            return qs.filter(opd=request.user.opd)
        return qs.none()

    def has_add_permission(self, request):
        if request.user.is_superuser: return True
        return request.user.is_authenticated and request.user.role == 'admin'

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser: return True
        if request.user.is_authenticated and request.user.role == 'admin':
            return obj is None or (hasattr(obj, 'opd') and obj.opd == request.user.opd)
        return False

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)

    def save_model(self, request, obj, form, change):
        if not change and not obj.pk and not request.user.is_superuser and request.user.opd:
            obj.opd = request.user.opd
        super().save_model(request, obj, form, change)


# ==========================================
# 3. ADMIN MEDICAL FACILITY (DINKES) - LEAFLET
# ==========================================
@admin.register(MedicalFacility)
class MedicalFacilityAdmin(OPDPermissionMixin, SoftDeleteAdminMixin, LeafletGeoAdminMixin, admin.ModelAdmin):
    # Leaflet settings override
    settings_overrides = {
        'DEFAULT_CENTER': (-6.2088, 106.8456),
        'DEFAULT_ZOOM': 13,
    }
    
    list_display = ['uuid', 'nama', 'tipe', 'status', 'operator', 'is_deleted', 'date_field']
    list_filter = ['is_deleted', 'status', 'tipe', 'operator__opd']
    search_fields = ['nama', 'koderumahsakit']
    readonly_fields = ['uuid', 'operator', 'is_deleted', 'deleted_at', 'date_field']


# ==========================================
# 4. ADMIN DISTRICT OFFICE FACILITY (SETDA) - LEAFLET
# ==========================================
@admin.register(DistrictOfficeFacility)
class DistrictOfficeFacilityAdmin(OPDPermissionMixin, SoftDeleteAdminMixin, LeafletGeoAdminMixin, admin.ModelAdmin):
    settings_overrides = {
        'DEFAULT_CENTER': (-6.2088, 106.8456),
        'DEFAULT_ZOOM': 13,
    }
    
    list_display = ['uuid', 'nama', 'tipe', 'status', 'operator', 'is_deleted', 'date_field']
    list_filter = ['is_deleted', 'status', 'tipe', 'operator__opd']
    search_fields = ['nama']
    readonly_fields = ['uuid', 'operator', 'is_deleted', 'deleted_at', 'date_field']


# ==========================================
# 5. ADMIN CCTV FACILITY (DISKOMINFO) - LEAFLET
# ==========================================
@admin.register(CCTVFacility)
class CCTVFacilityAdmin(OPDPermissionMixin, SoftDeleteAdminMixin, LeafletGeoAdminMixin, admin.ModelAdmin):
    settings_overrides = {
        'DEFAULT_CENTER': (-6.2088, 106.8456),
        'DEFAULT_ZOOM': 13,
    }
    
    list_display = ['uuid', 'kode_cam', 'nama_lokasi', 'wilayah', 'is_active', 'operator', 'is_deleted', 'date_field']
    list_filter = ['is_deleted', 'is_active', 'wilayah', 'operator__opd']
    search_fields = ['kode_cam', 'nama_lokasi']
    readonly_fields = ['uuid', 'operator', 'is_deleted', 'deleted_at', 'date_field']


# ==========================================
# 6. ADMIN BATAS KECAMATAN
# ==========================================
@admin.register(BatasKecamatan)
class BatasKecamatanAdmin(SoftDeleteAdminMixin, OPDPermissionMixin, admin.ModelAdmin):  # ✅ Tidak perlu Leaflet untuk Polygon
    list_display = ['uuid', 'kecamatan', 'kd_kcmtan', 'tipe', 'is_deleted']
    list_filter = ['is_deleted']
    search_fields = ['kecamatan', 'kd_kcmtan']
    readonly_fields = ['uuid', 'is_deleted', 'deleted_at']
    
    def has_module_permission(self, request):
        return request.user.is_superuser or (request.user.is_authenticated and request.user.role in ['admin', 'editor'])