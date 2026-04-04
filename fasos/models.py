# fasos/models.py
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models as gis_models
from django.conf import settings
from django.utils import timezone
from .managers import SoftDeleteManager, SoftDeleteUserManager


# ==========================================
# 1. MASTER OPD
# ==========================================
class OPD(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    nama = models.CharField(max_length=100)
    kode = models.CharField(max_length=20, unique=True)
    
    # ✅ ForeignKey dengan db_column='created_by_uuid'
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='created_opds',
        db_column='created_by_uuid',  # ✅ Nama kolom database
        to_field='uuid'  # ✅ Referensi ke field uuid, bukan id
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True, editable=False)
    objects = SoftDeleteManager()

    class Meta:
        verbose_name = "Organisasi Perangkat Daerah"
        verbose_name_plural = "Master OPD"
        ordering = ['kode']

    def __str__(self): return f"{self.kode} - {self.nama}"
    def delete(self, *args, **kwargs):
        self.is_deleted = True; self.deleted_at = timezone.now(); self.save(update_fields=['is_deleted', 'deleted_at'])
    def hard_delete(self, *args, **kwargs): super().delete(*args, **kwargs)
    def restore(self): self.is_deleted = False; self.deleted_at = None; self.save(update_fields=['is_deleted', 'deleted_at'])


# ==========================================
# 2. CUSTOM USER
# ==========================================
class CustomUser(AbstractUser):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    ROLE_CHOICES = [('admin', 'Admin'), ('editor', 'Editor'), ('viewer', 'Viewer')]
    
    # ✅ ForeignKey dengan db_column='opd_uuid'
    opd = models.ForeignKey(
        OPD, 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True, 
        related_name='users',
        db_column='opd_uuid',  # ✅ Nama kolom database
        to_field='uuid'  # ✅ Referensi ke field uuid
    )
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='viewer')
    
    # ✅ ForeignKey dengan db_column='created_by_uuid'
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='created_users',
        db_column='created_by_uuid',  # ✅ Nama kolom database
        to_field='uuid'  # ✅ Referensi ke field uuid
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True, editable=False)
    objects = SoftDeleteUserManager()

    class Meta:
        verbose_name = "User Sistem"
        verbose_name_plural = "Manajemen User"
        ordering = ['username']

    def __str__(self): return f"{self.username} ({self.opd.kode if self.opd else 'No OPD'})"
    def delete(self, *args, **kwargs):
        self.is_deleted = True; self.deleted_at = timezone.now(); self.save(update_fields=['is_deleted', 'deleted_at'])
    def hard_delete(self, *args, **kwargs): super().delete(*args, **kwargs)
    def restore(self): self.is_deleted = False; self.deleted_at = None; self.save(update_fields=['is_deleted', 'deleted_at'])


# ==========================================
# 3. FASILITAS KESEHATAN (DINKES)
# ==========================================
class MedicalFacility(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    
    TYPE_CHOICES = [('Rumah Sakit', 'Rumah Sakit'), ('Puskesmas', 'Puskesmas'), ('Klinik', 'Klinik'), ('Apotik', 'Apotik')]
    SPESIFIC_CHOICES = [('Rumah Sakit Umum', 'Rumah Sakit Umum'), ('Rumah Sakit Khusus', 'Rumah Sakit Khusus'), ('-', '-')]
    STATUS_CHOICES = [
        ('Perencanaan/Pengajuan', 'Perencanaan/Pengajuan'), ('Dalam Masa Peninjauan', 'Dalam Masa Peninjauan'),
        ('Perencanaan Dibatalkan', 'Perencanaan Dibatalkan'), ('Dalam Masa Pembangunan', 'Dalam Masa Pembangunan'),
        ('Pembangunan Selesai/Belum Beroperasi', 'Pembangunan Selesai/Belum Beroperasi'),
        ('Pembangunan Selesai/Sudah Beroperasi', 'Pembangunan Selesai/Sudah Beroperasi'),
        ('Tutup/Sudah Tidak Beroperasi', 'Tutup/Sudah Tidak Beroperasi')
    ]
    LEVEL_CHOICES = [('Kelas A', 'Kelas A'), ('Kelas B', 'Kelas B'), ('Kelas C', 'Kelas C'), ('Belum Mengisi Tingkatan', 'Belum Mengisi Tingkatan'), ('-', '-')]
    DAYS_CHOICES = [('Setiap Hari', 'Setiap Hari'), ('Senin - Jumat', 'Senin - Jumat'), ('Sabtu - Minggu', 'Sabtu - Minggu')]
    OWNERSHIP_STATUS_CHOICES = [('Dikelola Pemerintah', 'Dikelola Pemerintah'), ('Dikelola Swasta', 'Dikelola Swasta'), ('Dikelola Organisasi Sosial', 'Dikelola Organisasi Sosial'), ('Belum Mengisi Penyelenggara', 'Belum Mengisi Penyelenggara'), ('-', '-')]
    
    koderumahsakit = models.CharField(max_length=10)
    nama = models.CharField(max_length=150)
    tipe = models.CharField(max_length=50, choices=TYPE_CHOICES, default='Rumah Sakit')
    jenis = models.CharField(max_length=50, choices=SPESIFIC_CHOICES, default='Rumah Sakit Umum')
    tingkatan = models.CharField(max_length=50, choices=LEVEL_CHOICES, default='Belum Mengisi Tingkatan')
    kepemilikan = models.CharField(max_length=50, choices=OWNERSHIP_STATUS_CHOICES, default='Belum Mengisi Penyelenggara')
    alamat = models.TextField(max_length=255)
    no_telp = models.CharField(max_length=50)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Perencanaan/Pengajuan')
    hari_beroperasi = models.CharField(max_length=50, choices=DAYS_CHOICES, default='Setiap Hari')
    jam_beroperasi = models.CharField(max_length=50)
    location = gis_models.PointField(srid=4326, spatial_index=True)
    photo = models.ImageField(upload_to='medical_facility/', null=True, blank=True)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='created_medical_facilities',
        db_column='created_by_uuid',
        to_field='uuid'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    date_field = models.DateTimeField(auto_now=True)
    
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True, editable=False)
    objects = SoftDeleteManager()

    class Meta:
        verbose_name = "Fasilitas Kesehatan"
        verbose_name_plural = "Data Faskes (Dinkes)"
        ordering = ['-date_field']

    def __str__(self): return f"{self.nama} ({self.koderumahsakit})"
    def delete(self, *args, **kwargs):
        self.is_deleted = True; self.deleted_at = timezone.now(); self.save(update_fields=['is_deleted', 'deleted_at'])
    def hard_delete(self, *args, **kwargs): super().delete(*args, **kwargs)
    def restore(self): self.is_deleted = False; self.deleted_at = None; self.save(update_fields=['is_deleted', 'deleted_at'])


# ==========================================
# 4. KANTOR PEMERINTAH DAERAH (SETDA)
# ==========================================
class DistrictOfficeFacility(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    
    STATUS_CHOICES = [
        ('Perencanaan/Pengajuan', 'Perencanaan/Pengajuan'), ('Dalam Masa Peninjauan', 'Dalam Masa Peninjauan'),
        ('Perencanaan Dibatalkan', 'Perencanaan Dibatalkan'), ('Dalam Masa Pembangunan', 'Dalam Masa Pembangunan'),
        ('Pembangunan Selesai/Belum Beroperasi', 'Pembangunan Selesai/Belum Beroperasi'),
        ('Pembangunan Selesai/Sudah Beroperasi', 'Pembangunan Selesai/Sudah Beroperasi'),
        ('Tutup/Sudah Tidak Beroperasi', 'Tutup/Sudah Tidak Beroperasi')
    ]
    DAYS_CHOICES = [('Setiap Hari', 'Setiap Hari'), ('Senin - Jumat', 'Senin - Jumat'), ('Sabtu - Minggu', 'Sabtu - Minggu')]
    SPESIFIC_CHOICES = [('Perangkat Daerah', 'Perangkat Daerah'), ('Instansi Vertikal', 'Instansi Vertikal')]
    
    nama = models.CharField(max_length=150)
    tipe = models.CharField(max_length=50, choices=SPESIFIC_CHOICES, default='Perangkat Daerah')
    alamat = models.TextField(max_length=255)
    no_telp = models.CharField(max_length=50)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Perencanaan/Pengajuan')
    hari_beroperasi = models.CharField(max_length=50, choices=DAYS_CHOICES)
    jam_beroperasi = models.CharField(max_length=50)
    location = gis_models.PointField(srid=4326, spatial_index=True)
    photo = models.ImageField(upload_to='local_government_office/', null=True, blank=True)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='created_district_offices',
        db_column='created_by_uuid',
        to_field='uuid'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    date_field = models.DateTimeField(auto_now=True)
    
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True, editable=False)
    objects = SoftDeleteManager()

    class Meta:
        verbose_name = "Kantor Pemerintahan Daerah"
        verbose_name_plural = "Data Kantor Pemda (Setda)"
        ordering = ['-date_field']

    def __str__(self): return self.nama
    def delete(self, *args, **kwargs):
        self.is_deleted = True; self.deleted_at = timezone.now(); self.save(update_fields=['is_deleted', 'deleted_at'])
    def hard_delete(self, *args, **kwargs): super().delete(*args, **kwargs)
    def restore(self): self.is_deleted = False; self.deleted_at = None; self.save(update_fields=['is_deleted', 'deleted_at'])


# ==========================================
# 5. CCTV MONITORING (DISKOMINFO)
# ==========================================
class CCTVFacility(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    
    STATUS_CHOICES = [
        ('Perencanaan/Pengajuan', 'Perencanaan/Pengajuan'), ('Dalam Masa Peninjauan', 'Dalam Masa Peninjauan'),
        ('Perencanaan Dibatalkan', 'Perencanaan Dibatalkan'), ('Dalam Masa Pembangunan', 'Dalam Masa Pembangunan'),
        ('Pembangunan Selesai/Belum Beroperasi', 'Pembangunan Selesai/Belum Beroperasi'),
        ('Pembangunan Selesai/Sudah Beroperasi', 'Pembangunan Selesai/Sudah Beroperasi'),
        ('Tutup/Sudah Tidak Beroperasi', 'Tutup/Sudah Tidak Beroperasi')
    ]
    DAYS_CHOICES = [('Setiap Hari', 'Setiap Hari'), ('Senin - Jumat', 'Senin - Jumat'), ('Sabtu - Minggu', 'Sabtu - Minggu')]
    SPESIFIC_CHOICES = [
        ('Perangkat Keamanan Pemerintah Daerah - CCTV', 'Perangkat Keamanan Pemerintah Daerah- CCTV'),
        ('Perangkat Keamanan Instansi Vertikal - CCTV', 'Perangkat Keamanan Instansi Vertikal- CCTV')
    ]
    WILAYAH = [
        ('Polsek Balaraja', 'Polsek Balaraja'), ('Polsek Kresek', 'Polsek Kresek'), ('Polsek Mauk', 'Polsek Mauk'),
        ('Polsek Kronjo', 'Polsek Kronjo'), ('Polsek Pasar Kemis', 'Polsek Pasar Kemis'), ('Polsek Tigaraksa', 'Polsek Tigaraksa'),
        ('Polsek Panongan', 'Polsek Panongan'), ('Polsek Cikupa', 'Polsek Cikupa'), ('Polsek Cisoka', 'Polsek Cisoka'),
        ('Polresta Tangerang', 'Polresta Tangerang')
    ]
    
    kode_cam = models.CharField(max_length=50)
    nama_lokasi = models.TextField(max_length=150)
    tipe = models.CharField(max_length=50, choices=SPESIFIC_CHOICES, default='Perangkat Keamanan Pemerintah Daerah - CCTV')
    wilayah = models.CharField(max_length=100, choices=WILAYAH, default='Polresta Tangerang')
    sn_camera = models.CharField(max_length=100)
    sn_modem = models.CharField(max_length=100)
    tgl_pemasangan = models.DateField()
    is_active = models.BooleanField(default=False)
    location = gis_models.PointField(srid=4326, spatial_index=True)
    photo = models.ImageField(upload_to='cctv_etle/', null=True, blank=True)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='created_cctv_facilities',
        db_column='created_by_uuid',
        to_field='uuid'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    date_field = models.DateTimeField(auto_now=True)
    
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True, editable=False)
    objects = SoftDeleteManager()

    class Meta:
        verbose_name = "CCTV Monitoring"
        verbose_name_plural = "Data CCTV (Diskominfo)"
        ordering = ['-date_field']

    def __str__(self): return f"{self.kode_cam} - {self.nama_lokasi}"
    def delete(self, *args, **kwargs):
        self.is_deleted = True; self.deleted_at = timezone.now(); self.save(update_fields=['is_deleted', 'deleted_at'])
    def hard_delete(self, *args, **kwargs): super().delete(*args, **kwargs)
    def restore(self): self.is_deleted = False; self.deleted_at = None; self.save(update_fields=['is_deleted', 'deleted_at'])


# ==========================================
# 6. BATAS KECAMATAN (SPATIAL POLYGON - DTRB ONLY)
# ==========================================
class BatasKecamatan(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    kecamatan = models.CharField(max_length=150)
    kd_kcmtan = models.CharField(max_length=20, unique=True)
    tipe = models.CharField(max_length=20, default='Kecamatan')
    
    geom = gis_models.MultiPolygonField(srid=4326, spatial_index=True)
    geojson_file = models.FileField(upload_to='geojson_uploads/', null=True, blank=True,
                                    help_text="Upload file .geojson (Format: FeatureCollection)")
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='created_kecamatans',
        db_column='created_by_uuid',
        to_field='uuid'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True, editable=False)
    objects = SoftDeleteManager()

    class Meta:
        verbose_name = "Batas Kecamatan"
        verbose_name_plural = "Data Spasial Kecamatan (DTRB)"
    
    def __str__(self): return f"{self.kecamatan} ({self.kd_kcmtan})"
    def delete(self, *args, **kwargs):
        self.is_deleted = True; self.deleted_at = timezone.now(); self.save(update_fields=['is_deleted', 'deleted_at'])
    def hard_delete(self, *args, **kwargs): super().delete(*args, **kwargs)
    def restore(self): self.is_deleted = False; self.deleted_at = None; self.save(update_fields=['is_deleted', 'deleted_at'])