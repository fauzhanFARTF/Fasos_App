from django.contrib.gis import admin
from django.contrib.auth.admin import UserAdmin
from .models import OPD, CustomUser, MedicalFacility, CCTVFacility, DistrictOfficeFacility, BatasKecamatan

@admin.register(OPD)
class OPDAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'kode', 'nama']
    readonly_fields = ['uuid']
    search_fields = ['nama', 'kode']
    ordering = ['kode']

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['uuid', 'username', 'email', 'opd', 'role', 'is_staff']
    readonly_fields = ['uuid']
    fieldsets = UserAdmin.fieldsets + (('OPD & Role', {'fields': ('opd', 'role')}),)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'opd', 'role'),
        }),
    )

@admin.register(MedicalFacility)
class MedicalFacilityAdmin(admin.GISModelAdmin):
    gis_widget_kwargs = {"attrs": {"default_lon": 106.8, "default_lat": -6.2, "default_zoom": 10}}
    list_display = ['uuid', 'nama', 'tipe', 'status', 'operator']
    readonly_fields = ['uuid']

@admin.register(DistrictOfficeFacility)
class DistrictOfficeFacilityAdmin(admin.GISModelAdmin):
    gis_widget_kwargs = {"attrs": {"default_lon": 106.8, "default_lat": -6.2, "default_zoom": 10}}
    list_display = ['uuid', 'nama', 'tipe', 'status', 'operator']
    readonly_fields = ['uuid']

@admin.register(CCTVFacility)
class CCTVFacilityAdmin(admin.GISModelAdmin):
    gis_widget_kwargs = {"attrs": {"default_lon": 106.8, "default_lat": -6.2, "default_zoom": 10}}
    list_display = ['uuid', 'kode_cam', 'nama_lokasi', 'wilayah', 'is_active', 'operator']
    readonly_fields = ['uuid']

@admin.register(BatasKecamatan)
class BatasKecamatanAdmin(admin.GISModelAdmin):
    list_display = ['uuid', 'kecamatan', 'kd_kcmtan', 'tipe']
    readonly_fields = ['uuid']