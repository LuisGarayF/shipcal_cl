# -*- coding: utf-8 -*-
"""
Created on Wed Sep 28 17:08:53 2022

@author: Adrian
"""

from math import pi, exp, log


class Storage_Tank:
    '''
    Modelo computacional para un tanque cilíndrico vertical, en el cual se tiene en cuenta la estratificación de temperaturas.
    La estratificación se aproxima dividiendo el tanque en nodos, uno sobre otro, de igual volumen. Dentro de un nodo la temperatura se asume uniforme.
    Los flujos que entran y salen se simulan a través de dos "pares entrada-salida". La entrada y la salida de un mismo par tienen el mismo flujo en todo momento, de manera que se mantiene el volumen de agua dentro del estanque.
    El tanque tiene además 
    
    Parámetros de inicialización:
        - volume: volumen del tanque en m^3
        - AR: relación de aspecto (altura/diámetro)
        - top_loss_coeff: coeficiente de pérdidas térmicas en la cara superior del tanque
        - edge_loss_coeff: coeficiente de pérdidas térmicas en la pared lateral del tanque
        - bottom_loss_coeff: coeficiente de pérdidas térmicas en la cara inferior del tanque
        - N_nodes: número de nodos en los que se separará el tanque
        - inlet_1_node: nodo donde se encuentra ubicada la entrada del primer par entrada-salida.
        - outlet_1_node: nodo donde se encuentra ubicada la salida del primer par entrada-salida.
        - inlet_2_node: nodo donde se encuentra ubicada la entrada del segundo par entrada-salida.
        - outlet_2_node: nodo donde se encuentra ubicada la salida del segundo par entrada-salida.
        - HX1_eff
        - HX2_eff
        - HX1_top_node: primer nodo (siendo el nodo 1 el de más arriba) donde se encuentra el intercambiador de calor 1 (se asume que el nodo es "atravesado" por el intercambiador de calor a lo largo de toda su altura)
        - HX1_bottom_node: último nodo (siendo el nodo 1 el de más arriba) donde se encuentra el intercambiador de calor 1 (se asume que el nodo es "atravesado" por el intercambiador de calor a lo largo de toda su altura)
        - HX2_top_node: primer nodo (siendo el nodo 1 el de más arriba) donde se encuentra el intercambiador de calor 2 (se asume que el nodo es "atravesado" por el intercambiador de calor a lo largo de toda su altura)
        - HX2_bottom_node: último nodo (siendo el nodo 1 el de más arriba) donde se encuentra el intercambiador de calor 2 (se asume que el nodo es "atravesado" por el intercambiador de calor a lo largo de toda su altura)
        - fluid_props: Objeto de la clase "Properties" que define las características del fluido contenido en el estanque (se asume que dicho fluido es agua)
        - HX1_props: Objeto de la clase "Properties" que define las características del fluido que pasa por el intercambiador de calor 1
        - HX2_props: Objeto de la clase "Properties" que define las características del fluido que pasa por el intercambiador de calor 2
        - initial_temperatures: Temperaturas iniciales de los nodos. Debe ser un diccionario de la forma: {1: T1, 2: T2, 3: T3, ......, N: TN} donde Ti representa la temperatura inicial del nodo i, y N es la cantidad total de nodos en el tanque. Los nodos se cuentan desde arriba hacia abajo partiendo por 1
        - tolerance: Discrepancia máxima entre iteraciones sucesivas para considerar que se alcanzó la convergencia y, por lo tanto, entregar un resultado.
        - max_iterations: Número de iteraciones máximas antes de "abortar" búsqueda de la convergencia y entregar el último resultado iterado
        
    Atributos (ver lista de parámetros de inicialización para los atributos sin descripción)
        - cross_Area: área transversal del tanque
        - N_nodes
        - node_temperatures: temperaturas de los nodos determinadas en el time-step anterior de la simulación. Se inicializa con el parámetro de inicialización "initial_temperatures", y tiene el mismo formato para guardar la información.
        - top_loss_coeff
        - edge_loss_coeff 
        - bottom_loss_coeff 
        - node_height: altura de cada nodo
        - nodal_edge_area: área lateral de cada nodo (es decir, el área de pérdida de calor a través de la pared lateral del tanque para un solo nodo)
        - node_volume: volumen individual de cada nodo
        - inlets_and_outlets: diccionario de la forma: {'inlet_1': inlet_1_node, 'outlet_1': outlet_1_node, 'inlet_2': inlet_2_node, 'outlet_2': outlet_2_node}, donde cada valor es el número del nodo donde se encuentra la entrada/salida correspondiente. Los nodos se cuentan desde arriba, partiendo de 1.
        - HX1_top_node
        - HX1_bottom_node
        - HX1_partial_eff: efectividad de cada "porción" del intercambiador de calor 1 que pasa por un nodo individual.
        - HX1_props
        - HX2_top_node
        - HX2_bottom_node
        - HX2_partial_eff: efectividad de cada "porción" del intercambiador de calor 2 que pasa por un nodo individual.
        - HX2_props
        - fluid_props
        - fluid_spec_heat: calor específico del fluido contenido en el tanque
        - fluid_thermal_conductivity: conductividad térmica del fluido contenido en el tanque
        - node_thermal_capacity: capacidad calórica de cada nodo del tanque
        - max_iterations
        - tolerance
        - new_temperatures: Diccionario con el mismo formato que el diccionario "self.node_temperatures". Este diccionario se usa para almacenar provisionalmente las temperaturas de cada nodo determinadas en la última iteración del sistema completo. Sólo cuando las "outputs" e "inputs" de los elementos simulados convergen, se actualiza el atributo "self.node_temperatures" del tanque usando este atributo
    
    Métodos (funciones):
        - convergence: evalúa si los resultados de dos iteraciones sucesivas cumplen el criterio de convergencia.
        - mix_nodes: Función que mezcla los nodos del tanque cuando sus temperaturas resultantes al final del time-step son tales que la temperatura de un nodo es mayor a la temperatura del nodo que está por encima.
        - iteration: ejecuta una iteración para determinar las temperaturas de los nodos al final del time-step y las temperaturas promedio durante el time-step.
        - compute_outputs: ejecuta varias veces la función "iteration" hasta lograr el criterio de convergencia entre iteraciones sucesivas.
        - update_temperature: actualiza el diccionario "self.node_temperatures" usando el diccionario "self.new_temperatures". Esto debiese hacerse una vez que se logró la convergencia en el resto del sistema simulado.
    '''
    def __init__(self, volume, AR, top_loss_coeff, edge_loss_coeff, bottom_loss_coeff, N_nodes,
                 inlet_1_node, outlet_1_node, inlet_2_node, outlet_2_node,
                 HX1_eff, HX2_eff, HX1_top_node, HX1_bottom_node, HX2_top_node, HX2_bottom_node,
                 fluid_props, HX1_props, HX2_props, initial_temperatures,
                 tolerance = 1e-8, max_iterations = 100):
        diameter = (4*volume/(pi*AR))**(1/3)
        height = diameter*AR
        radius = diameter/2
        self.cross_Area = pi*radius**2
        self.N_nodes = N_nodes ## number of nodes
        self.node_temperatures = initial_temperatures
        self.top_loss_coeff = top_loss_coeff ## loss coefficient at the top
        self.edge_loss_coeff = edge_loss_coeff ## loss coefficient at the edge
        self.bottom_loss_coeff = bottom_loss_coeff ## loss coefficient at the bottom
        self.node_height = height/N_nodes ## height of each node
        self.nodal_edge_area = 2*pi*radius*self.node_height ## lateral area of each node
        self.node_volume = volume/N_nodes ## volume of each node
        ## self.inlets_and_outlets: dictionary to register the nodes where the inlets and outlets are
        if inlet_1_node != None:
            assert (inlet_1_node >= 1 and inlet_1_node <= N_nodes and
                    outlet_1_node >= 1 and outlet_1_node <= N_nodes)
        if inlet_2_node != None:
            assert (inlet_2_node >= 1 and inlet_2_node <= N_nodes and
                    outlet_2_node >= 1 and outlet_2_node <= N_nodes)
        self.inlets_and_outlets = {'inlet_1': inlet_1_node, 'outlet_1': outlet_1_node,
                                   'inlet_2': inlet_2_node, 'outlet_2': outlet_2_node}
        if HX1_top_node != None:
            assert (HX1_top_node >= 1 and HX1_top_node <= N_nodes and
                    HX1_bottom_node >= 1 and HX1_bottom_node <= N_nodes)
            self.HX1_top_node = HX1_top_node
            self.HX1_bottom_node = HX1_bottom_node
            L_HX1 = -log(1 - HX1_eff)
            self.HX1_partial_eff = 1 - exp(-L_HX1/(HX1_bottom_node - HX1_top_node + 1))
            self.HX1_props = HX1_props
        if HX2_top_node != None:
            assert (HX2_top_node >= 1 and HX2_top_node <= N_nodes and
                    HX2_bottom_node >= 1 and HX2_bottom_node <= N_nodes)
            self.HX2_top_node = HX2_top_node
            self.HX2_bottom_node = HX2_bottom_node
            L_HX2 = -log(1 - HX2_eff)
            self.HX2_partial_eff = 1 - exp(-L_HX2/(HX2_bottom_node - HX2_top_node + 1))
            self.HX2_props = HX2_props
        self.fluid_props = fluid_props
        self.fluid_spec_heat = self.fluid_props.fluid_spec_heat
        self.fluid_thermal_conductivity = self.fluid_props.fluid_thermal_conductivity
        self.node_thermal_capacity = self.node_volume*self.fluid_props.fluid_density*self.fluid_spec_heat
        self.max_iterations = max_iterations
        self.tolerance = tolerance
    ## convergence: Function that tests the convergence considering successive
    ## iterations of the tank.
    ## Parameters:
    ##      - dict1: dictionary with temperatures of the previous iteration
    ##      - dict2: dictionary with temperatures of the current iteration
    ##      - tolerance: number to define how small the difference between the iterations can be
    def convergence(self, dict1, dict2):
        '''
        Función que evalúa los resultados de dos iteraciones sucesivas y determina si se logró la convergencia.
        
        Parámetros:
            - dict1 : diccionario con temperaturas calculadas en la iteración anterior (temperatura promedio durante el time-step y temperatura al final del time-step, en °C).
            - dict2 : diccionario con temperaturas calculadas en la última iteración (temperatura promedio durante el time-step y temperatura al final del time-step, en °C).
        
        Retorna:
            - Valor Booleano: "True" si se alcancó la convergencia, "False" en caso contrario
        '''
        assert len(dict1) == len(dict2)
        N_nodes = len(dict1)
        List1 = [ abs((dict1[i]['T_ave'] -
                       dict2[i]['T_ave'])/(dict1[i]['T_ave']+273.15)) < self.tolerance
                 for i in range(1, N_nodes+1) ]
        List2 = [ abs((dict1[i]['T_final'] -
                       dict2[i]['T_final'])/(dict1[i]['T_final']+273.15)) < self.tolerance
                 for i in range(1, N_nodes+1) ]
        return all(List1) and all(List2)
    ## self.mix_nodes: function that mixes the nodes that are unstable. I.e. when some node is hotter than the node above it,
    ## this function mixes those nodes. The process is repeated until there is no instabilities.
    def mix_nodes(self, dict1):
        '''
        Función que mezcla los nodos del tanque si las temperaturas al final del time-step presentan una "inestabilidad". Se llama "inestabilidad" al hecho de que cierto nodo tenga una temperatura mayor a la temperatura del nodo que está por encima de él.
        
        El proceso de mezcla se realiza considerando las temperaturas al final del time-step; es instantáneo y adiabático. Las "outputs" que entrega el tanque son luego del proceso de mezcla.
        
        Parámetros:
           Un diccionario retornado por la función "iteration", con el formato: {1: {'T_ave': T_ave_1, 'T_final': T_final_1}, 2: {'T_ave': T_ave_2, 'T_final': T_final_2}, ... , N: {'T_ave': T_ave_N, 'T_final': T_final_N} } (ver la descripción del diccionario retornado por la función iteration para más detalles)
        
        Retorna:
            Un diccionario con el mismo formato que el diccionario recibido como parámetro, pero con las "T_final" actualizadas. Los valores de "T_ave" no se modifican.
        '''
        mixed_nodes = [ {'original_node_numbers': [i], 'T_final': dict1[i]['T_final'],
                         'mass':1} for i in dict1 ]
        while True:
            List1 = [ mixed_nodes[i]['T_final'] >= mixed_nodes[i+1]['T_final'] for i in range(len(mixed_nodes) - 1) ]
            if all(List1):
                break
            for i in range(len(mixed_nodes) - 1):
                if mixed_nodes[i]['T_final'] < mixed_nodes[i+1]['T_final']:
                    total_mass = mixed_nodes[i]['mass'] + mixed_nodes[i+1]['mass']
                    T_final = ((mixed_nodes[i]['mass']/total_mass)*mixed_nodes[i]['T_final'] +
                               (mixed_nodes[i+1]['mass']/total_mass)*mixed_nodes[i+1]['T_final'])
                    nodes_list = mixed_nodes[i]['original_node_numbers'] + mixed_nodes[i+1]['original_node_numbers']
                    mixed_nodes[i] = {'original_node_numbers': nodes_list, 'T_final': T_final,
                                      'mass': total_mass}
                    mixed_nodes.pop(i+1)
                    break
        R1 = {}
        for i in range(len(mixed_nodes)):
            for node_number in mixed_nodes[i]['original_node_numbers']:
                R1[node_number] = {'T_ave': dict1[node_number]['T_ave'], 'T_final': mixed_nodes[i]['T_final']}
        return R1
    ## self.iteration: it executes a single iteration to determine the temperatures of the nodes at the end of
    ## the time step and the average temperatures during the time step
    ## It usually must be called more than one time to converge to definitve outputs given a certain input.
    def iteration(self, inlet_1_flow_rate, inlet_1_T, inlet_2_flow_rate, inlet_2_T,
                  HX1_flow_rate, HX1_inlet_h, HX2_flow_rate, HX2_inlet_h,
                  T_amb, previous_result, time_step):
        '''
        Función que realiza una iteración individual para encontrar las outputs del tanque como función de las inputs y de sus condiciones internas (es decir, las temperaturas de cada nodo)

        Parámetros:
            - inlet_1_flow_rate: flujo másico en la entrada 1 (kg/hr)
            - inlet_1_T: temperatura del flujo en la entrada 1 (°C)
            - inlet_2_flow_rate: flujo másico en la entrada 2 (kg/hr)
            - inlet_2_T: 
            - HX1_flow_rate: 
            - HX1_inlet_h: 
            - HX2_flow_rate: 
            - HX2_inlet_h: 
            - T_amb: 
            - previous_result: 
            - time_step: 

        Retorns:
            A dictionary with the following format: {1: {'T_ave': T_ave_1, 'T_final': T_final_1}, 2: {'T_ave': T_ave_2, 'T_final': T_final_2}, ... , N: {'T_ave': T_ave_N, 'T_final': T_final_N} }
            where N is the number of nodes, T_ave_i is the average temperature of the i-th node during the time step, and T_final_i is the temperature of that node at the end of the time step 
        '''
        Sol = {}
        if HX1_inlet_h != None:
            HX1_T_in = {}
            HX1_T_out = {}
            T_in = self.HX1_props.h_to_T(HX1_inlet_h)
            for i in range(self.HX1_top_node, self.HX1_bottom_node + 1):
                T_out = T_in - self.HX1_partial_eff*(T_in - previous_result[i]['T_ave'])
                HX1_T_in[i] = T_in
                HX1_T_out[i] = T_out
                T_in = T_out
        if HX2_inlet_h != None:
            HX2_T_in = {}
            HX2_T_out = {}
            T_in = self.HX2_props.h_to_T(HX2_inlet_h)
            for i in range(self.HX2_top_node, self.HX2_bottom_node + 1):
                T_out = T_in - self.HX2_partial_eff*(T_in - previous_result[i]['T_ave'])
                HX2_T_in[i] = T_in
                HX2_T_out[i] = T_out
                T_in = T_out
        for i in range(1, self.N_nodes + 1):
            ## values of a and b are computed, according to the mathematical reference of type 158 of TRNSYS
            a = -self.nodal_edge_area*self.edge_loss_coeff
            b = self.nodal_edge_area*self.edge_loss_coeff*T_amb
            ## if the node has inlets or outlets, flow_in and flow_out are updated
            ## this also modifies the values of a and b
            flow_in  = 0
            if self.inlets_and_outlets['inlet_1'] == i:
                flow_in = flow_in + inlet_1_flow_rate
                a = a - inlet_1_flow_rate*self.fluid_spec_heat
                b = b + inlet_1_flow_rate*self.fluid_spec_heat*inlet_1_T
            if self.inlets_and_outlets['inlet_2'] == i:
                flow_in = flow_in + inlet_2_flow_rate
                a = a - inlet_2_flow_rate*self.fluid_spec_heat
                b = b + inlet_2_flow_rate*self.fluid_spec_heat*inlet_2_T
            flow_out = 0 ## flow going out of the node through outlets of the tank
            if self.inlets_and_outlets['outlet_1'] == i:
                flow_out = flow_out + inlet_1_flow_rate
            if self.inlets_and_outlets['outlet_2'] == i:
                flow_out = flow_out + inlet_2_flow_rate
            if HX1_inlet_h != None and i >= self.HX1_top_node and i <= self.HX1_bottom_node:
                if HX1_T_in[i] == self.HX1_props.T_sat:
                    HX1_delta_h = self.HX1_props.h_sat_liq - self.HX1_props.T_to_h(HX1_T_out[i])
                else:
                    HX1_delta_h = self.HX1_props.T_to_h(HX1_T_in[i]) - self.HX1_props.T_to_h(HX1_T_out[i])
                HX1_delta_T = HX1_T_in[i] - HX1_T_out[i]
                if HX1_delta_T != 0:
                    cp = HX1_delta_h/HX1_delta_T
                    a = a - HX1_flow_rate*cp*self.HX1_partial_eff
                    b = b + HX1_flow_rate*cp*self.HX1_partial_eff*HX1_T_in[i]
            if HX2_inlet_h != None and i >= self.HX2_top_node and i <= self.HX2_bottom_node:
                if HX2_T_in[i] == self.HX2_props.T_sat:
                    HX2_delta_h = self.HX2_props.h_sat_liq - self.HX2_props.T_to_h(HX2_T_out[i])
                else:
                    HX2_delta_h = self.HX2_props.T_to_h(HX2_T_in[i]) - self.HX2_props.T_to_h(HX2_T_out[i])
                HX2_delta_T = HX2_T_in[i] - HX2_T_out[i]
                if HX2_delta_T != 0:
                    cp = HX2_delta_h/HX2_delta_T
                    a = a - HX2_flow_rate*cp*self.HX2_partial_eff
                    b = b + HX2_flow_rate*cp*self.HX2_partial_eff*HX2_T_in[i]
            ## Case 1: Top node of the tank
            if i == 1:
                #flow_below = flow coming from the node below (if positive) or going to the node below (if negative)
                flow_below = flow_out - flow_in
                a = a - self.cross_Area*self.top_loss_coeff
                a = a - self.fluid_thermal_conductivity*self.cross_Area/self.node_height
                b = b + self.cross_Area*self.top_loss_coeff*T_amb
                b = b + self.fluid_thermal_conductivity*self.cross_Area*previous_result[i+1]['T_ave']/self.node_height
                if flow_below > 0:
                    a = a - flow_below*self.fluid_spec_heat
                    b = b + flow_below*self.fluid_spec_heat*previous_result[i+1]['T_ave']
                ## flow_above = -flow_below for the next node
                flow_above = -flow_below
            ## Case 2: Bottom node of the tank
            elif i == self.N_nodes:
                a = a - self.cross_Area*self.bottom_loss_coeff
                a = a - self.fluid_thermal_conductivity*self.cross_Area/self.node_height
                b = b + self.cross_Area*self.bottom_loss_coeff*T_amb
                b = b + self.fluid_thermal_conductivity*self.cross_Area*previous_result[i-1]['T_ave']/self.node_height
                ## since this is the bottom node, a warning is printed if 
                ## the flow coming from or going to a node below is larger than zero
                if abs(flow_above + flow_in - flow_out) > 0.0001:
                    print('Warning: A problem has occurred in the internal flow balance of the tank')
                if flow_above > 0:
                    a = a - flow_above*self.fluid_spec_heat
                    b = b + flow_above*self.fluid_spec_heat*previous_result[i-1]['T_ave']
            ## Case 3: Intermediate nodes of the tank
            else:
                ## flow_below corresponds to the flow coming from the node below (if positive)
                ## or going to the node below (if negative)
                ## flow_above has been defined when computing the previous node (node above)
                flow_below = flow_out - flow_in - flow_above
                a = a - 2*self.fluid_thermal_conductivity*self.cross_Area/self.node_height
                b = b + self.fluid_thermal_conductivity*self.cross_Area*previous_result[i+1]['T_ave']/self.node_height
                b = b + self.fluid_thermal_conductivity*self.cross_Area*previous_result[i-1]['T_ave']/self.node_height
                if flow_above > 0:
                    a = a - flow_above*self.fluid_spec_heat
                    b = b + flow_above*self.fluid_spec_heat*previous_result[i-1]['T_ave']
                if flow_below > 0:
                    a = a - flow_below*self.fluid_spec_heat
                    b = b + flow_below*self.fluid_spec_heat*previous_result[i+1]['T_ave']
                ## flow_above = -flow_below for the next node
                flow_above = -flow_below
            a = a/self.node_thermal_capacity
            b = b/self.node_thermal_capacity
            ## T_final: temperature of the node at the end of the time_step
            ## T_ave: average temperature during the time_step.
            T_final = (self.node_temperatures[i]+b/a)*exp(a*time_step)-b/a
            T_ave = (1/(a*time_step))*(self.node_temperatures[i]+b/a)*(exp(a*time_step)-1)-b/a
            Sol[i] = {'T_ave': T_ave, 'T_final': T_final}
        if HX1_inlet_h == None:
            HX1_h_out = None
        else:
            HX1_h_out = self.HX1_props.T_to_h(HX1_T_out[self.HX1_bottom_node])
        if HX2_inlet_h == None:
            HX2_h_out = None
        else:
            HX2_h_out = self.HX2_props.T_to_h(HX2_T_out[self.HX2_bottom_node])
        return Sol, HX1_h_out, HX2_h_out
    ## self.compute_outputs: given the inputs of the tank, this function calls the "iteration" function
    ## until convergence is achieved.
    def compute_outputs(self, inlet_1_flow_rate, inlet_1_h, inlet_2_flow_rate, inlet_2_h,
                        HX1_flow_rate, HX1_inlet_h, HX2_flow_rate, HX2_inlet_h,
                        T_amb, time_step):
        '''
        Function that calls the "iteration" function several times until the temperatures of the nodes reach convergence.
        
        This function computes the outputs of the tank but it does not update the tank temperatures, because the rest of the system must achieve convergence as well before the tank's temperatures are updated.

        Parameters:
            - inlet_1_flow_rate: mass flow through inlet 1 (kg/hr)
            - inlet_1_h: specific enthalpy of the flow entering through inlet 1 (°C)
            - inlet_2_flow_rate: mass flow through inlet 2 (kg/hr)
            - inlet_2_h: specific enthalpy of the flow entering through inlet 2 (°C)
            - T_amb: ambient temperature outside the tank (°C)
            - time_step: length of the time step that is being used (hr)

        Returns:
            a dictionary  with the following keys:
                - 'outlet_1_h': specific enthalpy of the flow leaving the tank through outlet 1
                - 'outlet_2_h': specific enthalpy of the flow leaving the tank through outlet 2
            
            This function also defines a new attribute: self.new_temperatures which is a dictionary to store the temperatures computed, in order to update the self.temperatures attribute of the model once convergence is achieved in the rest of the system. It has the format: {1: T_final_1, 2: T_final_2, .... , N: T_final_N} where T_final_i is the temperature of the i-th node at the end of the time step.
        '''
        ## the tempratures to initialize the iterations are the temperatures of the nodes at the beginning of the time step
        previous_result = {i: {'T_ave':self.node_temperatures[i], 'T_final': self.node_temperatures[i]}
                           for i in range(1, self.N_nodes + 1)}
        inlet_1_T = self.fluid_props.h_to_T(inlet_1_h)
        inlet_2_T = self.fluid_props.h_to_T(inlet_2_h)
        it = 0
        ## loop to call the iteration function
        while True:
            new_result, HX1_h_out, HX2_h_out = self.iteration(inlet_1_flow_rate, inlet_1_T,
                                                              inlet_2_flow_rate, inlet_2_T,
                                                              HX1_flow_rate, HX1_inlet_h,
                                                              HX2_flow_rate, HX2_inlet_h,
                                                              T_amb, previous_result, time_step)
            it = it + 1
            ## when convergence is achieved, the loop is ended
            if self.convergence(previous_result, new_result):
                maxIt = False
                break
            if it == self.max_iterations:
                maxIt = True
                break
            previous_result = new_result
        ## If some node is hotter than the node above it, the nodes are mixed until this problem is solved.
        new_result = self.mix_nodes(new_result)
        T_sat_reached = False
        Q_waste = 0
        for node in new_result:
            if new_result[node]['T_ave'] > self.fluid_props.T_sat:
                new_result[node]['T_ave'] = self.fluid_props.T_sat
                T_sat_reached = True
            if new_result[node]['T_final'] > self.fluid_props.T_sat:
                Q_waste = Q_waste + self.node_thermal_capacity*(new_result[node]['T_final'] - self.fluid_props.T_sat)
                new_result[node]['T_final'] = self.fluid_props.T_sat
                T_sat_reached = True
        ## self.new_temperatures is a provisional dictionary to save the temperatures that the algorithm determined.
        ## This temperatures are set as definitive temperatures of the tank only if the rest of the system has converged as well.
        ## If the inputs to the tank change during the current time step because no convergence has been achieved,
        ## the outputs must be computed again beginning with the temperatures stored in self.node_temperatures
        self.new_temperatures = {i: new_result[i]['T_final'] for i in new_result}
        ## extract outputs from the resulting temperatures
        if self.inlets_and_outlets['outlet_1'] == None:
            outlet_1_T = None
            outlet_1_h = None
        else:
            outlet_1_T = new_result[self.inlets_and_outlets['outlet_1']]['T_ave']
            if outlet_1_T == self.fluid_props.T_sat:
                outlet_1_h = self.fluid_props.h_sat_liq
            else:
                outlet_1_h = self.fluid_props.T_to_h(outlet_1_T)
        if self.inlets_and_outlets['outlet_2'] == None:
            outlet_2_T = None
            outlet_2_h = None
        else:
            outlet_2_T = new_result[self.inlets_and_outlets['outlet_2']]['T_ave']
            if outlet_2_T == self.fluid_props.T_sat:
                outlet_2_h = self.fluid_props.h_sat_liq
            else:
                outlet_2_h = self.fluid_props.T_to_h(outlet_2_T)
        heat_rate_to_demand = inlet_2_flow_rate*self.fluid_spec_heat*(outlet_2_T - inlet_2_T)
        Heat_Loss_Rate = sum([ self.nodal_edge_area*self.edge_loss_coeff*(new_result[i]['T_ave'] - T_amb)
                              for i in new_result])
        Heat_Loss_Rate = Heat_Loss_Rate + self.cross_Area*self.top_loss_coeff*(new_result[1]['T_ave'] - T_amb)
        Heat_Loss_Rate = Heat_Loss_Rate + self.cross_Area*self.bottom_loss_coeff*(new_result[self.N_nodes]['T_ave'] - T_amb)
        if HX1_inlet_h == None:
            HX1_Q = 0
        else:
            HX1_Q = HX1_flow_rate*(HX1_inlet_h - HX1_h_out)
        if HX2_inlet_h == None:
            HX2_Q = 0
        else:
            HX2_Q = HX2_flow_rate*(HX2_inlet_h - HX2_h_out)
        return {'outlet_1_h': outlet_1_h, 'outlet_2_h': outlet_2_h,
                'HX1_outlet_h': HX1_h_out, 'HX2_outlet_h': HX2_h_out, 'HX1_Q': HX1_Q, 'HX2_Q': HX2_Q,
                'Q_demand': heat_rate_to_demand, 'Q_loss': Heat_Loss_Rate, 'Q_waste': Q_waste, 'maxIt': maxIt, 'T_sat_reached':  T_sat_reached}
    ## self.update_temperature: only when confirming that the inputs and ouputs of the whole system have converged,
    ## the temperature of the tank is updated to the value that it previously determined
    def update_temperature(self):
        '''
        Function to update the temperature of the tank according to the last outputs computed, when convergence has been achieved in the whole system.
        
        No parameters, no returns.
        '''
        self.node_temperatures = self.new_temperatures