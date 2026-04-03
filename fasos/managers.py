# fasos/managers.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import UserManager


class SoftDeleteQuerySet(models.QuerySet):
    """Custom QuerySet untuk soft delete functionality"""

    def delete(self):
        """Override delete() untuk soft delete massal"""
        return self.update(is_deleted=True, deleted_at=timezone.now())

    def hard_delete(self):
        """Hapus permanen dari database"""
        return super().delete()

    def with_deleted(self):
        """Sertakan data yang sudah di-soft delete"""
        return self._chain() if hasattr(self, '_chain') else self.filter(is_deleted=True) | self.filter(is_deleted=False)

    def only_deleted(self):
        """Hanya tampilkan data yang sudah di-soft delete"""
        return self.filter(is_deleted=True)

    def restore(self):
        """Restore semua data di QuerySet"""
        return self.update(is_deleted=False, deleted_at=None)


class SoftDeleteUserManager(UserManager):
    """
    Custom UserManager untuk CustomUser dengan soft delete.
    Inherit dari Django's UserManager agar kompatibel dengan createsuperuser & auth system.
    """

    def get_queryset(self):
        """Default: hanya tampilkan data aktif (is_deleted=False)"""
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=False)

    def with_deleted(self):
        """Sertakan data yang sudah di-soft delete"""
        return SoftDeleteQuerySet(self.model, using=self._db)

    def only_deleted(self):
        """Hanya tampilkan data yang sudah di-soft delete"""
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=True)


class SoftDeleteManager(models.Manager):
    """Custom Manager untuk model non-user dengan soft delete"""

    def get_queryset(self):
        """Default: hanya tampilkan data aktif (is_deleted=False)"""
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=False)

    def with_deleted(self):
        """Sertakan data yang sudah di-soft delete"""
        return SoftDeleteQuerySet(self.model, using=self._db)

    def only_deleted(self):
        """Hanya tampilkan data yang sudah di-soft delete"""
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=True)