# -*- coding: utf-8 -*-
"""
Created on Sun Nov  6 10:35:24 2022

@author: adria

@modified:LGaray
"""

from Simulacion.Solar_Field_San_Joaquin import Solar_Field_parallel, Solar_Field_series
from Simulacion.Class_Storage import Storage_Tank
from Simulacion.Class_Boiler import Boiler_HX
from Simulacion.Class_Properties import Properties_water
from Simulacion.simulation_functions import corr_exp_solar, Irradiance_2
from math import cos, pi
import numpy as np
from scipy.interpolate import interp1d
from matplotlib import pyplot as plt
from timeit import default_timer
from bokeh.io import export_png
from bokeh.plotting import figure, show, output_file, save
from bokeh.models import LinearColorMapper, ColorBar
from bokeh.embed import components
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

system_params = {}

def getdict():
    
    file = f'{BASE_DIR}\Simulacion\dic\dict.py'
    
    with open(file, 'r', encoding="utf-8") as f:
        system_params= f.read()
        #print(system_params)
    return system_params
        




def Heat_Map_bokeh(Result, variable):
    print('Creando gráfico Heat Map...')
    if len(Result[variable])%365 != 0:
        print('Número de elementos en el vector de resultados no es válido')
        return
    time_steps_per_day = int( len( Result[variable] )/365 )
    matrix = np.reshape(Result[variable], ( 365, time_steps_per_day ) )
    matrix = np.transpose(matrix)
    color = LinearColorMapper(palette = "Turbo256", low = min(Result[variable]), high = max(Result[variable]))
    p = figure(tools="pan,wheel_zoom,box_zoom,reset",
               width=800,height=600, x_axis_label = 'Día', y_axis_label = 'Hora del día')
    p.title.text = variable + ' Map'
    p.title.text_font_size = '15pt'
    p.xaxis.axis_label = 'Día'
    p.xaxis.axis_label_text_font_size = "15pt"
    p.yaxis.axis_label = 'Hora del día'
    p.yaxis.axis_label_text_font_size = "15pt"
    
    p.image(image=[matrix], x=0, y=0, dw=10, dh=10, color_mapper = color, level="image")
        
    p.yaxis.ticker = [ 0, 10/6, 10/3,
                      5, 10*2/3,
                      10*5/6, 10]
    p.yaxis.major_label_overrides = { 0: '0',
                                      10/6: '4',
                                      10/3: '8',
                                      5: '12',
                                      10*2/3: '16',
                                      10*5/6: '20',
                                      10: '24'}
    p.xaxis.ticker = [ 0, 10*50/365, 10*100/365,
                      10*150/365, 10*200/365,
                      10*250/365, 10*300/365, 10*350/365]
    p.xaxis.major_label_overrides = { 0: '0',
                                      10*50/365: '50',
                                      10*100/365: '100',
                                      10*150/365: '150',
                                      10*200/365: '200',
                                      10*250/365: '250',
                                      10*300/365: '300',
                                      10*350/365: '350'}
    
    cb = ColorBar(color_mapper = color, location = (5,6))
    p.add_layout(cb, 'right')
    output_file(filename=f'{BASE_DIR}\FE1\\templates\heatmap_graph.html')
    
    #show(p) MUESTRA EL ARCHIVO EN UNA VENTANA DIFERENTE
    save(p)
    export_png(p, filename=f'{BASE_DIR}\FE1\static\img\heatmap_graph.png')

def Heat_Map(Result, variable):
    if len(Result[variable])%365 != 0:
        print('Número de elementos en el vector de resultados no es válido')
        return
    time_steps_per_day = int( len( Result[variable] )/365 )
    yticks = [ 0, int(time_steps_per_day/6), int(time_steps_per_day/3),
               int(time_steps_per_day/2), int(time_steps_per_day*2/3),
               int(time_steps_per_day*5/6), time_steps_per_day]
    ylabels = [0,4,8,12,16,20,24]
    matrix = np.reshape(Result[variable], ( 365, time_steps_per_day ) )
    matrix = np.transpose(matrix)
    plt.matshow(matrix, cmap=plt.cm.jet)
    plt.yticks(yticks, ylabels)
    plt.colorbar()
    plt.show()

def monthly_work_hours(month, t_start, t_end, work_day_list):
    if t_start == t_end:
        daily_working_hours = 24
    else:
        daily_working_hours = t_end - t_start
    work_hours = 0
    for day in range(1,366):
        if month_from_day(day) == month and week_day_from_day(day) in work_day_list:
            work_hours = work_hours + daily_working_hours
    return work_hours

def monthly_flows(total_demand, monthly_demands, monthly_temperatures, work_day_list, t_start, t_end, T_set):
    total_monthly = sum([ monthly_demands[i] for i in monthly_demands ])
    cp = 4.184
    month_flows = {}
    for month in monthly_demands:
        if monthly_work_hours(month, t_start, t_end, work_day_list) == 0:
            month_flows[month] = 0
        else:
            demand_month = total_demand*monthly_demands[month]/total_monthly
            m_month = demand_month/(cp*(T_set - monthly_temperatures[month]))
            month_flows[month] = m_month/monthly_work_hours(month, t_start, t_end, work_day_list)
    return month_flows

def T_mains_profile(T_max, T_min):
    T_mean = (T_max + T_min)/2
    amplitude = (T_max - T_min)/2
    return [ T_mean + amplitude*cos(2*pi*t/8760) for t in range(8760) ]

def convert_power(original_value, original_units):
    if original_units == 'kJ/h':
        return original_value
    if original_units == 'kW':
        return original_value*3600

def convert_flow(original_value, original_units):
    if original_units == 'kg/h' or original_units == 'l/h':
        return original_value
    if original_units == 'kg/min' or original_units == 'l/min':
        return original_value*60
    if original_units == 'kg/s' or original_units == 'l/s':
        return original_value*3600
    if original_units == 'gpm':
        return 227.125*original_value
    
def convert_pressure(original_value, original_units):
    if original_units == 'bar':
        return original_value
    if original_units == 'MPa':
        return original_value*10
    if original_units == 'psi':
        return original_value*0.06895

def convert_demand(original_value, original_units, fuel, boiler_type, boiler_efficiency):
    if original_units == 'MJ':
        return original_value*1000*boiler_efficiency
    if original_units == 'kWh':
        return original_value*3600*boiler_efficiency
    if original_units == 'MWh':
        return original_value*3600000*boiler_efficiency
    if original_units == 'BTU':
        return original_value*1.055*boiler_efficiency
    if original_units == 'kcal':
        return original_value*4.184*boiler_efficiency
    if (fuel == 'Propano' or fuel == 'Butano') and original_units == 'l':
        raise ValueError('No se puede expresar la demanda en litros cuando se usa un gas como combustible')
    if fuel == 'Electricidad':
        raise ValueError('El consumo eléctrico no puede expresarse en términos de kg, l ó m3')
    if fuel == 'Propano':
        fuel_density = 1.83
        if boiler_type == 'Condensación':
            fuel_heat_value = 50426
        else:
            fuel_heat_value = 46367
    if fuel == 'Butano':
        fuel_density = 2.52
        if boiler_type == 'Condensación':
            fuel_heat_value = 49652
        else:
            fuel_heat_value = 45765
    if fuel == 'Biomasa':
        fuel_density = 800
        if boiler_type == 'Condensación':
            fuel_heat_value = 19000
        else:
            fuel_heat_value = 17000
    if fuel == 'Diesel':
        fuel_density = 850
        if boiler_type == 'Condensación':
            fuel_heat_value = 45600
        else:
            fuel_heat_value = 42600
    if original_units == 'L':
        kJ_per_litre = fuel_density*fuel_heat_value/1000
        return kJ_per_litre*original_value*boiler_efficiency
    if original_units == 'm3':
        kJ_per_m3 = fuel_density*fuel_heat_value
        return kJ_per_m3*original_value*boiler_efficiency
    if original_units == 'kg':
        return fuel_heat_value*original_value*boiler_efficiency

def compute_cost_per_kJ(fuel, cost, cost_units, boiler_type):
    if cost_units == '$/kWh':
        return cost/3600
    if fuel == 'Electricidad':
        raise ValueError('El costo de la electricidad solo puede expresarse en $/kWh')
    if (fuel == 'Propano' or fuel == 'Butano') and cost_units == '$/l':
        raise ValueError('El costo del gas no puede expresarse en $/l')
    if fuel == 'Propano':
        fuel_density = 1.83
        if boiler_type == 'Condensación':
            fuel_heat_value = 50426
        else:
            fuel_heat_value = 46367
    if fuel == 'Butano':
        fuel_density = 2.52
        if boiler_type == 'Condensación':
            fuel_heat_value = 49652
        else:
            fuel_heat_value = 45765
    if fuel == 'Biomasa':
        fuel_density = 800
        fuel_heat_value = 18000   # No option for condensing boiler
    if fuel == 'Diesel':
        fuel_density = 850
        fuel_heat_value = 42600   # No option for condensing boiler
    if cost_units == '$/L':
        kJ_per_litre = fuel_density*fuel_heat_value/1000
        litres_per_kJ = 1/kJ_per_litre
        return cost*litres_per_kJ
    if cost_units == '$/m3':
        kJ_per_m3 = fuel_density*fuel_heat_value
        m3_per_kJ = 1/kJ_per_m3
        return cost*m3_per_kJ
    if cost_units == '$/kg':
        kg_per_kJ = 1/fuel_heat_value
        return cost*kg_per_kJ

def time_from_string(string):
    List = string.split(':')
    time = int(List[0])
    if List[1] == '30':
        time = time + 0.5
    return time

def week_day_from_day(day):
    week_day = day%7
    if week_day == 1:
        return 'Monday'
    if week_day == 2:
        return 'Tuesday'
    if week_day == 3:
        return 'Wednesday'
    if week_day == 4:
        return 'Thursday'
    if week_day == 5:
        return 'Friday'
    if week_day == 6:
        return 'Saturday'
    if week_day == 0:
        return 'Sunday'

def month_from_day(day):
    if day <= 31:
        return 'January'
    if day >= 32 and day <= 59:
        return 'February'
    if day >= 60 and day <= 90:
        return 'March'
    if day >= 91 and day <= 120:
        return 'April'
    if day >= 121 and day <= 151:
        return 'May'
    if day >= 152 and day <= 181:
        return 'June'
    if day >= 182 and day <= 212:
        return 'July'
    if day >= 213 and day <= 243:
        return 'August'
    if day >= 244 and day <= 273:
        return 'September'
    if day >= 274 and day <= 304:
        return 'October'
    if day >= 305 and day <= 334:
        return 'November'
    if day >= 335:
        return 'December'

def simulate_system(system_params):
    """
    Función capaz de simular cualquiera de los dos esquemas de integración considerados.

    Parámetros
    
    La función recibe un solo diccionario como parámetro; este diccionario tiene las siguientes keys:
        - 'sector'
        - 'sim_name'
        - 'application'
        - 'processes'
        - 'location'
        - 'latitude'
        - 'longitude'
        - 'fuel_name'
        - 'yearly_demand'
        - 'yearly_demand_unit'
        - 'demand_monday'
        - 'demand_tuesday'
        - 'demand_wednesday'
        - 'demand_thursday'
        - 'demand_friday'
        - 'demand_saturday'
        - 'demand_sunday'
        - 'operation_start'
        - 'operation_end'
        - 'demand_january'
        - 'demand_february'
        - 'demand_march'
        - 'demand_april'
        - 'demand_may'
        - 'demand_june'
        - 'demand_july'
        - 'demand_august'
        - 'demand_september'
        - 'demand_october'
        - 'demand_november'
        - 'demand_december'
        - 'boiler_nominal_power'
        - 'boiler_nominal_power_units'
        - 'boiler_pressure'
        - 'boiler_pressure_units'
        - 'boiler_type'
        - 'mains_inlet_temperature'
        - 'return_inlet_temperature'
        - 'temperature_january'
        - 'temperature_february'
        - 'temperature_march'
        - 'temperature_april'
        - 'temperature_may'
        - 'temperature_june'
        - 'temperature_july'
        - 'temperature_august'
        - 'temperature_september'
        - 'temperature_october'
        - 'temperature_november'
        - 'temperature_december'
        - 'outlet_temperature'
        - 'integration_scheme_name'
        - 'integration_scheme_initials'
        - 'aperture_area'
        - 'coll_n0'
        - 'coll_price'
        - 'coll_a2'
        - 'coll_a1'
        - 'coll_iam'
        - 'coll_test_flow'
        - 'coll_rows'
        - 'colls_per_row'
        - 'coll_tilt'
        - 'coll_azimuth'
        - 'field_mass_flow'
        - 'field_mass_flow_units'
        - 'fluid'
        - 'tank_volume'
        - 'tank_AR'
        - 'tank_material'
        - 'tank_insulation_material'
        - 'HX_eff'
        - 'fuel_cost'
        - 'fuel_cost_units'
        - 'coll_type'


    Retorna:
        
        Si el párametro 'integration_scheme_initials' es igual a 'PL_L_HB', los vectores en el diccionario son:
            - 't': Valores de tiempo considerados durante la simulación (hr)
            - 'rad': radiación incidente en el campo solar (kJ / ( m^2 * hr) ),
            - 'm_demand': flujo de agua demandada (kg/hr),
            - 'T_out_system': Temperatura del agua saliendo del sistema (°C)
            - 'Q_Solar': Calor aportado por el campo solar (kJ / hr)
            - 'Field_1_Q_useful': Calor aportado por el campo solar 1 (colectores planos) (kJ / hr)
            - 'Field_2_Q_useful': Calor aportado por el campo solar 2 (tubo evacuado) (kJ / hr)
            - 'Field_1_Q_waste': Calor purgado del campo solar 1 (colectores planos) (kJ / hr)
            - 'Field_2_Q_waste': Calor purgado del campo solar 2 (tubo evacuado) (kJ / hr)
            
        Si el párametro 'integration_scheme_initials' es igual a 'SL_L_SC', los vectores en el diccionario son:
            - 't': Valores de tiempo considerados durante la simulación (hr)
            - 'T_out_system': Temperatura del agua saliendo del sistema (°C)
            - 'T_out_Solar_Field': Temperatura del agua saliendo del intercambiador de calor del campo solar (flujo demandado) (°C)
            - 'T_out_Tank': Temperatura del agua saliendo del estanque de almacenamiento (°C)
            - 'Q_Solar':  Calor total aportado por el campo solar (colectores planos y de tubo evacuado) (kJ / hr)
            - 'Q_Boiler': Calor aportado por el boiler (kJ / hr)
            - 'Time_step_fuel_cost': Costo del combustible consumido durante el time step ($)
            - 'Field_1_Q_useful': Calor útil aportado por el campo solar 1 (colectores planos) (kJ / hr)
            - 'Field_2_Q_useful': Calor útil aportado por el campo solar 2 (tubo evacuado) (kJ / hr)
            - 'Field_1_Q_waste': Calor purgado por el campo solar 1 (colectores planos) (kJ / hr)
            - 'Field_2_Q_waste': Calor purgado por el campo solar 2 (tubo evacuado) (kJ / hr)

    """
    print('Ejecutando simulación. Espere...')
    #getdict()
    
    boiler_efficiency = 0.8
    m_source_boiler = 1000
    frac_field_1 = 0.6
    
    yearly_energy_demand = convert_demand(system_params['yearly_demand'],
                                          system_params['yearly_demand_unit'],
                                          system_params['fuel_name'],
                                          system_params['boiler_type'], boiler_efficiency)
    
    monthly_demands = {'January': system_params['demand_january'],
                       'February': system_params['demand_february'],
                       'March': system_params['demand_march'],
                       'April': system_params['demand_april'],
                       'May': system_params['demand_may'],
                       'June': system_params['demand_june'],
                       'July': system_params['demand_july'],
                       'August': system_params['demand_august'],
                       'September': system_params['demand_september'],
                       'October': system_params['demand_october'],
                       'November': system_params['demand_november'],
                       'December': system_params['demand_december']}
    
    monthly_temperatures = {'January': system_params['temperature_january'],
                            'February': system_params['temperature_february'],
                            'March': system_params['temperature_march'],
                            'April': system_params['temperature_april'],
                            'May': system_params['temperature_may'],
                            'June': system_params['temperature_june'],
                            'July': system_params['temperature_july'],
                            'August': system_params['temperature_august'],
                            'September': system_params['temperature_september'],
                            'October': system_params['temperature_october'],
                            'November': system_params['temperature_november'],
                            'December': system_params['temperature_december']}
    
    work_day_list = []
    if system_params['demand_monday']:
        work_day_list.append('Monday')
    if system_params['demand_tuesday']:
        work_day_list.append('Tuesday')
    if system_params['demand_wednesday']:
        work_day_list.append('Wednesday')
    if system_params['demand_thursday']:
        work_day_list.append('Thursday')
    if system_params['demand_friday']:
        work_day_list.append('Friday')
    if system_params['demand_saturday']:
        work_day_list.append('Saturday')
    if system_params['demand_sunday']:
        work_day_list.append('Sunday')
        
    t_start = time_from_string(system_params['operation_start'])
    t_end = time_from_string(system_params['operation_end'])
    
    T_set = system_params['outlet_temperature']
    
    flows_dict = monthly_flows(yearly_energy_demand,
                               monthly_demands,
                               monthly_temperatures,
                               work_day_list,
                               t_start,
                               t_end,
                               T_set)
    
    climate_data_file = f'{BASE_DIR}\Simulacion\DHTMY_SAM_E_9H23YU.csv'
    #climate_data_file = f'{BASE_DIR}\General_modules\API_ERN\tmy.csv' # Archivo climatico recuperado desde la api de ERN
    latitude, longitude, UTC, Climate_Data = corr_exp_solar(climate_data_file)
    DNI_corr,Diff_corr,Diff_ground_corr=Irradiance_2(latitude, longitude, UTC, Climate_Data,
                                                     tilt = system_params['coll_tilt'],
                                                     azimuth = system_params['coll_azimuth'])
    Climate_Data['DNI']=DNI_corr.values
    Climate_Data['DHI']=Diff_corr+Diff_ground_corr
    solar_rad_profile = [ 3.6*(Climate_Data['DNI'][hour]+Climate_Data['DHI'][hour]) for hour in range(8760) ]
    solar_rad_profile.append(solar_rad_profile[0])
    solar_rad = interp1d(range(8761), solar_rad_profile)
    dry_bulb_T_profile = [ Climate_Data['Tdry'][hour] for hour in range(8760) ]
    dry_bulb_T_profile.append(dry_bulb_T_profile[0])
    dry_bulb_T = interp1d(range(8761), dry_bulb_T_profile)
    
    T_max = 20
    T_min = 15
    mains_temp = T_mains_profile(T_max, T_min)
    mains_temp.append(mains_temp[0])
    T_mains_func = interp1d(range(8761),mains_temp)
    
    time_step = 0.1
    
    propsField1 = Properties_water(4)
    propsField2 = Properties_water(3)
    propsBoiler = Properties_water(convert_pressure(system_params['boiler_pressure'], system_params['boiler_pressure_units']))
    propsSystem = Properties_water(2)
    field_type = 'series'
    system_params['integration_scheme_initials'] = 'SL_L_SC' # Quitar una vez se arregle el modelo de siglas_esquema
    Solar_Field_params = {'field_1_coll_L': system_params['aperture_area'],
                          'field_1_coll_W': 1,
                          'field_1_coll_n0': system_params['coll_n0'],
                          'field_1_coll_a1': system_params['coll_a1'],
                          'field_1_coll_a2': system_params['coll_a2'],
                          'field_1_coll_rows': system_params['coll_rows'],
                          'field_1_colls_per_row': system_params['colls_per_row'],
                          'field_2_coll_L': 2.859,
                          'field_2_coll_W': 1,
                          'field_2_coll_n0': 0.7014,
                          'field_2_coll_a1': 1.2*3.6,
                          'field_2_coll_a2': 0.008*3.6,
                          'field_2_coll_rows': 3,
                          'field_2_colls_per_row': 8,
                          'field_1_HX_effectiveness': system_params['HX_eff'],
                          'main_HX_effectiveness': system_params['HX_eff'],
                          'fluid_props_1': propsField1,
                          'fluid_props_2': propsField2,
                          'fluid_props_load': propsSystem,
                          'm_in_field': 2700,
                          'm_closed_loop': convert_flow(system_params['field_mass_flow'], system_params['field_mass_flow_units']),
                          'frac_field_1': frac_field_1}
    start = default_timer()
    if system_params['integration_scheme_initials'] == 'PL_L_HB':
        
        Result = simulate_PL_L_HB(solar_rad, dry_bulb_T, flows_dict, monthly_temperatures, work_day_list, T_mains_func, field_type,
                                  Solar_Field_params, propsSystem, t_start, t_end, time_step)
        
    if system_params['integration_scheme_initials'] == 'SL_L_SC':
        
        t_launch = 10
        m_return = 1000
        tolerance = 1e-6
        max_iterations = 100
        
        Tank_params = {'volume': system_params['tank_volume'],
                       'AR': system_params['tank_AR'],
                       'top_loss_coeff': 5,
                       'edge_loss_coeff': 5,
                       'bottom_loss_coeff': 5,
                       'N_nodes': 10,
                       'inlet_1_node': 10,
                       'outlet_1_node': 1,
                       'inlet_2_node': 1,
                       'outlet_2_node': 1,
                       'fluid_props': propsSystem,
                       'initial_temperatures': {i: 20 for i in range(1,11)  }}
        
        Boiler_params = {'boiler_efficiency': boiler_efficiency,
                         'P_max': convert_power(system_params['boiler_nominal_power'], system_params['boiler_nominal_power_units']),
                         'HX_effectiveness': system_params['HX_eff'],
                         'cost_per_kJ': compute_cost_per_kJ(system_params['fuel_name'],
                                                            system_params['fuel_cost'],
                                                            system_params['fuel_cost_units'],
                                                            system_params['boiler_type']),
                         'm_source': m_source_boiler,
                         'fluid_props_source': propsBoiler,
                         'fluid_props_load': propsSystem}

        Result = simulate_SL_L_SC(solar_rad, dry_bulb_T, flows_dict, monthly_temperatures, work_day_list, T_mains_func, field_type,
                                  Solar_Field_params, Tank_params, Boiler_params, propsSystem, T_set, t_start, t_end,
                                  m_return, time_step, t_launch, tolerance, max_iterations)
    print('--- Simulación finalizada ---') 
    print('Simulation time: '+str(default_timer()-start))
    return Result

def simulate_PL_L_HB(rad_func, T_amb_func, flows_dict, monthly_temperatures_dict, work_day_list, T_mains_func, field_type,
                     Solar_Field_params, propsSystem, t_start, t_end, time_step):
    if field_type == 'series':
        Solar_Field = Solar_Field_series(Solar_Field_params['field_1_coll_L'], Solar_Field_params['field_1_coll_W'],
                                         Solar_Field_params['field_1_coll_n0'], Solar_Field_params['field_1_coll_a1'],
                                         Solar_Field_params['field_1_coll_a2'], Solar_Field_params['field_1_coll_rows'],
                                         Solar_Field_params['field_1_colls_per_row'], Solar_Field_params['field_2_coll_L'],
                                         Solar_Field_params['field_2_coll_W'], Solar_Field_params['field_2_coll_n0'],
                                         Solar_Field_params['field_2_coll_a1'], Solar_Field_params['field_2_coll_a2'],
                                         Solar_Field_params['field_2_coll_rows'], Solar_Field_params['field_2_colls_per_row'],
                                         Solar_Field_params['field_1_HX_effectiveness'], Solar_Field_params['main_HX_effectiveness'],
                                         Solar_Field_params['fluid_props_1'], Solar_Field_params['fluid_props_2'],
                                         Solar_Field_params['fluid_props_load'], Solar_Field_params['m_in_field'],
                                         Solar_Field_params['m_closed_loop'])
    if field_type == 'parallel':
        Solar_Field = Solar_Field_parallel(Solar_Field_params['field_1_coll_L'], Solar_Field_params['field_1_coll_W'],
                                           Solar_Field_params['field_1_coll_n0'], Solar_Field_params['field_1_coll_a1'],
                                           Solar_Field_params['field_1_coll_a2'], Solar_Field_params['field_1_coll_rows'],
                                           Solar_Field_params['field_1_colls_per_row'], Solar_Field_params['field_2_coll_L'],
                                           Solar_Field_params['field_2_coll_W'], Solar_Field_params['field_2_coll_n0'],
                                           Solar_Field_params['field_2_coll_a1'], Solar_Field_params['field_2_coll_a2'],
                                           Solar_Field_params['field_2_coll_rows'], Solar_Field_params['field_2_colls_per_row'],
                                           Solar_Field_params['field_1_HX_effectiveness'], Solar_Field_params['main_HX_effectiveness'],
                                           Solar_Field_params['fluid_props_1'], Solar_Field_params['fluid_props_2'],
                                           Solar_Field_params['fluid_props_load'], Solar_Field_params['m_in_field'],
                                           Solar_Field_params['m_closed_loop'], Solar_Field_params['frac_field_1'])
    
    Result = []
    t = 0
    while t < 8760:
        
        day_time = t%24
        day_of_year = int(t/24) + 1
        current_month = month_from_day(day_of_year)
        current_week_day = week_day_from_day(day_of_year)
        
        rad = float(rad_func(t))
        m_demand = flows_dict[current_month]
        
        if current_week_day in work_day_list and ((day_time >= t_start and day_time <= t_end) or t_start == t_end) and m_demand > 0:
            system_on = True
        else:
            system_on = False
        
        if system_on:
            T_amb = float(T_amb_func(t))
            T_in = monthly_temperatures_dict[current_month]
            T_mains = float(T_mains_func(t))
            h_in = propsSystem.T_to_h(T_in)
            h_mains = propsSystem.T_to_h(T_mains)
            
            Solar_Field_outputs = Solar_Field.compute_outputs(m_demand, h_in, h_mains, h_mains, h_mains, rad, T_amb)
            
            Result.append({'t': t,
                           'rad': rad,
                           'm_demand': m_demand,
                           'T_out_system': propsSystem.h_to_T(Solar_Field_outputs['h_out_load']),
                           'Q_Solar': Solar_Field_outputs['Q_useful_total'],
                           'Field_1_Q_useful': Solar_Field_outputs['Field_1_Power'],
                           'Field_2_Q_useful': Solar_Field_outputs['Field_2_Power'],
                           'Field_1_Q_waste': Solar_Field_outputs['Q_waste_Field_1'],
                           'Field_2_Q_waste': Solar_Field_outputs['Q_waste_Field_2']})
        else:
            T_in = monthly_temperatures_dict[current_month]
            Result.append({'t': t,
                           'rad': rad,
                           'm_demand': m_demand,
                           'T_out_system': T_in,
                           'Q_Solar': 0,
                           'Field_1_Q_useful': 0,
                           'Field_2_Q_useful': 0,
                           'Field_1_Q_waste': 0,
                           'Field_2_Q_waste': 0})
        t = t + time_step
        t = round(t, 3)
    
    Result2 = {}
    for key in Result[0]:
        Result2[key] = [ Result[i][key] for i in range(len(Result)) ]
    return Result2

def simulate_SL_L_SC(rad_func, T_amb_func, flows_dict, monthly_temperatures_dict, work_day_list, T_mains_func, field_type,
                     Solar_Field_params, Tank_params, Boiler_params,
                     propsSystem, T_set_Boiler, t_start, t_end, m_return, time_step, t_launch,
                     tolerance, max_iterations):
    
    if field_type == 'series':
        Solar_Field = Solar_Field_series(Solar_Field_params['field_1_coll_L'], Solar_Field_params['field_1_coll_W'],
                                         Solar_Field_params['field_1_coll_n0'], Solar_Field_params['field_1_coll_a1'],
                                         Solar_Field_params['field_1_coll_a2'], Solar_Field_params['field_1_coll_rows'],
                                         Solar_Field_params['field_1_colls_per_row'], Solar_Field_params['field_2_coll_L'],
                                         Solar_Field_params['field_2_coll_W'], Solar_Field_params['field_2_coll_n0'],
                                         Solar_Field_params['field_2_coll_a1'], Solar_Field_params['field_2_coll_a2'],
                                         Solar_Field_params['field_2_coll_rows'], Solar_Field_params['field_2_colls_per_row'],
                                         Solar_Field_params['field_1_HX_effectiveness'], Solar_Field_params['main_HX_effectiveness'],
                                         Solar_Field_params['fluid_props_1'], Solar_Field_params['fluid_props_2'],
                                         Solar_Field_params['fluid_props_load'], Solar_Field_params['m_in_field'],
                                         Solar_Field_params['m_closed_loop'])
    if field_type == 'parallel':
        Solar_Field = Solar_Field_parallel(Solar_Field_params['field_1_coll_L'], Solar_Field_params['field_1_coll_W'],
                                           Solar_Field_params['field_1_coll_n0'], Solar_Field_params['field_1_coll_a1'],
                                           Solar_Field_params['field_1_coll_a2'], Solar_Field_params['field_1_coll_rows'],
                                           Solar_Field_params['field_1_colls_per_row'], Solar_Field_params['field_2_coll_L'],
                                           Solar_Field_params['field_2_coll_W'], Solar_Field_params['field_2_coll_n0'],
                                           Solar_Field_params['field_2_coll_a1'], Solar_Field_params['field_2_coll_a2'],
                                           Solar_Field_params['field_2_coll_rows'], Solar_Field_params['field_2_colls_per_row'],
                                           Solar_Field_params['field_1_HX_effectiveness'], Solar_Field_params['main_HX_effectiveness'],
                                           Solar_Field_params['fluid_props_1'], Solar_Field_params['fluid_props_2'],
                                           Solar_Field_params['fluid_props_load'], Solar_Field_params['m_in_field'],
                                           Solar_Field_params['m_closed_loop'], Solar_Field_params['frac_field_1'])
    
    Tank = Storage_Tank(Tank_params['volume'], Tank_params['AR'],
                        Tank_params['top_loss_coeff'], Tank_params['edge_loss_coeff'],
                        Tank_params['bottom_loss_coeff'], Tank_params['N_nodes'],
                        Tank_params['inlet_1_node'], Tank_params['outlet_1_node'],
                        Tank_params['inlet_2_node'], Tank_params['outlet_2_node'],
                        Tank_params['fluid_props'], Tank_params['initial_temperatures'])
    
    Boiler = Boiler_HX(Boiler_params['boiler_efficiency'], Boiler_params['P_max'],
                       Boiler_params['HX_effectiveness'], Boiler_params['cost_per_kJ'],
                       Boiler_params['m_source'], Boiler_params['fluid_props_source'],
                       Boiler_params['fluid_props_load'])
    
    t = 8760 - t_launch*24
    while t < 8760:
        
        day_time = t%24
        day_of_year = int(t/24) + 1
        current_month = month_from_day(day_of_year)
        current_week_day = week_day_from_day(day_of_year)
        
        rad = float(rad_func(t))
        m_demand = flows_dict[current_month]
        
        if current_week_day in work_day_list and ((day_time >= t_start and day_time <= t_end) or t_start == t_end) and m_demand > 0:
            system_on = True
        else:
            system_on = False
        
        if system_on:
            T_amb = float(T_amb_func(t))
            T_in = monthly_temperatures_dict[current_month]
            T_mains = float(T_mains_func(t))
            h_in = propsSystem.T_to_h(T_in)
            h_mains = propsSystem.T_to_h(T_mains)
            Solar_Field_outputs = Solar_Field.compute_outputs(m_demand, h_in,
                                                              h_mains, h_mains,
                                                              h_mains, rad, T_amb)
            Tank_outputs = Tank.compute_outputs(m_demand, Solar_Field_outputs['h_out_load'],
                                                m_return, propsSystem.T_to_h(T_set_Boiler),
                                                T_amb, time_step)
            
            Boiler_h_in = (m_demand*Tank_outputs['outlet_1_h'] + m_return*Tank_outputs['outlet_2_h'])/(m_demand + m_return)
            
            Boiler_outputs = Boiler.compute_outputs(m_demand + m_return, Boiler_h_in, T_set_Boiler, h_mains, time_step)
            
            if Boiler_outputs['source_sat'] or Boiler_outputs['excess_temp'] or Boiler_outputs['P_max_reached']:
                h_in_Tank_return = Boiler_outputs['h_out']
                it = 0
                while True:
                    Tank_outputs = Tank.compute_outputs(m_demand, Solar_Field_outputs['h_out_load'],
                                                        m_return, h_in_Tank_return,
                                                        T_amb, time_step)
                    
                    Boiler_h_in = (m_demand*Tank_outputs['outlet_1_h'] + m_return*Tank_outputs['outlet_2_h'])/(m_demand + m_return)
                    
                    Boiler_outputs = Boiler.compute_outputs(m_demand + m_return, Boiler_h_in, T_set_Boiler, h_mains, time_step)
                    
                    it = it + 1
                    
                    if abs(Boiler_outputs['h_out'] - h_in_Tank_return)/h_in_Tank_return < tolerance:
                        maxIt = False
                        break
                    if it == max_iterations:
                        maxIt = True
                        break
                    h_in_Tank_return = Boiler_outputs['h_out']
        else:
            T_in = monthly_temperatures_dict[current_month]
            h_in = propsSystem.T_to_h(T_in)
            T_amb = float(T_amb_func(t))
            Tank_outputs = Tank.compute_outputs(0, h_in,
                                                0, h_in,
                                                T_amb, time_step)
        Tank.update_temperature()
        t = t + time_step
        t = round(t, 3)

    Result = []
    t = 0
    while t < 8760:
        
        day_time = t%24
        day_of_year = int(t/24) + 1
        current_month = month_from_day(day_of_year)
        current_week_day = week_day_from_day(day_of_year)
        
        rad = float(rad_func(t))
        m_demand = flows_dict[current_month]
        
        if current_week_day in work_day_list and ((day_time >= t_start and day_time <= t_end) or t_start == t_end) and m_demand > 0:
            system_on = True
        else:
            system_on = False
        
        if system_on:
            T_amb = float(T_amb_func(t))
            T_in = monthly_temperatures_dict[current_month]
            T_mains = float(T_mains_func(t))
            h_in = propsSystem.T_to_h(T_in)
            h_mains = propsSystem.T_to_h(T_mains)
            Solar_Field_outputs = Solar_Field.compute_outputs(m_demand, h_in,
                                                              h_mains, h_mains,
                                                              h_mains, rad, T_amb)
            Tank_outputs = Tank.compute_outputs(m_demand, Solar_Field_outputs['h_out_load'],
                                                m_return, propsSystem.T_to_h(T_set_Boiler),
                                                T_amb, time_step)
            
            Boiler_h_in = (m_demand*Tank_outputs['outlet_1_h'] + m_return*Tank_outputs['outlet_2_h'])/(m_demand + m_return)
            
            Boiler_outputs = Boiler.compute_outputs(m_demand + m_return, Boiler_h_in, T_set_Boiler, h_mains, time_step)
            
            if Boiler_outputs['source_sat'] or Boiler_outputs['excess_temp'] or Boiler_outputs['P_max_reached']:
                h_in_Tank_return = Boiler_outputs['h_out']
                it = 0
                while True:
                    Tank_outputs = Tank.compute_outputs(m_demand, Solar_Field_outputs['h_out_load'],
                                                        m_return, h_in_Tank_return,
                                                        T_amb, time_step)
                    
                    Boiler_h_in = (m_demand*Tank_outputs['outlet_1_h'] + m_return*Tank_outputs['outlet_2_h'])/(m_demand + m_return)
                    
                    Boiler_outputs = Boiler.compute_outputs(m_demand + m_return, Boiler_h_in, T_set_Boiler, h_mains, time_step)
                    
                    it = it + 1
                    
                    if abs(Boiler_outputs['h_out'] - h_in_Tank_return)/h_in_Tank_return < tolerance:
                        maxIt = False
                        break
                    if it == max_iterations:
                        maxIt = True
                        break
                    h_in_Tank_return = Boiler_outputs['h_out']
            Result.append({'t': t,
                           'rad': rad,
                           'm_demand': m_demand,
                           'T_out_system': propsSystem.h_to_T(Boiler_outputs['h_out']),
                           'T_out_Solar_Field': propsSystem.h_to_T(Solar_Field_outputs['h_out_load']),
                           'T_out_Tank': propsSystem.h_to_T(Tank_outputs['outlet_1_h']),
                           'Q_Solar': Solar_Field_outputs['Q_useful_total'],
                           'Q_Boiler': Boiler_outputs['Q_delivered'],
                           'Time_step_fuel_cost': Boiler_outputs['cost_time_step'],
                           'Field_1_Q_useful': Solar_Field_outputs['Field_1_Power'],
                           'Field_2_Q_useful': Solar_Field_outputs['Field_2_Power'],
                           'Field_1_Q_waste': Solar_Field_outputs['Q_waste_Field_1'],
                           'Field_2_Q_waste': Solar_Field_outputs['Q_waste_Field_2']})
        else:
            T_in = monthly_temperatures_dict[current_month]
            h_in = propsSystem.T_to_h(T_in)
            T_amb = float(T_amb_func(t))
            Tank_outputs = Tank.compute_outputs(0, h_in,
                                                0, h_in,
                                                T_amb, time_step)
            Result.append({'t': t,
                           'rad': rad,
                           'm_demand': m_demand,
                           'T_out_system': propsSystem.h_to_T(Tank_outputs['outlet_1_h']),
                           'T_out_Solar_Field': None,
                           'T_out_Tank': propsSystem.h_to_T(Tank_outputs['outlet_1_h']),
                           'Q_Solar': 0,
                           'Q_Boiler': 0,
                           'Time_step_fuel_cost': 0,
                           'Field_1_Q_useful': 0,
                           'Field_2_Q_useful': 0,
                           'Field_1_Q_waste': 0,
                           'Field_2_Q_waste': 0})
        Tank.update_temperature()
        t = t + time_step
        t = round(t, 3)
    
    Result2 = {}
    for key in Result[0]:
        Result2[key] = [ Result[i][key] for i in range(len(Result)) ]
    return Result2

system_params = {'sector': 'industrial',
                 'sim_name': 'Simulación de prueba',
                  'application': 'Ninguna',
                  'processes': 'Todos',
                  'location': 'Santiago',
                  'latitude': 235217,
                  'longitude': 245221,
                  'fuel_name': 'Diesel',
                  'yearly_demand': 20,
                  'yearly_demand_unit': 'm3',
                  'demand_monday': True,
                  'demand_tuesday': True,
                  'demand_wednesday': True,
                  'demand_thursday': True,
                  'demand_friday': True,
                  'demand_saturday': False,
                  'demand_sunday': False,
                  'operation_start': '7:30',
                  'operation_end': '19:30',
                  'demand_january': 10,
                  'demand_february': 12,
                  'demand_march': 13,
                  'demand_april': 13,
                  'demand_may': 15,
                  'demand_june': 16,
                  'demand_july': 16,
                  'demand_august': 16,
                  'demand_september': 14,
                  'demand_october': 12,
                  'demand_november': 10,
                  'demand_december': 10,
                  'boiler_nominal_power': 200,
                  'boiler_nominal_power_units': 'kW',
                  'boiler_pressure': 6,
                  'boiler_pressure_units': 'bar',
                  'boiler_type': 'Condensación',
                  'mains_inlet_temperature': None,
                  'return_inlet_temperature': None,
                  'temperature_january': 25,
                  'temperature_february': 25,
                  'temperature_march': 22,
                  'temperature_april': 19,
                  'temperature_may': 15,
                  'temperature_june': 15,
                  'temperature_july': 15,
                  'temperature_august': 15,
                  'temperature_september': 18,
                  'temperature_october': 22,
                  'temperature_november': 22,
                  'temperature_december': 25,
                  'outlet_temperature': 60,
                  'integration_scheme_name': 'SL_L_SC',
                  'integration_scheme_initials': 'SL_L_SC',
                  'aperture_area': 1.92,
                  'coll_n0': 0.756,
                  'coll_price': 1000,
                  'coll_a2': 0.0138*3.6,
                  'coll_a1': 4.052*3.6,
                  'coll_iam': None,
                  'coll_test_flow': None,
                  'coll_rows': 3,
                  'colls_per_row': 9,
                  'coll_tilt': 35,
                  'coll_azimuth': 354,
                  'field_mass_flow': 2700,
                  'field_mass_flow_units': 'kg/h',
                  'fluid': 'water',
                  'tank_volume': 1,
                  'tank_AR': 2.7,
                  'tank_material': 'Steel',
                  'tank_insulation_material': 'Plumavit',
                  'HX_eff': 0.8,
                  'fuel_cost': 1.3,
                  'fuel_cost_units': '$/l',
                  'coll_type': 'Evacuated Tube'}


#Result = simulate_system(system_params)

#plt.figure()
#plt.plot(Result['t'], Result['T_out_system'])
#plt.show()


#Heat_Map_bokeh(Result, 'T_out_system')

# np.savez('Result2.npz', **Result)

































