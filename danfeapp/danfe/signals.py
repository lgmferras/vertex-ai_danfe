from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Danfe

@receiver(post_delete, sender=Danfe)
def delete_file_on_danfe_delete(sender, instance, **kwargs):
    if instance.arquivo_pdf:
        instance.arquivo_pdf.delete(save=False)