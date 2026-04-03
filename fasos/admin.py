# fasos/admin.py
from django.contrib.gis import admin
from django.contrib.auth.admin import UserAdmin
from .models import OPD, CustomUser, MedicalFacility, CCTVFacility, DistrictOfficeFacility, BatasKecamatan

# ==========================================
# 1. ADMIN OPD (KUNCI: HANYA SUPERUSER)
# ==========================================
@admin.register(OPD)
class OPDAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'kode', 'nama']
    readonly_fields = ['uuid']
    search_fields = ['nama', 'kode']
    ordering = ['kode']

    # 🔒 KUNCI: Hanya Superuser yang boleh tambah/edit/hapus OPD
    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_module_permission(self, request):
        # Agar menu terlihat di sidebar, tapi tombol Add/Change hilang jika bukan superuser
        return request.user.is_staff


# ==========================================
# 2. ADMIN CUSTOM USER (KUNCI: ADMIN OPD BISA KELOLA USER)
# ==========================================
class OPDUserAdmin(UserAdmin):
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
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.is_authenticated and hasattr(request.user, 'opd') and request.user.opd:
            return qs.filter(opd=request.user.opd)
        return qs.none()

    def has_add_permission(self, request):
        # ✅ Admin OPD & Superuser bisa tambah user
        return request.user.is_superuser or (
            request.user.is_authenticated and request.user.role == 'admin'
        )

    def has_change_permission(self, request, obj=None):
        # ✅ Admin OPD & Superuser bisa edit user
        return request.user.is_superuser or (
            request.user.is_authenticated and request.user.role == 'admin'
        )

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)

    def has_module_permission(self, request):
        return request.user.is_staff

    def save_model(self, request, obj, form, change):
        if not change and not obj.pk:
            obj.opd = request.user.opd
        super().save_model(request, obj, form, change)


# ==========================================
# 3. ADMIN FASILITAS (KUNCI: ADMIN & EDITOR BISA INPUT)
# ==========================================
class OPDPermissionMixin:
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.is_authenticated and hasattr(request.user, 'opd') and request.user.opd:
            return qs.filter(operator__opd=request.user.opd)
        return qs.none()

    def save_model(self, request, obj, form, change):
        if not change:
            obj.operator = request.user
        super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        # ✅ Admin & Editor bisa tambah fasilitas
        return request.user.is_superuser or (
            request.user.is_authenticated and request.user.role in ['admin', 'editor']
        )

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or (
            request.user.is_authenticated and request.user.role in ['admin', 'editor']
        )

    def has_delete_permission(self, request, obj=None):
        # ✅ Hanya Admin & Superuser yang bisa hapus
        return request.user.is_superuser or (
            request.user.is_authenticated and request.user.role == 'admin'
        )

    def has_view_permission(self, request, obj=None):
        return request.user.is_authenticated

    def has_module_permission(self, request):
        return request.user.is_staff


@admin.register(MedicalFacility)
class MedicalFacilityAdmin(OPDPermissionMixin, admin.GISModelAdmin):
    gis_widget_kwargs = {"attrs": {"default_lon": 106.8, "default_lat": -6.2, "default_zoom": 10}}
    list_display = ['uuid', 'nama', 'tipe', 'status', 'operator']
    readonly_fields = ['uuid', 'operator']

@admin.register(DistrictOfficeFacility)
class DistrictOfficeFacilityAdmin(OPDPermissionMixin, admin.GISModelAdmin):
    gis_widget_kwargs = {"attrs": {"default_lon": 106.8, "default_lat": -6.2, "default_zoom": 10}}
    list_display = ['uuid', 'nama', 'tipe', 'status', 'operator']
    readonly_fields = ['uuid', 'operator']

@admin.register(CCTVFacility)
class CCTVFacilityAdmin(OPDPermissionMixin, admin.GISModelAdmin):
    gis_widget_kwargs = {"attrs": {"default_lon": 106.8, "default_lat": -6.2, "default_zoom": 10}}
    list_display = ['uuid', 'kode_cam', 'nama_lokasi', 'wilayah', 'is_active', 'operator']
    readonly_fields = ['uuid', 'operator']

@admin.register(BatasKecamatan)
class BatasKecamatanAdmin(admin.GISModelAdmin):
    list_display = ['uuid', 'kecamatan', 'kd_kcmtan', 'tipe']
    readonly_fields = ['uuid']