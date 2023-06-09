# Generated by Django 4.2 on 2023-05-26 06:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ssspi', '0008_remove_formsim_aplicacion_alter_formsim_profile_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArchivoTMY',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('archivo', models.FileField(upload_to='TMY_Simulaciones/')),
                ('simulacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ssspi.simulaciones')),
            ],
        ),
        migrations.AddField(
            model_name='simulaciones',
            name='archivo_tmy',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ssspi.archivotmy', verbose_name='TMY'),
        ),
    ]
