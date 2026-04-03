# fasos/admin.py
from django.contrib.gis import admin
from django.contrib.auth.admin import UserAdmin
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
# BASE ADMIN CLASS
# ==========================================
class SoftDeleteAdminMixin:
    list_display = ['uuid', 'is_deleted', 'deleted_at']
    list_filter = ['is_deleted']
    actions = [soft_delete_selected, restore_selected, hard_delete_selected]
    readonly_fields = ['uuid', 'is_deleted', 'deleted_at']

    def get_queryset(self, request):
        # Tampilkan semua data (aktif & terhapus) agar bisa di-restore
        return self.model.objects.with_deleted()

# ==========================================
# REGISTER MODELS
# ==========================================
@admin.register(OPD)
class OPDAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = ['uuid', 'kode', 'nama', 'is_deleted', 'deleted_at']
    search_fields = ['nama', 'kode']
    ordering = ['kode']
    readonly_fields = ['uuid']

@admin.register(CustomUser)
class CustomUserAdmin(SoftDeleteAdminMixin, UserAdmin):
    model = CustomUser
    list_display = ['uuid', 'username', 'email', 'opd', 'role', 'is_staff', 'is_deleted']
    readonly_fields = ['uuid', 'last_login', 'date_joined', 'is_deleted', 'deleted_at']
    fieldsets = UserAdmin.fieldsets + (('OPD & Role', {'fields': ('opd', 'role')}),)
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('username', 'email', 'password1', 'password2', 'opd', 'role')}),
    )
    def get_queryset(self, request):
        return self.model.objects.with_deleted()

@admin.register(MedicalFacility)
class MedicalFacilityAdmin(SoftDeleteAdminMixin, admin.GISModelAdmin):
    gis_widget_kwargs = {"attrs": {"default_lon": 106.8, "default_lat": -6.2, "default_zoom": 10}}
    list_display = ['uuid', 'nama', 'tipe', 'status', 'operator', 'is_deleted', 'date_field']
    list_filter = ['is_deleted', 'status', 'tipe']
    readonly_fields = ['uuid', 'operator', 'is_deleted', 'deleted_at']

@admin.register(DistrictOfficeFacility)
class DistrictOfficeFacilityAdmin(SoftDeleteAdminMixin, admin.GISModelAdmin):
    gis_widget_kwargs = {"attrs": {"default_lon": 106.8, "default_lat": -6.2, "default_zoom": 10}}
    list_display = ['uuid', 'nama', 'tipe', 'status', 'operator', 'is_deleted', 'date_field']
    list_filter = ['is_deleted', 'status', 'tipe']
    readonly_fields = ['uuid', 'operator', 'is_deleted', 'deleted_at']

@admin.register(CCTVFacility)
class CCTVFacilityAdmin(SoftDeleteAdminMixin, admin.GISModelAdmin):
    gis_widget_kwargs = {"attrs": {"default_lon": 106.8, "default_lat": -6.2, "default_zoom": 10}}
    list_display = ['uuid', 'kode_cam', 'nama_lokasi', 'wilayah', 'is_active', 'operator', 'is_deleted', 'date_field']
    list_filter = ['is_deleted', 'is_active', 'wilayah']
    readonly_fields = ['uuid', 'operator', 'is_deleted', 'deleted_at']

@admin.register(BatasKecamatan)
class BatasKecamatanAdmin(SoftDeleteAdminMixin, admin.GISModelAdmin):
    list_display = ['uuid', 'kecamatan', 'kd_kcmtan', 'tipe', 'is_deleted']
    list_filter = ['is_deleted']
    readonly_fields = ['uuid', 'is_deleted', 'deleted_at']