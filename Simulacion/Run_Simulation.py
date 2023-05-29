# -*- coding: utf-8 -*-
"""
Created on Sun Nov  6 10:35:24 2022

@author: adria
"""

from Simulacion.Class_Solar_Field import Solar_Field
from Simulacion.Class_Heat_Exchanger import Heat_Exchanger
from Simulacion.Class_Storage import Storage_Tank
from Simulacion.Class_Properties import Properties
from Simulacion.simulation_functions import zenith_function, azimuth_function, compute_monthly_flows, extract_weather_data, convert_power, convert_flow, convert_pressure, convert_demand, compute_cost_per_kJ, time_from_string, week_day_from_day, month_from_day, corr_exp_solar, compute_VAN, compute_TIR, compute_LCoH, compute_payback_time
from math import sin, cos, pi
from pvlib.solarposition import get_solarposition
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
import os
from ssspi.models import Simulaciones

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def Solar_HX_Tank(Field, HX, Tank, T_set, Boiler_type, boiler_nominal_power,
                  boiler_efficiency, cost_per_conventional_kJ,
                  work_day_list, monthly_flows, monthly_inlet_temperatures,
                  monthly_mains_temperatures, t_start, t_end,
                  PropsField, PropsHeatedFluid, mass_flow_field,
                  sky_diff_func, ground_diff_func, DNI_func, T_amb_func,
                  compute_zenith, compute_azimuth, corrected_time,
                  time_step, tolerance, max_iterations):
    
    if T_set == PropsHeatedFluid.T_sat:
        if Boiler_type in ['Convencional vapor', 'Condensación vapor']:
            h_set = PropsHeatedFluid.h_sat_vap
        else:
            h_set = PropsHeatedFluid.h_sat_liq
    else:
        h_set = PropsHeatedFluid.T_to_h(T_set)
    
    t = 8760 - 24*10
    previous_enthalpies = {'h_in_solar_field': PropsField.T_to_h(40), 'h_in_HX_load': PropsHeatedFluid.T_to_h(40)}
    while t < 8760:
                
        day = int(t/24) + 1
        month = month_from_day(day)
        week_day = week_day_from_day(day)
        day_time = corrected_time(t)%24
        
        sky_diffuse = float(sky_diff_func(t))
        ground_diffuse = float(ground_diff_func(t))
        DNIrr = float(DNI_func(t))
        T_amb = float(T_amb_func(t))
        T_in_system = monthly_inlet_temperatures[month]
        h_in_system = PropsHeatedFluid.T_to_h(T_in_system)
        T_mains = monthly_mains_temperatures[month]
        h_mains = PropsHeatedFluid.T_to_h(T_mains)
        h_mains_field = PropsField.T_to_h(T_mains)
        demanded_flow = monthly_flows[month]
        
        aoi, longi, trans = Field.incidence_angles(float(compute_zenith(t)), float(compute_azimuth(t)))
        if aoi == None:
            rad = sky_diffuse + ground_diffuse
        else:
            beam_rad = DNIrr*cos(aoi)
            rad = beam_rad + sky_diffuse + ground_diffuse
        
        if t_start == t_end and demanded_flow > 0 and week_day in work_day_list:
            system_operation = True
        elif t_start < t_end and day_time >= t_start and day_time <= t_end and demanded_flow > 0 and week_day in work_day_list:
            system_operation = True
        elif t_start > t_end and (day_time >= t_start or day_time <= t_end) and demanded_flow > 0 and week_day in work_day_list:
            system_operation = True
        else:
            system_operation = False
            solar_field_operation = False
        
        if system_operation:
            if rad > 0:
                solar_field_operation = True
                if aoi == None:
                    IAM_eff = (sky_diffuse*Field.sky_diffuse_iam + ground_diffuse*Field.ground_diffuse_iam)/rad
                else:
                    beam_iam = Field.IAM_func(aoi, longi, trans)
                    IAM_eff = (beam_rad*beam_iam + sky_diffuse*Field.sky_diffuse_iam + ground_diffuse*Field.ground_diffuse_iam)/rad
            else:
                solar_field_operation = False
            if solar_field_operation:
                it = 0
                while True:
                    Field_outputs = Field.compute_outputs(mass_flow_field, previous_enthalpies['h_in_solar_field'],
                                                          h_mains_field, rad, IAM_eff, T_amb)
                    HX_outputs = HX.compute_outputs(mass_flow_field, Field_outputs['h_out'],
                                                    mass_flow_field, previous_enthalpies['h_in_HX_load'], h_mains)
                    Tank_outputs = Tank.compute_outputs(mass_flow_field, HX_outputs['h_out_load'],
                                                        demanded_flow, h_in_system,
                                                        None, None, None, None,
                                                        T_amb, time_step)
                    it = it + 1
                    if (abs(HX_outputs['h_out_source'] - previous_enthalpies['h_in_solar_field'])/previous_enthalpies['h_in_solar_field'] < tolerance and
                        abs(Tank_outputs['outlet_1_h'] - previous_enthalpies['h_in_HX_load'])/previous_enthalpies['h_in_HX_load'] < tolerance):
                        maxIt = False
                        break
                    if it == max_iterations:
                        maxIt = True
                        break
                    previous_enthalpies = {'h_in_solar_field': HX_outputs['h_out_source'], 'h_in_HX_load': Tank_outputs['outlet_1_h']}
            else:
                Tank_outputs = Tank.compute_outputs(0, h_mains,
                                                    demanded_flow, h_mains,
                                                    None, None, None, None,
                                                    T_amb, time_step)
        else:
            Tank_outputs = Tank.compute_outputs(0, h_mains,
                                                0, h_mains,
                                                None, None, None, None,
                                                T_amb, time_step)
        Tank.update_temperature()
        t = np.round(t + time_step, 2)
    
    Result = {'t(hr)': [],
              'system_operation': [],
              'solar_field_operation': [],
              'total_irradiance_on_collector_plane(W/m2)': [],
              'storage_tank_outlet_temperature(C)': [],
              'useful_solar_power(W)': [],
              'wasted_solar_power(W)': [],
              'power_extracted_from_tank(W)': [],
              'aux_heater_power(W)': [],
              'demanded_flow_temperature(C)': [],
              'conventional_energy_cost': [],
              'aux_heater_nominal_power_surpassed': [],
              'setPoint_Temp_surpassed': [],
              'system_maximum_iterations_reached': [],
              'tank_maximum_iterations_reached': [] }
    t = 0
    while t < 8760:
                
        day = int(t/24) + 1
        month = month_from_day(day)
        week_day = week_day_from_day(day)
        day_time = corrected_time(t)%24
        
        sky_diffuse = float(sky_diff_func(t))
        ground_diffuse = float(ground_diff_func(t))
        DNIrr = float(DNI_func(t))
        T_amb = float(T_amb_func(t))
        T_in_system = monthly_inlet_temperatures[month]
        h_in_system = PropsHeatedFluid.T_to_h(T_in_system)
        T_mains = monthly_mains_temperatures[month]
        h_mains = PropsHeatedFluid.T_to_h(T_mains)
        h_mains_field = PropsField.T_to_h(T_mains)
        demanded_flow = monthly_flows[month]
        
        aoi, longi, trans = Field.incidence_angles(float(compute_zenith(t)), float(compute_azimuth(t)))
        if aoi == None:
            rad = sky_diffuse + ground_diffuse
        else:
            beam_rad = DNIrr*cos(aoi)
            rad = beam_rad + sky_diffuse + ground_diffuse
        
        if t_start == t_end and demanded_flow > 0 and week_day in work_day_list:
            system_operation = True
        elif t_start < t_end and day_time >= t_start and day_time <= t_end and demanded_flow > 0 and week_day in work_day_list:
            system_operation = True
        elif t_start > t_end and (day_time >= t_start or day_time <= t_end) and demanded_flow > 0 and week_day in work_day_list:
            system_operation = True
        else:
            system_operation = False
            solar_field_operation = False
        
        if system_operation:
            if rad > 0:
                solar_field_operation = True
                if aoi == None:
                    IAM_eff = (sky_diffuse*Field.sky_diffuse_iam + ground_diffuse*Field.ground_diffuse_iam)/rad
                else:
                    beam_iam = Field.IAM_func(aoi, longi, trans)
                    IAM_eff = (beam_rad*beam_iam + sky_diffuse*Field.sky_diffuse_iam + ground_diffuse*Field.ground_diffuse_iam)/rad
            else:
                solar_field_operation = False
            if solar_field_operation:
                it = 0
                while True:
                    Field_outputs = Field.compute_outputs(mass_flow_field, previous_enthalpies['h_in_solar_field'],
                                                          h_mains_field, rad, IAM_eff, T_amb)
                    HX_outputs = HX.compute_outputs(mass_flow_field, Field_outputs['h_out'],
                                                    mass_flow_field, previous_enthalpies['h_in_HX_load'], h_mains)
                    Tank_outputs = Tank.compute_outputs(mass_flow_field, HX_outputs['h_out_load'],
                                                        demanded_flow, h_in_system,
                                                        None, None, None, None,
                                                        T_amb, time_step)
                    it = it + 1
                    if (abs(HX_outputs['h_out_source'] - previous_enthalpies['h_in_solar_field'])/previous_enthalpies['h_in_solar_field'] < tolerance and
                        abs(Tank_outputs['outlet_1_h'] - previous_enthalpies['h_in_HX_load'])/previous_enthalpies['h_in_HX_load'] < tolerance):
                        maxIt = False
                        break
                    if it == max_iterations:
                        maxIt = True
                        break
                    previous_enthalpies = {'h_in_solar_field': HX_outputs['h_out_source'], 'h_in_HX_load': Tank_outputs['outlet_1_h']}
                
                useful_solar_power = HX_outputs['Q_useful']
                wasted_solar_power = Field_outputs['Q_waste'] + HX_outputs['Q_waste']
                
            else:
                maxIt = False
                Tank_outputs = Tank.compute_outputs(0, h_mains,
                                                    demanded_flow, h_mains,
                                                    None, None, None, None,
                                                    T_amb, time_step)
                
                useful_solar_power = 0
                wasted_solar_power = 0

            T_out_Tank = PropsHeatedFluid.h_to_T(Tank_outputs['outlet_2_h'])
            if T_out_Tank > T_set:
                boiler_power = 0
                T_out_boiler = T_out_Tank
                T_set_surpassed = True
                boiler_nominal_power_surpassed = False
            else:
                T_set_surpassed = False
                boiler_power = demanded_flow*(h_set - Tank_outputs['outlet_2_h'])
                
                if boiler_power > boiler_nominal_power:
                    boiler_nominal_power_surpassed = True
                    boiler_power = boiler_nominal_power
                    T_out_boiler = PropsHeatedFluid.h_to_T(Tank_outputs['outlet_2_h'] + boiler_power/demanded_flow)
                else:
                    boiler_nominal_power_surpassed = False
                    T_out_boiler = T_set
            
            
        else:
            maxIt = False
            Tank_outputs = Tank.compute_outputs(0, h_mains,
                                                0, h_mains,
                                                None, None, None, None,
                                                T_amb, time_step)

            boiler_power  = 0
            useful_solar_power = 0
            wasted_solar_power = 0
            T_set_surpassed = False
            boiler_nominal_power_surpassed = False
            T_out_boiler = np.nan
        
        TES_power = Tank_outputs['Q_demand']
        T_out_system = T_out_boiler
        conventional_energy_cost = boiler_power*time_step*cost_per_conventional_kJ/boiler_efficiency
        
        Result['t(hr)'].append(t)
        Result['system_operation'].append(system_operation)
        Result['solar_field_operation'].append(solar_field_operation)
        Result['total_irradiance_on_collector_plane(W/m2)'].append(rad/3.6)
        Result['storage_tank_outlet_temperature(C)'].append(PropsHeatedFluid.h_to_T(Tank_outputs['outlet_2_h']))
        Result['useful_solar_power(W)'].append(useful_solar_power/3.6)
        Result['wasted_solar_power(W)'].append(wasted_solar_power/3.6)
        Result['power_extracted_from_tank(W)'].append(TES_power/3.6)
        Result['aux_heater_power(W)'].append(boiler_power/3.6)
        Result['demanded_flow_temperature(C)'].append(T_out_system)
        Result['conventional_energy_cost'].append(conventional_energy_cost)
        Result['aux_heater_nominal_power_surpassed'].append(boiler_nominal_power_surpassed)
        Result['setPoint_Temp_surpassed'].append(T_set_surpassed)
        Result['system_maximum_iterations_reached'].append(maxIt)
        Result['tank_maximum_iterations_reached'].append(Tank_outputs['maxIt'])
        
        Tank.update_temperature()
        t = np.round(t + time_step, 2)
        
    return Result


def NP_IE_ACS__NS_L_SI(Field, HX, T_set, Boiler_type, boiler_nominal_power,
                       boiler_efficiency, cost_per_conventional_kJ,
                       work_day_list, monthly_flows, monthly_inlet_temperatures,
                       monthly_mains_temperatures, t_start, t_end,
                       PropsField, PropsHeatedFluid, mass_flow_field,
                       sky_diff_func, ground_diff_func, DNI_func, T_amb_func,
                       compute_zenith, compute_azimuth, corrected_time,
                       time_step, tolerance, max_iterations):
    
    if T_set == PropsHeatedFluid.T_sat:
        if Boiler_type in ['Convencional vapor', 'Condensación vapor']:
            h_set = PropsHeatedFluid.h_sat_vap
        else:
            h_set = PropsHeatedFluid.h_sat_liq
    else:
        h_set = PropsHeatedFluid.T_to_h(T_set)
    
    h_in_solar_field = PropsField.T_to_h(40)
    Result = {'t(hr)': [],
              'system_operation': [],
              'solar_field_operation': [],
              'total_irradiance_on_collector_plane(W/m2)': [],
              'heat_exchanger_load_outlet_temperature(C)': [],
              'demanded_flow_temperature(C)': [],
              'useful_solar_power(W)': [],
              'wasted_solar_power(W)': [],
              'aux_heater_power(W)': [],
              'conventional_energy_cost': [],
              'aux_heater_nominal_power_surpassed': [],
              'setPoint_Temp_surpassed': [],
              'system_maximum_iterations_reached': [] }
    t = 0
    while t < 8760:
                
        day = int(t/24) + 1
        month = month_from_day(day)
        week_day = week_day_from_day(day)
        day_time = corrected_time(t)%24
        
        sky_diffuse = float(sky_diff_func(t))
        ground_diffuse = float(ground_diff_func(t))
        DNIrr = float(DNI_func(t))
        T_amb = float(T_amb_func(t))
        T_in_system = monthly_inlet_temperatures[month]
        h_in_system = PropsHeatedFluid.T_to_h(T_in_system)
        T_mains = monthly_mains_temperatures[month]
        h_mains = PropsHeatedFluid.T_to_h(T_mains)
        h_mains_field = PropsField.T_to_h(T_mains)
        demanded_flow = monthly_flows[month]
        
        aoi, longi, trans = Field.incidence_angles(float(compute_zenith(t)), float(compute_azimuth(t)))
        if aoi == None:
            rad = sky_diffuse + ground_diffuse
        else:
            beam_rad = DNIrr*cos(aoi)
            rad = beam_rad + sky_diffuse + ground_diffuse
        
        if t_start == t_end and demanded_flow > 0 and week_day in work_day_list:
            system_operation = True
        elif t_start < t_end and day_time >= t_start and day_time <= t_end and demanded_flow > 0 and week_day in work_day_list:
            system_operation = True
        elif t_start > t_end and (day_time >= t_start or day_time <= t_end) and demanded_flow > 0 and week_day in work_day_list:
            system_operation = True
        else:
            system_operation = False
            solar_field_operation = False
        
        if system_operation:
            if rad > 0:
                solar_field_operation = True
                if aoi == None:
                    IAM_eff = (sky_diffuse*Field.sky_diffuse_iam + ground_diffuse*Field.ground_diffuse_iam)/rad
                else:
                    beam_iam = Field.IAM_func(aoi, longi, trans)
                    IAM_eff = (beam_rad*beam_iam + sky_diffuse*Field.sky_diffuse_iam + ground_diffuse*Field.ground_diffuse_iam)/rad
            else:
                solar_field_operation = False
            if solar_field_operation:
                it = 0
                while True:
                    Field_outputs = Field.compute_outputs(mass_flow_field, h_in_solar_field, h_mains_field, rad, IAM_eff, T_amb)
                    HX_outputs = HX.compute_outputs(mass_flow_field, Field_outputs['h_out'], demanded_flow, h_in_system, h_mains)
                    it = it + 1
                    if abs(HX_outputs['h_out_source'] - h_in_solar_field)/h_in_solar_field < tolerance:
                        maxIt = False
                        break
                    if it == max_iterations:
                        maxIt = True
                        break
                    h_in_solar_field = HX_outputs['h_out_source']
                    
                T_out_HX = PropsHeatedFluid.h_to_T(HX_outputs['h_out_load'])
                
                if T_out_HX > T_set:
                    boiler_power = 0
                    T_out_boiler = T_out_HX
                    boiler_nominal_power_surpassed = False
                    T_set_surpassed = True
                else:
                    T_set_surpassed = False
                    boiler_power = demanded_flow*(h_set - HX_outputs['h_out_load'])
                    
                    if boiler_power > boiler_nominal_power:
                        boiler_nominal_power_surpassed = True
                        boiler_power = boiler_nominal_power
                        T_out_boiler = PropsHeatedFluid.h_to_T(HX_outputs['h_out_load'] + boiler_power/demanded_flow)
                    else:
                        boiler_nominal_power_surpassed = False
                        T_out_boiler = T_set
                
                useful_solar_power = HX_outputs['Q_useful']
                wasted_solar_power = Field_outputs['Q_waste'] + HX_outputs['Q_waste']
                heat_exchanger_load_outlet_temperature = PropsHeatedFluid.h_to_T(HX_outputs['h_out_load'])
                    
            else:
                T_set_surpassed = False
                maxIt = False
                
                boiler_power = demanded_flow*(h_set - h_in_system)
                
                if boiler_power > boiler_nominal_power:
                    boiler_nominal_power_surpassed = True
                    boiler_power = boiler_nominal_power
                    T_out_boiler = PropsHeatedFluid.h_to_T(h_in_system + boiler_power/demanded_flow)
                else:
                    boiler_nominal_power_surpassed = False
                    T_out_boiler = T_set
                
                useful_solar_power = 0
                wasted_solar_power = 0
                heat_exchanger_load_outlet_temperature = PropsHeatedFluid.h_to_T(h_in_system)
        
        else:
            T_set_surpassed = False
            maxIt = False
            boiler_power = 0
            useful_solar_power = 0
            wasted_solar_power = 0
            boiler_nominal_power_surpassed = False
            T_out_boiler = np.nan
            heat_exchanger_load_outlet_temperature = np.nan
        
        T_out_system = T_out_boiler
        conventional_energy_cost = boiler_power*time_step*cost_per_conventional_kJ/boiler_efficiency
            
        Result['t(hr)'].append(t)
        Result['system_operation'].append(system_operation)
        Result['solar_field_operation'].append(solar_field_operation)
        Result['total_irradiance_on_collector_plane(W/m2)'].append(rad/3.6)
        Result['heat_exchanger_load_outlet_temperature(C)'].append(heat_exchanger_load_outlet_temperature)
        Result['demanded_flow_temperature(C)'].append(T_out_system)
        Result['useful_solar_power(W)'].append(useful_solar_power/3.6)
        Result['wasted_solar_power(W)'].append(wasted_solar_power/3.6)
        Result['aux_heater_power(W)'].append(boiler_power/3.6)
        Result['conventional_energy_cost'].append(conventional_energy_cost)
        Result['aux_heater_nominal_power_surpassed'].append(boiler_nominal_power_surpassed)
        Result['setPoint_Temp_surpassed'].append(T_set_surpassed)
        Result['system_maximum_iterations_reached'].append(maxIt)

        t = np.round(t + time_step, 2)
        
    return Result
    

def NS_L_PD(Field, T_set, boiler_nominal_power,
            boiler_efficiency, cost_per_conventional_kJ,
            work_day_list, monthly_flows, monthly_inlet_temperatures,
            monthly_mains_temperatures, t_start, t_end,
            PropsHeatedFluid, sky_diff_func, ground_diff_func, DNI_func,
            T_amb_func, compute_zenith, compute_azimuth, corrected_time,
            time_step, tolerance, max_iterations):
    
    if T_set >= PropsHeatedFluid.T_sat:
        h_set = PropsHeatedFluid.h_sat_liq
    else:
        h_set = PropsHeatedFluid.T_to_h(T_set)
        
    Result = {'t(hr)': [],
              'system_operation': [],
              'solar_field_operation': [],
              'total_irradiance_on_collector_plane(W/m2)': [],
              'solar_field_outlet_temperature(C)': [],
              'useful_solar_power(W)': [],
              'wasted_solar_power(W)': [],
              'aux_heater_power(W)': [],
              'aux_heater_outlet_temperature(C)': [],
              'demanded_flow_temperature(C)': [],
              'conventional_energy_cost': [],
              'aux_heater_nominal_power_surpassed': [],
              'setPoint_Temp_surpassed': [],
              'system_maximum_iterations_reached': [] }
    t = 0
    while t < 8760:
        
        day = int(t/24) + 1
        month = month_from_day(day)
        week_day = week_day_from_day(day)
        day_time = corrected_time(t)%24
        
        sky_diffuse = float(sky_diff_func(t))
        ground_diffuse = float(ground_diff_func(t))
        DNIrr = float(DNI_func(t))
        T_amb = float(T_amb_func(t))
        T_in_system = monthly_inlet_temperatures[month]
        h_in_system = PropsHeatedFluid.T_to_h(T_in_system)
        T_mains = monthly_mains_temperatures[month]
        h_mains = PropsHeatedFluid.T_to_h(T_mains)
        demanded_flow = monthly_flows[month]
        
        aoi, longi, trans = Field.incidence_angles(float(compute_zenith(t)), float(compute_azimuth(t)))
        if aoi == None:
            rad = sky_diffuse + ground_diffuse
        else:
            beam_rad = DNIrr*cos(aoi)
            rad = beam_rad + sky_diffuse + ground_diffuse
        
        if t_start == t_end and demanded_flow > 0 and week_day in work_day_list:
            system_operation = True
        elif t_start < t_end and day_time >= t_start and day_time <= t_end and demanded_flow > 0 and week_day in work_day_list:
            system_operation = True
        elif t_start > t_end and (day_time >= t_start or day_time <= t_end) and demanded_flow > 0 and week_day in work_day_list:
            system_operation = True
        else:
            system_operation = False
            solar_field_operation = False
        
        if system_operation:
            if rad > 0:
                solar_field_operation = True
                if aoi == None:
                    IAM_eff = (sky_diffuse*Field.sky_diffuse_iam + ground_diffuse*Field.ground_diffuse_iam)/rad
                else:
                    beam_iam = Field.IAM_func(aoi, longi, trans)
                    IAM_eff = (beam_rad*beam_iam + sky_diffuse*Field.sky_diffuse_iam + ground_diffuse*Field.ground_diffuse_iam)/rad
            else:
                solar_field_operation = False
            
            if solar_field_operation:
                
                flow_in_solar_field = demanded_flow
                Field_outputs = Field.compute_outputs(flow_in_solar_field, h_in_system, h_mains, rad, IAM_eff, T_amb)
                
                if Field_outputs['h_out'] >= h_set or Field_outputs['Q_waste'] > 0:
                    h_out_solar_field = Field_outputs['h_out']
                    T_out_solar_field = PropsHeatedFluid.h_to_T(h_out_solar_field)
                    h_out_system = h_out_solar_field
                    T_out_system = T_out_solar_field
                    useful_solar_power = Field_outputs['Q_useful']
                    wasted_solar_power = Field_outputs['Q_waste']
                    flow_in_solar_field = demanded_flow
                    flow_in_boiler = 0
                    boiler_power = 0
                    maxIt = False
                    boiler_nominal_power_surpassed = False
                    T_out_boiler = np.nan
                    if Field_outputs['h_out'] > h_set:
                        T_set_surpassed = True
                    else:
                        T_set_surpassed = False
                        
                
                else:
                    it = 0
                    while True:
                        field_total_power = Field_outputs['Q_useful']
                        if field_total_power == 0:
                            maxIt = False
                            h_out_solar_field = h_in_system
                            T_out_solar_field = np.nan
                            useful_solar_power = 0
                            wasted_solar_power = 0
                            flow_in_solar_field = 0
                            flow_in_boiler = demanded_flow
                            break
                        flow_in_solar_field = field_total_power/(h_set - h_in_system)
                        if flow_in_solar_field < demanded_flow*0.05:
                            maxIt = False
                            h_out_solar_field = h_in_system
                            T_out_solar_field = np.nan
                            useful_solar_power = 0
                            wasted_solar_power = 0
                            flow_in_solar_field = 0
                            flow_in_boiler = demanded_flow
                            break
                        flow_in_boiler = demanded_flow - flow_in_solar_field
                        Field_outputs = Field.compute_outputs(flow_in_solar_field, h_in_system, h_mains, rad, IAM_eff, T_amb)
                        h_out_solar_field = Field_outputs['h_out']
                        T_out_solar_field = PropsHeatedFluid.h_to_T(h_out_solar_field)
                        useful_solar_power = Field_outputs['Q_useful']
                        wasted_solar_power = Field_outputs['Q_waste']
                        it = it + 1
                        if abs(Field_outputs['h_out'] - h_set)/h_set < tolerance:
                            maxIt = False
                            break
                        if it == max_iterations:
                            maxIt = True
                            break
                    
                    boiler_power = flow_in_boiler*(h_set - h_in_system)
                    
                    if boiler_power > boiler_nominal_power:
                        boiler_nominal_power_surpassed = True
                        boiler_power = boiler_nominal_power
                        h_out_boiler = h_in_system + boiler_power/flow_in_boiler
                        T_out_boiler = PropsHeatedFluid.h_to_T(h_out_boiler)
                    else:
                        boiler_nominal_power_surpassed = False
                        h_out_boiler = h_set
                        T_out_boiler = T_set
                    
                    T_set_surpassed = False
                    h_out_system = (flow_in_boiler*h_out_boiler + flow_in_solar_field*h_out_solar_field)/demanded_flow
                    T_out_system = PropsHeatedFluid.h_to_T(h_out_system)
            
            else:
                
                T_set_surpassed = False
                
                maxIt = False
                flow_in_solar_field = 0
                flow_in_boiler = demanded_flow
                
                boiler_power = flow_in_boiler*(h_set - h_in_system)
                
                if boiler_power > boiler_nominal_power:
                    boiler_nominal_power_surpassed = True
                    boiler_power = boiler_nominal_power
                    h_out_boiler = h_in_system + boiler_power/flow_in_boiler
                    T_out_boiler = PropsHeatedFluid.h_to_T(h_out_boiler)
                else:
                    boiler_nominal_power_surpassed = False
                    h_out_boiler = h_set
                    T_out_boiler = T_set
                    
                h_out_system = h_out_boiler
                T_out_system = T_out_boiler
                
                h_out_solar_field = h_in_system
                T_out_solar_field = np.nan
                
                useful_solar_power = 0
                wasted_solar_power = 0
                
        else:
            
            maxIt = False
            boiler_power = 0
            useful_solar_power = 0
            wasted_solar_power = 0
            boiler_nominal_power_surpassed = False
            T_set_surpassed = False
            T_out_boiler = np.nan
            T_out_solar_field = np.nan
            T_out_system = np.nan
            
        conventional_energy_cost = boiler_power*time_step*cost_per_conventional_kJ/boiler_efficiency
        
        Result['t(hr)'].append(t)
        Result['system_operation'].append(system_operation)
        Result['solar_field_operation'].append(solar_field_operation)
        Result['total_irradiance_on_collector_plane(W/m2)'].append(rad/3.6)
        Result['solar_field_outlet_temperature(C)'].append(T_out_solar_field)
        Result['useful_solar_power(W)'].append(useful_solar_power/3.6)
        Result['wasted_solar_power(W)'].append(wasted_solar_power/3.6)
        Result['aux_heater_power(W)'].append(boiler_power/3.6)
        Result['aux_heater_outlet_temperature(C)'].append(T_out_boiler)
        Result['demanded_flow_temperature(C)'].append(T_out_system)
        Result['conventional_energy_cost'].append(conventional_energy_cost)
        Result['aux_heater_nominal_power_surpassed'].append(boiler_nominal_power_surpassed)
        Result['setPoint_Temp_surpassed'].append(T_set_surpassed)
        Result['system_maximum_iterations_reached'].append(maxIt)
        
        t = np.round(t + time_step, 2)
    
    return Result


def NS_L_PI(Field, HX, T_set, Boiler_type, boiler_nominal_power,
            boiler_efficiency, cost_per_conventional_kJ,
            work_day_list, monthly_flows, monthly_inlet_temperatures,
            monthly_mains_temperatures, t_start, t_end,
            PropsHeatedFluid, PropsField, mass_flow_field,
            sky_diff_func, ground_diff_func, DNI_func, T_amb_func,
            compute_zenith, compute_azimuth, corrected_time,
            time_step, tolerance, max_iterations):
    
    if T_set >= PropsHeatedFluid.T_sat:
        h_set = PropsHeatedFluid.h_sat_liq
    else:
        h_set = PropsHeatedFluid.T_to_h(T_set)
        
    Result = {'t(hr)': [],
              'system_operation': [],
              'solar_field_operation': [],
              'total_irradiance_on_collector_plane(W/m2)': [],
              'heat_exchanger_load_outlet_temperature(C)': [],
              'useful_solar_power(W)': [],
              'wasted_solar_power(W)': [],
              'aux_heater_power(W)': [],
              'aux_heater_outlet_temperature(C)': [],
              'demanded_flow_temperature(C)': [],
              'conventional_energy_cost': [],
              'aux_heater_nominal_power_surpassed': [],
              'setPoint_Temp_surpassed': [],
              'flow_maximum_iterations_reached': [],
              'solar_field_loop_maximum_iterations_reached': []}
    t = 0
    while t < 8760:
        
        day = int(t/24) + 1
        month = month_from_day(day)
        week_day = week_day_from_day(day)
        day_time = corrected_time(t)%24
        
        sky_diffuse = float(sky_diff_func(t))
        ground_diffuse = float(ground_diff_func(t))
        DNIrr = float(DNI_func(t))
        T_amb = float(T_amb_func(t))
        T_in_system = monthly_inlet_temperatures[month]
        h_in_system = PropsHeatedFluid.T_to_h(T_in_system)
        T_mains = monthly_mains_temperatures[month]
        h_mains = PropsHeatedFluid.T_to_h(T_mains)
        h_mains_field = PropsField.T_to_h(T_mains)
        demanded_flow = monthly_flows[month]
        
        aoi, longi, trans = Field.incidence_angles(float(compute_zenith(t)), float(compute_azimuth(t)))
        if aoi == None:
            rad = sky_diffuse + ground_diffuse
        else:
            beam_rad = DNIrr*cos(aoi)
            rad = beam_rad + sky_diffuse + ground_diffuse
        
        if t_start == t_end and demanded_flow > 0 and week_day in work_day_list:
            system_operation = True
        elif t_start < t_end and day_time >= t_start and day_time <= t_end and demanded_flow > 0 and week_day in work_day_list:
            system_operation = True
        elif t_start > t_end and (day_time >= t_start or day_time <= t_end) and demanded_flow > 0 and week_day in work_day_list:
            system_operation = True
        else:
            system_operation = False
            solar_field_operation = False
        
        if system_operation:
            if rad > 0:
                solar_field_operation = True
                if aoi == None:
                    IAM_eff = (sky_diffuse*Field.sky_diffuse_iam + ground_diffuse*Field.ground_diffuse_iam)/rad
                else:
                    beam_iam = Field.IAM_func(aoi, longi, trans)
                    IAM_eff = (beam_rad*beam_iam + sky_diffuse*Field.sky_diffuse_iam + ground_diffuse*Field.ground_diffuse_iam)/rad
            else:
                solar_field_operation = False
            
            if solar_field_operation:
                
                flow_in_HX_load = demanded_flow
                h_in_solar_field = PropsField.T_to_h(40)
                it2 = 0
                while True:
                    Field_outputs = Field.compute_outputs(mass_flow_field, h_in_solar_field, h_mains_field, rad, IAM_eff, T_amb)
                    HX_outputs = HX.compute_outputs(mass_flow_field, Field_outputs['h_out'], flow_in_HX_load, h_in_system, h_mains)
                    it2 = it2 + 1
                    if abs(HX_outputs['h_out_source'] - h_in_solar_field)/h_in_solar_field < tolerance:
                        maxIt2 = False
                        break
                    if it2 == max_iterations:
                        maxIt2 = True
                        break
                    h_in_solar_field = HX_outputs['h_out_source']
                
                if HX_outputs['h_out_load'] >= h_set:
                    h_out_HX_load = HX_outputs['h_out_load']
                    T_out_HX_load = PropsHeatedFluid.h_to_T(h_out_HX_load)
                    h_out_system = h_out_HX_load
                    T_out_system = T_out_HX_load
                    useful_solar_power = HX_outputs['Q_useful']
                    wasted_solar_power = Field_outputs['Q_waste'] + HX_outputs['Q_waste']
                    flow_in_HX_load = demanded_flow
                    flow_in_boiler = 0
                    boiler_power = 0
                    maxIt1 = False
                    boiler_nominal_power_surpassed = False
                    T_out_boiler = np.nan
                    if HX_outputs['h_out_load'] > h_set:
                        T_set_surpassed = True
                    else:
                        T_set_surpassed = False
                
                else:
                    it1 = 0
                    while True:
                        field_power = Field_outputs['Q_useful']
                        if field_power == 0:
                            maxIt1 = False
                            h_out_HX_load = h_in_system
                            T_out_HX_load = np.nan
                            useful_solar_power = 0
                            wasted_solar_power = 0
                            flow_in_HX_load = 0
                            flow_in_boiler = demanded_flow
                            break
                        flow_in_HX_load = field_power/(h_set - h_in_system)
                        if flow_in_HX_load < demanded_flow*0.05:
                            maxIt1 = False
                            h_out_HX_load = h_in_system
                            T_out_HX_load = np.nan
                            useful_solar_power = 0
                            wasted_solar_power = 0
                            flow_in_HX_load = 0
                            flow_in_boiler = demanded_flow
                            break
                        flow_in_boiler = demanded_flow - flow_in_HX_load
                        it2 = 0
                        while True:
                            Field_outputs = Field.compute_outputs(mass_flow_field, h_in_solar_field, h_mains_field, rad, IAM_eff, T_amb)
                            HX_outputs = HX.compute_outputs(mass_flow_field, Field_outputs['h_out'], flow_in_HX_load, h_in_system, h_mains)
                            it2 = it2 + 1
                            if abs(HX_outputs['h_out_source'] - h_in_solar_field)/h_in_solar_field < tolerance:
                                maxIt2 = False
                                break
                            if it2 == max_iterations:
                                maxIt2 = True
                                break
                            h_in_solar_field = HX_outputs['h_out_source']
                        h_out_HX_load = HX_outputs['h_out_load']
                        T_out_HX_load = PropsHeatedFluid.h_to_T(h_out_HX_load)
                        useful_solar_power = HX_outputs['Q_useful']
                        wasted_solar_power = Field_outputs['Q_waste'] + HX_outputs['Q_waste']
                        it1 = it1 + 1
                        if abs(HX_outputs['h_out_load'] - h_set)/h_set < tolerance:
                            maxIt1 = False
                            break
                        if it1 == max_iterations:
                            maxIt1 = True
                            break
                    
                    boiler_power = flow_in_boiler*(h_set - h_in_system)
                    
                    if boiler_power > boiler_nominal_power:
                        boiler_nominal_power_surpassed = True
                        boiler_power = boiler_nominal_power
                        h_out_boiler = h_in_system + boiler_power/flow_in_boiler
                        T_out_boiler = PropsHeatedFluid.h_to_T(h_out_boiler)
                    else:
                        boiler_nominal_power_surpassed = False
                        h_out_boiler = h_set
                        T_out_boiler = T_set
                    
                    T_set_surpassed = False
                    h_out_system = (flow_in_boiler*h_out_boiler + flow_in_HX_load*h_out_HX_load)/demanded_flow
                    T_out_system = PropsHeatedFluid.h_to_T(h_out_system)
            
            else:
                
                T_set_surpassed = False
                
                maxIt1 = False
                maxIt2 = False
                flow_in_HX_load = 0
                flow_in_boiler = demanded_flow
                
                boiler_power = flow_in_boiler*(h_set - h_in_system)
                
                if boiler_power > boiler_nominal_power:
                    boiler_nominal_power_surpassed = True
                    boiler_power = boiler_nominal_power
                    h_out_boiler = h_in_system + boiler_power/flow_in_boiler
                    T_out_boiler = PropsHeatedFluid.h_to_T(h_out_boiler)
                else:
                    boiler_nominal_power_surpassed = False
                    h_out_boiler = h_set
                    T_out_boiler = T_set
                    
                h_out_system = h_out_boiler
                T_out_system = T_out_boiler
                
                h_out_HX_load = h_in_system
                T_out_HX_load = np.nan
                
                useful_solar_power = 0
                wasted_solar_power = 0
                
        else:
            
            maxIt1 = False
            maxIt2 = False
            boiler_power = 0
            useful_solar_power = 0
            wasted_solar_power = 0
            boiler_nominal_power_surpassed = False
            T_set_surpassed = False
            T_out_boiler = np.nan
            T_out_HX_load = np.nan
            T_out_system = np.nan
            
        conventional_energy_cost = boiler_power*time_step*cost_per_conventional_kJ/boiler_efficiency
        
        Result['t(hr)'].append(t)
        Result['system_operation'].append(system_operation)
        Result['solar_field_operation'].append(solar_field_operation)
        Result['total_irradiance_on_collector_plane(W/m2)'].append(rad/3.6)
        Result['heat_exchanger_load_outlet_temperature(C)'].append(T_out_HX_load)
        Result['useful_solar_power(W)'].append(useful_solar_power/3.6)
        Result['wasted_solar_power(W)'].append(wasted_solar_power/3.6)
        Result['aux_heater_power(W)'].append(boiler_power/3.6)
        Result['aux_heater_outlet_temperature(C)'].append(T_out_boiler)
        Result['demanded_flow_temperature(C)'].append(T_out_system)
        Result['conventional_energy_cost'].append(conventional_energy_cost)
        Result['aux_heater_nominal_power_surpassed'].append(boiler_nominal_power_surpassed)
        Result['setPoint_Temp_surpassed'].append(T_set_surpassed)
        Result['flow_maximum_iterations_reached'].append(maxIt1)
        Result['solar_field_loop_maximum_iterations_reached'].append(maxIt2)
        
        t = np.round(t + time_step, 2)
    
    return Result

def NS_L_CA_1(Field, Tank, T_set, boiler_nominal_power,
              boiler_efficiency, cost_per_conventional_kJ,
              work_day_list, monthly_flows, monthly_inlet_temperatures,
              monthly_mains_temperatures, t_start, t_end,
              PropsHeatedFluid, PropsField, PropsBoiler, mass_flow_field,
              sky_diff_func, ground_diff_func, DNI_func, T_amb_func,
              compute_zenith, compute_azimuth, corrected_time,
              time_step, tolerance, max_iterations):
    
    if T_set > PropsHeatedFluid.T_sat - 5:
        T_set = PropsHeatedFluid.T_sat - 5
    
    boiler_mass_flow = 1.2*max([ monthly_flows[i] for i in monthly_flows ])
    
    previous_enthalpies = {'h_in_solar_field': PropsField.T_to_h(40), 'h_in_boiler': PropsBoiler.T_to_h(40)}
    boiler_state = 'OFF'

    t = 8760 - 24*10
    while t < 8760:
        
        day_now = int(t/24) + 1
        month_now = month_from_day(day_now)
        week_day_now = week_day_from_day(day_now)
        day_time_now = corrected_time(t)%24
        
        day_next_hour = int(t/24) + 1
        month_next_hour = month_from_day(day_next_hour)
        week_day_next_hour = week_day_from_day(day_next_hour)
        day_time_next_hour = corrected_time(t + 1)%24
        
        sky_diffuse = float(sky_diff_func(t))
        ground_diffuse = float(ground_diff_func(t))
        DNIrr = float(DNI_func(t))
        T_amb = float(T_amb_func(t))
        T_in_system = monthly_inlet_temperatures[month_now]
        h_in_system = PropsHeatedFluid.T_to_h(T_in_system)
        T_mains = monthly_mains_temperatures[month_now]
        h_mains = PropsHeatedFluid.T_to_h(T_mains)
        h_mains_field = PropsField.T_to_h(T_mains)
        
        aoi, longi, trans = Field.incidence_angles(float(compute_zenith(t)), float(compute_azimuth(t)))
        if aoi == None:
            rad = sky_diffuse + ground_diffuse
        else:
            beam_rad = DNIrr*cos(aoi)
            rad = beam_rad + sky_diffuse + ground_diffuse
            
        operation_now = ( (t_start == t_end and monthly_flows[month_now] > 0 and week_day_now in work_day_list) or 
                          (t_start < t_end and day_time_now >= t_start and day_time_now <= t_end and monthly_flows[month_now] > 0 and week_day_now in work_day_list) or
                          (t_start > t_end and (day_time_now >= t_start or day_time_now <= t_end) and monthly_flows[month_now] > 0 and week_day_now in work_day_list) )
        
        operation_next_hour = ( (t_start == t_end and monthly_flows[month_next_hour] > 0 and week_day_next_hour in work_day_list) or 
                                (t_start < t_end and day_time_next_hour >= t_start and day_time_next_hour <= t_end and monthly_flows[month_next_hour] > 0 and week_day_next_hour in work_day_list) or
                                (t_start > t_end and (day_time_next_hour >= t_start or day_time_next_hour <= t_end) and monthly_flows[month_next_hour] > 0 and week_day_next_hour in work_day_list) )
        
        if operation_now:
            system_operation = True
            demanded_flow = monthly_flows[month_now]
        elif operation_next_hour:
            system_operation = True
            demanded_flow = 0
        else:
            system_operation = False
            solar_field_operation = False
        
        if Tank.node_temperatures[1] >= T_set + 2:
            boiler_state = 'OFF'
        if Tank.node_temperatures[1] <= T_set:
            boiler_state = 'ON'
        
        if system_operation:
            if rad > 0:
                solar_field_operation = True
                if aoi == None:
                    IAM_eff = (sky_diffuse*Field.sky_diffuse_iam + ground_diffuse*Field.ground_diffuse_iam)/rad
                else:
                    beam_iam = Field.IAM_func(aoi, longi, trans)
                    IAM_eff = (beam_rad*beam_iam + sky_diffuse*Field.sky_diffuse_iam + ground_diffuse*Field.ground_diffuse_iam)/rad
            else:
                solar_field_operation = False
            
            if solar_field_operation:
                
                if boiler_state == 'ON':
                    it = 0
                    while True:
                        Field_outputs = Field.compute_outputs(mass_flow_field, previous_enthalpies['h_in_solar_field'], h_mains_field, rad, IAM_eff, T_amb)
                        h_out_boiler = previous_enthalpies['h_in_boiler'] + boiler_nominal_power/boiler_mass_flow
                        if h_out_boiler > PropsBoiler.h_sat_liq:
                            h_out_boiler = PropsBoiler.h_sat_liq
                        Tank_outputs = Tank.compute_outputs(0, h_mains, demanded_flow, h_in_system,
                                                            mass_flow_field, Field_outputs['h_out'], boiler_mass_flow, h_out_boiler,
                                                            T_amb, time_step)
                        it = it + 1
                        if (abs(Tank_outputs['HX1_outlet_h'] - previous_enthalpies['h_in_solar_field'])/previous_enthalpies['h_in_solar_field'] < tolerance and
                            abs(Tank_outputs['HX2_outlet_h'] - previous_enthalpies['h_in_boiler'])/previous_enthalpies['h_in_boiler'] < tolerance ):
                            maxIt = False
                            break
                        if it == max_iterations:
                            maxIt = True
                            break
                        previous_enthalpies = {'h_in_solar_field': Tank_outputs['HX1_outlet_h'], 'h_in_boiler': Tank_outputs['HX2_outlet_h']}
                    
                if boiler_state == 'OFF':
                    
                    it = 0
                    while True:
                        Field_outputs = Field.compute_outputs(mass_flow_field, previous_enthalpies['h_in_solar_field'], h_mains_field, rad, IAM_eff, T_amb)
                        Tank_outputs = Tank.compute_outputs(0, h_mains, demanded_flow, h_in_system,
                                                            mass_flow_field, Field_outputs['h_out'], None, None,
                                                            T_amb, time_step)
                        it = it + 1
                        if abs(Tank_outputs['HX1_outlet_h'] - previous_enthalpies['h_in_solar_field'])/previous_enthalpies['h_in_solar_field'] < tolerance:
                            maxIt = False
                            break
                        if it == max_iterations:
                            maxIt = True
                            break
                        previous_enthalpies['h_in_solar_field'] = Tank_outputs['HX1_outlet_h']
                
            else:

                if boiler_state == 'ON':
                    it = 0
                    while True:
                        h_out_boiler = previous_enthalpies['h_in_boiler'] + boiler_nominal_power/boiler_mass_flow
                        if h_out_boiler > PropsBoiler.h_sat_liq:
                            h_out_boiler = PropsBoiler.h_sat_liq
                        Tank_outputs = Tank.compute_outputs(0, h_mains, demanded_flow, h_in_system,
                                                            None, None, boiler_mass_flow, h_out_boiler,
                                                            T_amb, time_step)
                        it = it + 1
                        if abs(Tank_outputs['HX2_outlet_h'] - previous_enthalpies['h_in_boiler'])/previous_enthalpies['h_in_boiler'] < tolerance:
                            maxIt = False
                            break
                        if it == max_iterations:
                            maxIt = True
                            break
                        previous_enthalpies['h_in_boiler'] = Tank_outputs['HX2_outlet_h']
                
                if boiler_state == 'OFF':

                    Tank_outputs = Tank.compute_outputs(0, h_mains, demanded_flow, h_in_system,
                                                        None, None, None, None,
                                                        T_amb, time_step)
                    
        else:
            
            Tank_outputs = Tank.compute_outputs(0, h_mains, 0, h_in_system,
                                                None, None, None, None,
                                                T_amb, time_step)
        
        Tank.update_temperature()
        
        t = np.round(t + time_step, 2)

    Result = {'t(hr)': [],
              'system_operation': [],
              'solar_field_operation': [],
              'total_irradiance_on_collector_plane(W/m2)': [],
              'useful_solar_power(W)': [],
              'wasted_solar_power(W)': [],
              'aux_heater_power(W)': [],
              'demanded_flow_temperature(C)': [],
              'power_extracted_from_tank(W)': [],
              'conventional_energy_cost': [],
              'system_maximum_iterations_reached': [],
              'tank_maximum_iterations_reached': [] }
    t = 0
    while t < 8760:
        
        day_now = int(t/24) + 1
        month_now = month_from_day(day_now)
        week_day_now = week_day_from_day(day_now)
        day_time_now = corrected_time(t)%24
        
        day_next_hour = int(t/24) + 1
        month_next_hour = month_from_day(day_next_hour)
        week_day_next_hour = week_day_from_day(day_next_hour)
        day_time_next_hour = corrected_time(t + 1)%24
        
        sky_diffuse = float(sky_diff_func(t))
        ground_diffuse = float(ground_diff_func(t))
        DNIrr = float(DNI_func(t))
        T_amb = float(T_amb_func(t))
        T_in_system = monthly_inlet_temperatures[month_now]
        h_in_system = PropsHeatedFluid.T_to_h(T_in_system)
        T_mains = monthly_mains_temperatures[month_now]
        h_mains = PropsHeatedFluid.T_to_h(T_mains)
        h_mains_field = PropsField.T_to_h(T_mains)
        
        aoi, longi, trans = Field.incidence_angles(float(compute_zenith(t)), float(compute_azimuth(t)))
        if aoi == None:
            rad = sky_diffuse + ground_diffuse
        else:
            beam_rad = DNIrr*cos(aoi)
            rad = beam_rad + sky_diffuse + ground_diffuse
            
        operation_now = ( (t_start == t_end and monthly_flows[month_now] > 0 and week_day_now in work_day_list) or 
                          (t_start < t_end and day_time_now >= t_start and day_time_now <= t_end and monthly_flows[month_now] > 0 and week_day_now in work_day_list) or
                          (t_start > t_end and (day_time_now >= t_start or day_time_now <= t_end) and monthly_flows[month_now] > 0 and week_day_now in work_day_list) )
        
        operation_next_hour = ( (t_start == t_end and monthly_flows[month_next_hour] > 0 and week_day_next_hour in work_day_list) or 
                                (t_start < t_end and day_time_next_hour >= t_start and day_time_next_hour <= t_end and monthly_flows[month_next_hour] > 0 and week_day_next_hour in work_day_list) or
                                (t_start > t_end and (day_time_next_hour >= t_start or day_time_next_hour <= t_end) and monthly_flows[month_next_hour] > 0 and week_day_next_hour in work_day_list) )
        
        if operation_now:
            system_operation = True
            demanded_flow = monthly_flows[month_now]
        elif operation_next_hour:
            system_operation = True
            demanded_flow = 0
        else:
            system_operation = False
            solar_field_operation = False
        
        if Tank.node_temperatures[1] >= T_set + 2:
            boiler_state = 'OFF'
        if Tank.node_temperatures[1] <= T_set:
            boiler_state = 'ON'
        
        if system_operation:
            if rad > 0:
                solar_field_operation = True
                if aoi == None:
                    IAM_eff = (sky_diffuse*Field.sky_diffuse_iam + ground_diffuse*Field.ground_diffuse_iam)/rad
                else:
                    beam_iam = Field.IAM_func(aoi, longi, trans)
                    IAM_eff = (beam_rad*beam_iam + sky_diffuse*Field.sky_diffuse_iam + ground_diffuse*Field.ground_diffuse_iam)/rad
            else:
                solar_field_operation = False
            
            if solar_field_operation:
                
                if boiler_state == 'ON':
                    it = 0
                    while True:
                        Field_outputs = Field.compute_outputs(mass_flow_field, previous_enthalpies['h_in_solar_field'], h_mains_field, rad, IAM_eff, T_amb)
                        h_out_boiler = previous_enthalpies['h_in_boiler'] + boiler_nominal_power/boiler_mass_flow
                        if h_out_boiler > PropsBoiler.h_sat_liq:
                            h_out_boiler = PropsBoiler.h_sat_liq
                        Tank_outputs = Tank.compute_outputs(0, h_mains, demanded_flow, h_in_system,
                                                            mass_flow_field, Field_outputs['h_out'], boiler_mass_flow, h_out_boiler,
                                                            T_amb, time_step)
                        it = it + 1
                        if (abs(Tank_outputs['HX1_outlet_h'] - previous_enthalpies['h_in_solar_field'])/previous_enthalpies['h_in_solar_field'] < tolerance and
                            abs(Tank_outputs['HX2_outlet_h'] - previous_enthalpies['h_in_boiler'])/previous_enthalpies['h_in_boiler'] < tolerance ):
                            maxIt = False
                            break
                        if it == max_iterations:
                            maxIt = True
                            break
                        previous_enthalpies = {'h_in_solar_field': Tank_outputs['HX1_outlet_h'], 'h_in_boiler': Tank_outputs['HX2_outlet_h']}
                    
                    useful_solar_power = Tank_outputs['HX1_Q']
                    wasted_solar_power = Field_outputs['Q_waste']
                    boiler_power = Tank_outputs['HX2_Q']
                    
                if boiler_state == 'OFF':
                    
                    it = 0
                    while True:
                        Field_outputs = Field.compute_outputs(mass_flow_field, previous_enthalpies['h_in_solar_field'], h_mains_field, rad, IAM_eff, T_amb)
                        Tank_outputs = Tank.compute_outputs(0, h_mains, demanded_flow, h_in_system,
                                                            mass_flow_field, Field_outputs['h_out'], None, None,
                                                            T_amb, time_step)
                        it = it + 1
                        if abs(Tank_outputs['HX1_outlet_h'] - previous_enthalpies['h_in_solar_field'])/previous_enthalpies['h_in_solar_field'] < tolerance:
                            maxIt = False
                            break
                        if it == max_iterations:
                            maxIt = True
                            break
                        previous_enthalpies['h_in_solar_field'] = Tank_outputs['HX1_outlet_h']
                        
                    useful_solar_power = Tank_outputs['HX1_Q']
                    wasted_solar_power = Field_outputs['Q_waste']
                    boiler_power = 0
                
            else:

                if boiler_state == 'ON':
                    it = 0
                    while True:
                        h_out_boiler = previous_enthalpies['h_in_boiler'] + boiler_nominal_power/boiler_mass_flow
                        if h_out_boiler > PropsBoiler.h_sat_liq:
                            h_out_boiler = PropsBoiler.h_sat_liq
                        Tank_outputs = Tank.compute_outputs(0, h_mains, demanded_flow, h_in_system,
                                                            None, None, boiler_mass_flow, h_out_boiler,
                                                            T_amb, time_step)
                        it = it + 1
                        if abs(Tank_outputs['HX2_outlet_h'] - previous_enthalpies['h_in_boiler'])/previous_enthalpies['h_in_boiler'] < tolerance:
                            maxIt = False
                            break
                        if it == max_iterations:
                            maxIt = True
                            break
                        previous_enthalpies['h_in_boiler'] = Tank_outputs['HX2_outlet_h']
                        
                    useful_solar_power = 0
                    wasted_solar_power = 0
                    boiler_power = Tank_outputs['HX2_Q']
                
                if boiler_state == 'OFF':

                    Tank_outputs = Tank.compute_outputs(0, h_mains, demanded_flow, h_in_system,
                                                        None, None, None, None,
                                                        T_amb, time_step)
                    
                    useful_solar_power = 0
                    wasted_solar_power = 0
                    boiler_power = 0
                    maxIt = False
                    
        else:
            
            Tank_outputs = Tank.compute_outputs(0, h_mains, 0, h_in_system,
                                                None, None, None, None,
                                                T_amb, time_step)
            useful_solar_power = 0
            wasted_solar_power = 0
            boiler_power = 0
            maxIt = False
            
        conventional_energy_cost = boiler_power*time_step*cost_per_conventional_kJ/boiler_efficiency
        T_out_system = PropsHeatedFluid.h_to_T(Tank_outputs['outlet_2_h'])
        TES_power = Tank_outputs['Q_demand']
        
        Result['t(hr)'].append(t)
        Result['system_operation'].append(system_operation)
        Result['solar_field_operation'].append(solar_field_operation)
        Result['total_irradiance_on_collector_plane(W/m2)'].append(rad/3.6)
        Result['useful_solar_power(W)'].append(useful_solar_power/3.6)
        Result['wasted_solar_power(W)'].append(wasted_solar_power/3.6)
        Result['aux_heater_power(W)'].append(boiler_power/3.6)
        Result['demanded_flow_temperature(C)'].append(T_out_system)
        Result['power_extracted_from_tank(W)'].append(TES_power/3.6)
        Result['conventional_energy_cost'].append(conventional_energy_cost)
        Result['system_maximum_iterations_reached'].append(maxIt)
        Result['tank_maximum_iterations_reached'].append(Tank_outputs['maxIt'])
        
        Tank.update_temperature()
        
        t = np.round(t + time_step, 2)
    
    return Result



def NS_L_CA_2(Field, Tank, HX, T_set, boiler_nominal_power,
              boiler_efficiency, cost_per_conventional_kJ,
              work_day_list, monthly_flows, monthly_inlet_temperatures,
              monthly_mains_temperatures, t_start, t_end,
              PropsHeatedFluid, PropsField, PropsBoiler, mass_flow_field,
              sky_diff_func, ground_diff_func, DNI_func, T_amb_func,
              compute_zenith, compute_azimuth, corrected_time,
              time_step, tolerance, max_iterations):
    
    if T_set > PropsHeatedFluid.T_sat - 5:
        T_set = PropsHeatedFluid.T_sat - 5
    
    boiler_mass_flow = 1.2*max([ monthly_flows[i] for i in monthly_flows ])
    heat_exchanger_load_flow = mass_flow_field 
    
    previous_enthalpies = {'h_in_solar_field': PropsField.T_to_h(40), 'h_in_HX_load': PropsHeatedFluid.T_to_h(40), 'h_in_boiler': PropsBoiler.T_to_h(40)}
    boiler_state = 'OFF'

    t = 8760 - 24*10
    while t < 8760:
        
        day_now = int(t/24) + 1
        month_now = month_from_day(day_now)
        week_day_now = week_day_from_day(day_now)
        day_time_now = corrected_time(t)%24
        
        day_next_hour = int(t/24) + 1
        month_next_hour = month_from_day(day_next_hour)
        week_day_next_hour = week_day_from_day(day_next_hour)
        day_time_next_hour = corrected_time(t + 1)%24
        
        sky_diffuse = float(sky_diff_func(t))
        ground_diffuse = float(ground_diff_func(t))
        DNIrr = float(DNI_func(t))
        T_amb = float(T_amb_func(t))
        T_in_system = monthly_inlet_temperatures[month_now]
        h_in_system = PropsHeatedFluid.T_to_h(T_in_system)
        T_mains = monthly_mains_temperatures[month_now]
        h_mains = PropsHeatedFluid.T_to_h(T_mains)
        h_mains_field = PropsField.T_to_h(T_mains)
        
        aoi, longi, trans = Field.incidence_angles(float(compute_zenith(t)), float(compute_azimuth(t)))
        if aoi == None:
            rad = sky_diffuse + ground_diffuse
        else:
            beam_rad = DNIrr*cos(aoi)
            rad = beam_rad + sky_diffuse + ground_diffuse
            
        operation_now = ( (t_start == t_end and monthly_flows[month_now] > 0 and week_day_now in work_day_list) or 
                          (t_start < t_end and day_time_now >= t_start and day_time_now <= t_end and monthly_flows[month_now] > 0 and week_day_now in work_day_list) or
                          (t_start > t_end and (day_time_now >= t_start or day_time_now <= t_end) and monthly_flows[month_now] > 0 and week_day_now in work_day_list) )
        
        operation_next_hour = ( (t_start == t_end and monthly_flows[month_next_hour] > 0 and week_day_next_hour in work_day_list) or 
                                (t_start < t_end and day_time_next_hour >= t_start and day_time_next_hour <= t_end and monthly_flows[month_next_hour] > 0 and week_day_next_hour in work_day_list) or
                                (t_start > t_end and (day_time_next_hour >= t_start or day_time_next_hour <= t_end) and monthly_flows[month_next_hour] > 0 and week_day_next_hour in work_day_list) )
        
        if operation_now:
            system_operation = True
            demanded_flow = monthly_flows[month_now]
        elif operation_next_hour:
            system_operation = True
            demanded_flow = 0
        else:
            system_operation = False
            solar_field_operation = False
        
        if Tank.node_temperatures[1] >= T_set + 2:
            boiler_state = 'OFF'
        if Tank.node_temperatures[1] <= T_set:
            boiler_state = 'ON'
        
        if system_operation:
            if rad > 0:
                solar_field_operation = True
                if aoi == None:
                    IAM_eff = (sky_diffuse*Field.sky_diffuse_iam + ground_diffuse*Field.ground_diffuse_iam)/rad
                else:
                    beam_iam = Field.IAM_func(aoi, longi, trans)
                    IAM_eff = (beam_rad*beam_iam + sky_diffuse*Field.sky_diffuse_iam + ground_diffuse*Field.ground_diffuse_iam)/rad
            else:
                solar_field_operation = False
            
            if solar_field_operation:
                
                if boiler_state == 'ON':
                    it = 0
                    while True:
                        Field_outputs = Field.compute_outputs(mass_flow_field, previous_enthalpies['h_in_solar_field'], h_mains_field, rad, IAM_eff, T_amb)
                        HX_outputs = HX.compute_outputs(mass_flow_field, Field_outputs['h_out'], heat_exchanger_load_flow, previous_enthalpies['h_in_HX_load'], h_mains)
                        h_out_boiler = previous_enthalpies['h_in_boiler'] + boiler_nominal_power/boiler_mass_flow
                        if h_out_boiler > PropsBoiler.h_sat_liq:
                            h_out_boiler = PropsBoiler.h_sat_liq
                        Tank_outputs = Tank.compute_outputs(heat_exchanger_load_flow, HX_outputs['h_out_load'], demanded_flow, h_in_system,
                                                            None, None, boiler_mass_flow, h_out_boiler,
                                                            T_amb, time_step)
                        it = it + 1
                        if (abs(HX_outputs['h_out_source'] - previous_enthalpies['h_in_solar_field'])/previous_enthalpies['h_in_solar_field'] < tolerance and
                            abs(Tank_outputs['outlet_1_h'] - previous_enthalpies['h_in_HX_load'])/previous_enthalpies['h_in_HX_load'] < tolerance and
                            abs(Tank_outputs['HX2_outlet_h'] - previous_enthalpies['h_in_boiler'])/previous_enthalpies['h_in_boiler'] < tolerance ):
                            maxIt = False
                            break
                        if it == max_iterations:
                            maxIt = True
                            break
                        previous_enthalpies = {'h_in_solar_field': HX_outputs['h_out_source'], 'h_in_HX_load': Tank_outputs['outlet_1_h'], 'h_in_boiler': Tank_outputs['HX2_outlet_h']}
                    
                if boiler_state == 'OFF':
                    
                    it = 0
                    while True:
                        Field_outputs = Field.compute_outputs(mass_flow_field, previous_enthalpies['h_in_solar_field'], h_mains_field, rad, IAM_eff, T_amb)
                        HX_outputs = HX.compute_outputs(mass_flow_field, Field_outputs['h_out'], heat_exchanger_load_flow, previous_enthalpies['h_in_HX_load'], h_mains)
                        Tank_outputs = Tank.compute_outputs(heat_exchanger_load_flow, HX_outputs['h_out_load'], demanded_flow, h_in_system,
                                                            None, None, None, None,
                                                            T_amb, time_step)
                        it = it + 1
                        if (abs(HX_outputs['h_out_source'] - previous_enthalpies['h_in_solar_field'])/previous_enthalpies['h_in_solar_field'] < tolerance and
                            abs(Tank_outputs['outlet_1_h'] - previous_enthalpies['h_in_HX_load'])/previous_enthalpies['h_in_HX_load'] < tolerance):
                            maxIt = False
                            break
                        if it == max_iterations:
                            maxIt = True
                            break
                        previous_enthalpies['h_in_solar_field'] =  HX_outputs['h_out_source']
                        previous_enthalpies['h_in_HX_load'] = Tank_outputs['outlet_1_h']
                
            else:

                if boiler_state == 'ON':
                    it = 0
                    while True:
                        h_out_boiler = previous_enthalpies['h_in_boiler'] + boiler_nominal_power/boiler_mass_flow
                        if h_out_boiler > PropsBoiler.h_sat_liq:
                            h_out_boiler = PropsBoiler.h_sat_liq
                        Tank_outputs = Tank.compute_outputs(0, h_mains, demanded_flow, h_in_system,
                                                            None, None, boiler_mass_flow, h_out_boiler,
                                                            T_amb, time_step)
                        it = it + 1
                        if abs(Tank_outputs['HX2_outlet_h'] - previous_enthalpies['h_in_boiler'])/previous_enthalpies['h_in_boiler'] < tolerance:
                            maxIt = False
                            break
                        if it == max_iterations:
                            maxIt = True
                            break
                        previous_enthalpies['h_in_boiler'] = Tank_outputs['HX2_outlet_h']
                
                if boiler_state == 'OFF':

                    Tank_outputs = Tank.compute_outputs(0, h_mains, demanded_flow, h_in_system,
                                                        None, None, None, None,
                                                        T_amb, time_step)
                
        else:
            
            Tank_outputs = Tank.compute_outputs(0, h_mains, 0, h_in_system,
                                                None, None, None, None,
                                                T_amb, time_step)
        
        Tank.update_temperature()
        
        t = np.round(t + time_step, 2)

    Result = {'t(hr)': [],
              'system_operation': [],
              'solar_field_operation': [],
              'total_irradiance_on_collector_plane(W/m2)': [],
              'useful_solar_power(W)': [],
              'wasted_solar_power(W)': [],
              'aux_heater_power(W)': [],
              'demanded_flow_temperature(C)': [],
              'power_extracted_from_tank(W)': [],
              'conventional_energy_cost': [],
              'system_maximum_iterations_reached': [],
              'tank_maximum_iterations_reached': [] }
    t = 0
    while t < 8760:
        
        day_now = int(t/24) + 1
        month_now = month_from_day(day_now)
        week_day_now = week_day_from_day(day_now)
        day_time_now = corrected_time(t)%24
        
        day_next_hour = int(t/24) + 1
        month_next_hour = month_from_day(day_next_hour)
        week_day_next_hour = week_day_from_day(day_next_hour)
        day_time_next_hour = corrected_time(t + 1)%24
        
        sky_diffuse = float(sky_diff_func(t))
        ground_diffuse = float(ground_diff_func(t))
        DNIrr = float(DNI_func(t))
        T_amb = float(T_amb_func(t))
        T_in_system = monthly_inlet_temperatures[month_now]
        h_in_system = PropsHeatedFluid.T_to_h(T_in_system)
        T_mains = monthly_mains_temperatures[month_now]
        h_mains = PropsHeatedFluid.T_to_h(T_mains)
        h_mains_field = PropsField.T_to_h(T_mains)
        
        aoi, longi, trans = Field.incidence_angles(float(compute_zenith(t)), float(compute_azimuth(t)))
        if aoi == None:
            rad = sky_diffuse + ground_diffuse
        else:
            beam_rad = DNIrr*cos(aoi)
            rad = beam_rad + sky_diffuse + ground_diffuse
            
        operation_now = ( (t_start == t_end and monthly_flows[month_now] > 0 and week_day_now in work_day_list) or 
                          (t_start < t_end and day_time_now >= t_start and day_time_now <= t_end and monthly_flows[month_now] > 0 and week_day_now in work_day_list) or
                          (t_start > t_end and (day_time_now >= t_start or day_time_now <= t_end) and monthly_flows[month_now] > 0 and week_day_now in work_day_list) )
        
        operation_next_hour = ( (t_start == t_end and monthly_flows[month_next_hour] > 0 and week_day_next_hour in work_day_list) or 
                                (t_start < t_end and day_time_next_hour >= t_start and day_time_next_hour <= t_end and monthly_flows[month_next_hour] > 0 and week_day_next_hour in work_day_list) or
                                (t_start > t_end and (day_time_next_hour >= t_start or day_time_next_hour <= t_end) and monthly_flows[month_next_hour] > 0 and week_day_next_hour in work_day_list) )
        
        if operation_now:
            system_operation = True
            demanded_flow = monthly_flows[month_now]
        elif operation_next_hour:
            system_operation = True
            demanded_flow = 0
        else:
            system_operation = False
            solar_field_operation = False
        
        if Tank.node_temperatures[1] >= T_set + 2:
            boiler_state = 'OFF'
        if Tank.node_temperatures[1] <= T_set:
            boiler_state = 'ON'
        
        if system_operation:
            if rad > 0:
                solar_field_operation = True
                if aoi == None:
                    IAM_eff = (sky_diffuse*Field.sky_diffuse_iam + ground_diffuse*Field.ground_diffuse_iam)/rad
                else:
                    beam_iam = Field.IAM_func(aoi, longi, trans)
                    IAM_eff = (beam_rad*beam_iam + sky_diffuse*Field.sky_diffuse_iam + ground_diffuse*Field.ground_diffuse_iam)/rad
            else:
                solar_field_operation = False
            
            if solar_field_operation:
                
                if boiler_state == 'ON':
                    it = 0
                    while True:
                        Field_outputs = Field.compute_outputs(mass_flow_field, previous_enthalpies['h_in_solar_field'], h_mains_field, rad, IAM_eff, T_amb)
                        HX_outputs = HX.compute_outputs(mass_flow_field, Field_outputs['h_out'], heat_exchanger_load_flow, previous_enthalpies['h_in_HX_load'], h_mains)
                        h_out_boiler = previous_enthalpies['h_in_boiler'] + boiler_nominal_power/boiler_mass_flow
                        if h_out_boiler > PropsBoiler.h_sat_liq:
                            h_out_boiler = PropsBoiler.h_sat_liq
                        Tank_outputs = Tank.compute_outputs(heat_exchanger_load_flow, HX_outputs['h_out_load'], demanded_flow, h_in_system,
                                                            None, None, boiler_mass_flow, h_out_boiler,
                                                            T_amb, time_step)
                        it = it + 1
                        if (abs(HX_outputs['h_out_source'] - previous_enthalpies['h_in_solar_field'])/previous_enthalpies['h_in_solar_field'] < tolerance and
                            abs(Tank_outputs['outlet_1_h'] - previous_enthalpies['h_in_HX_load'])/previous_enthalpies['h_in_HX_load'] < tolerance and
                            abs(Tank_outputs['HX2_outlet_h'] - previous_enthalpies['h_in_boiler'])/previous_enthalpies['h_in_boiler'] < tolerance ):
                            maxIt = False
                            break
                        if it == max_iterations:
                            maxIt = True
                            break
                        previous_enthalpies = {'h_in_solar_field': HX_outputs['h_out_source'], 'h_in_HX_load': Tank_outputs['outlet_1_h'], 'h_in_boiler': Tank_outputs['HX2_outlet_h']}
                    
                    useful_solar_power = HX_outputs['Q_useful']
                    wasted_solar_power = Field_outputs['Q_waste'] + HX_outputs['Q_waste']
                    boiler_power = Tank_outputs['HX2_Q']
                    
                if boiler_state == 'OFF':
                    
                    it = 0
                    while True:
                        Field_outputs = Field.compute_outputs(mass_flow_field, previous_enthalpies['h_in_solar_field'], h_mains_field, rad, IAM_eff, T_amb)
                        HX_outputs = HX.compute_outputs(mass_flow_field, Field_outputs['h_out'], heat_exchanger_load_flow, previous_enthalpies['h_in_HX_load'], h_mains)
                        Tank_outputs = Tank.compute_outputs(heat_exchanger_load_flow, HX_outputs['h_out_load'], demanded_flow, h_in_system,
                                                            None, None, None, None,
                                                            T_amb, time_step)
                        it = it + 1
                        if (abs(HX_outputs['h_out_source'] - previous_enthalpies['h_in_solar_field'])/previous_enthalpies['h_in_solar_field'] < tolerance and
                            abs(Tank_outputs['outlet_1_h'] - previous_enthalpies['h_in_HX_load'])/previous_enthalpies['h_in_HX_load'] < tolerance):
                            maxIt = False
                            break
                        if it == max_iterations:
                            maxIt = True
                            break
                        previous_enthalpies['h_in_solar_field'] =  HX_outputs['h_out_source']
                        previous_enthalpies['h_in_HX_load'] = Tank_outputs['outlet_1_h']
                    
                    useful_solar_power = HX_outputs['Q_useful']
                    wasted_solar_power = Field_outputs['Q_waste'] + HX_outputs['Q_waste']
                    boiler_power = 0
                
            else:

                if boiler_state == 'ON':
                    it = 0
                    while True:
                        h_out_boiler = previous_enthalpies['h_in_boiler'] + boiler_nominal_power/boiler_mass_flow
                        if h_out_boiler > PropsBoiler.h_sat_liq:
                            h_out_boiler = PropsBoiler.h_sat_liq
                        Tank_outputs = Tank.compute_outputs(0, h_mains, demanded_flow, h_in_system,
                                                            None, None, boiler_mass_flow, h_out_boiler,
                                                            T_amb, time_step)
                        it = it + 1
                        if abs(Tank_outputs['HX2_outlet_h'] - previous_enthalpies['h_in_boiler'])/previous_enthalpies['h_in_boiler'] < tolerance:
                            maxIt = False
                            break
                        if it == max_iterations:
                            maxIt = True
                            break
                        previous_enthalpies['h_in_boiler'] = Tank_outputs['HX2_outlet_h']
                        
                    useful_solar_power = 0
                    wasted_solar_power = 0
                    boiler_power = Tank_outputs['HX2_Q']
                
                if boiler_state == 'OFF':

                    Tank_outputs = Tank.compute_outputs(0, h_mains, demanded_flow, h_in_system,
                                                        None, None, None, None,
                                                        T_amb, time_step)
                    
                    useful_solar_power = 0
                    wasted_solar_power = 0
                    boiler_power = 0
                    maxIt = False
                    
        else:
                        
            Tank_outputs = Tank.compute_outputs(0, h_mains, 0, h_in_system,
                                                None, None, None, None,
                                                T_amb, time_step)
            useful_solar_power = 0
            wasted_solar_power = 0
            boiler_power = 0
            maxIt = False
            
        conventional_energy_cost = boiler_power*time_step*cost_per_conventional_kJ/boiler_efficiency
        T_out_system = PropsHeatedFluid.h_to_T(Tank_outputs['outlet_2_h'])
        TES_power = Tank_outputs['Q_demand']
        
        Result['t(hr)'].append(t)
        Result['system_operation'].append(system_operation)
        Result['solar_field_operation'].append(solar_field_operation)
        Result['total_irradiance_on_collector_plane(W/m2)'].append(rad/3.6)
        Result['useful_solar_power(W)'].append(useful_solar_power/3.6)
        Result['wasted_solar_power(W)'].append(wasted_solar_power/3.6)
        Result['aux_heater_power(W)'].append(boiler_power/3.6)
        Result['demanded_flow_temperature(C)'].append(T_out_system)
        Result['power_extracted_from_tank(W)'].append(TES_power/3.6)
        Result['conventional_energy_cost'].append(conventional_energy_cost)
        Result['system_maximum_iterations_reached'].append(maxIt)
        Result['tank_maximum_iterations_reached'].append(Tank_outputs['maxIt'])
        
        Tank.update_temperature()
        
        t = np.round(t + time_step, 2)
    
    return Result

    
def NS_L_CA_MU(Field, Tank, HX, T_set, boiler_nominal_power,
               boiler_efficiency, cost_per_conventional_kJ,
               work_day_list, monthly_flows, monthly_inlet_temperatures,
               monthly_mains_temperatures, t_start, t_end,
               PropsHeatedFluid, PropsField, mass_flow_field,
               sky_diff_func, ground_diff_func, DNI_func, T_amb_func,
               compute_zenith, compute_azimuth, corrected_time,
               time_step, tolerance, max_iterations):
    
    if T_set >= PropsHeatedFluid.T_sat:
        h_set = PropsHeatedFluid.h_sat_liq
    else:
        h_set = PropsHeatedFluid.T_to_h(T_set)
        
    flow_returned_to_tank = max([ monthly_flows[i] for i in monthly_flows ])
    
    h_in_solar_field = PropsField.T_to_h(40)
    t = 8760 - 24*10
    while t < 8760:
        
        day = int(t/24) + 1
        month = month_from_day(day)
        week_day = week_day_from_day(day)
        day_time = corrected_time(t)%24
        
        sky_diffuse = float(sky_diff_func(t))
        ground_diffuse = float(ground_diff_func(t))
        DNIrr = float(DNI_func(t))
        T_amb = float(T_amb_func(t))
        T_in_system = monthly_inlet_temperatures[month]
        h_in_system = PropsHeatedFluid.T_to_h(T_in_system)
        T_mains = monthly_mains_temperatures[month]
        h_mains = PropsHeatedFluid.T_to_h(T_mains)
        h_mains_field = PropsField.T_to_h(T_mains)
        demanded_flow = monthly_flows[month]
        
        aoi, longi, trans = Field.incidence_angles(float(compute_zenith(t)), float(compute_azimuth(t)))
        if aoi == None:
            rad = sky_diffuse + ground_diffuse
        else:
            beam_rad = DNIrr*cos(aoi)
            rad = beam_rad + sky_diffuse + ground_diffuse
        
        if t_start == t_end and demanded_flow > 0 and week_day in work_day_list:
            system_operation = True
        elif t_start < t_end and day_time >= t_start and day_time <= t_end and demanded_flow > 0 and week_day in work_day_list:
            system_operation = True
        elif t_start > t_end and (day_time >= t_start or day_time <= t_end) and demanded_flow > 0 and week_day in work_day_list:
            system_operation = True
        else:
            system_operation = False
            solar_field_operation = False
        
        if system_operation:
            if rad > 0:
                solar_field_operation = True
                if aoi == None:
                    IAM_eff = (sky_diffuse*Field.sky_diffuse_iam + ground_diffuse*Field.ground_diffuse_iam)/rad
                else:
                    beam_iam = Field.IAM_func(aoi, longi, trans)
                    IAM_eff = (beam_rad*beam_iam + sky_diffuse*Field.sky_diffuse_iam + ground_diffuse*Field.ground_diffuse_iam)/rad
            else:
                solar_field_operation = False
            
            if solar_field_operation:
                it_solar = 0
                while True:
                    Field_outputs = Field.compute_outputs(mass_flow_field, h_in_solar_field, h_mains_field, rad, IAM_eff, T_amb)
                    HX_outputs = HX.compute_outputs(mass_flow_field, Field_outputs['h_out'], demanded_flow, h_in_system, h_mains)
                    it_solar = it_solar + 1
                    if abs(HX_outputs['h_out_source'] - h_in_solar_field)/h_in_solar_field < tolerance:
                        maxIt_solar = False
                        break
                    if it_solar == max_iterations:
                        maxIt_solar = True
                        break
                    h_in_solar_field = HX_outputs['h_out_source']
                    
                useful_solar_power = HX_outputs['Q_useful']
                wasted_solar_power = HX_outputs['Q_waste'] + Field_outputs['Q_waste']
                
                Tank_outputs = Tank.compute_outputs(demanded_flow, HX_outputs['h_out_load'], flow_returned_to_tank, h_set,
                                                    None, None, None, None,
                                                    T_amb, time_step)
                
                h_in_boiler = (demanded_flow*Tank_outputs['outlet_1_h'] + flow_returned_to_tank*Tank_outputs['outlet_2_h'])/(demanded_flow + flow_returned_to_tank)
                if h_in_boiler >= h_set:
                    maxIt_boiler = False
                    boiler_power = 0
                    h_out_system = h_in_boiler
                else:
                    boiler_power = (demanded_flow + flow_returned_to_tank)*(h_set - h_in_boiler)
                
                    if boiler_power > boiler_nominal_power:
                        h_out_boiler_previous = h_in_boiler + boiler_nominal_power/(demanded_flow + flow_returned_to_tank)
                        it_boiler = 0
                        while True:
                            Tank_outputs = Tank.compute_outputs(demanded_flow, HX_outputs['h_out_load'], flow_returned_to_tank, h_out_boiler_previous,
                                                                None, None, None, None,
                                                                T_amb, time_step)
                            h_in_boiler = (demanded_flow*Tank_outputs['outlet_1_h'] + flow_returned_to_tank*Tank_outputs['outlet_2_h'])/(demanded_flow + flow_returned_to_tank)
                            h_out_boiler = h_in_boiler + boiler_nominal_power/(demanded_flow + flow_returned_to_tank)
                            it_boiler = it_boiler + 1
                            if abs(h_out_boiler - h_out_boiler_previous)/h_out_boiler_previous < tolerance:
                                maxIt_boiler = False
                                break
                            if it_boiler == max_iterations:
                                maxIt_boiler = True
                                break
                            h_out_boiler_previous = h_out_boiler
                        
                        h_out_system = h_out_boiler
                        boiler_power = boiler_nominal_power
                
                    else:
                        maxIt_boiler = False
                        h_out_system = h_set
                
            else:
                
                maxIt_solar = False
                useful_solar_power = 0
                wasted_solar_power = 0
                
                Tank_outputs = Tank.compute_outputs(demanded_flow, h_in_system, flow_returned_to_tank, h_set,
                                                    None, None, None, None,
                                                    T_amb, time_step)
                
                h_in_boiler = (demanded_flow*Tank_outputs['outlet_1_h'] + flow_returned_to_tank*Tank_outputs['outlet_2_h'])/(demanded_flow + flow_returned_to_tank)
                if h_in_boiler >= h_set:
                    maxIt_boiler = False
                    boiler_power = 0
                    h_out_system = h_in_boiler
                else:
                    boiler_power = (demanded_flow + flow_returned_to_tank)*(h_set - h_in_boiler)
                
                    if boiler_power > boiler_nominal_power:
                        h_out_boiler_previous = h_in_boiler + boiler_nominal_power/(demanded_flow + flow_returned_to_tank)
                        it_boiler = 0
                        while True:
                            Tank_outputs = Tank.compute_outputs(demanded_flow, h_in_system, flow_returned_to_tank, h_out_boiler_previous,
                                                                None, None, None, None,
                                                                T_amb, time_step)
                            h_in_boiler = (demanded_flow*Tank_outputs['outlet_1_h'] + flow_returned_to_tank*Tank_outputs['outlet_2_h'])/(demanded_flow + flow_returned_to_tank)
                            h_out_boiler = h_in_boiler + boiler_nominal_power/(demanded_flow + flow_returned_to_tank)
                            it_boiler = it_boiler + 1
                            if abs(h_out_boiler - h_out_boiler_previous)/h_out_boiler_previous < tolerance:
                                maxIt_boiler = False
                                break
                            if it_boiler == max_iterations:
                                maxIt_boiler = True
                                break
                            h_out_boiler_previous = h_out_boiler
                        
                        h_out_system = h_out_boiler
                        boiler_power = boiler_nominal_power
                    
                    else:
                        maxIt_boiler = False
                        h_out_system = h_set
                        
        else:
            maxIt_boiler = False
            maxIt_solar = False
            useful_solar_power = 0
            wasted_solar_power = 0
            boiler_power = 0
            T_out_system = np.nan

            Tank_outputs = Tank.compute_outputs(0, h_mains, 0, h_mains,
                                                None, None, None, None,
                                                T_amb, time_step)
            
        Tank.update_temperature()
        
        t = np.round(t + time_step, 2)
    
    Result = {'t(hr)': [],
              'system_operation': [],
              'solar_field_operation': [],
              'total_irradiance_on_collector_plane(W/m2)': [],
              'useful_solar_power(W)': [],
              'wasted_solar_power(W)': [],
              'tank_outlet_temperature': [],
              'power_extracted_from_tank(W)': [],
              'aux_heater_power(W)': [],
              'demanded_flow_temperature(C)': [],
              'conventional_energy_cost': [],
              'aux_heater_nominal_power_surpassed': [],
              'setPoint_Temp_surpassed': [],
              'solar_loop_maximum_iterations_reached': [],
              'boiler_outlet_temperature_maximum_iterations_reached': [],
              'tank_maximum_iterations_reached': [] }
    t = 0
    while t < 8760:
        
        day = int(t/24) + 1
        month = month_from_day(day)
        week_day = week_day_from_day(day)
        day_time = corrected_time(t)%24
        
        sky_diffuse = float(sky_diff_func(t))
        ground_diffuse = float(ground_diff_func(t))
        DNIrr = float(DNI_func(t))
        T_amb = float(T_amb_func(t))
        T_in_system = monthly_inlet_temperatures[month]
        h_in_system = PropsHeatedFluid.T_to_h(T_in_system)
        T_mains = monthly_mains_temperatures[month]
        h_mains = PropsHeatedFluid.T_to_h(T_mains)
        h_mains_field = PropsField.T_to_h(T_mains)
        demanded_flow = monthly_flows[month]
        
        aoi, longi, trans = Field.incidence_angles(float(compute_zenith(t)), float(compute_azimuth(t)))
        if aoi == None:
            rad = sky_diffuse + ground_diffuse
        else:
            beam_rad = DNIrr*cos(aoi)
            rad = beam_rad + sky_diffuse + ground_diffuse
        
        if t_start == t_end and demanded_flow > 0 and week_day in work_day_list:
            system_operation = True
        elif t_start < t_end and day_time >= t_start and day_time <= t_end and demanded_flow > 0 and week_day in work_day_list:
            system_operation = True
        elif t_start > t_end and (day_time >= t_start or day_time <= t_end) and demanded_flow > 0 and week_day in work_day_list:
            system_operation = True
        else:
            system_operation = False
            solar_field_operation = False
        
        if system_operation:
            if rad > 0:
                solar_field_operation = True
                if aoi == None:
                    IAM_eff = (sky_diffuse*Field.sky_diffuse_iam + ground_diffuse*Field.ground_diffuse_iam)/rad
                else:
                    beam_iam = Field.IAM_func(aoi, longi, trans)
                    IAM_eff = (beam_rad*beam_iam + sky_diffuse*Field.sky_diffuse_iam + ground_diffuse*Field.ground_diffuse_iam)/rad
            else:
                solar_field_operation = False
            
            if solar_field_operation:
                it_solar = 0
                while True:
                    Field_outputs = Field.compute_outputs(mass_flow_field, h_in_solar_field, h_mains_field, rad, IAM_eff, T_amb)
                    HX_outputs = HX.compute_outputs(mass_flow_field, Field_outputs['h_out'], demanded_flow, h_in_system, h_mains)
                    it_solar = it_solar + 1
                    if abs(HX_outputs['h_out_source'] - h_in_solar_field)/h_in_solar_field < tolerance:
                        maxIt_solar = False
                        break
                    if it_solar == max_iterations:
                        maxIt_solar = True
                        break
                    h_in_solar_field = HX_outputs['h_out_source']
                    
                useful_solar_power = HX_outputs['Q_useful']
                wasted_solar_power = HX_outputs['Q_waste'] + Field_outputs['Q_waste']
                
                Tank_outputs = Tank.compute_outputs(demanded_flow, HX_outputs['h_out_load'], flow_returned_to_tank, h_set,
                                                    None, None, None, None,
                                                    T_amb, time_step)
                
                h_in_boiler = (demanded_flow*Tank_outputs['outlet_1_h'] + flow_returned_to_tank*Tank_outputs['outlet_2_h'])/(demanded_flow + flow_returned_to_tank)
                if h_in_boiler >= h_set:
                    maxIt_boiler = False
                    boiler_power = 0
                    boiler_nominal_power_surpassed = False
                    h_out_system = h_in_boiler
                    if h_in_boiler > h_set:
                        T_set_surpassed = True
                    else:
                        T_set_surpassed = False
                else:
                    T_set_surpassed = False
                    boiler_power = (demanded_flow + flow_returned_to_tank)*(h_set - h_in_boiler)
                
                    if boiler_power > boiler_nominal_power:
                        boiler_nominal_power_surpassed = True
                        h_out_boiler_previous = h_in_boiler + boiler_nominal_power/(demanded_flow + flow_returned_to_tank)
                        it_boiler = 0
                        while True:
                            Tank_outputs = Tank.compute_outputs(demanded_flow, HX_outputs['h_out_load'], flow_returned_to_tank, h_out_boiler_previous,
                                                                None, None, None, None,
                                                                T_amb, time_step)
                            h_in_boiler = (demanded_flow*Tank_outputs['outlet_1_h'] + flow_returned_to_tank*Tank_outputs['outlet_2_h'])/(demanded_flow + flow_returned_to_tank)
                            h_out_boiler = h_in_boiler + boiler_nominal_power/(demanded_flow + flow_returned_to_tank)
                            it_boiler = it_boiler + 1
                            if abs(h_out_boiler - h_out_boiler_previous)/h_out_boiler_previous < tolerance:
                                maxIt_boiler = False
                                break
                            if it_boiler == max_iterations:
                                maxIt_boiler = True
                                break
                            h_out_boiler_previous = h_out_boiler
                        
                        h_out_system = h_out_boiler
                        boiler_power = boiler_nominal_power
                
                    else:
                        boiler_nominal_power_surpassed = False
                        maxIt_boiler = False
                        h_out_system = h_set
                
            else:
                
                maxIt_solar = False
                useful_solar_power = 0
                wasted_solar_power = 0
                
                Tank_outputs = Tank.compute_outputs(demanded_flow, h_in_system, flow_returned_to_tank, h_set,
                                                    None, None, None, None,
                                                    T_amb, time_step)
                
                h_in_boiler = (demanded_flow*Tank_outputs['outlet_1_h'] + flow_returned_to_tank*Tank_outputs['outlet_2_h'])/(demanded_flow + flow_returned_to_tank)
                if h_in_boiler >= h_set:
                    maxIt_boiler = False
                    boiler_power = 0
                    boiler_nominal_power_surpassed = False
                    h_out_system = h_in_boiler
                    if h_in_boiler > h_set:
                        T_set_surpassed = True
                    else:
                        T_set_surpassed = False
                else:
                    T_set_surpassed = False
                    boiler_power = (demanded_flow + flow_returned_to_tank)*(h_set - h_in_boiler)
                
                    if boiler_power > boiler_nominal_power:
                        boiler_nominal_power_surpassed = True
                        h_out_boiler_previous = h_in_boiler + boiler_nominal_power/(demanded_flow + flow_returned_to_tank)
                        it_boiler = 0
                        while True:
                            Tank_outputs = Tank.compute_outputs(demanded_flow, h_in_system, flow_returned_to_tank, h_out_boiler_previous,
                                                                None, None, None, None,
                                                                T_amb, time_step)
                            h_in_boiler = (demanded_flow*Tank_outputs['outlet_1_h'] + flow_returned_to_tank*Tank_outputs['outlet_2_h'])/(demanded_flow + flow_returned_to_tank)
                            h_out_boiler = h_in_boiler + boiler_nominal_power/(demanded_flow + flow_returned_to_tank)
                            it_boiler = it_boiler + 1
                            if abs(h_out_boiler - h_out_boiler_previous)/h_out_boiler_previous < tolerance:
                                maxIt_boiler = False
                                break
                            if it_boiler == max_iterations:
                                maxIt_boiler = True
                                break
                            h_out_boiler_previous = h_out_boiler
                        
                        h_out_system = h_out_boiler
                        boiler_power = boiler_nominal_power
                    
                    else:
                        boiler_nominal_power_surpassed = False
                        maxIt_boiler = False
                        h_out_system = h_set
            
            T_out_system = PropsHeatedFluid.h_to_T(h_out_system)
                        
        else:
            
            boiler_nominal_power_surpassed = False
            T_set_surpassed = False
            maxIt_boiler = False
            maxIt_solar = False
            useful_solar_power = 0
            wasted_solar_power = 0
            boiler_power = 0
            T_out_system = np.nan
            
            Tank_outputs = Tank.compute_outputs(0, h_mains, 0, h_mains,
                                                None, None, None, None,
                                                T_amb, time_step)
            
            h_in_boiler = Tank_outputs['outlet_1_h']
            
        T_out_Tank = PropsHeatedFluid.h_to_T(h_in_boiler)
        conventional_energy_cost = boiler_power*time_step*cost_per_conventional_kJ/boiler_efficiency
        TES_power = Tank_outputs['Q_demand']
        
        Result['t(hr)'].append(t)
        Result['system_operation'].append(system_operation)
        Result['solar_field_operation'].append(solar_field_operation)
        Result['total_irradiance_on_collector_plane(W/m2)'].append(rad/3.6)
        Result['useful_solar_power(W)'].append(useful_solar_power/3.6)
        Result['wasted_solar_power(W)'].append(wasted_solar_power/3.6)
        Result['tank_outlet_temperature'].append(T_out_Tank)
        Result['power_extracted_from_tank(W)'].append(TES_power/3.6)
        Result['aux_heater_power(W)'].append(boiler_power/3.6)
        Result['demanded_flow_temperature(C)'].append(T_out_system)
        Result['conventional_energy_cost'].append(conventional_energy_cost)
        Result['aux_heater_nominal_power_surpassed'].append(boiler_nominal_power_surpassed)
        Result['setPoint_Temp_surpassed'].append(T_set_surpassed)
        Result['solar_loop_maximum_iterations_reached'].append(maxIt_solar)
        Result['boiler_outlet_temperature_maximum_iterations_reached'].append(maxIt_boiler)
        Result['tank_maximum_iterations_reached'].append(Tank_outputs['maxIt'])
        
        Tank.update_temperature()
        
        t = np.round(t + time_step, 2)
    
    return Result

def simulate_system(system_params,simulacion_id, time_step = 0.1, tolerance = 1e-6, max_iterations = 100):
    
    # TMY_file_name = system_params['TMY_file_name']
    # if not TMY_file_name[len(TMY_file_name)-4:] == '.csv':
    #     TMY_file_name = TMY_file_name + '.csv'
    # latitude, longitude, weather_data = corr_exp_solar(TMY_file_name)
    # year_list, DNI, GHI, DHI, temp = extract_weather_data(weather_data)
    # Obtén la instancia de simulación

    simulacion = Simulaciones.objects.get(id_simulacion=simulacion_id)

    # Asegúrate de que el archivo TMY asociado existe
    if simulacion.archivo_tmy:
        # Usa el nombre de archivo en la simulación
        TMY_file_name = simulacion.archivo_tmy.archivo.name

        # Continúa con el resto de tu código
        if not TMY_file_name[len(TMY_file_name)-4:] == '.csv':
            TMY_file_name = TMY_file_name + '.csv'
        latitude, longitude, weather_data = corr_exp_solar(TMY_file_name)
        year_list, DNI, GHI, DHI, temp = extract_weather_data(weather_data)
    else:
        # Trata el caso en que el archivo TMY asociado no exista
        print("No existe un archivo TMY asociado con la simulación.")
    
    albedo = 0.25
    sky_diff = 0.5*( 1 + cos(system_params['coll_tilt']*pi/180) )*np.array(DHI)
    ground_diff = 0.5*albedo*( 1 - cos(system_params['coll_tilt']*pi/180) )*np.array(GHI)
    
    time_january = pd.date_range(str(year_list[0]) + '-01-01', str(year_list[0]) + '-02-01', inclusive='left', freq='min', tz = 'Etc/GMT+3')
    time_february = pd.date_range(str(year_list[1]) + '-02-01', str(year_list[1]) + '-03-01', inclusive='left', freq='min', tz = 'Etc/GMT+3')
    time_march = pd.date_range(str(year_list[2]) + '-03-01', str(year_list[2]) + '-04-01', inclusive='left', freq='min', tz = 'Etc/GMT+3')
    time_april = pd.date_range(str(year_list[3]) + '-04-01', str(year_list[3]) + '-05-01', inclusive='left', freq='min', tz = 'Etc/GMT+3')
    time_may = pd.date_range(str(year_list[4]) + '-05-01', str(year_list[4]) + '-06-01', inclusive='left', freq='min', tz = 'Etc/GMT+3')
    time_june = pd.date_range(str(year_list[5]) + '-06-01', str(year_list[5]) + '-07-01', inclusive='left', freq='min', tz = 'Etc/GMT+3')
    time_july = pd.date_range(str(year_list[6]) + '-07-01', str(year_list[6]) + '-08-01', inclusive='left', freq='min', tz = 'Etc/GMT+3')
    time_august = pd.date_range(str(year_list[7]) + '-08-01', str(year_list[7]) + '-09-01', inclusive='left', freq='min', tz = 'Etc/GMT+3')
    time_september = pd.date_range(str(year_list[8]) + '-09-01', str(year_list[8]) + '-10-01', inclusive='left', freq='min', tz = 'Etc/GMT+3')
    time_october = pd.date_range(str(year_list[9]) + '-10-01', str(year_list[9]) + '-11-01', inclusive='left', freq='min', tz = 'Etc/GMT+3')
    time_november = pd.date_range(str(year_list[10]) + '-11-01', str(year_list[10]) + '-12-01', inclusive='left', freq='min', tz = 'Etc/GMT+3')
    time_december = pd.date_range(str(year_list[11]) + '-12-01', str(year_list[11] + 1) + '-01-01', inclusive='left', freq='min', tz = 'Etc/GMT+3')

    if len(time_february) == 41760:
        time_february = pd.date_range(str(year_list[1]) + '-02-01', str(year_list[1]) + '-02-29', inclusive='left', freq='min', tz = 'Etc/GMT+3')
    
    solpos_january = get_solarposition(time_january, latitude, longitude)
    azimuth_january = solpos_january['azimuth']
    zenith_january = solpos_january['zenith']
    
    solpos_february = get_solarposition(time_february, latitude, longitude)
    azimuth_february = solpos_february['azimuth']
    zenith_february = solpos_february['zenith']
    
    solpos_march = get_solarposition(time_march, latitude, longitude)
    azimuth_march = solpos_march['azimuth']
    zenith_march = solpos_march['zenith']
    
    solpos_april = get_solarposition(time_april, latitude, longitude)
    azimuth_april = solpos_april['azimuth']
    zenith_april = solpos_april['zenith']
    
    solpos_may = get_solarposition(time_may, latitude, longitude)
    azimuth_may = solpos_may['azimuth']
    zenith_may = solpos_may['zenith']
    
    solpos_june = get_solarposition(time_june, latitude, longitude)
    azimuth_june = solpos_june['azimuth']
    zenith_june = solpos_june['zenith']
    
    solpos_july = get_solarposition(time_july, latitude, longitude)
    azimuth_july = solpos_july['azimuth']
    zenith_july = solpos_july['zenith']
    
    solpos_august = get_solarposition(time_august, latitude, longitude)
    azimuth_august = solpos_august['azimuth']
    zenith_august = solpos_august['zenith']
    
    solpos_september = get_solarposition(time_september, latitude, longitude)
    azimuth_september = solpos_september['azimuth']
    zenith_september = solpos_september['zenith']
    
    solpos_october = get_solarposition(time_october, latitude, longitude)
    azimuth_october = solpos_october['azimuth']
    zenith_october = solpos_october['zenith']
    
    solpos_november = get_solarposition(time_november, latitude, longitude)
    azimuth_november = solpos_november['azimuth']
    zenith_november = solpos_november['zenith']
    
    solpos_december = get_solarposition(time_december, latitude, longitude)
    azimuth_december = solpos_december['azimuth']
    zenith_december = solpos_december['zenith']
    
    solar_azimuth_list = (azimuth_january.tolist() +
                          azimuth_february.tolist() +
                          azimuth_march.tolist() +
                          azimuth_april.tolist() +
                          azimuth_may.tolist() +
                          azimuth_june.tolist() +
                          azimuth_july.tolist() +
                          azimuth_august.tolist() +
                          azimuth_september.tolist() +
                          azimuth_october.tolist() +
                          azimuth_november.tolist() +
                          azimuth_december.tolist() )
    
    solar_zenith_list = (zenith_january.tolist() +
                         zenith_february.tolist() +
                         zenith_march.tolist() +
                         zenith_april.tolist() +
                         zenith_may.tolist() +
                         zenith_june.tolist() +
                         zenith_july.tolist() +
                         zenith_august.tolist() +
                         zenith_september.tolist() +
                         zenith_october.tolist() +
                         zenith_november.tolist() +
                         zenith_december.tolist() )
    
    compute_azimuth = azimuth_function(solar_azimuth_list)
    compute_zenith = zenith_function(solar_zenith_list)
    
    time = range(8761)

    sky_diff_func = interp1d(time, sky_diff)
    ground_diff_func = interp1d(time, ground_diff)
    DNI_func = interp1d(time, DNI)
    T_amb_func = interp1d(time, temp)
    
    
    temp_january = np.mean(temp[:744])
    temp_february = np.mean(temp[744:1416])
    temp_march = np.mean(temp[1416:2160])
    temp_april = np.mean(temp[2160:2880])
    temp_may = np.mean(temp[2880:3624])
    temp_june = np.mean(temp[3624:4344])
    temp_july = np.mean(temp[4344:5088])
    temp_august = np.mean(temp[5088:5832])
    temp_september = np.mean(temp[5832:6552])
    temp_october = np.mean(temp[6552:7296])
    temp_november = np.mean(temp[7296:8016])
    temp_december = np.mean(temp[8016:8760])
    T_month_list = [temp_january,
                    temp_february,
                    temp_march,
                    temp_april,
                    temp_may,
                    temp_june,
                    temp_july,
                    temp_august,
                    temp_september,
                    temp_october,
                    temp_november,
                    temp_december ]
    T_amb_ann = np.mean(temp)
    delta_T_amb = ( max(T_month_list) - min(T_month_list) )/2
    delta_T_offset = 3.3333333
    T_ref = 6.6666667
    K1 = 0.4
    K2 = 0.018
    K3 = 35*pi/180
    K4 = -3.1416e-4
    delta_T_mains = (K1 + K2*(T_amb_ann - T_ref))*delta_T_amb
    phi_lag = K3 + K4*(T_amb_ann - T_ref)
    phi_amb = (104.8 + 180)*pi/180
    T_mains_avg = T_amb_ann + delta_T_offset
    def T_mains_func(t):
        '''
        Función que recibe el instante del año (en horas) y retorna la temperatura estimada para el agua de la red.

        Parámetros:
            - t: Instante del año (en horas)

        Retorna:
            - Temperatura estimada para el agua de la red (en °C)
        '''
        return T_mains_avg + delta_T_mains*sin(2*pi*t/8760 - phi_lag - phi_amb)
    
    monthly_mains_temperatures = {'January': np.mean( [ T_mains_func(t) for t in range(744) ] ),
                                  'February': np.mean( [ T_mains_func(t) for t in range(744, 1416) ] ),
                                  'March': np.mean( [ T_mains_func(t) for t in range(1416, 2160) ] ),
                                  'April': np.mean( [ T_mains_func(t) for t in range(2160, 2880) ] ),
                                  'May': np.mean( [ T_mains_func(t) for t in range(2880, 3624) ] ),
                                  'June': np.mean( [ T_mains_func(t) for t in range(3624, 4344) ] ),
                                  'July': np.mean( [ T_mains_func(t) for t in range(4344, 5088) ] ),
                                  'August': np.mean( [ T_mains_func(t) for t in range(5088, 5832) ] ),
                                  'September': np.mean( [ T_mains_func(t) for t in range(5832, 6552) ] ),
                                  'October': np.mean( [ T_mains_func(t) for t in range(6552, 7296) ] ),
                                  'November': np.mean( [ T_mains_func(t) for t in range(7296, 8016) ] ),
                                  'December': np.mean( [ T_mains_func(t) for t in range(8016, 8760) ] ) }
    
    if system_params['closed_system']:
        if system_params['monthly_return_temperature']:
            monthly_inlet_temperatures = {'January': system_params['temperature_january'],
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
                                          'December': system_params['temperature_december'] }
        else:
            monthly_inlet_temperatures = {'January': system_params['return_inlet_temperature'],
                                          'February': system_params['return_inlet_temperature'],
                                          'March': system_params['return_inlet_temperature'],
                                          'April': system_params['return_inlet_temperature'],
                                          'May': system_params['return_inlet_temperature'],
                                          'June': system_params['return_inlet_temperature'],
                                          'July': system_params['return_inlet_temperature'],
                                          'August': system_params['return_inlet_temperature'],
                                          'September': system_params['return_inlet_temperature'],
                                          'October': system_params['return_inlet_temperature'],
                                          'November': system_params['return_inlet_temperature'],
                                          'December': system_params['return_inlet_temperature'] }
    else:
        monthly_inlet_temperatures = monthly_mains_temperatures
    
    field_fluid = system_params['fluid']
    field_pressure = 5
    if field_fluid == 'Agua':
        glycol_percentage = 0
    else:
        glycol_percentage = int(system_params['fluid'][7:9])
    PropsField = Properties(glycol_percentage, field_pressure)
    
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
    
    monthly_demands = {'January': convert_demand(system_params['demand_january'], system_params['yearly_demand_unit'], system_params['fuel_name'], system_params['boiler_type'], system_params['boiler_efficiency']),
                       'February': convert_demand(system_params['demand_february'], system_params['yearly_demand_unit'], system_params['fuel_name'], system_params['boiler_type'], system_params['boiler_efficiency']),
                       'March': convert_demand(system_params['demand_march'], system_params['yearly_demand_unit'], system_params['fuel_name'], system_params['boiler_type'], system_params['boiler_efficiency']),
                       'April': convert_demand(system_params['demand_april'], system_params['yearly_demand_unit'], system_params['fuel_name'], system_params['boiler_type'], system_params['boiler_efficiency']),
                       'May': convert_demand(system_params['demand_may'], system_params['yearly_demand_unit'], system_params['fuel_name'], system_params['boiler_type'], system_params['boiler_efficiency']),
                       'June': convert_demand(system_params['demand_june'], system_params['yearly_demand_unit'], system_params['fuel_name'], system_params['boiler_type'], system_params['boiler_efficiency']),
                       'July': convert_demand(system_params['demand_july'], system_params['yearly_demand_unit'], system_params['fuel_name'], system_params['boiler_type'], system_params['boiler_efficiency']),
                       'August': convert_demand(system_params['demand_august'], system_params['yearly_demand_unit'], system_params['fuel_name'], system_params['boiler_type'], system_params['boiler_efficiency']),
                       'September': convert_demand(system_params['demand_september'], system_params['yearly_demand_unit'], system_params['fuel_name'], system_params['boiler_type'], system_params['boiler_efficiency']),
                       'October': convert_demand(system_params['demand_october'], system_params['yearly_demand_unit'], system_params['fuel_name'], system_params['boiler_type'], system_params['boiler_efficiency']),
                       'November': convert_demand(system_params['demand_november'], system_params['yearly_demand_unit'], system_params['fuel_name'], system_params['boiler_type'], system_params['boiler_efficiency']),
                       'December': convert_demand(system_params['demand_december'], system_params['yearly_demand_unit'], system_params['fuel_name'], system_params['boiler_type'], system_params['boiler_efficiency'])}
    
    t_start = time_from_string(system_params['operation_start'])
    t_end = time_from_string(system_params['operation_end'])
    
    if latitude < 49:
        def corrected_time(t):
            '''
            Función que recibe la hora del año (entre 0 y 8760) y retorna la hora considerando el cambio de hora (entre 0 y 8760).
            
            Esta función considera que su argumento es la hora según el horario UTC-3, y en caso de encontrarse en el rango de tiempo durante el cual la hora oficial es UTC-4, resta 1 al valor recibido.
            
            En caso de que la simulación se realice en la región de Magallanes (el criterio para estar en la región de Magallanes es que la latitud sea más al sur que -49°), la función SIEMPRE retorna el mismo valor recibido como argumento.
            
            Se considera que los cambios de hora se realizan los días 7 de abril y 8 de septiembre a las 24:00 horas.
    
            Prámetros:
                - t: Hora del año de acuerdo al horario UTC-3
    
            Retorna:
                - Hora del año de acuerdo al horario UTC-3 o UTC-4, según corresponda.
            '''
            if t >= 24*97 and t - 1 < 24*251:
                return t - 1
            else:
                return t
    else:
        def corrected_time(t):
            '''
            Función que recibe la hora del año (entre 0 y 8760) y retorna la hora considerando el cambio de hora (entre 0 y 8760).
            
            Esta función considera que su argumento es la hora según el horario UTC-3, y en caso de encontrarse en el rango de tiempo durante el cual la hora oficial es UTC-4, resta 1 al valor recibido.
            
            En caso de que la simulación se realice en la región de Magallanes (el criterio para estar en la región de Magallanes es que la latitud sea más al sur que -49°), la función SIEMPRE retorna el mismo valor recibido como argumento.
            
            Se considera que los cambios de hora se realizan los días 7 de abril y 8 de septiembre a las 24:00 horas.
    
            Prámetros:
                - t: Hora del año de acuerdo al horario UTC-3
    
            Retorna:
                - Hora del año de acuerdo al horario UTC-3 o UTC-4, según corresponda.
            '''
            return t
    
    cost_per_kJ = compute_cost_per_kJ(system_params['fuel_name'], system_params['fuel_cost'], system_params['fuel_cost_units'], system_params['boiler_type'])
    
    if system_params['integration_scheme_name'] in ['NP_IE_ACS', 'NS_L_SI'] or system_params['integration_scheme_initials'] in ['NP_IE_ACS', 'NS_L_SI']:
        
        test_fluid_props = Properties(0,3)
        Field = Solar_Field(system_params['aperture_area'], system_params['coll_n0'],
                            system_params['coll_a1'], system_params['coll_a2'],
                            system_params['coll_iam'], system_params['coll_test_flow']*3600,
                            test_fluid_props, system_params['coll_tilt'], system_params['coll_azimuth'],
                            system_params['coll_rows'], system_params['colls_per_row'], PropsField)
        
        heated_fluid_pressure = convert_pressure(system_params['boiler_pressure'], system_params['boiler_pressure_units'])
        PropsHeatedFluid = Properties(0, heated_fluid_pressure)
        
        HX = Heat_Exchanger(system_params['HX_eff'], PropsField, PropsHeatedFluid)
        
        Boiler_type = system_params['boiler_type']
        boiler_nominal_power = convert_power(system_params['boiler_nominal_power'], system_params['boiler_nominal_power_units'])
        boiler_efficiency = system_params['boiler_efficiency']
            
        monthly_flows = compute_monthly_flows(monthly_demands, monthly_inlet_temperatures, work_day_list, t_start, t_end, system_params['outlet_temperature'], PropsHeatedFluid)
        
        T_set = system_params['outlet_temperature']
        
        mass_flow_field = convert_flow(system_params['field_mass_flow'], system_params['field_mass_flow_units'], glycol_percentage)
        
        Result = NP_IE_ACS__NS_L_SI(Field, HX, T_set, Boiler_type, boiler_nominal_power, boiler_efficiency,
                                    cost_per_kJ, work_day_list, monthly_flows, monthly_inlet_temperatures,
                                    monthly_mains_temperatures, t_start, t_end, PropsField, PropsHeatedFluid, mass_flow_field,
                                    sky_diff_func, ground_diff_func, DNI_func, T_amb_func, compute_zenith, compute_azimuth,
                                    corrected_time, time_step, tolerance, max_iterations)
        
    elif system_params['integration_scheme_name'] == 'NS_L_PI' or system_params['integration_scheme_initials'] == 'NS_L_PI':
        
        test_fluid_props = Properties(0,3)
        Field = Solar_Field(system_params['aperture_area'], system_params['coll_n0'],
                            system_params['coll_a1'], system_params['coll_a2'],
                            system_params['coll_iam'], system_params['coll_test_flow']*3600,
                            test_fluid_props, system_params['coll_tilt'], system_params['coll_azimuth'],
                            system_params['coll_rows'], system_params['colls_per_row'], PropsField)
        
        heated_fluid_pressure = convert_pressure(system_params['boiler_pressure'], system_params['boiler_pressure_units'])
        PropsHeatedFluid = Properties(0, heated_fluid_pressure)
        
        HX = Heat_Exchanger(system_params['HX_eff'], PropsField, PropsHeatedFluid)
        
        Boiler_type = system_params['boiler_type']
        boiler_nominal_power = convert_power(system_params['boiler_nominal_power'], system_params['boiler_nominal_power_units'])
        boiler_efficiency = system_params['boiler_efficiency']
            
        monthly_flows = compute_monthly_flows(monthly_demands, monthly_inlet_temperatures, work_day_list, t_start, t_end, system_params['outlet_temperature'], PropsHeatedFluid)
        
        T_set = system_params['outlet_temperature']
        
        mass_flow_field = convert_flow(system_params['field_mass_flow'], system_params['field_mass_flow_units'], glycol_percentage)
        
        Result = NS_L_PI(Field, HX, T_set, Boiler_type, boiler_nominal_power, boiler_efficiency,
                          cost_per_kJ, work_day_list, monthly_flows, monthly_inlet_temperatures,
                          monthly_mains_temperatures, t_start, t_end, PropsHeatedFluid, PropsField, mass_flow_field,
                          sky_diff_func, ground_diff_func, DNI_func, T_amb_func, compute_zenith, compute_azimuth,
                          corrected_time, time_step, tolerance, max_iterations)
        
    elif system_params['integration_scheme_name'] == 'SAM' or system_params['integration_scheme_initials'] == 'SAM':
        
        test_fluid_props = Properties(0,3)
        Field = Solar_Field(system_params['aperture_area'], system_params['coll_n0'],
                            system_params['coll_a1'], system_params['coll_a2'],
                            system_params['coll_iam'], system_params['coll_test_flow']*3600,
                            test_fluid_props, system_params['coll_tilt'], system_params['coll_azimuth'],
                            system_params['coll_rows'], system_params['colls_per_row'], PropsField)
        
        heated_fluid_pressure = convert_pressure(system_params['boiler_pressure'], system_params['boiler_pressure_units'])
        PropsHeatedFluid = Properties(0, heated_fluid_pressure)
        
        HX = Heat_Exchanger(system_params['HX_eff'], PropsField, PropsHeatedFluid)
        
        tank_volume = system_params['tank_volume']
        tank_AR = system_params['tank_AR']
        top_loss_coeff = 3.5
        edge_loss_coeff = 3.5
        bottom_loss_coeff = 3.5
        tank_nodes = 10
        inlet_1_node = 1
        outlet_1_node = 10
        inlet_2_node = 10
        outlet_2_node = 1
        tank_initial_temperatures = { i: 20 for i in range(1,11) }
        Tank = Storage_Tank(tank_volume, tank_AR, top_loss_coeff, edge_loss_coeff, bottom_loss_coeff,
                            tank_nodes, inlet_1_node, outlet_1_node, inlet_2_node, outlet_2_node,
                            None, None, None, None, None, None,
                            PropsHeatedFluid, None, None, tank_initial_temperatures)
        
        Boiler_type = system_params['boiler_type']
        boiler_nominal_power = convert_power(system_params['boiler_nominal_power'], system_params['boiler_nominal_power_units'])
        boiler_efficiency = system_params['boiler_efficiency']
            
        monthly_flows = compute_monthly_flows(monthly_demands, monthly_inlet_temperatures, work_day_list, t_start, t_end, system_params['outlet_temperature'], PropsHeatedFluid)
        
        T_set = system_params['outlet_temperature']
        
        mass_flow_field = convert_flow(system_params['field_mass_flow'], system_params['field_mass_flow_units'], glycol_percentage)
        
        Result = Solar_HX_Tank(Field, HX, Tank, T_set, Boiler_type, boiler_nominal_power, boiler_efficiency,
                                cost_per_kJ, work_day_list, monthly_flows, monthly_inlet_temperatures,
                                monthly_mains_temperatures, t_start, t_end, PropsField, PropsHeatedFluid, mass_flow_field,
                                sky_diff_func, ground_diff_func, DNI_func, T_amb_func, compute_zenith, compute_azimuth,
                                corrected_time, time_step, tolerance, max_iterations)
        
    elif system_params['integration_scheme_name'] == 'NS_L_PD' or system_params['integration_scheme_initials'] == 'NS_L_PD':
        
        heated_fluid_pressure = convert_pressure(system_params['boiler_pressure'], system_params['boiler_pressure_units'])
        PropsHeatedFluid = Properties(0, heated_fluid_pressure)
        
        monthly_flows = compute_monthly_flows(monthly_demands, monthly_inlet_temperatures, work_day_list, t_start, t_end, system_params['outlet_temperature'], PropsHeatedFluid)
        
        T_set = system_params['outlet_temperature']
        
        test_fluid_props = Properties(0,3)
        Field = Solar_Field(system_params['aperture_area'], system_params['coll_n0'],
                            system_params['coll_a1'], system_params['coll_a2'],
                            system_params['coll_iam'], system_params['coll_test_flow']*3600,
                            test_fluid_props, system_params['coll_tilt'], system_params['coll_azimuth'],
                            system_params['coll_rows'], system_params['colls_per_row'], PropsHeatedFluid)
        
        boiler_nominal_power = convert_power(system_params['boiler_nominal_power'], system_params['boiler_nominal_power_units'])
        boiler_efficiency = system_params['boiler_efficiency']
        
        Result = NS_L_PD(Field, T_set, boiler_nominal_power, boiler_efficiency,
                          cost_per_kJ, work_day_list, monthly_flows, monthly_inlet_temperatures,
                          monthly_mains_temperatures, t_start, t_end, PropsHeatedFluid,
                          sky_diff_func, ground_diff_func, DNI_func, T_amb_func,
                          compute_zenith, compute_azimuth, corrected_time,
                          time_step, tolerance, max_iterations)
        
    elif system_params['integration_scheme_name'] == 'NS_L_CA_MU' or system_params['integration_scheme_initials'] == 'NS_L_CA_MU':
        
        test_fluid_props = Properties(0,3)
        Field = Solar_Field(system_params['aperture_area'], system_params['coll_n0'],
                            system_params['coll_a1'], system_params['coll_a2'],
                            system_params['coll_iam'], system_params['coll_test_flow']*3600,
                            test_fluid_props, system_params['coll_tilt'], system_params['coll_azimuth'],
                            system_params['coll_rows'], system_params['colls_per_row'], PropsField)
        
        heated_fluid_pressure = convert_pressure(system_params['boiler_pressure'], system_params['boiler_pressure_units'])
        PropsHeatedFluid = Properties(0, heated_fluid_pressure)
        
        HX = Heat_Exchanger(system_params['HX_eff'], PropsField, PropsHeatedFluid)
        
        tank_volume = system_params['tank_volume']
        tank_AR = system_params['tank_AR']
        top_loss_coeff = 3.5
        edge_loss_coeff = 3.5
        bottom_loss_coeff = 3.5
        tank_nodes = 10
        inlet_1_node = 10
        outlet_1_node = 1
        inlet_2_node = 10
        outlet_2_node = 1
        tank_initial_temperatures = { i: 20 for i in range(1,11) }
        Tank = Storage_Tank(tank_volume, tank_AR, top_loss_coeff, edge_loss_coeff, bottom_loss_coeff,
                            tank_nodes, inlet_1_node, outlet_1_node, inlet_2_node, outlet_2_node,
                            None, None, None, None, None, None,
                            PropsHeatedFluid, None, None, tank_initial_temperatures)
        
        boiler_nominal_power = convert_power(system_params['boiler_nominal_power'], system_params['boiler_nominal_power_units'])
        boiler_efficiency = system_params['boiler_efficiency']
            
        monthly_flows = compute_monthly_flows(monthly_demands, monthly_inlet_temperatures, work_day_list, t_start, t_end, system_params['outlet_temperature'], PropsHeatedFluid)
        
        T_set = system_params['outlet_temperature']
        
        mass_flow_field = convert_flow(system_params['field_mass_flow'], system_params['field_mass_flow_units'], glycol_percentage)
        
        Result = NS_L_CA_MU(Field, Tank, HX, T_set, boiler_nominal_power, boiler_efficiency,
                            cost_per_kJ, work_day_list, monthly_flows,
                            monthly_inlet_temperatures, monthly_mains_temperatures, t_start, t_end,
                            PropsHeatedFluid, PropsField, mass_flow_field,
                            sky_diff_func, ground_diff_func, DNI_func, T_amb_func,
                            compute_zenith, compute_azimuth, corrected_time,
                            time_step, tolerance, max_iterations)
        
    elif system_params['integration_scheme_name'] == 'NS_L_CA_1' or system_params['integration_scheme_initials'] == 'NS_L_CA_1':
        
        test_fluid_props = Properties(0,3)
        Field = Solar_Field(system_params['aperture_area'], system_params['coll_n0'],
                            system_params['coll_a1'], system_params['coll_a2'],
                            system_params['coll_iam'], system_params['coll_test_flow']*3600,
                            test_fluid_props, system_params['coll_tilt'], system_params['coll_azimuth'],
                            system_params['coll_rows'], system_params['colls_per_row'], PropsField)
        
        boiler_pressure = convert_pressure(system_params['boiler_pressure'], system_params['boiler_pressure_units'])
        heated_fluid_pressure = max([ field_pressure, boiler_pressure ])
        PropsBoiler = Properties(0, boiler_pressure)
        PropsHeatedFluid = Properties(0, heated_fluid_pressure)
        HX1_props = PropsField
        HX2_props = PropsBoiler
        
        HX_eff = system_params['HX_eff']
        
        tank_volume = system_params['tank_volume']
        tank_AR = system_params['tank_AR']
        top_loss_coeff = 3.5
        edge_loss_coeff = 3.5
        bottom_loss_coeff = 3.5
        tank_nodes = 10
        inlet_2_node = 10
        outlet_2_node = 1
        tank_initial_temperatures = { i: 20 for i in range(1,11) }
        Tank = Storage_Tank(tank_volume, tank_AR, top_loss_coeff, edge_loss_coeff, bottom_loss_coeff,
                            tank_nodes, None, None, inlet_2_node, outlet_2_node,
                            HX_eff, HX_eff, 7, 9, 2, 4,
                            PropsHeatedFluid, HX1_props, HX2_props, tank_initial_temperatures)

        
        boiler_nominal_power = convert_power(system_params['boiler_nominal_power'], system_params['boiler_nominal_power_units'])
        boiler_efficiency = system_params['boiler_efficiency']
            
        monthly_flows = compute_monthly_flows(monthly_demands, monthly_inlet_temperatures, work_day_list, t_start, t_end, system_params['outlet_temperature'], PropsHeatedFluid)
        
        T_set = system_params['outlet_temperature']
        
        mass_flow_field = convert_flow(system_params['field_mass_flow'], system_params['field_mass_flow_units'], glycol_percentage)
        
        Result = NS_L_CA_1(Field, Tank, T_set, boiler_nominal_power, boiler_efficiency,
                            cost_per_kJ, work_day_list, monthly_flows,
                            monthly_inlet_temperatures, monthly_mains_temperatures, t_start, t_end,
                            PropsHeatedFluid, PropsField, PropsBoiler, mass_flow_field,
                            sky_diff_func, ground_diff_func, DNI_func, T_amb_func, compute_zenith, compute_azimuth, corrected_time, time_step, tolerance, max_iterations)
        
    elif system_params['integration_scheme_name'] == 'NS_L_CA_2' or system_params['integration_scheme_initials'] == 'NS_L_CA_2':
        
        test_fluid_props = Properties(0,3)
        Field = Solar_Field(system_params['aperture_area'], system_params['coll_n0'],
                            system_params['coll_a1'], system_params['coll_a2'],
                            system_params['coll_iam'], system_params['coll_test_flow']*3600,
                            test_fluid_props, system_params['coll_tilt'], system_params['coll_azimuth'],
                            system_params['coll_rows'], system_params['colls_per_row'], PropsField)
        
        boiler_pressure = convert_pressure(system_params['boiler_pressure'], system_params['boiler_pressure_units'])
        heated_fluid_pressure = max([ field_pressure, boiler_pressure ])
        PropsBoiler = Properties(0, boiler_pressure)
        PropsHeatedFluid = Properties(0, heated_fluid_pressure)
        
        HX_eff = system_params['HX_eff']
        HX = Heat_Exchanger(HX_eff, PropsField, PropsHeatedFluid)
        
        tank_volume = system_params['tank_volume']
        tank_AR = system_params['tank_AR']
        top_loss_coeff = 3.5
        edge_loss_coeff = 3.5
        bottom_loss_coeff = 3.5
        tank_nodes = 10
        inlet_1_node = 7
        outlet_1_node = 10
        inlet_2_node = 10
        outlet_2_node = 1
        tank_initial_temperatures = { i: 20 for i in range(1,11) }
        Tank = Storage_Tank(tank_volume, tank_AR, top_loss_coeff, edge_loss_coeff, bottom_loss_coeff,
                            tank_nodes, inlet_1_node, outlet_1_node, inlet_2_node, outlet_2_node,
                            None, HX_eff, None, None, 2, 4,
                            PropsHeatedFluid, None, PropsBoiler, tank_initial_temperatures)
        
        boiler_nominal_power = convert_power(system_params['boiler_nominal_power'], system_params['boiler_nominal_power_units'])
        boiler_efficiency = system_params['boiler_efficiency']
            
        monthly_flows = compute_monthly_flows(monthly_demands, monthly_inlet_temperatures, work_day_list, t_start, t_end, system_params['outlet_temperature'], PropsHeatedFluid)
        
        T_set = system_params['outlet_temperature']
        
        mass_flow_field = convert_flow(system_params['field_mass_flow'], system_params['field_mass_flow_units'], glycol_percentage)
        
        Result = NS_L_CA_2(Field, Tank, HX, T_set, boiler_nominal_power, boiler_efficiency,
                           cost_per_kJ, work_day_list, monthly_flows, monthly_inlet_temperatures,
                           monthly_mains_temperatures, t_start, t_end, PropsHeatedFluid, PropsField, PropsBoiler,
                           mass_flow_field, sky_diff_func, ground_diff_func, DNI_func, T_amb_func,
                           compute_zenith, compute_azimuth, corrected_time,
                           time_step, tolerance, max_iterations)
    
    return {'Result': Result,
            'integration_scheme_name': system_params['integration_scheme_name'],
            'integration_scheme_initials': system_params['integration_scheme_initials'],
            'cost_per_kJ': cost_per_kJ,
            'work_day_list': work_day_list,
            'monthly_demands': monthly_demands,
            'monthly_mains_temperatures': monthly_mains_temperatures,
            'monthly_flows': monthly_flows,
            'closed_system': system_params['closed_system'],
            'boiler_efficiency': system_params['boiler_efficiency'],
            'time_step': time_step,
            'coll_area': system_params['aperture_area'],
            'coll_price': system_params['coll_price'],
            'coll_rows': system_params['coll_rows'],
            'colls_per_row': system_params['colls_per_row'],
            'Tank_volume': system_params['tank_volume'],
            'Tank_cost_per_m3': system_params['tank_cost'],
            'BoP_cost_per_m2': system_params['BOP'],
            'installation_cost': system_params['installation_cost'],
            'operation_and_maintanence': system_params['operation_cost'],
            'tax_rate': system_params['tax_rate'],
            'discount_factor': system_params['discount_factor']}