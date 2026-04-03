# fasos/managers.py
from django.db import models
from django.utils import timezone

class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        """Override delete() pada QuerySet untuk soft delete massal"""
        return self.update(is_deleted=True, deleted_at=timezone.now())

    def hard_delete(self):
        """Hapus permanen dari database"""
        return super().delete()

    def with_deleted(self):
        """Sertakan data yang sudah di-soft delete"""
        return super().get_queryset()

    def only_deleted(self):
        """Hanya tampilkan data yang sudah di-soft delete"""
        return super().get_queryset().filter(is_deleted=True)

    def restore(self):
        """Restore semua data di QuerySet"""
        return self.update(is_deleted=False, deleted_at=None)


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        """Default: hanya tampilkan data aktif"""
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=False)

    def with_deleted(self):
        return self.get_queryset().with_deleted()

    def only_deleted(self):
        return self.get_queryset().only_deleted()