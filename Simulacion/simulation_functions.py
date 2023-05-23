#!/usr/bin/env python
# coding: utf-8



import numpy as np
import pandas as pd
import pvlib as pv
from scipy import interpolate
from matplotlib import pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy.interpolate import interp1d
from scipy.optimize import minimize, Bounds

def zenith_function(zenith_list):
    assert len(zenith_list)%8760 == 0
    factor = int(len(zenith_list)/8760)
    time = [ t/factor for t in range(len(zenith_list)) ]
    time.append(8760)
    zenith_list.append(zenith_list[0])
    return interp1d(time, zenith_list)

def azimuth_function(azimuth_list):
    assert len(azimuth_list)%8760 == 0
    factor = int(len(azimuth_list)/8760)
    time = [ t/factor for t in range(len(azimuth_list)) ]
    i = 0
    while i <  len(azimuth_list) - 1:
        if azimuth_list[i + 1] - azimuth_list[i] > 200:
            if azimuth_list[i] == 0 and azimuth_list[i + 1] == 360:
                i = i + 1
            else:
                delta_t = time[i + 1] - time[i]
                delta_t_1 = azimuth_list[i]*delta_t/(azimuth_list[i] + (360 - azimuth_list[i + 1]))
                time.insert(i + 1, time[i] + delta_t_1)
                azimuth_list.insert(i + 1, 0)
                time.insert(i + 2, time[i] + delta_t_1)
                azimuth_list.insert(i + 2, 360)
                i = i + 3
        elif azimuth_list[i] - azimuth_list[i + 1] > 200:
            if azimuth_list[i] == 360 and azimuth_list[i + 1] == 0:
                i = i + 1
            else:
                delta_t = time[i + 1] - time[i]
                delta_t_1 = (360 - azimuth_list[i])*delta_t/((360 - azimuth_list[i]) + azimuth_list[i + 1])
                time.insert(i + 1, time[i] + delta_t_1)
                azimuth_list.insert(i + 1, 360)
                time.insert(i + 2, time[i] + delta_t_1)
                azimuth_list.insert(i + 2, 0)
                i = i + 3
        else:
            i = i + 1
    time.append(8760)
    azimuth_list.append(azimuth_list[0])
    return interp1d(time, azimuth_list)

def plot_4_days(Curve, work_day_list, title, ylabel, filename):
    
    if work_day_list == []:
        print('Sin días laborales en toda la semana')
        return
    
    if len(Curve)%8760 != 0:
        print('Número de elementos en el vector de resultados no es válido')
        return
    time_steps_per_hour = int(len(Curve)/8760)
    plt.ioff()
    plt.rc('xtick', labelsize=14)
    plt.rc('ytick', labelsize=14)
    figure, axis = plt.subplots(2, 2, figsize = (13,8), dpi = 300)
    figure.suptitle(title, fontsize = 16)
    plt.tight_layout(pad = 2, h_pad = 3, w_pad = 1)
    time = np.linspace(0, 24, 24*time_steps_per_hour + 1)
    
    day_to_plot = 80
    while True:
        week_day = week_day_from_day(day_to_plot)
        if week_day in work_day_list:
            axis[0, 0].plot(time, Curve[(day_to_plot - 1)*24*time_steps_per_hour:day_to_plot*24*time_steps_per_hour + 1])
            axis[0, 0].set_title(date_spanish(day_to_plot), fontsize = 14)
            axis[0, 0].set_ylabel(ylabel, fontsize = 12)
            axis[0, 0].set_xlim([0,24])
            axis[0, 0].set_xticks(ticks = [0,4,8,12,16,20,24], labels = ['0:00', '4:00', '8:00', '12:00', '16:00', '20:00', '24:00'])
            break
        day_to_plot = day_to_plot + 1
    
    day_to_plot = 172
    while True:
        week_day = week_day_from_day(day_to_plot)
        if week_day in work_day_list:
            axis[0, 1].plot(time, Curve[((day_to_plot - 1)*24 + 1)*time_steps_per_hour:(day_to_plot*24 + 1)*time_steps_per_hour + 1])
            axis[0, 1].set_title(date_spanish(day_to_plot), fontsize = 14)
            axis[0, 1].set_ylabel(ylabel, fontsize = 12)
            axis[0, 1].set_xlim([0,24])
            axis[0, 1].set_xticks(ticks = [0,4,8,12,16,20,24], labels = ['0:00', '4:00', '8:00', '12:00', '16:00', '20:00', '24:00'])
            break
        day_to_plot = day_to_plot + 1
    
    day_to_plot = 264
    while True:
        week_day = week_day_from_day(day_to_plot)
        if week_day in work_day_list:
            axis[1, 0].plot(time, Curve[(day_to_plot - 1)*24*time_steps_per_hour:day_to_plot*24*time_steps_per_hour + 1])
            axis[1, 0].set_title(date_spanish(day_to_plot), fontsize = 14)
            axis[1, 0].set_ylabel(ylabel, fontsize = 12)
            axis[1, 0].set_xlim([0,24])
            axis[1, 0].set_xticks(ticks = [0,4,8,12,16,20,24], labels = ['0:00', '4:00', '8:00', '12:00', '16:00', '20:00', '24:00'])
            break
        day_to_plot = day_to_plot + 1
    
    day_to_plot = 355
    while True:
        week_day = week_day_from_day(day_to_plot)
        if week_day in work_day_list:
            axis[1, 1].plot(time, Curve[(day_to_plot - 1)*24*time_steps_per_hour:day_to_plot*24*time_steps_per_hour + 1])
            axis[1, 1].set_title(date_spanish(day_to_plot), fontsize = 14)
            axis[1, 1].set_ylabel(ylabel, fontsize = 12)
            axis[1, 1].set_xlim([0,24])
            axis[1, 1].set_xticks(ticks = [0,4,8,12,16,20,24], labels = ['0:00', '4:00', '8:00', '12:00', '16:00', '20:00', '24:00'])
            break
        day_to_plot = day_to_plot + 1
    
    if filename[len(filename) - 4:] != '.jpg':
        filename = filename + '.jpg'
    plt.savefig(filename, bbox_inches='tight')
    plt.close()

def Heat_Map(Curve, title, filename):
    '''
    Función para generar un "mapa" de alguna variable (con las horas del día en el eje vertical y los días del año en el eje horizontal)

    Parámetros:
        - Curve : Lista de datos de la variable a plotear. Debe ser de un largo divisible en 365, de forma que para cada día del año haya la misma cantidad de datos.
        - title : Título de la figura
        - filename : Nombre del archivo (imagen) con el que se guardará el plot.

    Retorna:
        - None
    '''
    if len(Curve)%365 != 0:
        print('Número de elementos en el vector de resultados no es válido')
        return
    time_steps_per_day = int( len( Curve )/365 )
    plt.ioff()
    plt.rc('xtick', labelsize=14)
    plt.rc('ytick', labelsize=14)
    yticks = [ 0, int(time_steps_per_day/6), int(time_steps_per_day/3),
               int(time_steps_per_day/2), int(time_steps_per_day*2/3),
               int(time_steps_per_day*5/6), time_steps_per_day]
    ylabels = [0,4,8,12,16,20,24]
    matrix = np.reshape(Curve, ( 365, time_steps_per_day ) )
    matrix = np.transpose(matrix)
    fig = plt.figure(figsize = (8,12), dpi = 300)
    ax = plt.gca()
    cmap = plt.cm.get_cmap("jet").copy()
    cmap.set_bad('white',1.)
    im = ax.matshow(matrix, cmap = cmap, origin = 'lower')
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.2)
    plt.colorbar(im, cax=cax)
    ax.set_yticks(yticks, ylabels)
    ax.xaxis.set_ticks_position('bottom')
    ax.xaxis.set_label_position('bottom')
    ax.set_ylabel('Hora del día (UTC-3)', fontsize = 14)
    ax.set_xlabel('Día del año', fontsize = 14)
    ax.set_title(title, fontsize = 16, loc = 'left')
    if filename[len(filename) - 4:] != '.jpg':
        filename = filename + '.jpg'
    plt.savefig(filename, bbox_inches='tight')
    plt.close()
    
    
def Energy_share(filename, Result):
    Result = Result['Result']
    if len(Result['useful_solar_power(W)'])%8760 != 0:
        print('Número de elementos en el vector de resultados no es válido')
        return
    assert len(Result['useful_solar_power(W)']) == len(Result['aux_heater_power(W)'])
    time_steps_per_hour = int(len(Result['useful_solar_power(W)'])/8760)
    time_step = 1/time_steps_per_hour
    Solar_Energy = [ time_step*Result['useful_solar_power(W)'][i]/1000 for i in range(len(Result['useful_solar_power(W)'])) ]
    Boiler_Energy = [ time_step*Result['aux_heater_power(W)'][i]/1000 for i in range(len(Result['aux_heater_power(W)'])) ]
    month_changes = [ 0, 744, 1416, 2160, 2880, 3624, 4344, 5088, 5832, 6552, 7296, 8016, 8760 ]
    Boiler_Heights = [ sum( Boiler_Energy[ month_changes[i]*time_steps_per_hour:month_changes[i + 1]*time_steps_per_hour ] ) for i in range(len(month_changes) - 1) ]
    Solar_Heights = [ sum( Solar_Energy[ month_changes[i]*time_steps_per_hour:month_changes[i + 1]*time_steps_per_hour ] ) for i in range(len(month_changes) - 1) ]
    plt.ioff()
    plt.rc('xtick', labelsize=10)
    plt.rc('ytick', labelsize=14)
    fig = plt.figure(figsize = (13,8), dpi = 300)
    plt.bar(range(1,13), Boiler_Heights, tick_label = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'], color = 'dodgerblue', label = 'Auxiliar')
    plt.bar(range(1,13), Solar_Heights, bottom = Boiler_Heights, color = 'gold', label = 'Solar')
    plt.title('Distribución de energía mensual', fontsize = 18)
    plt.ylabel('Energía (kWh)', fontsize = 14)
    plt.legend(framealpha = 0.7, loc = 'lower right')
    if filename[len(filename) - 4:] != '.jpg':
        filename = filename + '.jpg'
    plt.savefig(filename, bbox_inches='tight')
    plt.close()
    
def generate_text_file(text_file_name, Result):
    
    if text_file_name[len(text_file_name) - 4:] != '.txt':
        text_file_name = text_file_name + '.txt'
    
    Record_dict = Result['Result']
    integration_scheme_name = Result['integration_scheme_name']
    integration_scheme_initials = Result['integration_scheme_initials']
    cost_per_kJ = Result['cost_per_kJ']
    monthly_demands = Result['monthly_demands']
    monthly_mains_temperatures = Result['monthly_mains_temperatures']
    monthly_flows = Result['monthly_flows']
    closed_system = Result['closed_system']
    boiler_efficiency = Result['boiler_efficiency']
    time_step = Result['time_step']
    coll_area = Result['coll_area']
    coll_price = Result['coll_price']
    coll_rows = Result['coll_rows']
    colls_per_row = Result['colls_per_row']
    Tank_volume = Result['Tank_volume']
    Tank_cost_per_m3 = Result['Tank_cost_per_m3']
    BoP_cost_per_m2 = Result['BoP_cost_per_m2']
    installation_cost_percentage = Result['installation_cost']
    operation_and_maintanence_percentage = Result['operation_and_maintanence']
    tax_rate = Result['tax_rate']
    discount_factor = Result['discount_factor']
    
    if tax_rate < 1:
        tax_rate = tax_rate*100
    if discount_factor < 0.5:
        discount_factor = discount_factor*100
    
    if len(Record_dict['useful_solar_power(W)'])%8760 != 0:
        print('Número de elementos en el vector de resultados no es válido')
        return
    assert len(Record_dict['useful_solar_power(W)']) == len(Record_dict['aux_heater_power(W)'])
    time_steps_per_hour = int(len(Record_dict['useful_solar_power(W)'])/8760)
    
    yearly_cost_without_solar = sum([ cost_per_kJ*monthly_demands[i]/boiler_efficiency for i in monthly_demands ])
    yearly_cost_with_solar = sum(Record_dict['conventional_energy_cost'])
    yearly_fuel_savings = yearly_cost_without_solar - yearly_cost_with_solar
    total_yearly_energy = sum([ time_step*Record_dict['useful_solar_power(W)'][i]/1000 for i in range(len(Record_dict['useful_solar_power(W)'])) ])
    wasted_energy_time = time_step*np.array([ Record_dict['wasted_solar_power(W)'][i] > 0 for i in range(len(Record_dict['wasted_solar_power(W)'])) ]).sum()
    total_wasted_energy = sum([ time_step*Record_dict['wasted_solar_power(W)'][i]/1000 for i in range(len(Record_dict['wasted_solar_power(W)'])) ])
    
    yearly_solar_frac = sum(Record_dict['useful_solar_power(W)'])/(sum(Record_dict['useful_solar_power(W)']) + sum(Record_dict['aux_heater_power(W)']))
    month_changes = [ 0, 744, 1416, 2160, 2880, 3624, 4344, 5088, 5832, 6552, 7296, 8016, 8760 ]
    monthly_solar_fracs = []
    for i in range(len(month_changes) - 1):
        monthly_solar = sum( Record_dict['useful_solar_power(W)'][ month_changes[i]*time_steps_per_hour:month_changes[i + 1]*time_steps_per_hour ] )
        monthly_aux = sum( Record_dict['aux_heater_power(W)'][ month_changes[i]*time_steps_per_hour:month_changes[i + 1]*time_steps_per_hour ] )
        monthly_solar_fracs.append(monthly_solar/(monthly_aux + monthly_solar))
    
    
    total_coll_cost = coll_price*coll_rows*colls_per_row
    total_BoP_cost = BoP_cost_per_m2*coll_area*coll_rows*colls_per_row
    
    if integration_scheme_name in ['SAM','NS_L_CA_MU','NS_L_CA_1','NS_L_CA_2'] or integration_scheme_initials in ['SAM','NS_L_CA_MU','NS_L_CA_1','NS_L_CA_2']:
        total_tank_cost = Tank_cost_per_m3*Tank_volume
        equipment_cost = total_coll_cost + total_tank_cost + total_BoP_cost
    else:
        equipment_cost = total_coll_cost + total_BoP_cost
    
    total_installation_cost = installation_cost_percentage*equipment_cost/100    
    yearly_operation_and_maintanence_cost = operation_and_maintanence_percentage*equipment_cost/100
    initial_investment = equipment_cost + total_installation_cost
    
    collector_depreciation_time = 10
    project_evaluation_period = 20
    VAN = compute_VAN(initial_investment, yearly_fuel_savings, yearly_operation_and_maintanence_cost, discount_factor, tax_rate, total_coll_cost, collector_depreciation_time, project_evaluation_period)
    TIR = compute_TIR(initial_investment, yearly_fuel_savings, yearly_operation_and_maintanence_cost, tax_rate, total_coll_cost, collector_depreciation_time, project_evaluation_period)
    LCoH = compute_LCoH(initial_investment, yearly_operation_and_maintanence_cost, total_yearly_energy, discount_factor, tax_rate, total_coll_cost, collector_depreciation_time, project_evaluation_period)
    payBack_time = compute_payback_time(initial_investment, yearly_fuel_savings, yearly_operation_and_maintanence_cost, tax_rate, total_coll_cost, collector_depreciation_time, project_evaluation_period)
    
    if integration_scheme_name in ['NS_L_CA_1','NS_L_CA_2'] or integration_scheme_initials in ['NS_L_CA_1','NS_L_CA_2']:
        setPoint_surpass_time = 0
        boiler_nominal_power_surpass_time = 0
    else:
        setPoint_surpass_time = time_step*np.array(Record_dict['setPoint_Temp_surpassed']).sum()
        boiler_nominal_power_surpass_time = time_step*np.array(Record_dict['aux_heater_nominal_power_surpassed']).sum()
        max_outlet_temp = max(Record_dict['demanded_flow_temperature(C)'])
        min_outlet_temp = min(Record_dict['demanded_flow_temperature(C)'])
        
    text_file = open(text_file_name, 'w')
    if not closed_system:
        text_file.write('La temperatura del agua entrando desde la red al sistema de calentamiento se considera constante durante cada mes. Las temperaturas son:\n\n')
        text_file.write('\tEnero: '+str(monthly_mains_temperatures['January'])+' °C\n')
        text_file.write('\tFebrero: '+str(monthly_mains_temperatures['February'])+' °C\n')
        text_file.write('\tMarzo: '+str(monthly_mains_temperatures['March'])+' °C\n')
        text_file.write('\tAbril: '+str(monthly_mains_temperatures['April'])+' °C\n')
        text_file.write('\tMayo: '+str(monthly_mains_temperatures['May'])+' °C\n')
        text_file.write('\tJunio: '+str(monthly_mains_temperatures['June'])+' °C\n')
        text_file.write('\tJulio: '+str(monthly_mains_temperatures['July'])+' °C\n')
        text_file.write('\tAgosto: '+str(monthly_mains_temperatures['August'])+' °C\n')
        text_file.write('\tSeptiembre: '+str(monthly_mains_temperatures['September'])+' °C\n')
        text_file.write('\tOctubre: '+str(monthly_mains_temperatures['October'])+' °C\n')
        text_file.write('\tNoviembre: '+str(monthly_mains_temperatures['November'])+' °C\n')
        text_file.write('\tDiciembre: '+str(monthly_mains_temperatures['December'])+' °C\n\n')
    
    text_file.write('El flujo de agua pasando por el sistema de calentamiento se considera constante durante cada mes (sólo mientras el sistema está operativo). Los flujos son:\n\n')
    text_file.write('\tEnero: '+str(monthly_flows['January']/60)+' L/min\n')
    text_file.write('\tFebrero: '+str(monthly_flows['February']/60)+' L/min\n')
    text_file.write('\tMarzo: '+str(monthly_flows['March']/60)+' L/min\n')
    text_file.write('\tAbril: '+str(monthly_flows['April']/60)+' L/min\n')
    text_file.write('\tMayo: '+str(monthly_flows['May']/60)+' L/min\n')
    text_file.write('\tJunio: '+str(monthly_flows['June']/60)+' L/min\n')
    text_file.write('\tJulio: '+str(monthly_flows['July']/60)+' L/min\n')
    text_file.write('\tAgosto: '+str(monthly_flows['August']/60)+' L/min\n')
    text_file.write('\tSeptiembre: '+str(monthly_flows['September']/60)+' L/min\n')
    text_file.write('\tOctubre: '+str(monthly_flows['October']/60)+' L/min\n')
    text_file.write('\tNoviembre: '+str(monthly_flows['November']/60)+' L/min\n')
    text_file.write('\tDiciembre: '+str(monthly_flows['December']/60)+' L/min\n\n')
    
    text_file.write('Se considera que los cambios de hora se realizan los días 7 de abril y 8 de septiembre. Si la simulación se realiza en la Región de Magallanes (el criterio para esto es que la latitud sea más al sur que -49°), el horario es UTC-3 durante todo el año.\n')
    if integration_scheme_name in ['NS_L_CA_1','NS_L_CA_2'] or integration_scheme_initials in ['NS_L_CA_1','NS_L_CA_2']:
        text_file.write('En el mapa de calor entregado por el campo solar, el horario corresponde a UTC-3 durante todo el año.\n\n')
    else:
        text_file.write('En los mapas de calor correspondientes al campo solar y al calentador auxiliar, el horario corresponde a UTC-3 durante todo el año.\n\n')
    
    text_file.write('La energía útil total entregada por el campo solar durante el año simulado es de '+str(total_yearly_energy)+' kWh.\n\n')
    
    if wasted_energy_time > 0:
        text_file.write('En el sistema de calentamiento solar se produjo y expulsó vapor durante '+str(np.round(wasted_energy_time,1))+' horas a lo largo del año simulado. En términos energéticos, esto se traduce en '+str(np.round(total_wasted_energy,1))+' kWh no aprovechados.\n\n')
    
    text_file.write('La fracción solar anual (es decir, la fracción entre la energía útil entregada por el campo solar y la energía total entregada al flujo de agua) es de '+str(np.round(yearly_solar_frac*100,1))+'%.\n')
    text_file.write('Las fracciones solares mensuales son las siguientes:\n\n')
    text_file.write('\tEnero: '+str(np.round(100*monthly_solar_fracs[0],1))+'%\n')
    text_file.write('\tFebrero: '+str(np.round(100*monthly_solar_fracs[1],1))+'%\n')
    text_file.write('\tMarzo: '+str(np.round(100*monthly_solar_fracs[2],1))+'%\n')
    text_file.write('\tAbril: '+str(np.round(100*monthly_solar_fracs[3],1))+'%\n')
    text_file.write('\tMayo: '+str(np.round(100*monthly_solar_fracs[4],1))+'%\n')
    text_file.write('\tJunio: '+str(np.round(100*monthly_solar_fracs[5],1))+'%\n')
    text_file.write('\tJulio: '+str(np.round(100*monthly_solar_fracs[6],1))+'%\n')
    text_file.write('\tAgosto: '+str(np.round(100*monthly_solar_fracs[7],1))+'%\n')
    text_file.write('\tSeptiembre: '+str(np.round(100*monthly_solar_fracs[8],1))+'%\n')
    text_file.write('\tOctubre: '+str(np.round(100*monthly_solar_fracs[9],1))+'%\n')
    text_file.write('\tNoviembre: '+str(np.round(100*monthly_solar_fracs[10],1))+'%\n')
    text_file.write('\tDiciembre: '+str(np.round(100*monthly_solar_fracs[11],1))+'%\n\n')
    
    if wasted_energy_time > 0:
        text_file.write('La potencia máxima (útil, es decir, no usada para producir vapor que luego es purgado) lograda por el campo solar fue de '+str(np.round(max(Record_dict['useful_solar_power(W)']),1))+' W')
    else:
        text_file.write('La potencia máxima lograda por el campo solar fue de '+str(np.round(max(Record_dict['useful_solar_power(W)']),1))+' W.\n')
    
    if setPoint_surpass_time > 0:
        text_file.write('El flujo saliendo del sistema de calentamiento superó el Set Point de temperatura (por exceso de potencia en el campo solar) durante '+str(np.round(setPoint_surpass_time,1))+' horas a lo largo del año, alcanzando una temperatura máxima de '+str(np.round(max_outlet_temp,1))+' °C.\n')
    if boiler_nominal_power_surpass_time > 0:
        text_file.write('El flujo saliendo del sistema de calentamiento no alcanzó el Set Point de temperatura (por falta de potencia del calentador auxiliar) durante '+str(np.round(boiler_nominal_power_surpass_time,1))+' horas a lo largo del año, alcanzando una temperatura mínima de' +str(np.round(min_outlet_temp,1))+' °C.\n\n')
    else:
        text_file.write('\n')
        
    if VAN < 0:
        VAN_str = '-$'+str(np.round(abs(VAN), 1))
    else:
        VAN_str = '$'+str(np.round(VAN, 1))
    
    if payBack_time == 1:
        payBack_time_str = str(payBack_time)+' año'
    else:
        payBack_time_str = str(payBack_time)+' años'
    
    text_file.write('ANÁLISIS FINANCIERO:\n')
    text_file.write('El ahorro anual estimado (considerando tanto el ahorro en fuentes de energía convencionales como el gasto extra generado por la operación y mantenimiento del campo solar) es de $'+str(np.round(yearly_fuel_savings - yearly_operation_and_maintanence_cost,1))+'.\n')
    text_file.write('El Valor Actual Neto (VAN) del proyecto es de '+VAN_str+'.\n')
    text_file.write('La Tasa Interna de Retorno (TIR) del proyecto es de '+str(np.round(TIR, 2))+'%.\n')
    text_file.write('El Costo Nivelado del Calor (Levelized Cost of Heat, LCoH) es de $'+str(np.round(LCoH, 1))+'/kWh.\n')
    text_file.write('El tiempo de recuperación de la inversión (Payback Time) es de '+payBack_time_str+'.')
    
    text_file.close()
    
    

def monthly_work_hours(month, t_start, t_end, work_day_list):
    if t_start == t_end:
        daily_working_hours = 24
    else:
        if t_end > t_start:
            daily_working_hours = t_end - t_start
        else:
            daily_working_hours = 24 - t_start + t_end
    work_hours = 0
    for day in range(1,366):
        if month_from_day(day) == month and week_day_from_day(day) in work_day_list:
            work_hours = work_hours + daily_working_hours
    return work_hours

def compute_monthly_flows(monthly_demands, monthly_temperatures, work_day_list, t_start, t_end, T_set, fluid_properties):
    flows = {}
    for month in monthly_demands:
        delta_h = fluid_properties.T_to_h(T_set) - fluid_properties.T_to_h(monthly_temperatures[month])
        if monthly_work_hours(month, t_start, t_end, work_day_list) == 0:
            flows[month] = 0
        else:
            m_month = monthly_demands[month]/delta_h
            flows[month] = m_month/monthly_work_hours(month, t_start, t_end, work_day_list)
    return flows

def extract_weather_data(dataframe):
    years = dataframe['Year'].values
    year_january = years[0]
    year_february = years[744]
    year_march = years[1416]
    year_april = years[2160]
    year_may = years[2880]
    year_june = years[3624]
    year_july = years[4344]
    year_august = years[5088]
    year_september = years[5832]
    year_october = years[6552]
    year_november = years[7296]
    year_december = years[8016]
    DNI = dataframe['DNI'].values
    GHI = dataframe['GHI'].values
    DHI = dataframe['DHI'].values
    temp = dataframe['Tdry']
    DNI = [ DNI[8759] ] + DNI[:8759].tolist()
    GHI = [ GHI[8759] ] + GHI[:8759].tolist()
    DHI = [ DHI[8759] ] + DHI[:8759].tolist() 
    temp = [ temp[8759] ] + temp[:8759].tolist()
    DNI.append(DNI[0])
    GHI.append(GHI[0])
    DHI.append(DHI[0])
    temp.append(temp[0])
    assert len(DNI) == 8761 and len(GHI) == 8761 and len(DHI) == 8761 and len(temp) == 8761
    DNI = [ 3.6*DNI[i] for i in range(len(DNI)) ]
    GHI = [ 3.6*GHI[i] for i in range(len(GHI)) ]
    DHI = [ 3.6*DHI[i] for i in range(len(DHI)) ]
    year_list = [year_january,
                 year_february,
                 year_march,
                 year_april,
                 year_may,
                 year_june,
                 year_july,
                 year_august,
                 year_september,
                 year_october,
                 year_november,
                 year_december ]
    return year_list, DNI, GHI, DHI, temp

def convert_power(original_value, original_units):
    if original_units == 'kJ/h':
        return original_value
    if original_units == 'kW':
        return original_value*3600
    if original_units == 'Ton/h':
        return original_value*2257000

def convert_flow(original_value, original_units, glycol_percentage):
    if original_units == 'kg/h':
        return original_value
    if original_units == 'kg/min':
        return original_value*60
    if original_units == 'kg/s':
        return original_value*3600
    glycol_fraction = glycol_percentage/100
    density = 1.11/( (1 - glycol_fraction)*1.11 + glycol_fraction )
    if original_units == 'L/h':
        return density*original_value
    if original_units == 'L/min':
        return density*original_value*60
    if original_units == 'L/s':
        return density*original_value*3600
    if original_units == 'gpm':
        return 227.125*density*original_value
    
def convert_pressure(original_value, original_units):
    if original_units == 'bar':
        pressure_bar =  original_value
    if original_units == 'MPa':
        pressure_bar = original_value*10
    if original_units == 'psi':
        pressure_bar = original_value*0.06895
    possible_pressures = [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6]
    diffs = [ abs(pressure_bar - possible_pressures[i]) for i in range(len(possible_pressures)) ]
    return possible_pressures[np.argmin(diffs)]

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
    if fuel == 'Electricidad':
        raise ValueError('El consumo eléctrico solo puede expresarse en unidades de energía (MJ, kWh, MWh, BTU o kcal); no en kg, L ni m3')
    if fuel == 'Propano':
        fuel_density = 1.83
        if boiler_type == 'Condensación líquido' or boiler_type == 'Condensación vapor':
            fuel_heat_value = 50426
        else:
            fuel_heat_value = 46367
    if fuel == 'Butano':
        fuel_density = 2.52
        if boiler_type == 'Condensación líquido' or boiler_type == 'Condensación vapor':
            fuel_heat_value = 49652
        else:
            fuel_heat_value = 45765
    if fuel == 'Biomasa':
        fuel_density = 800
        if boiler_type == 'Condensación líquido' or boiler_type == 'Condensación vapor':
            fuel_heat_value = 19000
        else:
            fuel_heat_value = 17000
    if fuel == 'Diesel':
        fuel_density = 850
        if boiler_type == 'Condensación líquido' or boiler_type == 'Condensación vapor':
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
    if fuel == 'Propano':
        fuel_density = 1.83
        if boiler_type == 'Condensación líquido' or boiler_type == 'Condensación vapor':
            fuel_heat_value = 50426
        else:
            fuel_heat_value = 46367
    if fuel == 'Butano':
        fuel_density = 2.52
        if boiler_type == 'Condensación líquido' or boiler_type == 'Condensación vapor':
            fuel_heat_value = 49652
        else:
            fuel_heat_value = 45765
    if fuel == 'Biomasa':
        fuel_density = 800
        if boiler_type == 'Condensación líquido' or boiler_type == 'Condensación vapor':
            fuel_heat_value = 19000
        else:
            fuel_heat_value = 17000
    if fuel == 'Diesel':
        fuel_density = 850
        if boiler_type == 'Condensación líquido' or boiler_type == 'Condensación vapor':
            fuel_heat_value = 45600
        else:
            fuel_heat_value = 42600
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
        time = np.round(time + 0.5, 1)
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
    if day >= 1 and day <= 31:
        return 'January'
    elif day >= 32 and day <= 59:
        return 'February'
    elif day >= 60 and day <= 90:
        return 'March'
    elif day >= 91 and day <= 120:
        return 'April'
    elif day >= 121 and day <= 151:
        return 'May'
    elif day >= 152 and day <= 181:
        return 'June'
    elif day >= 182 and day <= 212:
        return 'July'
    elif day >= 213 and day <= 243:
        return 'August'
    elif day >= 244 and day <= 273:
        return 'September'
    elif day >= 274 and day <= 304:
        return 'October'
    elif day >= 305 and day <= 334:
        return 'November'
    elif day >= 335 and day <= 365:
        return 'December'
    else:
        raise ValueError('Día fuera de rango')
        
def date_spanish(day):
    month_beginnings = {'January': 1,
                        'February': 32,
                        'March': 60,
                        'April': 91,
                        'May': 121,
                        'June': 152,
                        'July': 182,
                        'August': 213,
                        'September': 244,
                        'October': 274,
                        'November': 305,
                        'December': 335 }
    months_spanish = {'January': 'enero',
                      'February': 'febrero',
                      'March': 'marzo',
                      'April': 'abril',
                      'May': 'mayo',
                      'June': 'junio',
                      'July': 'julio',
                      'August': 'agosto',
                      'September': 'septiembre',
                      'October': 'octubre',
                      'November': 'noviembre',
                      'December': 'diciembre'}
    month = month_from_day(day)
    month_day = day - month_beginnings[month] + 1
    return str(month_day) + ' de ' + months_spanish[month]

    
def compute_VAN(initial_investment, yearly_fuel_savings, yearly_operation_and_maintanence_cost,
                discount_factor, tax_rate, initial_dep_value, dep_time, evaluation_time):
    
    discount_factor_real = discount_factor/100
    tax_rate_real = tax_rate/100
    yearly_savings = yearly_fuel_savings - yearly_operation_and_maintanence_cost
    VAN = -initial_investment
    for year in range(1, evaluation_time + 1):
        if year <= dep_time:
            utility = yearly_savings - initial_dep_value/dep_time
        else:
            utility = yearly_savings
        utility = (1 - tax_rate_real)*utility
        if year <= dep_time:
            utility = utility + initial_dep_value/dep_time
        VAN = VAN + utility/( (1 + discount_factor_real)**year )
    return VAN
    

def VAN_squared(discount_factor, initial_investment, yearly_fuel_savings, yearly_operation_and_maintanence_cost, tax_rate, initial_dep_value, dep_time, evaluation_time):
    return (compute_VAN(initial_investment, yearly_fuel_savings, yearly_operation_and_maintanence_cost, discount_factor, tax_rate, initial_dep_value, dep_time, evaluation_time))**2
    
def compute_TIR(initial_investment, yearly_fuel_savings, yearly_operation_and_maintanence_cost, tax_rate, initial_dep_value, dep_time, evaluation_time):
    discount_factor_bounds = Bounds(lb = 0, ub = np.inf)
    solution = minimize(VAN_squared, x0 = 7, args = (initial_investment, yearly_fuel_savings, yearly_operation_and_maintanence_cost, tax_rate, initial_dep_value, dep_time, evaluation_time), bounds = discount_factor_bounds)
    return solution.x[0]

def compute_LCoH(initial_investment, yearly_operation_and_maintanence_cost, total_yearly_energy, discount_factor, tax_rate, initial_dep_value, dep_time, evaluation_time):
    discount_factor_real = discount_factor/100
    tax_rate_real = tax_rate/100
    LCoH = initial_investment
    for year in range(1,evaluation_time + 1):
        if year <= dep_time:
            LCoH = LCoH + (yearly_operation_and_maintanence_cost*(1 - tax_rate_real) - initial_dep_value*tax_rate_real/dep_time)/((1 + discount_factor_real)**year)
        else:
            LCoH = LCoH + yearly_operation_and_maintanence_cost*(1 - tax_rate_real)/((1 + discount_factor_real)**year)
    LCoH = LCoH/sum([ total_yearly_energy/(1 + discount_factor_real)**year for year in range(1,21) ])
    
    return LCoH

def compute_payback_time(initial_investment, yearly_fuel_savings, yearly_operation_and_maintanence_cost,
                         tax_rate, initial_dep_value, dep_time, evaluation_time):
    
    tax_rate_real = tax_rate/100
    yearly_savings = yearly_fuel_savings - yearly_operation_and_maintanence_cost
    year = 0
    money = -initial_investment
    while True:
        year = year + 1
        if year <= dep_time:
            utility = yearly_savings - initial_dep_value/dep_time
        else:
            utility = yearly_savings
        utility = (1 - tax_rate_real)*utility
        if year <= dep_time:
            utility = utility + initial_dep_value/dep_time
        money = money + utility
        if money >= 0:
            return year
        if year == 100:
            return year
        

def corr_exp_solar(FILENAME = 'DHTMY_SAM_E_9H23YU.csv'):

    '''
    Función que corrige los valores de DNI y DHI proporcionados por el explorador solar
    
    Parámetros:
    ----------
    -FILENAME: String con el nombre del csv TMY HORARIO SAM entregado por el explorador. Tanto el script como el 
    archivo csv deben estar en la misma carpeta.
    
    Output:
    ----------
    -latitude : Latitud, °
    -longitude: Longitud, °
    -UTC      : UTC
    -DATA     : Dataframe de pandas con las correcciones de irradiancia difusa y directa
    
    '''
 
    # get latitude, longitude, utc and elevation
    DATA = pd.read_csv(FILENAME, nrows=1)
    latitude = DATA.iloc[0][5]
    longitude = DATA.iloc[0][6]
    UTC = -DATA.iloc[0][7]

    # get meteorological variables
    DATA = pd.read_csv(FILENAME, header=2)
    GHI = DATA['GHI'].values


    # get cloud coverage variabilty
    # load coordinate matrices, X=LONG;Y=LAT

    XCF = pd.read_csv('XCF.csv').values
    YCF = pd.read_csv('YCF.csv').values

    # load cloud coverage variability layer
    CF = pd.read_csv('CF.csv').values

    # calculate by interpolation the effective variability of cloud coverage
    # for the target location

    # Se reajustan las dimensiones de las matrices a arreglos de una dimensión
    YCF = YCF.reshape(-1)
    XCF = XCF.reshape(-1)
    CF = np.array([CF.reshape(-1)]).T

    # Se crea un arreglo de dos dimensiones donde cada entrada incluye latitud y longitud
    XYCF = np.vstack((YCF, XCF)).T

    # Se realiza una interpolación 
    CFSTD = interpolate.griddata(XYCF, CF, (latitude, longitude), method='nearest')

    # Calculate solar geometry
    tz = f'Etc/GMT+{UTC}'
    times = pd.date_range('2021-01-01 00:30:00', '2022-01-01 00:30:00', inclusive='left',
                          freq='H', tz=tz)
    solpos = pv.solarposition.ephemeris(times, latitude, longitude)
    elevationangle = solpos['elevation']


    ast = solpos['solar_time']


    # Extraterrestrial irradiance
    epsilon = pv.solarposition.pyephem_earthsun_distance(times)
    Io = np.maximum(0,1367*epsilon*np.sin(elevationangle*np.pi/180))


    # Calculate clearness index and diffuse fraction

    GHI = np.minimum(Io,GHI) #% limit GHI to under Io
    Kt = GHI/Io
    Kt[np.where(Io <= 0)[0]] = 0

    # Load coefficients for BRL predictor generation

    P = [[275.614845282659  ,-84.0341464533378  ,-1.86015047743254   ],
         [-123.987004786273 ,44.2818520840966   ,6.59582239895984    ],
         [-5.10707452673121 ,1.72451283166942   ,-0.163934905299144  ],
         [-1.06584246650315 ,0.243994275140034  ,-0.0184549284117407 ],
         [-81.5719886815895 ,20.4764911164922   ,2.22797398848424    ],
         [26.9296725403115  ,-6.13579726686233  ,0.360110809734099   ]]

    # Calculate BRL predictors

    B = []
    for i in range(0,6):
        B.append(P[i][0]*CFSTD**2 + P[i][1]*CFSTD + P[i][2])

    #Apply BRL model
    # Calculate persistence

    per = []
    UTCc = 0

    for counter in range(len(Kt)):
        if counter >= 1 and counter <= (len(Kt) - 2):
            if elevationangle[counter - 1] <= 0 and elevationangle[counter] > 0:
                per.append(Kt[counter + 1 - UTCc])

            elif elevationangle[counter - 1] > 0 and elevationangle[counter] <= 0:
                per.append(Kt[counter - 1 - UTCc])

            else:
                per.append(0.5*(Kt[counter + 1 - UTCc] + Kt[counter - 1 - UTCc]))

        else:
            per.append(0)


    per = np.array(per)

    # Calculate daily KT
    KT = sum(GHI.values.reshape(24, int(len(GHI)/24)))/sum(Io.values.reshape(24, int(len(Io)/24)))
    KT_aux = []
    for i in range(len(KT)):
        KT_aux.append(KT[i]*np.ones([24, 1]))
    KT_aux = np.array(KT_aux)
    KT = KT_aux.reshape(-1)


    #Apply model
    Kbrl = 1/(1+np.exp(B[0] + B[1]*Kt + B[2]*ast + B[3]*elevationangle + B[4]*KT + B[5]*per))

    # Reconstruct irradiance
    DHIbrl = Kbrl*Kt*Io # DHI by BRL reconstruction
    DNIbrl = (GHI - DHIbrl)/np.sin(elevationangle*np.pi/180) # % DNI by BRL reconstruction
    DNIbrl[ np.where(elevationangle <= 1)[0] ] = 0 # for very low solar elevations, make DNI=0 and GHI=DHI
    DHIbrl[ np.where(elevationangle <= 1)[0] ] = GHI[ np.where(elevationangle <= 1)[0] ]

    DATA['DNI'] = DNIbrl.values
    DATA['DHI'] = DHIbrl.values
    
    return latitude, longitude, DATA


