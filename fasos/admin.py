# from django.contrib import admin
from django.contrib.gis import admin
from .models import MedicalFacility, DistrictOfficeFacility, CCTVFacility, BatasKecamatan, OPD, CustomUser

# ==========================================
# 1. ADMIN OPD
# ==========================================
@admin.register(OPD)
class OPDAdmin(admin.ModelAdmin):
    list_display = ['kode', 'nama']
    search_fields = ['nama', 'kode']
    ordering = ['kode']

# ==========================================
# 2. ADMIN CUSTOM USER
# ==========================================
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'opd', 'role', 'is_staff']
    list_filter = ['opd', 'role', 'is_staff']
    search_fields = ['username', 'email']

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
        ('OPD & Role', {'fields': ('opd', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('username', 'email', 'opd', 'role', 'password1', 'password2')}),
    )

# ==========================================
# 3. ADMIN MEDICAL FACILITY (GIS)
# ==========================================
@admin.register(MedicalFacility)
class MedicalFacilityAdmin(admin.GISModelAdmin):
    gis_widget_kwargs = {"attrs": {"default_lon": 106.8, "default_lat": -6.2, "default_zoom": 10}}
    list_display = ['nama', 'tipe', 'status', 'operator']

# ==========================================
# 4. ADMIN DISTRICT OFFICE FACILITY (GIS)
# ==========================================

@admin.register(DistrictOfficeFacility)
class DistrictOfficeFacilityAdmin(admin.GISModelAdmin):
    gis_widget_kwargs = {"attrs": {"default_lon": 106.8, "default_lat": -6.2, "default_zoom": 10}}
    list_display = ['nama', 'tipe', 'status', 'operator']
    
# ==========================================
# 5. ADMINCCTV FACILITY (GIS)
# ==========================================

@admin.register(CCTVFacility)
class CCTVFacilityAdmin(admin.GISModelAdmin):
    gis_widget_kwargs = {"attrs": {"default_lon": 106.8, "default_lat": -6.2, "default_zoom": 10}}
    list_display = ['kode_cam', 'nama_lokasi', 'wilayah', 'is_active', 'operator']

# ==========================================
# 6. ADMIN BATAS KECAMATAN (GIS)
# ==========================================

@admin.register(BatasKecamatan)
class BatasKecamatanAdmin(admin.OSMGeoAdmin): # Note: PolygonField works fine with GISModelAdmin too
    list_display = ['kecamatan', 'kd_kcmtan', 'tipe']