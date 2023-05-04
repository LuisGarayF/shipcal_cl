from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from ssspi.models import *


# Formulario para creación de usuarios

class UserForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, label='Nombre')
    last_name = forms.CharField(max_length=50, label='Apellido')
    email = forms.EmailField(max_length=50, label='Correo Electrónico')
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)
    institucion = forms.CharField(label='Institución Eduacional o Empresa', max_length=200)
    username = forms.CharField(label='Nombre de Usuario', max_length=50)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2', 'institucion')
        labels = {'username': _("Nombre de Usuario")}

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['institucion', 'direccion', 'telefono', 'email']
        exclude = ['user']

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields =['first_name','last_name','email']

        
# Formulario de contacto

class ContactForm(forms.ModelForm):
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}), label="Mensaje")

    class Meta:
        model = Contactform
        fields = ['customer_email', 'customer_name', 'subject', 'message']

# Formulario simulador

class SimForm(forms.ModelForm):
   
    sector = forms.ModelChoiceField(queryset=Sector.objects.all(),widget=forms.Select(attrs={'class': 'browser-default'}))
    aplicacion = forms.ModelChoiceField(queryset= Aplicacion.objects.none(), to_field_name='aplicacion', widget=forms.Select(attrs={'class': 'browser-default'}), required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['aplicacion'].queryset = Aplicacion.objects.none()
        
        

    def aplicacion_choices(self):
        sector_id = self.data.get('sector')
        if sector_id:
            self.fields['aplicacion'].queryset = Aplicacion.objects.filter(sector_id=sector_id)
        
    
    nombre_ubicacion = forms.ModelChoiceField(queryset=Ubicacion.objects.all(), to_field_name='nombre_ubicacion',required=False, widget=forms.Select(attrs={'class': 'form-select'}), initial="Santiago")
    latitud = forms.FloatField(required=False, widget=forms.NumberInput(attrs={'step': '0.01'}))
    longitud = forms.FloatField(required=False, widget=forms.NumberInput(attrs={'step': '0.01'}))
    latitud_personalizada = forms.FloatField(required=False, widget=forms.NumberInput(attrs={'step': '0.01'}))
    longitud_personalizada = forms.FloatField(required=False, widget=forms.NumberInput(attrs={'step': '0.01'}))
    combustible =forms.ModelChoiceField(queryset=Combustible.objects.all(), to_field_name='combustible', widget=forms.Select(attrs={'class': 'form-select'}), required=False, empty_label=" ", initial="Diesel")
    ini_jornada = forms.ModelChoiceField(queryset=Inicio_Jornada.objects.all(), to_field_name='ini_jornada', widget=forms.Select(attrs={'class': 'form-select'}), required=False, empty_label=" ", initial="00:00")
    term_jornada = forms.ModelChoiceField(queryset=Termino_Jornada.objects.all(), to_field_name='term_jornada', widget=forms.Select(attrs={'class': 'form-select'}), required=False, empty_label=" ", initial="23:30") 
    demanda_anual= forms.FloatField(widget=forms.NumberInput(attrs={'readonly':'readonly'}),required = False)
    unidad_demanda = forms.ModelChoiceField(queryset=Unidad_Demanda.objects.all(), to_field_name='unidad_demanda', widget=forms.Select(attrs={'class': 'form-select'}), required=False, empty_label=" Unidad de demanda")
    unidad_potencia = forms.ModelChoiceField(queryset=Unidad_Potencia.objects.all(), to_field_name='unidad_potencia', widget=forms.Select(attrs={'class': 'form-select'}), required=False, empty_label="Unidad de Potencia")
    unidad_presion = forms.ModelChoiceField(queryset=Unidad_Presion.objects.all(), to_field_name='unidad_presion', widget=forms.Select(attrs={'class': 'form-select'}), required=False, empty_label="Unidad de Presión")
    sup_colectores = forms.FloatField(widget=forms.NumberInput(attrs={'readonly':'readonly','step': '0.01'}),required = False)
    total_colectores = forms.IntegerField(widget=forms.NumberInput(attrs={'readonly':'readonly'}),required = False)
    tipo_caldera = forms.ModelChoiceField(queryset=Tipo_Caldera.objects.all(), to_field_name='tipo_caldera', widget=forms.Select(attrs={'class': 'form-select'}), required=False, empty_label="Tipo de caldera")
    nombre_colector = forms.CharField(initial='TEST',required=False)
    unidad_flujo_masico = forms.ModelChoiceField(queryset=Unidad_Flujo_Masico.objects.all(), to_field_name='unidad_flujo_masico', widget=forms.Select(attrs={'class': 'form-select'}), required=False, empty_label="Unidad Flujo Másico", initial="kg/s")
    tipo_fluido = forms.ModelChoiceField(queryset=Tipo_Fluido.objects.all(), to_field_name='tipo_fluido', widget=forms.Select(attrs={'class': 'form-select'}), required=False, empty_label="Tipo de Fluido", initial="Glicol 10%")
    rango_flujo_prueba = forms.FloatField(required=False, initial="0")
    iam = forms.FloatField()
    iam_longitudinal = forms.FloatField(required = False)
    relacion_aspecto = forms.ModelChoiceField(queryset=Relacion_Aspecto.objects.all(), to_field_name='relacion_aspecto', widget=forms.Select(attrs={'class': 'form-select'}), required=False, empty_label="Relación de Aspecto", initial="2")
    material_almacenamiento = forms.ModelChoiceField(queryset=Material_Almacenamiento.objects.all(), to_field_name='material_almacenamiento', widget=forms.Select(attrs={'class': 'form-select'}), required=False, empty_label="Material Almacenamiento", initial="Acero inoxidable")
    material_aislamiento = forms.ModelChoiceField(queryset=Material_Aislamiento.objects.all(), to_field_name='material_aislamiento', widget=forms.Select(attrs={'class': 'form-select'}), required=False, empty_label="Material Aislamiento", initial="Lana de vidrio")
    unidad_costo_combustible= forms.ModelChoiceField(queryset=Unidad_Costo_Combustible.objects.all(), to_field_name='unidad_costo_combustible', widget=forms.Select(attrs={'class': 'form-select'}), required=False, empty_label="Unidad Costo Combustible", initial="$/l") 
    t_enero = forms.FloatField(widget=forms.NumberInput(attrs={'readonly':'readonly'}))
    t_febrero = forms.FloatField(widget=forms.NumberInput(attrs={'readonly':'readonly'}))
    t_marzo = forms.FloatField(widget=forms.NumberInput(attrs={'readonly':'readonly'}))
    t_abril = forms.FloatField(widget=forms.NumberInput(attrs={'readonly':'readonly'}))
    t_mayo = forms.FloatField(widget=forms.NumberInput(attrs={'readonly':'readonly'}))
    t_junio = forms.FloatField(widget=forms.NumberInput(attrs={'readonly':'readonly'}))
    t_julio = forms.FloatField(widget=forms.NumberInput(attrs={'readonly':'readonly'}))
    t_agosto = forms.FloatField(widget=forms.NumberInput(attrs={'readonly':'readonly'}))
    t_septiembre = forms.FloatField(widget=forms.NumberInput(attrs={'readonly':'readonly'}))
    t_octubre = forms.FloatField(widget=forms.NumberInput(attrs={'readonly':'readonly'}))
    t_noviembre = forms.FloatField(widget=forms.NumberInput(attrs={'readonly':'readonly'}))
    t_diciembre = forms.FloatField(widget=forms.NumberInput(attrs={'readonly':'readonly'}))
    siglas_esquema = forms.CharField(required=False,widget=forms.TextInput(attrs={'readonly':'readonly'}))
    imagen_esquema = forms.ImageField(label="Imagen")
    
    

        
    class Meta:
        model = FormSim
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        nombre_ubicacion = cleaned_data.get('nombre_ubicacion')
        latitud_personalizada = cleaned_data.get('latitud_personalizada')
        longitud_personalizada = cleaned_data.get('longitud_personalizada')
        
        if not nombre_ubicacion and not (latitud_personalizada and longitud_personalizada):
            raise forms.ValidationError("Debe seleccionar una ubicación o especificar la latitud y longitud personalizadas.")
        
        if nombre_ubicacion and (latitud_personalizada or longitud_personalizada):
            raise forms.ValidationError("No puede seleccionar una ubicación y especificar la latitud y longitud personalizadas al mismo tiempo.")