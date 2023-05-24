from django.shortcuts import render,redirect, get_object_or_404
import os
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from ssspi.forms import *
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.core.mail import send_mail, BadHeaderError
from ssspi.models import *
from Simulacion.Run_Simulation import simulate_system
import json
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from django.core.serializers.json import DjangoJSONEncoder


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'index.html', {})


def login(request):
    return render(request, 'registration/login.html', {})

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('index')
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        response.delete_cookie('sessionid')
        response.delete_cookie('csrftoken')
        return redirect(reverse_lazy('index'))


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            messages.success(
                request, f'Usuario : {username} creado correctamente.')
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def dashboardView(request):
    profile = Profile.objects.get(user=request.user)
    simulaciones = Simulaciones.objects.filter(id_user=request.user).select_related('Simulacion')
    return render(request, 'dashboard.html', {'profile': profile, 'simulaciones': simulaciones})


@login_required
def update_profile(request):
    return render(request, 'update_profile.html', {})



@login_required
def profile(request):
    simulaciones = FormSim.objects.all()
    try:
        profile = request.user.profile
        
    except Profile.DoesNotExist:
        profile = None
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return HttpResponseRedirect('/dashboard/')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)

    return render(request, 'update_profile.html', {'u_form': u_form, 'p_form': p_form, 'simulaciones':simulaciones})




def acerca(request):
    return render(request, 'about.html', {})


def contacto(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)

        if form.is_valid():
            form.save()

            subject = "Contacto"
            message = f"Nombre: {form.cleaned_data['customer_name']}\n" \
                      f"Correo electrónico: {form.cleaned_data['customer_email']}\n" \
                      f"Asunto: {form.cleaned_data['subject']}\n" \
                      f"Mensaje: {form.cleaned_data['message']}"

            try:
                send_mail(subject, message, 'jmcardem@uc.cl', ['jmcardem@uc.cl'])
            except BadHeaderError:
                return HttpResponse('Header Invalido.')

            return HttpResponseRedirect('/exito')
    else:
        form = ContactForm()

    return render(request, 'contacto.html', {'form': form})


# Formulario Simulaciones


# Cargar mapas
# 
def cargar_mapa(request):
    ubicacion_nombre = request.POST.get('ubicacion')

    ubicacion = get_object_or_404(Ubicacion, nombre_ubicacion=ubicacion_nombre)

    response_data = {
        'result': True,
        'latitud': str(ubicacion.latitud),
        'longitud': str(ubicacion.longitud),
    }

    return JsonResponse(response_data)       


@login_required
def simulacion(request):
    profile = Profile.objects.get(user=request.user)
    datos = Tabla_colectores.objects.all()
    esquema_list = Esquema.objects.all()
    
    
    if request.method == 'POST':
        form = SimForm(request.POST, request.FILES)
        if form.is_valid():
            nombre_simulacion = form.cleaned_data['nombre_simulacion']
            sector = form.cleaned_data['sector']
            nombre_ubicacion = form.cleaned_data['nombre_ubicacion']
            # Obtener la ubicación seleccionada
            ubicacion = get_object_or_404(Ubicacion, nombre_ubicacion=nombre_ubicacion)

           # Si se ingresaron manualmente la latitud y longitud, se guardan en la ubicación personalizada
            if form.cleaned_data['latitud'] and form.cleaned_data['longitud']:
                ubicacion.latitud_personalizada = form.cleaned_data['latitud']
                ubicacion.longitud_personalizada = form.cleaned_data['longitud']
                ubicacion.save()

                # Crear un diccionario con los campos relevantes de la ubicación
                ubicacion_data = {
                    'latitud': str(ubicacion.latitud),
                    'longitud': str(ubicacion.longitud),
                }
                #return json.dumps(ubicacion_data)
                

                # Agregar los atributos adicionales al diccionario
                ubicacion_data['result'] = True
            raw_results['ubicacion'] = ubicacion_data
    

            esquema = form.cleaned_data['esquema']
            siglas_esquema = form.cleaned_data['siglas_esquema']
            combustible = form.cleaned_data['combustible']
            demanda_anual = form.cleaned_data['demanda_anual']
            unidad_demanda = form.cleaned_data['unidad_demanda']
            ini_jornada = str(form.cleaned_data['ini_jornada'])
            term_jornada = str(form.cleaned_data['term_jornada'])
            demanda_lun = form.cleaned_data['demanda_lun']
            demanda_mar = form.cleaned_data['demanda_mar']
            demanda_mie = form.cleaned_data['demanda_mie']
            demanda_jue = form.cleaned_data['demanda_jue']
            demanda_vie = form.cleaned_data['demanda_vie']
            demanda_sab = form.cleaned_data['demanda_sab']
            demanda_dom = form.cleaned_data['demanda_dom']
            demanda_enero = form.cleaned_data['demanda_enero']
            demanda_febrero = form.cleaned_data['demanda_febrero']
            demanda_marzo = form.cleaned_data['demanda_marzo']
            demanda_abril = form.cleaned_data['demanda_abril']
            demanda_mayo = form.cleaned_data['demanda_mayo']
            demanda_junio = form.cleaned_data['demanda_junio']
            demanda_julio = form.cleaned_data['demanda_julio']
            demanda_agosto = form.cleaned_data['demanda_agosto']
            demanda_septiembre = form.cleaned_data['demanda_septiembre']
            demanda_octubre = form.cleaned_data['demanda_octubre']
            demanda_noviembre = form.cleaned_data['demanda_noviembre']
            demanda_diciembre = form.cleaned_data['demanda_diciembre']
            potencia_caldera = form.cleaned_data['potencia_caldera']
            unidad_potencia = form.cleaned_data['unidad_potencia']
            presion_caldera = form.cleaned_data['presion_caldera']
            unidad_presion = form.cleaned_data['unidad_presion']
            tipo_caldera = form.cleaned_data['tipo_caldera']
            eficiencia_caldera = form.cleaned_data['eficiencia_caldera']
            temperatura_retorno = form.cleaned_data['temperatura_retorno']
            t_enero = form.cleaned_data['t_enero']
            t_febrero = form.cleaned_data['t_febrero']
            t_marzo = form.cleaned_data['t_marzo']
            t_abril = form.cleaned_data['t_abril']
            t_mayo = form.cleaned_data['t_mayo']
            t_junio = form.cleaned_data['t_junio']
            t_julio = form.cleaned_data['t_julio']
            t_agosto = form.cleaned_data['t_agosto']
            t_septiembre = form.cleaned_data['t_septiembre']
            t_octubre = form.cleaned_data['t_octubre']
            t_noviembre = form.cleaned_data['t_noviembre']
            t_diciembre = form.cleaned_data['t_diciembre']
            t_salida = form.cleaned_data['t_salida']
            area_apertura = form.cleaned_data['area_apertura']
            eficiencia_optica = form.cleaned_data['eficiencia_optica']
            coef_per_lineales = form.cleaned_data['coef_per_lineales']
            coef_per_cuadraticas = form.cleaned_data['coef_per_cuadraticas']
            precio_colector = form.cleaned_data['precio_colector']
            cantidad_bat = form.cleaned_data['cantidad_bat']
            total_colectores = form.cleaned_data['total_colectores']
            col_bat = form.cleaned_data['col_bat']
            sup_colectores = form.cleaned_data['sup_colectores']
            inclinacion_col = form.cleaned_data['inclinacion_col']
            azimut = form.cleaned_data['azimut']
            flujo_masico = form.cleaned_data['flujo_masico']
            unidad_flujo_masico = form.cleaned_data['unidad_flujo_masico']
            tipo_fluido = form.cleaned_data['tipo_fluido']
            rango_flujo_prueba = form.cleaned_data['rango_flujo_prueba']
            iam = form.cleaned_data['iam']
            volumen = form.cleaned_data['volumen']
            relacion_aspecto = form.cleaned_data['relacion_aspecto']
            material_almacenamiento = form.cleaned_data['material_almacenamiento']
            material_aislamiento = form.cleaned_data['material_aislamiento']
            efectividad = form.cleaned_data['efectividad']
            costo_combustible = form.cleaned_data['costo_combustible']
            unidad_costo_combustible = form.cleaned_data['unidad_costo_combustible']
            iam_longitudinal = form.cleaned_data['iam_longitudinal']
            
            
            
            raw_results = {'sim_name': nombre_simulacion, 'location': nombre_ubicacion,'shema': esquema, 'integration_scheme_initials': siglas_esquema,'sector':sector,
                           'latitude': ubicacion_data['latitud'], 'longitude': ubicacion_data['longitud'], 'fuel_name': combustible, 'operation_start': ini_jornada, 'operation_end': term_jornada, 'yearly_demand': demanda_anual, 'yearly_demand_unit': unidad_demanda,
                           'demand_monday': demanda_lun, 'demand_tuesday': demanda_mar, 'demand_wednesday': demanda_mie,
                           'demand_thursday': demanda_jue, 'demand_friday': demanda_vie, 'demand_saturday': demanda_sab, 'demand_sunday':  demanda_dom, 'demand_january': demanda_enero,
                           'demand_february': demanda_febrero, 'demand_march': demanda_marzo, 'demand_april': demanda_abril, 'demand_may': demanda_mayo, 'demand_june': demanda_junio,
                           'demand_july': demanda_julio, 'demand_august': demanda_agosto, 'demand_september': demanda_septiembre, 'demand_october': demanda_octubre,
                           'demand_november': demanda_noviembre, 'demand_december': demanda_diciembre, 'boiler_nominal_power': potencia_caldera,
                           'boiler_nominal_power_units': unidad_potencia,  'boiler_pressure': presion_caldera, 'boiler_pressure_units': unidad_presion, 'boiler_type': tipo_caldera,
                           'return_inlet_temperature': temperatura_retorno, 'temperature_january': t_enero,
                           'temperature_february': t_febrero, 'temperature_march': t_marzo, 'temperature_april': t_abril, 'temperature_may': t_mayo, 'temperature_june': t_junio,
                           'temperature_july': t_julio, 'temperature_august': t_agosto, 'temperature_september': t_septiembre, 'temperature_october': t_octubre,
                           'temperature_november': t_noviembre, 'temperature_december': t_diciembre, 'outlet_temperature': t_salida, 'aperture_area': area_apertura,
                           'coll_n0': eficiencia_optica, 'coll_a2': coef_per_lineales, 'coll_a1': coef_per_cuadraticas, 'coll_price': precio_colector,  'coll_rows': cantidad_bat,
                           'total_collectors': total_colectores,  'colls_per_row': col_bat, 'field_land_area': sup_colectores, 'coll_tilt': inclinacion_col, 'coll_azimuth': azimut,
                           'field_mass_flow': flujo_masico, 'field_mass_flow_units': unidad_flujo_masico, 'fluid': tipo_fluido, 'field_mass_flow_range': rango_flujo_prueba,
                           'iam': iam,'longitudinal_iam': iam_longitudinal ,'tank_volume': volumen, 'tank_AR': relacion_aspecto, 'tank_material': material_almacenamiento, 'tank_isulation_material': material_aislamiento,
                           'HX_eff': efectividad, 'fuel_cost': costo_combustible, 'fuel_cost_units': unidad_costo_combustible, 'boiler_efficiency': eficiencia_caldera}


            raw_results_json = json.dumps(raw_results, cls=DjangoJSONEncoder)
            
            # Crea y guarda una instancia de Simulaciones asociada al usuario autenticado
            simulacion = Simulaciones(id_user=request.user, resultado= raw_results_json)
            simulacion.save()
            messages.success(request, f'La simulación {nombre_simulacion} ha sido creada correctamente')

            # Llama a la función simulate_system con los datos
            Result = simulate_system( raw_results_json)

            return render(request, 'results.html', {})
        else:
            form = SimForm(request.POST)
    else:
        form = SimForm()

    return render(request, 'simulacion.html', {'form': form, 'datos': datos, 'profile': profile, 'esquema_list': esquema_list})


# def resultados(request,Result):
def results(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    # plt.figure()
    # plt.plot(Result['t'], Result['T_out_system'])
    # plt.show()

    #Heat_Map_bokeh(Result, 'T_out_system')

    #np.savez('Result2.npz', **Result)

    return render(request, 'results.html', {})


# Detalle de una simulación
@login_required
def simulacion_detail(request, id):
    profile = Profile.objects.get(user=request.user)
    simulacion = get_object_or_404(Simulaciones, id_simulacion=id)
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'simulacion_detail.html', {'simulacion': simulacion, 'profile': profile})

# Eliminar una simulación
@login_required
def simulacion_delete(request, id):
    simulacion = get_object_or_404(Simulaciones, id_simulacion=id)
    if request.method == 'POST':
        simulacion.delete()
        messages.success(request, f'La simulación {simulacion.nombre_simulacion} ha sido eliminada correctamente')
        return redirect('dashboard')
    return render(request, 'simulacion_confirm_delete.html', {'simulacion': simulacion})

# Actualizar una simulación
@login_required
def simulacion_update(request, id):
    profile = Profile.objects.get(user=request.user)
    simulacion = get_object_or_404(Simulaciones, id_simulacion=id)
    form = SimForm(request.POST or None, instance=simulacion)
    if form.is_valid():
        form.save()
        messages.success(request, f'La simulación {simulacion.nombre_simulacion} ha sido actualizada correctamente')
        return redirect('simulacion_detail', id=simulacion.id)
    return render(request, 'simulacion_edit.html', {'form': form, 'simulacion': simulacion, 'profile': profile})