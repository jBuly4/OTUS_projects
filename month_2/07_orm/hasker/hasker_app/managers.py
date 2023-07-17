from django.db import models


class PublishedManager(models.Manager):
    def get_queryset(self):
        """Manager to be used in models with status fields."""
        return super().get_queryset().filter(status=self.model.Status.PUBLISHED)
