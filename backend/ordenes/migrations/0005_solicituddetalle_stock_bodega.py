# Generated by Django 5.1.6 on 2025-03-06 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ordenes', '0004_solicitud_folio_solicitud_stock_bodega'),
    ]

    operations = [
        migrations.AddField(
            model_name='solicituddetalle',
            name='stock_bodega',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
