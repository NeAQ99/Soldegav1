# Generated by Django 5.1.6 on 2025-03-03 15:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ordenes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordenescompras',
            name='mercaderia_puesta_en',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='ordenescompras',
            name='nro_cotizacion',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='ordenescompras',
            name='estado',
            field=models.CharField(default='pendiente', max_length=20),
        ),
        migrations.AlterField(
            model_name='ordenescompras',
            name='proveedor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ordenes.proveedor'),
        ),
    ]
