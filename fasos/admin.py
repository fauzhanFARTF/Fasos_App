# fasos/admin.py
from django.contrib.gis import admin
from django.contrib.auth.admin import UserAdmin
from .models import OPD, CustomUser, MedicalFacility, CCTVFacility, DistrictOfficeFacility, BatasKecamatan

# ==========================================
# MIXIN: PERMISSION BASED ON ROLE & OPD
# ==========================================
class OPDPermissionMixin:
    """
    Mixin untuk membatasi akses berdasarkan role dan memfilter data per OPD.
    - Admin: Full access (add/change/delete) untuk OPD-nya
    - Editor: Add/Change only untuk OPD-nya
    - Viewer: Read-only untuk OPD-nya
    """
    
    def get_queryset(self, request):
        """Filter data hanya milik OPD user yang login"""
        qs = super().get_queryset(request)
        
        # Superuser lihat semua
        if request.user.is_superuser:
            return qs
        
        # User biasa hanya lihat data OPD-nya
        if request.user.is_authenticated and hasattr(request.user, 'opd') and request.user.opd:
            return qs.filter(operator__opd=request.user.opd)
        
        return qs.none()

    def save_model(self, request, obj, form, change):
        """Auto-assign operator ke user yang sedang login"""
        if not change:  # Saat create baru
            obj.operator = request.user
        super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        """Admin & Editor bisa tambah, Viewer tidak"""
        return request.user.is_superuser or (
            request.user.is_authenticated and request.user.role in ['admin', 'editor']
        )

    def has_change_permission(self, request, obj=None):
        """Admin & Editor bisa edit, Viewer tidak"""
        return request.user.is_superuser or (
            request.user.is_authenticated and request.user.role in ['admin', 'editor']
        )

    def has_delete_permission(self, request, obj=None):
        """Hanya Admin & Superuser yang bisa hapus"""
        return request.user.is_superuser or (
            request.user.is_authenticated and request.user.role == 'admin'
        )

    def has_view_permission(self, request, obj=None):
        """Semua user login bisa lihat"""
        return request.user.is_authenticated

    def has_module_permission(self, request):
        """Tampilkan menu di sidebar jika user adalah staff"""
        return request.user.is_staff


# ==========================================
# ADMIN CUSTOM USER (STRICT PERMISSIONS)
# ==========================================
class OPDUserAdmin(UserAdmin):
    """
    Admin khusus CustomUser dengan permission strict:
    - Hanya role 'admin' yang bisa create/edit/delete user
    - User hanya bisa lihat user di OPD yang sama
    """
    model = CustomUser
    list_display = ['uuid', 'username', 'email', 'opd', 'role', 'is_staff', 'is_active']
    readonly_fields = ['uuid', 'last_login', 'date_joined']
    
    fieldsets = UserAdmin.fieldsets + (
        ('OPD & Role', {'fields': ('opd', 'role')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'opd', 'role'),
        }),
    )

    def get_queryset(self, request):
        """Filter user hanya dari OPD yang sama (kecuali superuser)"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.is_authenticated and hasattr(request.user, 'opd') and request.user.opd:
            return qs.filter(opd=request.user.opd)
        return qs.none()

    def has_add_permission(self, request):
        """HANYA role 'admin' atau superuser yang bisa tambah user"""
        return request.user.is_superuser or (
            request.user.is_authenticated and request.user.role == 'admin'
        )

    def has_change_permission(self, request, obj=None):
        """HANYA role 'admin' atau superuser yang bisa edit user"""
        return request.user.is_superuser or (
            request.user.is_authenticated and request.user.role == 'admin'
        )

    def has_delete_permission(self, request, obj=None):
        """HANYA role 'admin' atau superuser yang bisa hapus user"""
        return self.has_change_permission(request, obj)

    def has_module_permission(self, request):
        """Tampilkan menu User di sidebar"""
        return request.user.is_staff

    def save_model(self, request, obj, form, change):
        """Auto-assign OPD ke user baru (dari OPD pembuat)"""
        if not change and not obj.pk:
            obj.opd = request.user.opd
        super().save_model(request, obj, form, change)


# ==========================================
# REGISTER MODELS
# ==========================================
@admin.register(OPD)
class OPDAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'kode', 'nama']
    readonly_fields = ['uuid']
    search_fields = ['nama', 'kode']
    ordering = ['kode']

@admin.register(MedicalFacility)
class MedicalFacilityAdmin(OPDPermissionMixin, admin.GISModelAdmin):
    gis_widget_kwargs = {
        "attrs": {
            "default_lon": 106.8,
            "default_lat": -6.2,
            "default_zoom": 10
        }
    }
    list_display = ['uuid', 'nama', 'tipe', 'status', 'operator', 'date_field']
    readonly_fields = ['uuid', 'operator', 'date_field']
    list_filter = ['status', 'tipe', 'operator__opd']
    search_fields = ['nama', 'koderumahsakit']

@admin.register(DistrictOfficeFacility)
class DistrictOfficeFacilityAdmin(OPDPermissionMixin, admin.GISModelAdmin):
    gis_widget_kwargs = {
        "attrs": {
            "default_lon": 106.8,
            "default_lat": -6.2,
            "default_zoom": 10
        }
    }
    list_display = ['uuid', 'nama', 'tipe', 'status', 'operator', 'date_field']
    readonly_fields = ['uuid', 'operator', 'date_field']
    list_filter = ['status', 'tipe', 'operator__opd']
    search_fields = ['nama']

@admin.register(CCTVFacility)
class CCTVFacilityAdmin(OPDPermissionMixin, admin.GISModelAdmin):
    gis_widget_kwargs = {
        "attrs": {
            "default_lon": 106.8,
            "default_lat": -6.2,
            "default_zoom": 10
        }
    }
    list_display = ['uuid', 'kode_cam', 'nama_lokasi', 'wilayah', 'is_active', 'operator', 'date_field']
    readonly_fields = ['uuid', 'operator', 'date_field']
    list_filter = ['is_active', 'wilayah', 'operator__opd']
    search_fields = ['kode_cam', 'nama_lokasi']

@admin.register(BatasKecamatan)
class BatasKecamatanAdmin(admin.GISModelAdmin):
    list_display = ['uuid', 'kecamatan', 'kd_kcmtan', 'tipe']
    readonly_fields = ['uuid']
    search_fields = ['kecamatan', 'kd_kcmtan']