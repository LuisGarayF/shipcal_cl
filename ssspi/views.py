from django.shortcuts import render,redirect, get_object_or_404
import os
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from ssspi.forms import *
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse, HttpResponseNotAllowed,FileResponse
from django.core.mail import send_mail, BadHeaderError
from ssspi.models import *
from Simulacion.Run_Simulation import simulate_system
import json
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from django.core.serializers.json import DjangoJSONEncoder
from django.views.static import serve
from Simulacion.apiern import consultar_api


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
    simulaciones = FormSim.objects.filter(simulacion__id_user=request.user).select_related('simulacion')
    return render(request, 'dashboard.html', {'profile': profile, 'simulaciones': simulaciones})

def descargar_archivo(request, simulacion_id):
    
    simulacion = Simulaciones.objects.get(id=simulacion_id)
    ubicacion = simulacion.ubicacion    
    consultar_api(ubicacion.latitud_personalizada, ubicacion.longitud_personalizada, simulacion_id)
    
    try:

        archivo_tmy = ArchivoTMY.objects.get(simulacion_id=simulacion_id)
    
    except ArchivoTMY.DoesNotExist:
        messages.error(request, 'El archivo no se encuentra en la base de datos.')
        return redirect('dashboard')
    
    archivo = archivo_tmy.archivo

    ruta_archivo = archivo.path

    response = FileResponse(open(ruta_archivo, 'rb'))

    return response


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
    
    

    raw_results = {}
    
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
                ubicacion.latitud_personalizada = float(form.cleaned_data['latitud'])
                ubicacion.longitud_personalizada = float(form.cleaned_data['longitud'])
                ubicacion.save()


                # Crear un diccionario con los campos relevantes de la ubicación
                ubicacion_data = {
                    'latitud': ubicacion.latitud_personalizada,
                    'longitud': ubicacion.longitud_personalizada,
                }

            
            esquema = form.cleaned_data['esquema']
            siglas_esquema = form.cleaned_data['siglas_esquema']
            combustible = form.cleaned_data['combustible']
            demanda_anual = form.cleaned_data['demanda_anual']

            # Si se ha ingresado la demanda anual, establecer ese valor para todos los campos de demanda mensuales
            if demanda_anual:
                demanda_enero = demanda_febrero = demanda_marzo = demanda_abril = demanda_mayo = demanda_junio = \
                    demanda_julio = demanda_agosto = demanda_septiembre = demanda_octubre = demanda_noviembre = \
                    demanda_diciembre = demanda_anual

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

            # Si se ha ingresado la demanda anual, establecer ese valor para todos los campos de demanda mensuales
            if temperatura_retorno:
                t_enero = t_febrero = t_marzo = t_abril = t_mayo = t_junio = \
                    t_julio = t_agosto = t_septiembre = t_octubre = t_noviembre = \
                    t_diciembre = temperatura_retorno

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
            col_bat = form.cleaned_data['col_bat']

            # Calcular el valor de sup_colectores
            sup_colectores = round(area_apertura * col_bat * cantidad_bat * 1.3, 3)
            
            # Calcular el valor de total_colectores
            total_colectores = col_bat * cantidad_bat

            total_colectores = form.cleaned_data['total_colectores']
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

                
            # Agregar los valores al diccionario raw_results con claves personalizadas
            raw_results['sim_name'] = nombre_simulacion
            raw_results['sector'] = sector
            raw_results['latitude'] = ubicacion_data['latitud']
            raw_results['longitude'] = ubicacion_data['longitud']
            raw_results['shema'] = esquema
            raw_results['integration_scheme_initials'] = siglas_esquema
            raw_results['fuel_name'] = combustible
            raw_results['operation_start'] = ini_jornada
            raw_results['operation_end'] = term_jornada
            raw_results['yearly_demand'] = demanda_anual
            raw_results['yearly_demand_unit'] = unidad_demanda
            raw_results['demand_monday'] = demanda_lun
            raw_results['demand_tuesday'] = demanda_mar
            raw_results['demand_wednesday'] = demanda_mie
            raw_results['demand_thursday'] = demanda_jue
            raw_results['demand_friday'] = demanda_vie
            raw_results['demand_saturday'] = demanda_sab
            raw_results['demand_sunday'] = demanda_dom
            raw_results['demand_january'] = demanda_enero
            raw_results['demand_february'] = demanda_febrero
            raw_results['demand_march'] = demanda_marzo
            raw_results['demand_april'] = demanda_abril
            raw_results['demand_may'] = demanda_mayo
            raw_results['demand_june'] = demanda_junio
            raw_results['demand_july'] = demanda_julio
            raw_results['demand_august'] = demanda_agosto
            raw_results['demand_september'] = demanda_septiembre
            raw_results['demand_october'] = demanda_octubre
            raw_results['demand_november'] = demanda_noviembre
            raw_results['demand_december'] = demanda_diciembre
            raw_results['boiler_nominal_power'] = potencia_caldera
            raw_results['boiler_nominal_power_units'] = unidad_potencia
            raw_results['boiler_pressure'] = presion_caldera
            raw_results['boiler_pressure_units'] = unidad_presion
            raw_results['boiler_type'] = tipo_caldera
            raw_results['return_inlet_temperature'] = temperatura_retorno
            raw_results['temperature_january'] = t_enero
            raw_results['temperature_february'] = t_febrero
            raw_results['temperature_march'] = t_marzo
            raw_results['temperature_april'] = t_abril
            raw_results['temperature_may'] = t_mayo
            raw_results['temperature_june'] = t_junio
            raw_results['temperature_july'] = t_julio
            raw_results['temperature_august'] = t_agosto
            raw_results['temperature_september'] = t_septiembre
            raw_results['temperature_october'] = t_octubre
            raw_results['temperature_november'] = t_noviembre
            raw_results['temperature_december'] = t_diciembre
            raw_results['outlet_temperature'] = t_salida
            raw_results['aperture_area'] = area_apertura
            raw_results['coll_n0'] = eficiencia_optica
            raw_results['coll_a2'] = coef_per_lineales
            raw_results['coll_a1'] = coef_per_cuadraticas
            raw_results['coll_price'] = precio_colector
            raw_results['coll_rows'] = cantidad_bat
            raw_results['total_collectors'] = total_colectores
            raw_results['colls_per_row'] = col_bat
            raw_results['field_land_area'] = sup_colectores
            raw_results['coll_tilt'] = inclinacion_col
            raw_results['coll_azimuth'] = azimut
            raw_results['field_mass_flow'] = flujo_masico
            raw_results['field_mass_flow_units'] = unidad_flujo_masico
            raw_results['fluid'] = tipo_fluido
            raw_results['field_mass_flow_range'] = rango_flujo_prueba
            raw_results['iam'] = iam
            raw_results['longitudinal_iam'] = iam_longitudinal
            raw_results['tank_volume'] = volumen
            raw_results['tank_AR'] = relacion_aspecto
            raw_results['tank_material'] = material_almacenamiento
            raw_results['tank_isulation_material'] = material_aislamiento
            raw_results['HX_eff'] = efectividad
            raw_results['fuel_cost'] = costo_combustible
            raw_results['fuel_cost_units'] = unidad_costo_combustible
            raw_results['boiler_efficiency'] = eficiencia_caldera


            # Crea y guarda una instancia de Simulaciones asociada al usuario autenticado
            simulacion = Simulaciones(id_user=request.user, resultado= raw_results)
            simulacion.save()
            messages.success(request, f'La simulación {nombre_simulacion} ha sido creada correctamente')

            simulacion_id = simulacion.id_simulacion

            consultar_api(ubicacion.latitud_personalizada, ubicacion.longitud_personalizada, simulacion_id)



            # Llama a la función simulate_system con los datos
            Result = simulate_system(raw_results, simulacion_id, ubicacion.latitud_personalizada, ubicacion.longitud_personalizada)

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
    form_sim = get_object_or_404(FormSim, id=id)
    return render(request, 'simulacion_detail.html', {'simulacion': form_sim.simulacion, 'profile': profile})

@login_required
def simulacion_delete(request, id):
    form_sim = get_object_or_404(FormSim, id=id)
    if request.method == 'POST':
        form_sim.delete()
        #messages.success(request, f'La simulación {simulacion.nombre_simulacion} ha sido eliminada correctamente')
        return redirect('dashboard')
    else:
        return HttpResponseNotAllowed(['POST'])  # Solo se aceptan solicitudes POST

# Actualizar una simulación
@login_required
def simulacion_update(request, id):
    profile = Profile.objects.get(user=request.user)
    form_sim = get_object_or_404(FormSim, id=id)
    form = SimForm(request.POST or None, instance=form_sim.simulacion)
    if form.is_valid():
        form.save()
        #messages.success(request, f'La simulación {simulacion.nombre_simulacion} ha sido actualizada correctamente')
        return redirect('simulacion_detail', id=form_sim.id)
    return render(request, 'simulacion_update.html', {'form': form, 'simulacion': form_sim.simulacion, 'profile': profile})