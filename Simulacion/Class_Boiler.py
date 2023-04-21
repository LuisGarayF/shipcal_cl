# -*- coding: utf-8 -*-
"""
Created on Fri Oct 14 12:37:41 2022

@author: adria
"""

from Simulacion.Class_Heat_Exchanger import Heat_Exchanger

class Boiler_HX:
    def __init__(self, boiler_efficiency, P_max, HX_effectiveness, cost_per_kJ,
                 m_source, fluid_props_source, fluid_props_load, tolerance = 1e-6, max_iterations = 50):
        self.fluid_props_source = fluid_props_source
        self.fluid_props_load = fluid_props_load
        self.Boiler_eff = boiler_efficiency
        self.P_max = P_max
        self.HX_effectiveness = HX_effectiveness
        self.HX = Heat_Exchanger(HX_effectiveness, fluid_props_source, fluid_props_load)
        self.cost_per_kJ = cost_per_kJ
        self.m_source = m_source
        self.tolerance = tolerance
        self.max_iterations = max_iterations
    def efficiency(self, T_in, T_set):
        return self.Boiler_eff
    def compute_outputs(self, m_load, h_in_load, T_set, h_mains, time_step):
        T_in_load = self.fluid_props_load.h_to_T(h_in_load)
        if T_in_load >= T_set:
            return {'h_out': h_in_load,
                    'Q_delivered': 0,
                    'Q_combustion': 0,
                    'cost_time_step': 0,
                    'source_sat': False,
                    'excess_temp': True,
                    'P_max_reached': False}
        h_out_load_needed = self.fluid_props_load.T_to_h(T_set)
        Q_needed = m_load*(h_out_load_needed - h_in_load)
        if Q_needed > self.P_max:
            it = 0
            h_in_boiler = self.fluid_props_source.T_to_h(self.fluid_props_load.h_to_T(h_in_load))
            while True:
                h_out_boiler = h_in_boiler + self.P_max/self.m_source
                if h_out_boiler > self.fluid_props_source.h_sat_liq:
                    h_out_boiler = self.fluid_props_source.h_sat_liq
                    HX_outputs = self.HX.compute_outputs(self.m_source, h_out_boiler, m_load, h_in_load, h_mains)
                    h_out_load = HX_outputs['h_out_load']
                    Q_delivered = HX_outputs['Q_useful']
                    T_in_Boiler = self.fluid_props_source.h_to_T(HX_outputs['h_out_source'])
                    Q_combustion = Q_delivered/self.efficiency(Q_delivered, T_in_Boiler)
                    cost_time_step = self.cost_per_kJ*Q_combustion*time_step
                    return {'h_out': h_out_load,
                            'Q_delivered': Q_delivered,
                            'Q_combustion': Q_combustion,
                            'cost_time_step': cost_time_step,
                            'source_sat': True,
                            'excess_temp': False,
                            'P_max_reached': False}
                HX_outputs = self.HX.compute_outputs(self.m_source, h_out_boiler, m_load, h_in_load, h_mains)
                it = it + 1
                if abs(HX_outputs['h_out_source'] - h_in_boiler)/h_in_boiler < self.tolerance:
                    maxIt = False
                    break
                if it == self.max_iterations:
                    maxIt = True
                    break
                h_in_boiler = HX_outputs['h_out_source']
            h_out_load = HX_outputs['h_out_load']
            Q_delivered = HX_outputs['Q_useful']
            T_in_Boiler = self.fluid_props_source.h_to_T(HX_outputs['h_out_source'])
            Q_combustion = Q_delivered/self.efficiency(Q_delivered, T_in_Boiler)
            cost_time_step = self.cost_per_kJ*Q_combustion*time_step
            return {'h_out': h_out_load,
                    'Q_delivered': Q_delivered,
                    'Q_combustion': Q_combustion,
                    'cost_time_step': cost_time_step,
                    'source_sat': False,
                    'excess_temp': False,
                    'P_max_reached': True}
        Q_max_needed = Q_needed/self.HX_effectiveness
        h_hyp_load = h_in_load + Q_max_needed/m_load
        if h_hyp_load >= self.fluid_props_load.h_sat_liq:
            T_in_source_1 = (self.fluid_props_load.T_sat +
                             (h_hyp_load -
                              self.fluid_props_load.h_sat_liq)/
                             self.fluid_props_load.fluid_spec_heat)
        else:
            T_in_source_1 = self.fluid_props_load.h_to_T(h_hyp_load)
        h_hyp_source = self.fluid_props_source.T_to_h(T_in_load) + Q_max_needed/self.m_source
        T_in_source_2 = self.fluid_props_source.h_to_T(h_hyp_source)
        T_in_source = max([T_in_source_1, T_in_source_2])
        if T_in_source >= self.fluid_props_source.T_sat:
            h_in_source = self.fluid_props_source.h_sat_liq
            source_sat = True
        else:
            h_in_source = self.fluid_props_source.T_to_h(T_in_source)
            source_sat = False
        HX_outputs = self.HX.compute_outputs(self.m_source, h_in_source,
                                             m_load, h_in_load, h_mains)
        Q_delivered = HX_outputs['Q_useful']
        T_in_Boiler = self.fluid_props_source.h_to_T(HX_outputs['h_out_source'])
        Q_combustion = Q_delivered/self.efficiency(Q_delivered, T_in_Boiler)
        cost_time_step = self.cost_per_kJ*Q_combustion*time_step
        return {'h_out': HX_outputs['h_out_load'],
                'Q_delivered': Q_delivered,
                'Q_combustion': Q_combustion,
                'cost_time_step': cost_time_step,
                'source_sat': source_sat,
                'excess_temp': False,
                'P_max_reached': False}
        