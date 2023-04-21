from django.db import models
from django.contrib.auth.models import User

# Dashboard simulaciones

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
