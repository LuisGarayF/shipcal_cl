# Generated by Django 4.2 on 2023-05-05 04:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ssspi', '0006_remove_formsim_profile_formsim_simulacion'),
    ]

    operations = [
        migrations.AddField(
            model_name='formsim',
            name='profile',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='ssspi.profile', verbose_name='Usuario'),
            preserve_default=False,
        ),
    ]
