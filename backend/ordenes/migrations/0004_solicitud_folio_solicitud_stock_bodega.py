# Generated by Django 5.1.6 on 2025-03-06 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ordenes', '0003_solicituddetalle'),
    ]

    operations = [
        migrations.AddField(
            model_name='solicitud',
            name='folio',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='solicitud',
            name='stock_bodega',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
