from django.db import models
from utils.model_validators import validate_danfe, save_danfe
from project import settings


class Danfe(models.Model):
    class Meta:
        verbose_name = 'DANFE'
        verbose_name_plural = 'DANFEs'

    arquivo_pdf = models.FileField(
        upload_to='pdf/%Y/%m', 
        max_length=255, 
        verbose_name='DANFE em PDF',
        help_text='Arquivo PDF da DANFE',
        validators=[validate_danfe],
    )
    slug = models.SlugField(unique=True, max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    created_day = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.slug = self.arquivo_pdf.name
        if settings.DEBUG:
            print(f"\n\U00002705 Saving {self.arquivo_pdf.name}")
        save_danfe(self.arquivo_pdf)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):                    
        if settings.DEBUG:
            print(f"\n\U0000274C Deleting {self.arquivo_pdf.name}")
        self.arquivo_pdf.delete(save=False)
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.arquivo_pdf.name

