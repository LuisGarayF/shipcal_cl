# Generated by Django 4.2 on 2023-04-21 04:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ssspi', '0004_remove_formsim_procesos_alter_formsim_profile_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ubicacion',
            name='latitud_personalizada',
            field=models.FloatField(blank=True, max_length=50, null=True, verbose_name='Latitud Personalizada'),
        ),
        migrations.AddField(
            model_name='ubicacion',
            name='longitud_personalizada',
            field=models.FloatField(blank=True, max_length=50, null=True, verbose_name='Longitud Personalizada'),
        ),
    ]
