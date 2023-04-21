# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 16:31:34 2022

@author: adria
"""

from Simulacion.Class_Solar_Field import Solar_Field
from Simulacion.Class_Heat_Exchanger import Heat_Exchanger



class Solar_Field_series:
    def __init__(self, field_1_coll_L, field_1_coll_W, field_1_coll_n0, field_1_coll_a1,
                 field_1_coll_a2, field_1_coll_rows, field_1_colls_per_row,
                 field_2_coll_L, field_2_coll_W, field_2_coll_n0, field_2_coll_a1,
                 field_2_coll_a2, field_2_coll_rows, field_2_colls_per_row,
                 field_1_HX_effectiveness, main_HX_effectiveness, fluid_props_1,
                 fluid_props_2, fluid_props_load, m_in_field, m_closed_loop,
                 tolerance = 1e-6, maxIt = 50):
        ## coll_L, coll_W, coll_n0, coll_a1, coll_a2,
        ## coll_rows, colls_per_row, fluid_props,
        ## tolerance = 1e-6, maxIt = 50
        self.Field_1 = Solar_Field(field_1_coll_L, field_1_coll_W,
                                   field_1_coll_n0, field_1_coll_a1,
                                   field_1_coll_a2, field_1_coll_rows,
                                   field_1_colls_per_row, fluid_props_1)
        self.Field_2 = Solar_Field(field_2_coll_L, field_2_coll_W,
                                   field_2_coll_n0, field_2_coll_a1,
                                   field_2_coll_a2, field_2_coll_rows,
                                   field_2_colls_per_row, fluid_props_2)
        self.Field1_HX = Heat_Exchanger(field_1_HX_effectiveness, fluid_props_1, fluid_props_2)
        self.main_HX = Heat_Exchanger(main_HX_effectiveness, fluid_props_2, fluid_props_load)
        self.m_in_field = m_in_field
        self.m_closed_loop = m_closed_loop
        self.tolerance = tolerance
        self.maxIt = maxIt
    def compute_outputs(self, m_load, h_in_load, h_mains_1, h_mains_2, h_mains_load, rad, T_amb):
        if m_load == 0:
            return {'h_out_load': h_in_load,
                    'Field_1_Power': 0,
                    'Field_2_Power': 0,
                    'Q_useful_total': 0,
                    'Q_waste_Field_1': 0,
                    'Q_waste_Field_2': 0,
                    'Q_waste_Field_1_HX': 0}
        h_in_field = self.main_HX.fluid_props_source.T_to_h(self.main_HX.fluid_props_load.h_to_T(h_in_load))
        it1 = 0
        while True:
            h_in_field_1 = self.Field1_HX.fluid_props_source.T_to_h(self.Field1_HX.fluid_props_load.h_to_T(h_in_field))
            it2 = 0
            while True:
                Field_1_outputs = self.Field_1.compute_outputs(self.m_closed_loop, h_in_field_1,
                                                               h_mains_1, rad, T_amb)
                Field1_HX_outputs = self.Field1_HX.compute_outputs(self.m_closed_loop, Field_1_outputs['h_out'],
                                                                   self.m_in_field, h_in_field, h_mains_2)
                it2 = it2 + 1
                if abs(Field1_HX_outputs['h_out_source'] - h_in_field_1)/h_in_field_1 < self.tolerance:
                    maxIt2 = False
                    break
                if it2 == self.maxIt:
                    maxIt2 = True
                    break
                h_in_field_1 = Field1_HX_outputs['h_out_source']
            Field_2_outputs = self.Field_2.compute_outputs(self.m_in_field, Field1_HX_outputs['h_out_load'], h_mains_2, rad, T_amb)
            main_HX_outputs = self.main_HX.compute_outputs(self.m_in_field, Field_2_outputs['h_out'],
                                            m_load, h_in_load, h_mains_load)
            it1 = it1 + 1
            if abs(main_HX_outputs['h_out_source'] - h_in_field)/h_in_field < self.tolerance:
                maxIt1 = False
                break
            if it1 == self.maxIt:
                maxIt1 = True
                break
            h_in_field = main_HX_outputs['h_out_source']
        return {'h_out_load': main_HX_outputs['h_out_load'],
                'Field_1_Power': Field_1_outputs['Q_useful'],
                'Field_2_Power': Field_2_outputs['Q_useful'],
                'Q_useful_total': main_HX_outputs['Q_useful'],
                'Q_waste_Field_1': Field_1_outputs['Q_waste'],
                'Q_waste_Field_2': Field_2_outputs['Q_waste'],
                'Q_waste_Field_1_HX': Field1_HX_outputs['Q_waste']}


class Solar_Field_parallel:
    def __init__(self, field_1_coll_L, field_1_coll_W, field_1_coll_n0, field_1_coll_a1,
                 field_1_coll_a2, field_1_coll_rows, field_1_colls_per_row,
                 field_2_coll_L, field_2_coll_W, field_2_coll_n0, field_2_coll_a1,
                 field_2_coll_a2, field_2_coll_rows, field_2_colls_per_row,
                 field_1_HX_effectiveness, main_HX_effectiveness, fluid_props_1,
                 fluid_props_2, fluid_props_load, m_in_field, m_closed_loop, frac_field_1,
                 tolerance = 1e-6, maxIt = 50):
        self.Field_1 = Solar_Field(field_1_coll_L, field_1_coll_W,
                                   field_1_coll_n0, field_1_coll_a1,
                                   field_1_coll_a2, field_1_coll_rows,
                                   field_1_colls_per_row, fluid_props_1)
        self.Field_2 = Solar_Field(field_2_coll_L, field_2_coll_W,
                                   field_2_coll_n0, field_2_coll_a1,
                                   field_2_coll_a2, field_2_coll_rows,
                                   field_2_colls_per_row, fluid_props_2)
        self.Field1_HX = Heat_Exchanger(field_1_HX_effectiveness, fluid_props_1, fluid_props_2)
        self.main_HX = Heat_Exchanger(main_HX_effectiveness, fluid_props_2, fluid_props_load)
        self.m_in_field = m_in_field
        self.m_closed_loop = m_closed_loop
        self.tolerance = tolerance
        self.maxIt = maxIt
        self.frac_field_1 = frac_field_1
    def compute_outputs(self, m_load, h_in_load, h_mains_1, h_mains_2, h_mains_load, rad, T_amb):
        if m_load == 0:
            return {'h_out_load': h_in_load,
                    'Field_1_Power': 0,
                    'Field_2_Power': 0,
                    'Q_useful_total': 0,
                    'Q_waste_Field_1': 0,
                    'Q_waste_Field_2': 0,
                    'Q_waste_Field_1_HX': 0}
        h_in_field = self.main_HX.fluid_props_source.T_to_h(self.main_HX.fluid_props_load.h_to_T(h_in_load))
        it1 = 0
        while True:
            h_in_field_1 = self.Field1_HX.fluid_props_source.T_to_h(self.Field1_HX.fluid_props_load.h_to_T(h_in_field))
            it2 = 0
            while True:
                Field_1_outputs = self.Field_1.compute_outputs(self.m_closed_loop, h_in_field_1,
                                                               h_mains_1, rad, T_amb)
                Field1_HX_outputs = self.Field1_HX.compute_outputs(self.m_closed_loop,
                                                                   Field_1_outputs['h_out'],
                                                                   self.frac_field_1*self.m_in_field,
                                                                   h_in_field, h_mains_2)
                it2 = it2 + 1
                if abs(Field1_HX_outputs['h_out_source'] - h_in_field_1)/h_in_field_1 < self.tolerance:
                    maxIt2 = False
                    break
                if it2 == self.maxIt:
                    maxIt2 = True
                    break
                h_in_field_1 = Field1_HX_outputs['h_out_source']
            Field_2_outputs = self.Field_2.compute_outputs((1 - self.frac_field_1)*self.m_in_field,
                                                           h_in_field, h_mains_2, rad, T_amb)
            h_out = self.frac_field_1*Field1_HX_outputs['h_out_load'] + (1-self.frac_field_1)*Field_2_outputs['h_out']
            main_HX_outputs = self.main_HX.compute_outputs(self.m_in_field, h_out, m_load,
                                            h_in_load, h_mains_load)
            it1 = it1 + 1
            if abs(main_HX_outputs['h_out_source'] - h_in_field)/h_in_field < self.tolerance:
                maxIt1 = False
                break
            if it1 == self.maxIt:
                maxIt1 = True
                break
            h_in_field = main_HX_outputs['h_out_source']
        return {'h_out_load': main_HX_outputs['h_out_load'],
                'Field_1_Power': Field_1_outputs['Q_useful'],
                'Field_2_Power': Field_2_outputs['Q_useful'],
                'Q_useful_total': main_HX_outputs['Q_useful'],
                'Q_waste_Field_1': Field_1_outputs['Q_waste'],
                'Q_waste_Field_2': Field_2_outputs['Q_waste'],
                'Q_waste_Field_1_HX': Field1_HX_outputs['Q_waste']}