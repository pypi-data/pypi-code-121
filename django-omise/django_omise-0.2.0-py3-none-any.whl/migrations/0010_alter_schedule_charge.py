# Generated by Django 3.2.13 on 2022-05-21 02:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('django_omise', '0009_alter_schedule_end_on'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedule',
            name='charge',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='django_omise.chargeschedule'),
        ),
    ]
