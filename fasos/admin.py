# fasos/admin.py
from django.contrib.gis import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from .models import OPD, CustomUser, MedicalFacility, CCTVFacility, DistrictOfficeFacility, BatasKecamatan


# ==========================================
# ACTIONS UNTUK SOFT DELETE
# ==========================================
def soft_delete_selected(modeladmin, request, queryset):
    """Soft delete selected records"""
    queryset.update(is_deleted=True, deleted_at=timezone.now())
    modeladmin.message_user(request, f"{queryset.count()} record berhasil di-soft delete.")


soft_delete_selected.short_description = "🗑️ Soft Delete Selected"


def restore_selected(modeladmin, request, queryset):
    """Restore selected records"""
    queryset.update(is_deleted=False, deleted_at=None)
    modeladmin.message_user(request, f"{queryset.count()} record berhasil di-restore.")


restore_selected.short_description = "♻️ Restore Selected"


def hard_delete_selected(modeladmin, request, queryset):
    """Permanently delete selected records"""
    count = queryset.count()
    queryset.hard_delete()
    modeladmin.message_user(request, f"{count} record dihapus permanen.")


hard_delete_selected.short_description = "⚠️ Hard Delete Permanent"


# ==========================================
# MIXIN: SOFT DELETE ADMIN
# ==========================================
class SoftDeleteAdminMixin:
    """Mixin untuk menambahkan actions & filter soft delete"""
    list_filter = ['is_deleted']
    actions = [soft_delete_selected, restore_selected, hard_delete_selected]

    def get_queryset(self, request):
        """Tampilkan semua data (aktif & terhapus) di admin"""
        return self.model.objects.with_deleted()


# ==========================================
# MIXIN: OPD PERMISSION
# ==========================================
class OPDPermissionMixin:
    """Mixin untuk membatasi akses berdasarkan role & OPD"""

    def get_queryset(self, request):
        """Filter data hanya milik OPD user yang login"""
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        if request.user.is_authenticated and hasattr(request.user, 'opd') and request.user.opd:
            return qs.filter(operator__opd=request.user.opd)

        return qs.none()

    def save_model(self, request, obj, form, change):
        """Auto-assign operator ke user yang sedang login"""
        if not change:
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
# 1. ADMIN OPD (HANYA SUPERUSER)
# ==========================================
@admin.register(OPD)
class OPDAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = ['uuid', 'kode', 'nama', 'is_deleted', 'deleted_at']
    readonly_fields = ['uuid']
    search_fields = ['nama', 'kode']
    ordering = ['kode']

    def has_add_permission(self, request):
        """HANYA superuser yang bisa tambah OPD"""
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        """HANYA superuser yang bisa edit OPD"""
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        """HANYA superuser yang bisa hapus OPD"""
        return request.user.is_superuser


# ==========================================
# 2. ADMIN CUSTOM USER (ADMIN OPD BISA KELOLA USER)
# ==========================================
@admin.register(CustomUser)
class OPDUserAdmin(SoftDeleteAdminMixin, UserAdmin):
    model = CustomUser
    list_display = ['uuid', 'username', 'email', 'opd', 'role', 'is_staff', 'is_active', 'is_deleted']
    readonly_fields = ['uuid', 'last_login', 'date_joined', 'is_deleted', 'deleted_at']

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
        qs = CustomUser.objects.with_deleted()

        if request.user.is_superuser:
            return qs

        if request.user.is_authenticated and hasattr(request.user, 'opd') and request.user.opd:
            return qs.filter(opd=request.user.opd)

        return qs.none()

    def has_add_permission(self, request):
        """
        - Superuser: bisa create user dengan role apapun
        - Admin OPD: hanya bisa create user dengan role editor/viewer
        """
        if request.user.is_superuser:
            return True
        return request.user.is_authenticated and request.user.role == 'admin'

    def has_change_permission(self, request, obj=None):
        """
        - Superuser: bisa edit semua user
        - Admin OPD: hanya bisa edit user di OPD-nya
        """
        if request.user.is_superuser:
            return True

        if request.user.is_authenticated and request.user.role == 'admin':
            if obj is None:
                return True
            return hasattr(obj, 'opd') and obj.opd == request.user.opd

        return False

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)

    def has_module_permission(self, request):
        """Tampilkan menu User di sidebar"""
        return request.user.is_staff

    def save_model(self, request, obj, form, change):
        """Auto-assign OPD ke user baru (dari OPD pembuat)"""
        if not change and not obj.pk:
            # Jika yang membuat adalah admin OPD, otomatis set opd-nya
            if not request.user.is_superuser and request.user.opd:
                obj.opd = request.user.opd
            # Jika superuser, biarkan opd sesuai yang dipilih di form
        super().save_model(request, obj, form, change)


# ==========================================
# 3. ADMIN MEDICAL FACILITY (DINKES)
# ==========================================
@admin.register(MedicalFacility)
class MedicalFacilityAdmin(OPDPermissionMixin, SoftDeleteAdminMixin, admin.GISModelAdmin):
    gis_widget_kwargs = {
        "attrs": {
            "default_lon": 106.8,
            "default_lat": -6.2,
            "default_zoom": 10
        }
    }
    list_display = ['uuid', 'nama', 'tipe', 'status', 'operator', 'is_deleted', 'date_field']
    list_filter = ['is_deleted', 'status', 'tipe', 'operator__opd']
    search_fields = ['nama', 'koderumahsakit']
    readonly_fields = ['uuid', 'operator', 'is_deleted', 'deleted_at', 'date_field']


# ==========================================
# 4. ADMIN DISTRICT OFFICE FACILITY (SETDA)
# ==========================================
@admin.register(DistrictOfficeFacility)
class DistrictOfficeFacilityAdmin(OPDPermissionMixin, SoftDeleteAdminMixin, admin.GISModelAdmin):
    gis_widget_kwargs = {
        "attrs": {
            "default_lon": 106.8,
            "default_lat": -6.2,
            "default_zoom": 10
        }
    }
    list_display = ['uuid', 'nama', 'tipe', 'status', 'operator', 'is_deleted', 'date_field']
    list_filter = ['is_deleted', 'status', 'tipe', 'operator__opd']
    search_fields = ['nama']
    readonly_fields = ['uuid', 'operator', 'is_deleted', 'deleted_at', 'date_field']


# ==========================================
# 5. ADMIN CCTV FACILITY (DISKOMINFO)
# ==========================================
@admin.register(CCTVFacility)
class CCTVFacilityAdmin(OPDPermissionMixin, SoftDeleteAdminMixin, admin.GISModelAdmin):
    gis_widget_kwargs = {
        "attrs": {
            "default_lon": 106.8,
            "default_lat": -6.2,
            "default_zoom": 10
        }
    }
    list_display = ['uuid', 'kode_cam', 'nama_lokasi', 'wilayah', 'is_active', 'operator', 'is_deleted', 'date_field']
    list_filter = ['is_deleted', 'is_active', 'wilayah', 'operator__opd']
    search_fields = ['kode_cam', 'nama_lokasi']
    readonly_fields = ['uuid', 'operator', 'is_deleted', 'deleted_at', 'date_field']


# ==========================================
# 6. ADMIN BATAS KECAMATAN
# ==========================================
@admin.register(BatasKecamatan)
class BatasKecamatanAdmin(SoftDeleteAdminMixin, admin.GISModelAdmin):
    list_display = ['uuid', 'kecamatan', 'kd_kcmtan', 'tipe', 'is_deleted']
    list_filter = ['is_deleted']
    search_fields = ['kecamatan', 'kd_kcmtan']
    readonly_fields = ['uuid', 'is_deleted', 'deleted_at']