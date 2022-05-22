
from django.db import models
from django.utils.translation import ugettext_lazy as _

from tecdoc.constants import ADDITIONAL_CODES_MAX_LENGTH


class Manufacturer(models.Model):

    description = models.CharField(max_length=255)

    def __str__(self):
        return self.description

    class Meta:
        db_table = 'manufacturers'


class Supplier(models.Model):

    description = models.CharField(max_length=255)

    matchcode = models.CharField(max_length=255)

    def __str__(self):
        return self.description

    class Meta:
        db_table = 'suppliers'


class ArticleAttribute(models.Model):

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        db_column='supplierid')

    article_number = models.CharField(
        max_length=255,
        db_column='datasupplierarticlenumber',
        primary_key=True)

    description = models.TextField(
        db_column='description')

    value = models.TextField(
        db_column='displayvalue')

    def __str__(self):
        return self.article_number

    class Meta:
        db_table = 'article_attributes'


class ArticleEAN(models.Model):

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        db_column='supplierid')

    article_number = models.CharField(
        max_length=255,
        db_column='datasupplierarticlenumber',
        primary_key=True)

    ean = models.CharField(max_length=255)

    def __str__(self):
        return self.ean

    class Meta:
        db_table = 'article_ean'


class Cross(models.Model):

    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.PROTECT,
        db_column='manufacturerId')

    oen_br = models.CharField(
        max_length=255,
        db_column='OENbr')

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        db_column='SupplierId')

    article_number = models.CharField(
        max_length=255,
        db_column='PartsDataSupplierArticleNumber',
        primary_key=True)

    def __str__(self):
        return self.article_number

    class Meta:
        db_table = 'article_cross'


class Article(models.Model):

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        db_column='supplierId')

    article_number = models.CharField(
        max_length=255,
        db_column='DataSupplierArticleNumber',
        primary_key=True)

    clean_article_number = models.CharField(
        max_length=255,
        db_column='FoundString')

    description = models.TextField(
        db_column='NormalizedDescription')

    def get_attributes(self):
        return ArticleAttribute.objects.filter(
            article_number=self.article_number,
            supplier_id=self.supplier_id)

    def get_crosses(self):
        return ArticleAttribute.objects.filter(
            article_number=self.article_number,
            supplier_id=self.supplier_id)

    def get_ean_codes(self):
        return ArticleEAN.objects.filter(article_number=self.article_number)

    def get_images(self):
        return Image.objects \
         .filter(
            article_number=self.article_number,
            supplier_id=self.supplier_id)

    def __str__(self):
        return self.article_number

    class Meta:
        db_table = 'articles'


class ArticleOE(models.Model):

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        db_column='supplierId')

    article_number = models.CharField(
        max_length=255,
        db_column='DataSupplierArticleNumber',
        primary_key=True)

    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.PROTECT,
        db_column='manufacturerId')

    oen_br = models.CharField(
        max_length=255,
        db_column='OENbr')

    def __str__(self):
        return self.article_number

    class Meta:
        db_table = 'article_oe'


class Image(models.Model):

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        db_column='supplierId')

    article_number = models.CharField(
        max_length=255,
        db_column='DataSupplierArticleNumber')

    picture_name = models.CharField(
        max_length=255,
        db_column='PictureName',
        primary_key=True)

    def __str__(self):
        return self.picture_name

    class Meta:
        db_table = 'article_images'


class AdditionalCodesField(models.TextField):

    def __init__(
            self,
            verbose_name=_('Additional codes'),
            blank=True,
            db_index=True,
            max_length=ADDITIONAL_CODES_MAX_LENGTH,
            *args,
            **kwargs):

        super().__init__(
            verbose_name=verbose_name,
            blank=blank,
            db_index=db_index,
            max_length=max_length,
            *args,
            **kwargs)
