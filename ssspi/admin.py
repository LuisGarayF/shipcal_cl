from django.contrib import admin

from ssspi.models import (Aplicacion, Esquema, Sector, Tabla_colectores, Ubicacion, Combustible, Inicio_Jornada,
                        Termino_Jornada, Unidad_Potencia, Unidad_Presion, Tipo_Caldera, Unidad_Flujo_Masico, Tipo_Fluido,
                        Relacion_Aspecto, Material_Aislamiento, Material_Almacenamiento, Unidad_Costo_Combustible, FormSim, Profile, Unidad_Demanda)

class SimulacionAdmin(admin.ModelAdmin):
    # Define los campos de creación y actualización como solo lectura
    readonly_fields = ('created_at', 'updated') 

class UbicacionAdmin(admin.ModelAdmin):
    list_display=("nombre_ubicacion","latitud","longitud")
    search_fields =("nombre_ubicacion",) 

class TablaColectoresAdmin(admin.ModelAdmin):
    list_display=("nombre","tipo","rango_flujo_prueba","area","frta","frul","iam")
    search_fields =("nombre","tipo") 

admin.site.register(Profile)
admin.site.register(FormSim)
admin.site.register(Sector)
admin.site.register(Aplicacion)
admin.site.register(Ubicacion,UbicacionAdmin)
admin.site.register(Combustible)
admin.site.register(Unidad_Demanda)
admin.site.register(Inicio_Jornada)
admin.site.register(Termino_Jornada)
admin.site.register(Unidad_Potencia)
admin.site.register(Unidad_Presion)
admin.site.register(Tipo_Caldera)
admin.site.register(Esquema)
admin.site.register(Unidad_Flujo_Masico)
admin.site.register(Tipo_Fluido)
admin.site.register(Relacion_Aspecto)
admin.site.register(Material_Almacenamiento)
admin.site.register(Material_Aislamiento)
admin.site.register(Unidad_Costo_Combustible)
admin.site.register(Tabla_colectores,TablaColectoresAdmin)
