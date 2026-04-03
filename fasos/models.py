from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models as gis_models
from django.conf import settings

# Create your models here.

# ==========================================
# 1. MASTER OPD & CUSTOM USER (WAJIB ADA)
# ==========================================
class OPD(models.Model):
    nama = models.CharField(max_length=100)
    kode = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return f"{self.kode} - {self.nama}"

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('editor', 'Editor'),
        ('viewer', 'Viewer'),
    ]
    opd = models.ForeignKey(
        OPD, 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True, 
        related_name='users'
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='viewer')
    
    def __str__(self):
        return f"{self.username} ({self.opd.kode if self.opd else 'No OPD'})"

# ==========================================
# 2. DATA FASILITAS KES (GIS)
# ==========================================
class MedicalFacility(models.Model):
    TYPE_CHOICES = [
        ('Rumah Sakit', 'Rumah Sakit'),
        ('Puskesmas', 'Puskesmas'),
        ('Klinik', 'Klinik'),
        ('Apotik', 'Apotik')
    ]
    STATUS_CHOICES = [
        ('Perencanaan/Pengajuan', 'Perencanaan/Pengajuan'),
        ('Dalam Masa Peninjauan', 'Dalam Masa Peninjauan'),
        ('Perencanaan Dibatalkan', 'Perencanaan Dibatalkan'),
        ('Dalam Masa Pembangunan', 'Dalam Masa Pembangunan'),
        ('Pembangunan Selesai/Belum Beroperasi', 'Pembangunan Selesai/Belum Beroperasi'),
        ('Pembangunan Selesai/Sudah Beroperasi', 'Pembangunan Selesai/Sudah Beroperasi'),
        ('Tutup/Sudah Tidak Beroperasi', 'Tutup/Sudah Tidak Beroperasi')
    ]
    LEVEL_CHOICES = [
        ('Fasilitas Kesehatan Tingkat 1', 'Fasilitas Kesehatan Tingkat 1'),
        ('Fasilitas Kesehatan Tingkat 2', 'Fasilitas Kesehatan Tingkat 2'),
        ('Fasilitas Kesehatan Tingkat 3', 'Fasilitas Kesehatan Tingkat 3')
    ]
    DAYS_CHOICES = [
        ('Setiap Hari', 'Setiap Hari'),
        ('Senin - Jumat', 'Senin - Jumat'),
        ('Sabtu - Minggu', 'Sabtu - Minggu')
    ]

    nama = models.CharField(max_length=100)
    jenis = models.CharField(max_length=50, choices=TYPE_CHOICES, default='Rumah Sakit')
    tingkatan = models.CharField(max_length=100, choices=LEVEL_CHOICES)
    alamat = models.TextField(max_length=255)
    no_telp = models.CharField(max_length=50)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Perencanaan/Pengajuan')
    hari_beroperasi = models.CharField(max_length=50, choices=DAYS_CHOICES)
    jam_beroperasi = models.CharField(max_length=50)
    location = gis_models.PointField(srid=4326, spatial_index=True)
    photo = models.ImageField(upload_to='medical_facility/', null=True, blank=True)
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='facilities'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.nama} ({self.jenis})"