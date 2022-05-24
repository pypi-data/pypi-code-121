from django.db import models
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _

class CustomUrl(models.Model):
    CONTENT_TYPES = [
        ('text/plain', 'Plain Text'),
        ('text/csv', 'CSV'),
        ('application/vnd.ms-excel', 'MS Excel'),
        ('application/msword', 'MS Word'),
        ('application/vnd.ms-powerpoint', 'MS PowerPoint'),
        ('image/gif', 'GIF'),
        ('image/jpeg', 'JPEG'),
        ('image/png', 'PNG'),
        ('image/tiff', 'TIFF'),
        ('image/svg+xml', 'SVG'),
        ('application/pdf', 'PDF'),
    ]
    url = models.CharField(max_length=100, db_index=True, unique=True, verbose_name=_('URL'))
    file = models.FileField(
        upload_to='custom_url',
        validators=[
            FileExtensionValidator(
                allowed_extensions=['txt', 'csv', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'gif', 'jpg', 'jpeg', 'png', 'tif', 'tiff', 'svg', 'pdf']
            )
        ],
        verbose_name=_('File'),
        help_text = _('Allowed format files: Plain Text, CSV, Excel, Word, PowerPoint, GIF, JPEG, PNG, TIFF, SVG, PDF')
    )
    file_type = models.CharField(max_length=50, choices=CONTENT_TYPES, verbose_name=_('File Type'))

    def __str__(self):
        return self.url