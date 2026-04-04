# fasos/admin.py
import json
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from django.contrib.admin import SimpleListFilter
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon
from .models import OPD, CustomUser, MedicalFacility, CCTVFacility, DistrictOfficeFacility, BatasKecamatan
from .widgets import SearchableLeafletWidget
from django import forms


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


# ✅ 1. BUAT CUSTOM FORM
class MedicalFacilityForm(forms.ModelForm):
    class Meta:
        model = MedicalFacility
        fields = '__all__'

    class Media:
        # ✅ Load JS yang baru dibuat
        js = ('fasos/js/medical_facility_admin.js',)

    def clean(self):
        """
        ✅ Validasi Server-Side:
        Memastikan Jenis & Tingkatan otomatis menjadi '-' jika Tipe bukan Rumah Sakit.
        Ini mencegah data tidak konsisten jika user bypass JS.
        """
        cleaned_data = super().clean()
        tipe = cleaned_data.get('tipe')
        
        if tipe != 'Rumah Sakit':
            cleaned_data['jenis'] = '-'
            cleaned_data['tingkatan'] = '-'
            
        return cleaned_data



# ==========================================
# CUSTOM FILTER: DEFAULT KE "NO" (AKTIF)
# ==========================================
class ActiveStatusFilter(SimpleListFilter):
    """
    Filter kustom yang default-nya menampilkan data Aktif (is_deleted=False).
    User tetap bisa klik 'Terhapus' untuk melihat data soft delete.
    """
    title = 'Status Data'
    parameter_name = 'is_deleted'

    def lookups(self, request, model_admin):
        return (
            ('no', 'Aktif (No)'),
            ('yes', 'Terhapus (Yes)'),
            ('all', 'Semua Data'),
        )

    def queryset(self, request, queryset):
        # Jika tidak ada parameter filter di URL (default load), tampilkan yang Aktif saja
        if self.value() is None:
            return queryset.filter(is_deleted=False)
        
        if self.value() == 'no':
            return queryset.filter(is_deleted=False)
        if self.value() == 'yes':
            return queryset.filter(is_deleted=True)
        if self.value() == 'all':
            return queryset
        return queryset


# ==========================================
# MIXIN: SOFT DELETE ADMIN
# ==========================================
class SoftDeleteAdminMixin:
    # ✅ Gunakan Custom Filter di sini agar berlaku global
    list_filter = [ActiveStatusFilter]
    actions = [soft_delete_selected, restore_selected, hard_delete_selected]

    def get_queryset(self, request):
        # Tetap return with_deleted() agar filter 'Yes' bisa berfungsi
        return self.model.objects.with_deleted()


# ==========================================
# MIXIN: UUID DISPLAY & TIMESTAMPS
# ==========================================
class UUIDTimestampMixin:
    """Mixin untuk menampilkan UUID creator, OPD, dan Timestamp di Admin"""
    
    def created_by_uuid(self, obj):
        return obj.created_by.uuid if obj.created_by else "-"
    created_by_uuid.short_description = "Created By (UUID)"
    created_by_uuid.admin_order_field = 'created_by__uuid'
    
    def opd_uuid(self, obj):
        return obj.opd.uuid if obj.opd else "-"
    opd_uuid.short_description = "OPD (UUID)"
    opd_uuid.admin_order_field = 'opd__uuid'
    
    def created_by_detail(self, obj):
        if obj.created_by:
            return f"{obj.created_by.username} ({obj.created_by.email})\nUUID: {obj.created_by.uuid}"
        return "System / Unknown"
    created_by_detail.short_description = "Creator Information"


# ==========================================
# 1. ADMIN OPD (MASTER OPD)
# ==========================================
@admin.register(OPD)
class OPDAdmin(SoftDeleteAdminMixin, UUIDTimestampMixin, admin.ModelAdmin):
    list_display = ['uuid', 'kode', 'nama', 'created_by_uuid', 'created_at', 'updated_at', 'is_deleted']
    
    readonly_fields = [
        'uuid', 'created_by', 'created_by_detail', 'created_at', 'updated_at', 'is_deleted', 'deleted_at'
    ]
    fields = ['nama', 'kode']
    search_fields = ['nama', 'kode']
    ordering = ['kode']

    def has_add_permission(self, request): return request.user.is_superuser
    def has_change_permission(self, request, obj=None): return request.user.is_superuser
    def has_delete_permission(self, request, obj=None): return request.user.is_superuser
    def has_module_permission(self, request): return request.user.is_superuser

    def save_model(self, request, obj, form, change):
        if not obj.pk: obj.created_by = request.user
        super().save_model(request, obj, form, change)


# ==========================================
# 2. ADMIN CUSTOM USER (MANAJEMEN USER)
# ==========================================
@admin.register(CustomUser)
class CustomUserAdmin(SoftDeleteAdminMixin, UUIDTimestampMixin, UserAdmin):
    model = CustomUser
    list_display = ['uuid', 'username', 'email', 'opd_uuid', 'role', 'created_by_uuid', 'created_at', 'updated_at', 'is_staff', 'is_active', 'is_deleted']
    
    readonly_fields = [
        'uuid', 'last_login', 'date_joined', 'created_by', 'created_by_detail', 'created_at', 'updated_at', 'is_deleted', 'deleted_at'
    ]

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('OPD & Role', {'fields': ('opd', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )

    def get_queryset(self, request):
        qs = CustomUser.objects.with_deleted().select_related('created_by', 'opd')
        if request.user.is_superuser: return qs
        if request.user.is_authenticated and request.user.opd:
            return qs.filter(opd=request.user.opd)
        return qs.none()

    def get_add_fieldsets(self, request):
        if request.user.is_superuser:
            return (
                (None, {
                    'classes': ('wide',),
                    'fields': ('username', 'email', 'password1', 'password2', 'opd', 'role'),
                }),
            )
        return (
            (None, {
                'classes': ('wide',),
                'fields': ('username', 'email', 'password1', 'password2', 'role'),
            }),
        )

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return self.get_add_fieldsets(request)
        if request.user.is_superuser:
            return self.fieldsets
        
        fieldsets_list = []
        for name, opts in self.fieldsets:
            fields = list(opts.get('fields', []))
            if 'opd' in fields:
                fields.remove('opd')
                fieldsets_list.append((name, {'fields': fields}))
                fieldsets_list.append(('OPD (Tidak dapat diubah)', {
                    'fields': ('opd',), 'classes': ('collapse',)
                }))
            else:
                fieldsets_list.append((name, opts))
        return tuple(fieldsets_list)

    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        if obj and not request.user.is_superuser:
            if 'opd' not in readonly: readonly.append('opd')
            if request.user.role != 'admin':
                readonly.extend(['username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff'])
        return tuple(readonly)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and request.user.opd:
            obj.opd = request.user.opd
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
        if not change and obj.opd:
            self.message_user(request, f"User {obj.username} berhasil dibuat untuk OPD: {obj.opd.nama}", level=messages.SUCCESS)

    def has_add_permission(self, request):
        if request.user.is_superuser: return True
        return request.user.is_authenticated and request.user.role == 'admin'

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser: return True
        if not request.user.is_authenticated: return False
        if obj is None: return request.user.role in ['admin', 'editor', 'viewer']
        if request.user.role == 'admin' and hasattr(obj, 'opd') and obj.opd == request.user.opd: return True
        if request.user.role in ['editor', 'viewer'] and obj.id == request.user.id: return True
        return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser: return True
        return request.user.is_authenticated and request.user.role == 'admin'
    
    def has_module_permission(self, request):
        if request.user.is_superuser: return True
        return request.user.is_authenticated and request.user.role in ['admin', 'editor', 'viewer']


# ==========================================
# MIXIN: OPD PERMISSION (UNTUK FACILITIES)
# ==========================================
class OPDPermissionMixin:
    ALLOWED_FACILITY_MODELS = {
        'DINKES': ['MedicalFacility'],
        'DISKOMINFO': ['CCTVFacility'],
        'SETDA': ['DistrictOfficeFacility'],
    }

    def has_module_permission(self, request):
        if request.user.is_superuser: return True
        user = request.user
        if not user.is_authenticated or not hasattr(user, 'opd') or not user.opd:
            return False
        model_name = self.model.__name__
        if model_name in ['OPD', 'CustomUser']:
            return user.role in ['admin', 'editor']
        allowed = self.ALLOWED_FACILITY_MODELS.get(user.opd.kode, [])
        return model_name in allowed

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('created_by')
        if request.user.is_superuser: return qs
        if request.user.is_authenticated and request.user.opd:
            return qs.filter(created_by__opd=request.user.opd)
        return qs.none()

    def save_model(self, request, obj, form, change):
        if not obj.pk: obj.created_by = request.user
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
# 3. ADMIN MEDICAL FACILITY (DINKES)
# ==========================================
@admin.register(MedicalFacility)
class MedicalFacilityAdmin(OPDPermissionMixin, SoftDeleteAdminMixin, UUIDTimestampMixin, admin.ModelAdmin):
    list_display = ['uuid', 'nama', 'tipe', 'status', 'created_by_uuid', 'created_at', 'updated_at', 'is_deleted']
    list_filter = [ActiveStatusFilter, 'status', 'tipe']
    search_fields = ['nama', 'koderumahsakit']
    readonly_fields = ['uuid', 'created_by', 'created_by_detail', 'created_at', 'updated_at', 'is_deleted', 'deleted_at', 'date_field']

    # ✅ 2. ASSIGN FORM CUSTOM KE ADMIN
    form = MedicalFacilityForm

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'location':
            kwargs['widget'] = SearchableLeafletWidget
        return super().formfield_for_dbfield(db_field, request, **kwargs)


# ==========================================
# 4. ADMIN DISTRICT OFFICE FACILITY (SETDA)
# ==========================================
@admin.register(DistrictOfficeFacility)
class DistrictOfficeFacilityAdmin(OPDPermissionMixin, SoftDeleteAdminMixin, UUIDTimestampMixin, admin.ModelAdmin):
    list_display = ['uuid', 'nama', 'tipe', 'status', 'created_by_uuid', 'created_at', 'updated_at', 'is_deleted']
    # ✅ Ganti 'is_deleted' dengan ActiveStatusFilter
    list_filter = [ActiveStatusFilter, 'status', 'tipe']
    search_fields = ['nama']
    readonly_fields = ['uuid', 'created_by', 'created_by_detail', 'created_at', 'updated_at', 'is_deleted', 'deleted_at', 'date_field']

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'location': kwargs['widget'] = SearchableLeafletWidget
        return super().formfield_for_dbfield(db_field, request, **kwargs)


# ==========================================
# 5. ADMIN CCTV FACILITY (DISKOMINFO)
# ==========================================
@admin.register(CCTVFacility)
class CCTVFacilityAdmin(OPDPermissionMixin, SoftDeleteAdminMixin, UUIDTimestampMixin, admin.ModelAdmin):
    list_display = ['uuid', 'kode_cam', 'nama_lokasi', 'wilayah', 'is_active', 'created_by_uuid', 'created_at', 'updated_at', 'is_deleted']
    # ✅ Ganti 'is_deleted' dengan ActiveStatusFilter
    list_filter = [ActiveStatusFilter, 'is_active', 'wilayah']
    search_fields = ['kode_cam', 'nama_lokasi']
    readonly_fields = ['uuid', 'created_by', 'created_by_detail', 'created_at', 'updated_at', 'is_deleted', 'deleted_at', 'date_field']

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'location': kwargs['widget'] = SearchableLeafletWidget
        return super().formfield_for_dbfield(db_field, request, **kwargs)


# ==========================================
# 6. ADMIN BATAS KECAMATAN (DTRB ONLY - UPLOAD ONLY)
# ==========================================
@admin.register(BatasKecamatan)
class BatasKecamatanAdmin(SoftDeleteAdminMixin, UUIDTimestampMixin, admin.ModelAdmin):
    list_display = ['uuid', 'kecamatan', 'kd_kcmtan', 'tipe', 'created_by_uuid', 'created_at', 'updated_at', 'is_deleted']
    # ✅ Hapus list_filter manual agar mewarisi ActiveStatusFilter dari Mixin
    # list_filter = ['is_deleted'] <-- HAPUS BARIS INI
    search_fields = ['kecamatan', 'kd_kcmtan']
    readonly_fields = ['uuid', 'created_by', 'created_by_detail', 'created_at', 'updated_at', 'is_deleted', 'deleted_at']
    fields = ['geojson_file']

    def has_module_permission(self, request):
        if request.user.is_superuser: return True
        user = request.user
        if not user.is_authenticated or not hasattr(user, 'opd') or not user.opd:
            return False
        return user.opd.kode == 'DTRB' or user.role in ['admin', 'editor']

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('created_by')
        if request.user.is_superuser: return qs
        if request.user.is_authenticated and hasattr(request.user, 'opd') and request.user.opd:
            if request.user.opd.kode == 'DTRB': return qs
        return qs.none()

    def has_add_permission(self, request):
        if request.user.is_superuser: return True
        return request.user.is_authenticated and request.user.opd and request.user.opd.kode == 'DTRB' and request.user.role in ['admin', 'editor']

    def has_change_permission(self, request, obj=None): return self.has_add_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser: return True
        return request.user.is_authenticated and request.user.opd and request.user.opd.kode == 'DTRB' and request.user.role == 'admin'

    def save_model(self, request, obj, form, change):
        if not obj.pk: obj.created_by = request.user
        if obj.geojson_file and not change:
            try:
                data = json.loads(obj.geojson_file.read())
                if data.get('type') == 'FeatureCollection':
                    count = 0
                    for feature in data.get('features', []):
                        props = feature.get('properties', {})
                        geom_data = feature.get('geometry')
                        if geom_data and props:
                            kec_name = props.get('KECAMATAN', props.get('kecamatan', 'Unknown'))
                            kd_kcmtan = props.get('KD_KCMTAN', props.get('kd_kcmtan', ''))
                            if kd_kcmtan:
                                geom = GEOSGeometry(json.dumps(geom_data), srid=4326)
                                if geom.geom_type == 'Polygon': geom = MultiPolygon(geom, srid=4326)
                                BatasKecamatan.objects.update_or_create(
                                    kd_kcmtan=kd_kcmtan,
                                    defaults={'kecamatan': kec_name, 'geom': geom, 'tipe': 'Kecamatan', 'created_by': request.user}
                                )
                                count += 1
                    self.message_user(request, f"✅ Berhasil mengimpor {count} data kecamatan.", level=messages.SUCCESS)
                else:
                    self.message_user(request, "❌ Format GeoJSON salah.", level=messages.ERROR)
            except Exception as e:
                self.message_user(request, f"❌ Error: {str(e)}", level=messages.ERROR)
            return
        super().save_model(request, obj, form, change)