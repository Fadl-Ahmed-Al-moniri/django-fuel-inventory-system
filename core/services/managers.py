from django.db import models

class ActiveManager(models.Manager):
    """
    A dedicated manager that returns only the active records (is_active=True).
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)