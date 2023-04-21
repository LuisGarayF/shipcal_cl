# -*- coding: utf-8 -*-
"""
Created on Wed Sep 28 17:08:53 2022

@author: Adrian
"""



class Solar_Field:
    '''
    Model for a thermal solar field. The model considers energy losses which are produced due to vapor production and expuslion (this is considered only when pure water is used as working fluid).
    When vapor is produced due to boiling inside the collectors, a flow of mains water is introduced in the inlet of the corresponding row in order to compensate the loss of mass due to vapor expulsion.
    
    Initialization parameters:
        - coll_L: length of each individual collector (m)
        - coll_W: width of each individual collector (m)
        - coll_n0: optical efficiency of the collectors (no units)
        - coll_a1: Linear thermal loss coefficient of the collectors ( kJ / (hr * m^2 * K) )
        - coll_a2: Quadratic thermal loss coefficient of the collectors ( kJ / (hr * m^2 * K^2) )
        - coll_rows: Number of collector rows in the solar field (rows are arranged in parallel; within each row, the collectors are arranged in series) (no units)
        - colls_per_row: Number of collectors in each row (no units)
        - fluid_props: Object of the class "Properties" to define the fluid that is used as working fluid to extract heat from the collectors.
        - tolerance: Maximum discrepancy between successive iterations which is allowed to yield the outputs of the field (iterations are only needed when vapor is being generated inside the collectors) (no units)
        - maxIt: Maximum number of iterations permitted until the outputs are yielded despite convergence has not been achieved (no units)
        
    Attributes (See initialization parameters for description):
        - self.coll_L
        - self.coll_W
        - self.coll_A = self.coll_L * self.coll_W  #area of the collector
        - self.n0
        - self.a1
        - self.a2
        - self.coll_rows
        - self.colls_per_row
        - self.fluid_props
        - self.tolerance
        - self.maxIt
        
    Methods:
        - self.convergence: evaluates whether convergence has been achieved, in the case that iterations are needed due to vapor generation.
        - self.h_out_coll: output computation for a single collector
        - self.h_out_row: output computation for a row of collectors
        - self.compute_outputs: output computation for the whole field
    '''
    def __init__(self, coll_L, coll_W, coll_n0, coll_a1, coll_a2,
                 coll_rows, colls_per_row, fluid_props,
                 tolerance = 1e-6, maxIt = 50):
        self.coll_L = coll_L
        self.coll_W = coll_W
        self.coll_A = self.coll_L * self.coll_W
        self.n0 = coll_n0
        self.a1 = coll_a1
        self.a2 = coll_a2
        self.coll_rows = coll_rows
        self.colls_per_row = colls_per_row
        self.fluid_props = fluid_props
        self.tolerance = tolerance
        self.maxIt = maxIt
    def convergence(self, m_mains, m_vap):
        """
        Function that evaluates the convergence of the iterations (iterations are only necessary when vapor is being generated).
        In each iteration, a flow of mains water is introduced into the collector row to compensate the mass loss due to vapor expulsion.
        In order to achieve convergence, the mass flow of water being introduced and the mass flow of vapor being produced must be equal (or have a discrepancy smaller than a "tolerance" parameter)

        Parameters:
            - m_mains: mass flow of mains water that was introduced into the collector at the beginning of the iteration (kg/hr).
            - m_vap: mass flow of vapor produced due to the heat of the collectors (kg/hr).

        Returns:
            a boolean value which is True if convergence has been achieved, and False otherwise.
        """
        if m_mains == m_vap:
            return True
        m_max = max([ m_mains, m_vap ])
        return abs(m_mains - m_vap)/m_max < self.tolerance
    def h_out_coll(self, m_in, h_in, rad, T_amb):
        '''
        Function that computes the specific enthalpy of the flow leaving an individual collector.
        It considers the flow temperature and the ambient temperature in order to estimate the efficiency of the collector.

        Parameters:
            - m_in: mass flow entering the collector (kg/hr)
            - h_in: specific enthalpy of the flow entering the collector (kJ/kg)
            - rad: solar radiation reaching the collector ( kJ / ( hr * m^2 ) )
            - T_amb: ambient temperature (°C)

        Returns:
            - specific enthalpy of the flow leaving the collector.
        '''
        if rad <= 0:
            return h_in
        T_in = self.fluid_props.h_to_T(h_in)
        if T_amb > T_in:
            eff = self.n0
        else:
            eff = self.n0 - self.a1*(T_in - T_amb)/rad - self.a2*((T_in - T_amb)**2)/rad
        if eff < 0:
            eff = 0
        power = eff*rad*self.coll_A
        return h_in + power/m_in
    def h_out_row(self, m_in_row, h_in_row, h_mains, rad, T_amb):
        '''
        Function that computes the specific enthalpy of the flow leaving a row of collectors.

        Parameters:
            - m_in_row: mass flow entering the row (kg/hr)
            - h_in_row: specific enthalpy of the flow entering the row (kJ/kg)
            - h_mains: specific enthalpy of the mains flow that will be introduced into the field in the case that vapor is generated inside the collectors (kJ/kg).
            - rad: solar radiation reaching the collector row ( kJ / ( hr * m^2 ) )
            - T_amb: ambient temperature (°C)

        Returns a tuple with the following elements:
            - specific enthalpy of the flow leaving the row (kJ/kg)
            - power being "wasted" (only when vapor is generated) to heat the mains flow that is introduced to compensate the vapor loss. This flow is heated from its initial enthalpy to the specific enthalpy of vapor at saturation (kJ/hr).
            - vapor mass flow being released (or mains water flow being introduced to compensate the vapor loss) (kg/hr)
            - number of iterations executed to achieve convergence (no units)
            - a boolean value which is True if the maximal number of allowed iterations was reached without achieving convergence, and False otherwise.
        '''
        if m_in_row == 0:
            return h_in_row, 0, 0, 0, False
        m_mains = 0
        it = 0
        while True:
            m_in = m_in_row + m_mains
            h_in = (m_in_row*h_in_row + m_mains*h_mains)/m_in
            for i in range(self.colls_per_row):
                h_in = self.h_out_coll(m_in, h_in, rad, T_amb)
            h_out = h_in
            m_vap = self.fluid_props.quality(h_out)*m_in
            it = it+1
            if self.convergence(m_mains, m_vap):
                maxIt = False
                break
            if it == self.maxIt:
                maxIt = True
                break
            Q_useful = m_in_row*(self.fluid_props.h_sat_liq - h_in_row)
            Q_actual = m_in*(h_out - (m_in_row*h_in_row + m_mains*h_mains)/m_in)
            Q_waste = Q_actual - Q_useful
            m_mains = Q_waste/(self.fluid_props.h_sat_vap - h_mains)
        if m_vap > 0:
            return self.fluid_props.h_sat_liq, m_vap*(self.fluid_props.h_sat_vap - h_mains), m_vap, it, maxIt
        else:
            return h_out, 0, 0, it, maxIt
    def compute_outputs(self, m_in_field, h_in_field, h_mains, rad, T_amb):
        '''
        Function that computes the specific enthalpy of the flow that is leaving the solar field.

        Parameters:
            - m_in_field: mass flow entering the solar field (kg/hr).
            - h_in_field: specific enthalpy of the flow entering the solar field (kJ/kg).
            - h_mains: specific enthalpy of the mains flow that will be introduced into the field in the case that vapor is generated inside the collectors (kJ/kg).
            - rad: solar radiation reaching the solar field ( kJ / ( hr * m^2 ) )
            - T_amb: ambient temperature (°C)

        Returns a dictionary with the following keys:
            - 'h_out': specific enthalpy of the flow leaving the tank (kJ/kg)
            - 'Q_useful': useful energy delivered to the flow (i.e. all energy which is not used to generate vapor) (kJ/hr)
            - 'Q_waste': wasted energy which is used to generate vapor inside the collectors (kJ/hr)
            - 'm_vap': mass flow of vapor being released from the field. (kg/hr)
            - 'iterations': number of iterations that were necessary to achieve convergence between the introduced mains flow and the vapor flow being released (no units)
            - 'maxIt': boolean value which is True if the maximum number of allowed iterations was reached without achieving convergence.
        '''
        rad_first_row = rad
        rad_other_rows = rad
        m_in_rows = m_in_field/self.coll_rows
        h_out_first_row, Q_waste_first_row, m_waste_first_row, it_first_row, maxIt_first_row = self.h_out_row(m_in_rows, h_in_field, h_mains, rad_first_row, T_amb)
        h_out_other_rows, Q_waste_other_rows, m_waste_other_rows, it_other_rows, maxIt_other_rows = self.h_out_row(m_in_rows, h_in_field, h_mains, rad_other_rows, T_amb)
        h_out_field = (h_out_first_row + (self.coll_rows - 1)*h_out_other_rows)/self.coll_rows
        Q_waste = Q_waste_first_row + (self.coll_rows - 1)*Q_waste_other_rows
        Q_useful = m_in_field*(h_out_field - h_in_field)
        m_waste = m_waste_first_row + m_waste_other_rows
        it = it_first_row + it_other_rows
        maxIt = maxIt_first_row or maxIt_other_rows
        return {'h_out': h_out_field,
                'm_out': m_in_field,
                'Q_useful': Q_useful,
                'Q_waste': Q_waste,
                'm_vap': m_waste,
                'iterations': it,
                'maxIt': maxIt}