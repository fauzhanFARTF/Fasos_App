from django.contrib import admin
from django.contrib.gis import admin
from .models import MedicalFacility

# Register your models here.
@admin.register(MedicalFacility)
class MedicalFacilityAdmin(admin.OSMGeoAdmin):
    default_zoom = 10
    list_filter = ['status', 'jenis', 'tingkatan']
    list_display = ['nama', 'jenis', 'tingkatan', 'status', 'operator', 'created_at']
    search_fields = ['nama', 'alamat']