from django.db import models
from django.contrib.auth.models import User

# Dashboard simulaciones

# Tabla de usuarios


class Usuario(models.Model):
    id_user = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE, null=True)

class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, verbose_name="Usuario")
    institucion = models.CharField(
        max_length=400, null=False, blank=False, verbose_name="Institución")
    direccion_completa = models.CharField(max_length=300, null=False, blank=False, verbose_name="Dirección completa")
    numero_telefono = models.CharField(max_length=12, verbose_name="Número de teléfono")
    email = models.EmailField(verbose_name="Correo Electrónico")
    
    class Meta:
        verbose_name_plural = 'Perfiles'
        db_table = 'auth_perfil'

    def __str__(self):
        return f'{self.user.username} - {self.institucion}'

# Dashboard

class Simulaciones(models.Model):
    id_user = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL, null=True, db_index=True)
    nombre_simulacion = models.CharField(
        max_length=100, null=False, blank=False, verbose_name="Nombre de simulación")
    description = models.TextField(blank=True, verbose_name="Descripción")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación")
    updated = models.DateTimeField(
        auto_now=True, verbose_name="Fecha Modificación")

    class Meta:
        verbose_name_plural = 'Simulaciones'
        db_table = 'simulaciones'

    def __str__(self):
        return f'{self.id_user}: {self.nombre_simulacion}'
    

# Formulario Simulaciones

class Sector(models.Model):
    sector = models.CharField(max_length=100, null=False, blank=False,
                              verbose_name="Sector Industrial", db_column='sector')

    class Meta:
        verbose_name_plural = 'Sectores'
        db_table = 'sector'

    def __str__(self):
        return f'{self.sector}'


class Aplicacion(models.Model):
    aplicacion = models.CharField(
        max_length=100, verbose_name="Aplicación Industrial",  db_column='aplicacion',blank=True, null=True)
    sector = models.ForeignKey('Sector', on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name_plural = 'Aplicaciones'
        db_table = 'aplicacion'

    def __str__(self):  
        return f'{self.aplicacion}'


class Proceso(models.Model):
    proceso = models.CharField(max_length=100, blank=True)
    aplicacion = models.ForeignKey('Aplicacion', on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = "Proceso Industrial"
        verbose_name_plural = 'Procesos Industriales'
        db_table = 'procesos'

    def __str__(self):
        return f'{self.proceso}'



