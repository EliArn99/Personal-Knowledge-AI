from django.db.models.signals import (
    post_delete,
)
from django.dispatch import receiver

from .models import Document


@receiver(
    post_delete,
    sender=Document,
)
def delete_document_file(
    sender,
    instance,
    **kwargs,
):
    if instance.file:
        instance.file.delete(
            save=False
        )