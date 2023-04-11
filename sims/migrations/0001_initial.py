# Generated by Django 4.2 on 2023-04-11 04:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Aplicacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('aplicacion', models.CharField(blank=True, db_column='aplicacion', max_length=100, null=True, verbose_name='Aplicación Industrial')),
            ],
            options={
                'verbose_name_plural': 'Aplicaciones',
                'db_table': 'aplicacion',
            },
        ),
        migrations.CreateModel(
            name='Sector',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sector', models.CharField(db_column='sector', max_length=100, verbose_name='Sector Industrial')),
            ],
            options={
                'verbose_name_plural': 'Sectores',
                'db_table': 'sector',
            },
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Simulaciones',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_simulacion', models.CharField(max_length=100, verbose_name='Nombre de simulación')),
                ('description', models.TextField(blank=True, verbose_name='Descripción')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Fecha Modificación')),
                ('id_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Simulaciones',
                'db_table': 'simulaciones',
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('institucion', models.CharField(max_length=400, verbose_name='Institución')),
                ('direccion_completa', models.CharField(max_length=300, verbose_name='Dirección completa')),
                ('numero_telefono', models.CharField(max_length=12, verbose_name='Número de teléfono')),
                ('email', models.EmailField(max_length=254, verbose_name='Correo Electrónico')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Usuario')),
            ],
            options={
                'verbose_name_plural': 'Perfiles',
                'db_table': 'auth_perfil',
            },
        ),
        migrations.CreateModel(
            name='Proceso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('proceso', models.CharField(blank=True, max_length=100)),
                ('aplicacion', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='sims.aplicacion')),
            ],
            options={
                'verbose_name': 'Proceso Industrial',
                'verbose_name_plural': 'Procesos Industriales',
                'db_table': 'procesos',
            },
        ),
        migrations.AddField(
            model_name='aplicacion',
            name='sector',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='sims.sector'),
        ),
    ]