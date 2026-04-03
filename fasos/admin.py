# from django.contrib import admin
from django.contrib.gis import admin
from .models import MedicalFacility

@admin.register(MedicalFacility)
class MedicalFacilityAdmin(admin.GISModelAdmin):
    # Konfigurasi tampilan peta default
    gis_widget_kwargs = {
        "attrs": {
            "default_lon": 106.8,
            "default_lat": -6.2,
            "default_zoom": 10
        }
    }
    list_filter = ['status', 'jenis', 'tingkatan']
    list_display = ['nama', 'jenis', 'tingkatan', 'status', 'operator', 'created_at']
    search_fields = ['nama', 'alamat']