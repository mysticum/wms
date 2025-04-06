from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Document
from .services import DocumentService


@receiver(pre_save, sender=Document)
def prepare_document(sender, instance, **kwargs):
    """
    Signal handler to prepare a document before saving
    - Sets document number
    - Generates barcode
    - Sets initial status if needed
    """
    # Only run for new documents
    if not instance.pk:
        DocumentService.prepare_document_for_save(instance)


@receiver(post_save, sender=Document)
def set_document_initial_status(sender, instance, created, **kwargs):
    """
    Signal handler to set the initial status after document creation
    """
    if created:
        # Set initial status in the status history
        DocumentService.set_initial_status(instance, instance.created_by)
