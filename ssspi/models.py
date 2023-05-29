from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission, User
from django.urls import reverse_lazy as _
from django.db import models
import uuid
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django import forms



# Tabla de usuarios

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


class Usuario(AbstractUser):
    grupo = models.ManyToManyField(
        Group,
        verbose_name='Usuarios',
        related_name='usuarios_grupo',
        blank=True
    )
    permiso = models.ManyToManyField(
        Permission,
        verbose_name='Permisos',
        related_name='usuarios_permiso',
        blank=True
    )

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Usuario"
    )
    nombre = models.CharField(
        max_length=400,
        null=True,
        blank=True,
        verbose_name="Nombre"
    )
    apellido = models.CharField(
        max_length=400,
        null=True,
        blank=True,
        verbose_name="Apellido"
    )
    institucion = models.CharField(
        max_length=400,
        null=False,
        blank=False,
        verbose_name="Institución"
    )
    direccion = models.CharField(max_length=300, null=False, blank=False)
    telefono = models.CharField(max_length=12, verbose_name="Teléfono")
    email = models.EmailField(verbose_name="Correo Electrónico")

    class Meta:
        verbose_name_plural = 'Perfiles'
        db_table = 'auth_perfil'

    def __str__(self):
        return f'{self.user.username} {self.institucion}'


class Contactform(models.Model):
    contact_form_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    customer_email = models.EmailField(
        null=True, verbose_name="Correo Electrónico")
    customer_name = models.CharField(max_length=64, verbose_name="Nombre")
    subject = models.CharField(max_length=255, verbose_name="Asunto")
    message = models.CharField(max_length=2000, verbose_name="Mensaje")

    class Meta:
        managed = False
        db_table = 'contactform'

    def __str__(self):
        return f'{self.customer_name} {self.customer_email} {self.subject} {self.message}'

# Campos formulario simulacion


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

    
class Unidad_Demanda(models.Model):
    unidad_demanda = models.CharField(
        max_length=300, verbose_name="unidad_demanda")

    class Meta:
        verbose_name_plural = 'Unidades demanda'
        db_table = 'unidad_demanda'

    def __str__(self):
        return f'{self.unidad_demanda}'


class Inicio_Jornada(models.Model):
    ini_jornada = models.CharField(max_length=300, default="00:00")

    class Meta:
        verbose_name_plural = 'Inicio Jornadas'
        db_table = 'inicio_jornada'

    def __str__(self):
        return f'{self.ini_jornada}'


class Termino_Jornada(models.Model):
    term_jornada = models.CharField(max_length=300, default="23:30")

    class Meta:
        verbose_name_plural = 'Término Jornadas'
        db_table = 'termino_jornada'

    def __str__(self):
        return f'{self.term_jornada}'


class Combustible(models.Model):
    combustible = models.CharField(max_length=300, verbose_name="combustible")

    class Meta:
        verbose_name_plural = 'combustibles'
        db_table = 'combustible'

    def __str__(self):
        return f'{self.combustible}'


class Unidad_Potencia(models.Model):
    unidad_potencia = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'Unidades de Potencia Caldera'
        verbose_name = "Unidad Potencia Caldera"
        db_table = 'unidad_potencia'

    def __str__(self):
        return f'{self.unidad_potencia}'


class Unidad_Presion(models.Model):
    unidad_presion = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'Unidades de Presión Caldera'
        verbose_name = "Unidad de Presión Caldera"
        db_table = 'unidad_presion'

    def __str__(self):
        return f'{self.unidad_presion}'


class Tipo_Caldera(models.Model):
    tipo_caldera = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'Tipos de Caldera'
        verbose_name = "Tipo de Caldera"
        db_table = 'tipo_caldera'

    def __str__(self):
        return f'{self.tipo_caldera}'


class Ubicacion(models.Model):
    nombre_ubicacion = models.CharField(
        max_length=100, null=False, verbose_name="Ubicación")
    latitud = models.FloatField(
        null=False, blank=False, max_length=50, verbose_name="Latitud")
    longitud = models.FloatField(
        null=False, blank=False, max_length=50, verbose_name="Longitud")
    latitud_personalizada = models.FloatField(
        null=True, blank=True, max_length=50, verbose_name="Latitud Personalizada")
    longitud_personalizada = models.FloatField(
        null=True, blank=True, max_length=50, verbose_name="Longitud Personalizada")

    class Meta:
        verbose_name_plural = 'Ubicaciones'
        db_table = 'ubicacion'

    def __str__(self):
        return f'{self.nombre_ubicacion}'
    


class Esquema(models.Model):
    esquema = models.CharField(max_length=200, verbose_name="Esquema de integración",
                               blank=True, default="Campo solar y caldera en serie con recirculación desde caldera")
    siglas_esquema = models.CharField(
        max_length=20, verbose_name="Siglas esquema Integration", default="SL_L_PD")
    # Copiar url base
    imagen_esquema = models.FileField(
        verbose_name="Imagen", upload_to='./static/img/esquemas_integracion/')

    class Meta:
        verbose_name = "esquema de integración"
        verbose_name_plural = 'esquemas de integración'
        db_table = 'esquema_integracion'

    def __str__(self):
        return f'{self.esquema} {self.imagen_esquema}{self.siglas_esquema}'


class Unidad_Flujo_Masico(models.Model):
    unidad_flujo_masico = models.CharField(
        max_length=20, verbose_name="Unidad flujo másico", default="kg/s")

    class Meta:
        verbose_name = "Unidad Flujo Másico"
        verbose_name_plural = 'Unidades Flujo Másico'
        db_table = 'unidad_flujo_masico'

    def __str__(self):
        return f'{self.unidad_flujo_masico}'


class Tipo_Fluido(models.Model):
    tipo_fluido = models.CharField(max_length=200, default="Agua")

    class Meta:
        verbose_name = "Tipo Fluido"
        verbose_name_plural = 'Tipos de Fluidos'
        db_table = 'tipo_fluido'

    def __str__(self):
        return f'{self.tipo_fluido}'


class Relacion_Aspecto(models.Model):
    relacion_aspecto = models.CharField(max_length=200)

    class Meta:
        verbose_name = "Relación de Aspecto"
        verbose_name_plural = 'Relaciones de Aspecto'
        db_table = 'relacion_aspecto'

    def __str__(self):
        return f'{self.relacion_aspecto}'


class Material_Almacenamiento(models.Model):
    material_almacenamiento = models.CharField(max_length=200)

    class Meta:
        verbose_name = "Material Almacenamiento"
        verbose_name_plural = 'Materiales Almacenamiento'
        db_table = 'material_almacenamiento'

    def __str__(self):
        return f'{self.material_almacenamiento}'


class Material_Aislamiento(models.Model):
    material_aislamiento = models.CharField(max_length=200)

    class Meta:
        verbose_name = "Material Aislamiento"
        verbose_name_plural = 'Materiales Aislamiento'
        db_table = 'material_aislacion'

    def __str__(self):
        return f'{self.material_aislamiento}'


class Tabla_colectores(models.Model):
    nombre = models.CharField(max_length=300, null=False, blank=True)
    numero_srcc = models.CharField(max_length=200, null=False, blank=True)
    tipo = models.CharField(max_length=200, null=False, blank=True)
    fluido_prueba = models.PositiveIntegerField()
    rango_flujo_prueba = models.FloatField()
    area = models.FloatField()
    frta = models.FloatField()
    frul = models.FloatField()
    iam = models.FloatField()

    class Meta:
        verbose_name = "Tabla de colectores"
        verbose_name_plural = 'Tabla de colectores'
        db_table = 'tabla_colectores'

    def __str__(self):
        return f'{self.nombre} {self.tipo} {self.rango_flujo_prueba} {self.area} {self.frta} {self.frul} {self.iam}'


class Unidad_Costo_Combustible(models.Model):
    unidad_costo_combustible = models.CharField(max_length=30)

    class Meta:
        verbose_name = "Unidad Costo Combustible"
        verbose_name_plural = 'Unidades Costo Combustible'
        db_table = 'costo_combustible'

    def __str__(self):
        return f'{self.unidad_costo_combustible}'

class ArchivoTMY(models.Model):
    simulacion = models.ForeignKey('Simulaciones', on_delete=models.CASCADE)
    archivo = models.FileField(upload_to='TMY_Simulaciones/')

    def __str__(self):
        return self.archivo.name
    

# Dashboard

class ContadorSimulacion(models.Model):
    ultima_simulacion = models.IntegerField(default=0)

class Simulaciones(models.Model):
    id_simulacion = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_user = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        verbose_name='Usuario',
        related_name='usuario_simulacion'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_ultima_modificacion = models.DateTimeField(auto_now=True)
    resultado = models.TextField(verbose_name='Resultado', blank=True)
    archivo_tmy = models.ForeignKey(ArchivoTMY, verbose_name='TMY', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Simulaciones'
        db_table = 'auth_simulaciones'

    def __str__(self):
        return f'{self.id_simulacion} {self.id_user.username} {self.fecha_creacion}' 
    

    
# Formulario Simulacion

class FormSim(models.Model):
    simulacion = models.OneToOneField(Simulaciones, on_delete=models.CASCADE, related_name='Simulacion', blank=True,null=True)
    profile = models.ForeignKey(Profile, verbose_name='Usuario', on_delete=models.CASCADE, null=True, blank=True)
    nombre_simulacion = models.CharField(
        max_length=100, blank=False, verbose_name="Nombre de simulación", unique=True)
    sector = models.ForeignKey('Sector', on_delete=models.CASCADE, null=True)
    # aplicacion = models.ForeignKey(
    #     'Aplicacion', on_delete=models.CASCADE, null=True, blank=True)
    ubicacion = models.ForeignKey(
        'Ubicacion', on_delete=models.CASCADE, blank=True, null=True)
    esquema = models.ForeignKey(
        'Esquema', on_delete=models.CASCADE, blank=True, null=True, related_name='esquema_int')
    combustible = models.ForeignKey(
        'Combustible', on_delete=models.CASCADE, null=True)
    ini_jornada = models.ForeignKey(
        'Inicio_Jornada', on_delete=models.CASCADE, blank=True)
    trno_jornada = models.ForeignKey(
        'Termino_Jornada', on_delete=models.CASCADE, blank=True)
    demanda_anual = models.FloatField(max_length=300)
    unidad_demanda = models.ForeignKey(
        'Unidad_Demanda', on_delete=models.CASCADE, null=True)
    tabla_colectores = models.ForeignKey(
        'Tabla_Colectores', on_delete=models.CASCADE, null=True, blank=True)
    demanda_enero = models.FloatField(max_length=300)
    demanda_febrero = models.FloatField(max_length=300)
    demanda_marzo = models.FloatField(max_length=300)
    demanda_abril = models.FloatField(max_length=300)
    demanda_mayo = models.FloatField(max_length=300)
    demanda_junio = models.FloatField(max_length=300)
    demanda_julio = models.FloatField(max_length=300)
    demanda_agosto = models.FloatField(max_length=300)
    demanda_septiembre = models.FloatField(max_length=300)
    demanda_octubre = models.FloatField(max_length=300)
    demanda_noviembre = models.FloatField(max_length=300)
    demanda_diciembre = models.FloatField(max_length=300)
    demanda_lun = models.BooleanField(max_length=300, default=True)
    demanda_mar = models.BooleanField(max_length=300, default=True)
    demanda_mie = models.BooleanField(max_length=300, default=True)
    demanda_jue = models.BooleanField(max_length=300, default=True)
    demanda_vie = models.BooleanField(max_length=300, default=True)
    demanda_sab = models.BooleanField(max_length=300, default=True)
    demanda_dom = models.BooleanField(max_length=300, default=True)
    potencia_caldera = models.FloatField(
        max_length=300, verbose_name="Potencia Nominal Caldera")
    unidad_potencia = models.ForeignKey(
        'Unidad_Potencia', on_delete=models.CASCADE, null=True)
    presion_caldera = models.FloatField(
        max_length=300, verbose_name="Presión de la Caldera")
    unidad_presion = models.ForeignKey(
        'Unidad_Presion', on_delete=models.CASCADE, null=True)
    tipo_caldera = models.ForeignKey(
        'Tipo_Caldera', on_delete=models.CASCADE, null=True)
    eficiencia_caldera = models.FloatField(null=True, blank=True)
    temperatura_red = models.FloatField(
        max_length=50, verbose_name="Temperatura de la red", null=True, blank=True)
    temperatura_retorno = models.FloatField(
        max_length=50, verbose_name="Temperatura retorno", null=True, blank=True)
    t_enero = models.FloatField(
        max_length=50, verbose_name="Temperatura enero", null=True, blank=True)
    t_febrero = models.FloatField(
        max_length=50, verbose_name="Temperatura febrero", null=True, blank=True)
    t_marzo = models.FloatField(
        max_length=50, verbose_name="Temperatura marzo", null=True, blank=True)
    t_abril = models.FloatField(
        max_length=50, verbose_name="Temperatura abril", null=True, blank=True)
    t_mayo = models.FloatField(
        max_length=50, verbose_name="Temperatura mayo", null=True, blank=True)
    t_junio = models.FloatField(
        max_length=50, verbose_name="Temperatura junio", null=True, blank=True)
    t_julio = models.FloatField(
        max_length=50, verbose_name="Temperatura julio", null=True, blank=True)
    t_agosto = models.FloatField(
        max_length=50, verbose_name="Temperatura agosto", null=True, blank=True)
    t_septiembre = models.FloatField(
        max_length=50, verbose_name="Temperatura septiembre", null=True, blank=True)
    t_octubre = models.FloatField(
        max_length=50, verbose_name="Temperatura octubre", null=True, blank=True)
    t_noviembre = models.FloatField(
        max_length=50, verbose_name="Temperatura noviembre", null=True, blank=True)
    t_diciembre = models.FloatField(
        max_length=50, verbose_name="Temperatura diciembre", null=True, blank=True)
    t_salida = models.FloatField(
        max_length=50, verbose_name="Temperatura de salida", null=True, blank=True)
    nombre_colector = models.CharField(
        max_length=200, verbose_name="Nombre de colector", blank=True, default='Colector 1')
    area_apertura = models.FloatField()
    eficiencia_optica = models.FloatField()
    coef_per_lineales = models.FloatField()
    coef_per_cuadraticas = models.FloatField()
    iam_longitudinal = models.FloatField(
        null=True, blank=True, verbose_name="IAM longitudinal")
    precio_colector = models.FloatField()
    cantidad_bat = models.PositiveIntegerField()
    col_bat = models.PositiveIntegerField()
    total_colectores = models.PositiveIntegerField(blank=True, null=True)
    sup_colectores = models.FloatField(null=True, blank=True)
    inclinacion_col = models.FloatField()
    azimut = models.FloatField()
    flujo_masico = models.FloatField()
    unidad_flujo_masico = models.ForeignKey(
        'Unidad_Flujo_Masico', on_delete=models.CASCADE, null=True)
    tipo_fluido = models.ForeignKey(
        'Tipo_Fluido', on_delete=models.CASCADE, null=True)
    volumen = models.FloatField(max_length=100)
    relacion_aspecto = models.ForeignKey(
        'Relacion_Aspecto', on_delete=models.CASCADE, null=True)
    material_almacenamiento = models.ForeignKey(
        'Material_Almacenamiento', on_delete=models.CASCADE, null=True)
    material_aislamiento = models.ForeignKey(
        'Material_Aislamiento', on_delete=models.CASCADE, null=True)
    espesor_aislante = models.FloatField(null=True, blank=True)
    efectividad = models.FloatField(default="0.8")
    costo_combustible = models.PositiveIntegerField(default="100")
    unidad_costo_combustible = models.ForeignKey(
        'Unidad_Costo_Combustible', on_delete=models.CASCADE, null=True)
    costo_tanque = models.PositiveIntegerField(null=True)
    balance = models.PositiveIntegerField(null=True)
    instalacion = models.PositiveIntegerField(null=True)
    operacion = models.PositiveIntegerField(null=True)
    impuesto = models.FloatField(null=True)
    descuento = models.FloatField(null=True)
    inflacion = models.IntegerField(null=True)

    class Meta:
        managed = True
        db_table = 'FormSim'
        verbose_name = "simulacion"
        verbose_name_plural = 'simulaciones'
        
    def __str__(self):
        return f'{self.nombre_simulacion}' 