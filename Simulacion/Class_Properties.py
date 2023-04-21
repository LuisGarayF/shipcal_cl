# -*- coding: utf-8 -*-
"""
Created on Wed Sep 28 17:08:53 2022

@author: Adrian
"""

from CoolProp.CoolProp import PropsSI
from numpy import polyfit, poly1d,linspace


class Properties:
    def __init__(self, fluid, P):
        h_sat_liq = PropsSI('H', 'P', 100000*P, 'Q', 0, fluid)
        h_sat_vap = PropsSI('H', 'P', 100000*P, 'Q', 1, fluid)
        T = 253.15
        while True:
            try:
                h_min = PropsSI('H', 'T', T, 'P', 100000*P, fluid)
                break
            except:
                T = T + 0.01
        T_sat = PropsSI('T', 'P', 100000*P, 'Q', 0.5, fluid)
        h_vap_max = PropsSI('H', 'T', T_sat + 200, 'P', 100000*P, fluid)
        h_liq_List = linspace(h_min, h_sat_liq, 100)
        h_vap_List = linspace(h_sat_vap, h_vap_max, 100)
        T_liq_List = [ PropsSI('T', 'H', h_liq_List[i], 'P', 100000*P, fluid) - 273.15 for i in range(len(h_liq_List)) ]
        T_vap_List = [ PropsSI('T', 'H', h_vap_List[i], 'P', 100000*P, fluid) - 273.15 for i in range(len(h_vap_List))]
        h_liq_List = h_liq_List/1000
        h_vap_List = h_vap_List/1000
        self.fluid_spec_heat = PropsSI('C', 'T', T_sat - 1, 'P', 100000*P, fluid)/1000
        self.h_sat_liq = h_sat_liq/1000
        self.h_sat_vap = h_sat_vap/1000
        self.T_sat = T_sat - 273.15
        self.h_to_T_liq = poly1d(polyfit(h_liq_List, T_liq_List,3))
        self.T_to_h_liq = poly1d(polyfit(T_liq_List, h_liq_List,3))
        self.h_to_T_vap = poly1d(polyfit(h_vap_List, T_vap_List,3))
        self.T_to_h_vap = poly1d(polyfit(T_vap_List, h_vap_List,3))
    def h_to_T(self, h):
        if h > self.h_sat_vap:
            return self.h_to_T_vap(h)
        if h < self.h_sat_liq:
            return self.h_to_T_liq(h)
        return self.T_sat
    def T_to_h(self, T):
        if T == self.T_sat:
            raise ValueError('Specific enthalpy cannot be computed at saturation temperature: '
                             +str(self.T_sat)+' °C')
        if T > self.T_sat:
            return self.T_to_h_vap(T)
        return self.T_to_h_liq(T)
    def quality(self, h):
        if h > self.h_sat_vap:
            return 1
        if h < self.h_sat_liq:
            return 0
        return (h - self.h_sat_liq)/(self.h_sat_vap - self.h_sat_liq)


class Properties_water:
    '''
    Class that is used to store and yield the properties of water at a pressure provided by the user.
    
    Initialization parameters:
        - pressure: Pressure of the water (bar).
        
    Attributes:
        - self.fluid_spec_heat: Specific heat capacity of the water at liquid state ( kJ / ( kg * K ) ). The value is computed at a temperature of 40°C and is considered to be independent from temperature.
        - self.fluid_density: Density of the water at liquid state ( kg / m^3 ). The value is computed at a temperature of 40°C and is considered to be independent from temperature.
        - self.fluid_thermal_conductivity: Thermal conductivity of the water at liquid state ( kJ / ( hr * m * K ) ). The value is computed at a temperature of 40°C and is considered to be independent from temperature.
        - self.cp_vap: Specific heat capacity of the water at vapor state ( kJ / ( kg * K ) ). The value is computed at a temperature 50°C over the saturation temperature at the corresponding pressure and is considerd to be independent from temperature.
        - self.T_sat: Saturation temperature of water at the corresponding pressure (°C).
        - self.h_sat_liq: Specific enthalpy of liquid at saturation temperature (kJ / kg).
        - self.h_sat_vap: Specific enthalpy of vapor at saturation temperature (kJ/kg).
        
    Methods:
        - self.h_to_T: Function to convert specific enthalpy to temperature.
        - self.T_to_h: Function to convert temperature to specific enthalpy.
        - self.quality: Function to obtain the quality (vapor-to-liquid proportion, no units) of the fluid at a certain enthalpy.
        
    Exceptions:
        - The model yields a ValueError when exactly the saturation temperature is provided as argument for the self.T_to_h function 
    '''
    def __init__(self, pressure):
        self.fluid_spec_heat = PropsSI('C', 'T', 273.15 + 40, 'P', 100000*pressure, 'water')/1000
        self.fluid_density = PropsSI('D', 'T', 273.15 + 40, 'P', 100000*pressure, 'water')
        self.fluid_thermal_conductivity = 3.6*PropsSI('CONDUCTIVITY', 'T', 273.15 + 40,
                                                      'P', 100000*pressure, 'water')
        T_sat = PropsSI('T', 'P', 100000*pressure, 'Q', 0, 'water')
        self.cp_vap = PropsSI('C', 'T', T_sat + 50, 'P', 100000*pressure, 'water')/1000
        self.T_sat = T_sat - 273.15
        self.h_sat_liq = PropsSI('H', 'P', 100000*pressure, 'Q', 0, 'water')/1000
        self.h_sat_vap = PropsSI('H', 'P', 100000*pressure, 'Q', 1, 'water')/1000
    def h_to_T(self, h):
        '''
        Function that receives the specific enthalpy and yields the temperature of water at the initialization pressure and the given enthalpy.

        Parameters
        ----------
        h : specific enthalpy (kJ/kg)

        Returns:
            - Temperature (°C)
        '''
        if h > self.h_sat_vap:
            return self.T_sat + (h - self.h_sat_vap)/self.cp_vap
        if h < self.h_sat_liq:
            return self.T_sat - (self.h_sat_liq - h)/self.fluid_spec_heat
        return self.T_sat
    def T_to_h(self, T):
        '''
        Function that receives the temperature and yields the specific enthalpy of water at the initialization pressure and the given temperature.

        Parameters:
            - T : Temperature of the water (°C).

        Returns:
            - Specific enthalpy of the water at the initialization pressure and the given temperature (kJ/kg).
            
        Raises:
            This function raises a ValueError when exactly the saturation temperature is provided as argument.
        '''
        if T == self.T_sat:
            raise ValueError('Specific enthalpy cannot be computed at saturation temperature: '
                             +str(self.T_sat)+' °C')
        if T > self.T_sat:
            return self.h_sat_vap + self.cp_vap*(T - self.T_sat)
        return self.h_sat_liq - self.fluid_spec_heat*(self.T_sat - T)
    def quality(self, h):
        '''
        Function that receives a specific enthalpy and yields the quality of the vapor-liquid mixture (in the case that the fluid is saturated).

        Parameters:
            - h: Specific enthalpy of the fluid (kJ/kg).

        Returns:
            Quality of the fluid at the given enthalpy. If the enthalpy is below the saturation enthalpy of liquid water, the returned value is 0. If the enthalpy is over the saturation enthalpy of vapor, the returned value is 1. If the provided specific enthalpy is between those values, the returned value is between 0 and 1.
        '''
        if h < self.h_sat_liq:
            return 0
        if h > self.h_sat_vap:
            return 1
        return (h - self.h_sat_liq)/(self.h_sat_vap - self.h_sat_liq)