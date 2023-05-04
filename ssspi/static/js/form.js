/* Lógica de formulario en el DOM */


// Inicializador de selects
document.addEventListener('DOMContentLoaded', function() {
    var elems = document.querySelectorAll('select');
    var instances = M.FormSelect.init(elems);
    var modals = document.querySelectorAll('.modal');
    var instances = M.Modal.init(modals);
    
    /* Listener de tabla */

    document.querySelector('#tabla_colectores tbody').addEventListener('click', (e) => {

        let table = new DataTable('#tabla_colectores');   
        let data = table.row(e.target).data();
        //console.log(data[2], data[3], data[4], data[5]);
        $area.value = parseFloat(data[2].replace(",", "."));
        coef_per_lineales.value = parseFloat(data[3].replace(",", "."));
        eficiencia_optica.value = parseFloat(data[4].replace(",", "."));
        coef_per_cuadraticas.value = 0;
        iam.value = parseFloat(data[5].replace(",", "."));
        iam_longitudinal.value = 0;
        

    });

    // Parametros colector

    toogle_switch = document.getElementById('toogle_switch');
    toogle_switch.addEventListener('change', (e)=> {
        
        let t = document.getElementById("tabla_cs");
        let m = document.getElementById("i_manual");
        if (e.target.checked == true) {
            //Selección por ingreso manual
            t.style.display = "none";
            m.style.display = "block";
        }
        else {
            //Selección de ingreso por tabla
            t.style.display = "block";
            m.style.display = "none";
        }
    });

});
      
// Inputs

let $area = document.getElementById('id_area_apertura');// Area de apertura de colector
let $col_b = document.getElementById('id_col_bat');// Colectores por bateria
let $cant_bat = document.getElementById('id_cantidad_bat');// Cantidad de baterias
let sup_col = document.getElementById('id_sup_colectores'); // Superficie colectores
let tot_col = document.getElementById('id_total_colectores'); // Total de colectores

let demanda_anual = document.querySelector('#id_demanda_anual');



// Inputs Temperaturas //
let t_red = document.getElementById('id_temperatura_red'); // Input temperatura desde la red
let temp_retorno = document.getElementById('id_temperatura_retorno'); // Input temperatura de retorno

// Temperatura por mes //
let t_ene = document.getElementById('id_t_enero');
let t_feb = document.getElementById('id_t_febrero');
let t_mar = document.getElementById('id_t_marzo');
let t_abr = document.getElementById('id_t_abril');
let t_may = document.getElementById('id_t_mayo');
let t_jun = document.getElementById('id_t_junio');
let t_jul = document.getElementById('id_t_julio');
let t_ago = document.getElementById('id_t_agosto');
let t_sep = document.getElementById('id_t_septiembre');
let t_oct = document.getElementById('id_t_octubre');
let t_nov = document.getElementById('id_t_noviembre');
let t_dic = document.getElementById('id_t_diciembre');

// Demanda por mes //

const demanda_enero = document.getElementById('id_demanda_enero');
const demanda_febrero = document.getElementById('id_demanda_febrero');
const demanda_marzo = document.getElementById('id_demanda_marzo');
const demanda_abril = document.getElementById('id_demanda_abril');
const demanda_mayo = document.getElementById('id_demanda_mayo');
const demanda_julio = document.getElementById('id_demanda_julio');
const demanda_junio = document.getElementById('id_demanda_junio');
const demanda_agosto = document.getElementById('id_demanda_agosto');
const demanda_septiembre = document.getElementById('id_demanda_septiembre');
const demanda_octubre = document.getElementById('id_demanda_octubre');
const demanda_noviembre = document.getElementById('id_demanda_noviembre');
const demanda_diciembre = document.getElementById('id_demanda_diciembre');

// Demanda Semanal ///

const d_lunes_res = document.getElementById('d_lunes_res');
const d_martes_res = document.getElementById('d_martes_res');
const d_miercoles_res = document.getElementById('d_miercoles_res');
const d_jueves_res = document.getElementById('d_jueves_res');
const d_viernes_res = document.getElementById('d_viernes_res');
const d_sabado_res = document.getElementById('d_sabado_res');
const d_domingo_res = document.getElementById('d_domingo_res');

// Layout CSS

let rango_flujo_prueba = document.getElementById('id_rango_flujo_prueba');
let coef_per_lineales = document.getElementById('id_coef_per_lineales');
let coef_per_cuadraticas = document.getElementById('id_coef_per_cuadraticas');
let iam = document.getElementById('id_iam');
let iam_longitudinal = document.getElementById('id_iam_longitudinal');
let total_colectores = document.getElementById('id_total_colectores');
let tipo_fluido = document.getElementById('id_tipo_fluido');
let eficiencia_optica = document.getElementById('id_eficiencia_optica');

// Otros


let tabla_colectores = document.getElementById('tabla_colectores');
let btn_simular = document.getElementById('btn_simular');

// Contenedores //

const colector = document.getElementById('colector');                        // Contenedor de inputs colectores
let temp_container = document.getElementById('temperaturas');                // Contenedor principal de las temperaturas
let t_entrada = document.getElementById('t_entrada');                        // Contenedor de temperatura de entrada desde la red
let t_retorno = document.getElementById('t_retorno');                        // Contenedor con la temperatura de entrada desde el retorno del proceso   
let t_retorno_cte = document.getElementById('t_retorno_cte');                // Contenedor con la temperatura de retorno constante anual  
let t_retorno_variable = document.getElementById('t_retorno_variable');      // Contenedor con las temperatura de retorno variable mensual
let cont_ident = document.getElementById('cont_ident');                      // Contenedor identificación
let cont_ubica = document.getElementById('cont_ubica');                      // Contenedor ubicación 
let cont_demanda_mensual = document.getElementById('cont_demanda_mensual');  // Contenedor de la demanda mensual
let cont_layout = document.getElementById('cont_layout');                    // Contenedor la layout del campo solar
let cont_perfil_de = document.getElementById('cont_perfil_de');              // Contenedor perfil demanda semanal y diaria
let cont_param_caldera = document.getElementById('cont_param_caldera');      // Contenedor parametros de la caldera
let cont_almacenamiento = document.getElementById('cont_almacenamiento');    // Contenedor almacenamiento
let cont_param_financiero = document.getElementById('cont_param_financiero');// Contenedor parametros financieros

//-----------------------//
//       Resumen         //
//-----------------------//

// Boton de simular //

btn_simular.addEventListener('click', (e)=>{
    console.log('Simulando...');
});

// Campo Resumen Demandas //

//const d_anual_res = document.getElementById('d_anual_res'); //Demanda anual

// Demandas Mensuales //

const d_enero_res = document.getElementById('d_enero_res');
const d_febrero_res = document.getElementById('d_febrero_res');
const d_marzo_res = document.getElementById('d_marzo_res');
const d_abril_res = document.getElementById('d_abril_res');
const d_mayo_res = document.getElementById('d_mayo_res');
const d_junio_res = document.getElementById('d_junio_res');
const d_julio_res = document.getElementById('d_julio_res');
const d_agosto_res = document.getElementById('d_agosto_res');
const d_septiembre_res = document.getElementById('d_septiembre_res');
const d_octubre_res = document.getElementById('d_octubre_res');
const d_noviembre_res = document.getElementById('d_noviembre_res');
const d_diciembre_res = document.getElementById('d_diciembre_res');
const unidad_demanda_res = document.getElementById('unidad_demanda_res'); // Unidad de demanda

// Resumen Temperaturas //

const t_entrada_res = document.getElementById('t_entrada_res'); //Temperatura de entrada desde la red
const t_anual_res = document.getElementById('t_anual_res'); // Temperatura Constante

// Temperatura variable //

const t_enero_res = document.getElementById('t_enero_res');
const t_febrero_res = document.getElementById('t_febrero_res');
const t_marzo_res = document.getElementById('t_marzo_res');
const t_abril_res = document.getElementById('t_abril_res');
const t_mayo_res = document.getElementById('t_mayo_res');
const t_junio_res = document.getElementById('t_junio_res');
const t_julio_res = document.getElementById('t_julio_res');
const t_agosto_res = document.getElementById('t_agosto_res');
const t_septiembre_res = document.getElementById('t_septiembre_res');
const t_octubre_res = document.getElementById('t_octubre_res');
const t_noviembre_res = document.getElementById('t_noviembre_res');
const t_diciembre_res = document.getElementById('t_diciembre_res');

const t_red_res = document.getElementById('t_entrada_res');// Temperatura de entrada desde la red

// Campo resumen perfil de demanda

const combustible_res = document.getElementById('combustible_res');
const ini_jornada_res = document.getElementById('ini_res');
const term_jornada_res = document.getElementById('term_res');


const area_apertura_res = document.getElementById('area_apertura_res');
const eficiencia_optica_res = document.getElementById('eficiencia_optica_res');
const rango_flujo_prueba_res = document.getElementById('rango_flujo_prueba_res');
const coef_per_lineales_res = document.getElementById('coef_per_lineales_res');
const coef_per_cuadraticas_res = document.getElementById('coef_per_cuadraticas_res');
const iam_res = document.getElementById('iam_res');
const iam_longi_res = document.getElementById('iam_longi_res');
const col_bat_res = document.getElementById('col_bat_res');
const cant_bat_res = document.getElementById('cant_bat_res');
const total_colectores_res = document.getElementById('total_colectores_res');
const sup_colectores_res = document.getElementById('sup_colectores_res');
const inclinacion_res = document.getElementById('inclinacion_res');
const azimut_res = document.getElementById('azimut_res');
const flujo_masico_res = document.getElementById('flujo_masico_res');
const unidad_flujo_masico_res = document.getElementById('unidad_flujo_masico_res');
const fluido_res = document.getElementById('fluido_res');
const potencia_res = document.getElementById('potencia_res');
const unidad_potencia_res = document.getElementById('unidad_potencia_res');
const presion_res = document.getElementById('presion_res');
const unidad_presion_res = document.getElementById('unidad_presion_res');
const tipo_caldera_res = document.getElementById('tipo_caldera_res');
const eficiencia_res = document.getElementById('eficiencia_res');
const volumen_res = document.getElementById('volumen_res');
const relacion_aspecto_res = document.getElementById('relacion_aspecto_res');
const material_almacenamiento_res = document.getElementById('material_almacenamiento_res');
const material_aislacion_res = document.getElementById('material_aislacion_res');
const espesor_res = document.getElementById('espesor_res');
const efectividad_res = document.getElementById('efectividad_res');
const costo_combustible_res = document.getElementById('costo_combustible_res');
const unidad_costo_combustible_res = document.getElementById('unidad_costo_combustible_res');
const precio_colector_res = document.getElementById('precio_colector_res');
const costo_tanque_res = document.getElementById('costo_tanque_res');
const balance_res = document.getElementById('balance_res');
const instalacion_res = document.getElementById('instalacion_res');
const operacion_res = document.getElementById('operacion_res');
const impuesto_res = document.getElementById('impuesto_res');
const descuento_res = document.getElementById('descuento_res');
const inflacion_res = document.getElementById('inflacion_res');


/* Cálculo Superficie estimada y total de colectores */

function handleInputChange(e) {
    if (e.target && e.target.tagName === 'INPUT') {
        if (['id_area_apertura', 'id_col_bat', 'id_cantidad_bat'].includes(e.target.id)) {
            
            const area = parseFloat($area.value);
            const colectoresPorBateria = parseFloat($col_b.value);
            const numBaterias = parseFloat($cant_bat.value);

            calc_sup_tcol(area, colectoresPorBateria, numBaterias);
        }
    }
}

colector.addEventListener('change', handleInputChange);

function calc_sup_tcol(area, colectoresPorBateria, numBaterias) {
    try {
        
        area = area || 0;
        colectoresPorBateria = colectoresPorBateria || 0;
        numBaterias = numBaterias || 0;

        const superficie = parseFloat((area * colectoresPorBateria * numBaterias * 1.3).toFixed(3));
        const totalColectores = colectoresPorBateria * numBaterias;

        
        sup_col.value = superficie;
        tot_col.value = totalColectores;
        sup_colectores_res.innerHTML = superficie;
        total_colectores_res.innerText = totalColectores;
    } catch (e) {
        
        console.error('Error al calcular la superficie y el total de colectores:', e);
    }
}


document.querySelector('.final-step').addEventListener('click', updateSummary);

function updateSummary() {
    const nombreSimulacion = document.querySelector('#id_nombre_simulacion').value;
    const sector = document.querySelector('#id_sector option:checked').textContent;
    const aplicacion = document.querySelector('#id_aplicacion option:checked').textContent;
    const ubicacion = document.querySelector('#id_nombre_ubicacion option:checked').textContent;
    const latitud = document.querySelector('#id_latitud').value;
    const longitud = document.querySelector('#id_longitud').value;
    const combustible = document.querySelector('#id_combustible');
    const unidad_demanda = document.querySelector('#id_unidad_demanda');
    const ini_jornada = document.querySelector('#id_ini_jornada');
    const term_jornada = document.querySelector('#id_term_jornada');
    const potencia_caldera = document.querySelector('#id_potencia_caldera');
    const presion_caldera = document.querySelector('#id_presion_caldera');
    const tipo_caldera = document.querySelector('#id_tipo_caldera');
    const eficiencia_caldera = document.querySelector('#id_eficiencia_caldera');
    const unidad_potencia = document.querySelector('#id_unidad_potencia');
    const unidad_presion = document.querySelector('#id_unidad_presion');
    const temperatura_salida = document.querySelector('#id_t_salida');
    const efectividad = document.querySelector('#id_efectividad');
    const esquema = document.querySelector('input[name="esquema"]:checked').parentNode.textContent.trim().split(':')[0];
    const siglasEsquema = document.querySelector('input[name="esquema"]:checked').parentNode.querySelector('.tooltipped').getAttribute('data-tooltip');
    const imagenEsquema = document.querySelector('input[name="esquema"]:checked').parentNode.nextElementSibling.querySelector('img').getAttribute('src');
    const area_apertura = document.querySelector('#id_area_apertura');
    const flujo_prueba = document.querySelector('#id_rango_flujo_prueba');
    const eficiencia_optica = document.querySelector('#id_eficiencia_optica');
    const coef_per_lineales = document.querySelector('#id_coef_per_lineales');
    const coef_per_cuadraticas = document.querySelector('#id_coef_per_cuadraticas');
    const iam = document.querySelector('#id_iam');
    const iam_longitudinal = document.querySelector('#id_iam_longitudinal');
    const inclinacion_col = document.querySelector('#id_inclinacion_col');
    const azimut = document.querySelector('#id_azimut');
    const flujo_masico = document.querySelector('#id_flujo_masico');
    const unidad_flujo_masico = document.querySelector('#id_unidad_flujo_masico');
    const tipo_fluido = document.querySelector('#id_tipo_fluido');
    const volumen = document.querySelector('#id_volumen');
    const relacion_aspecto = document.querySelector('#id_relacion_aspecto');
    const material_almacenamiento = document.querySelector('#id_material_almacenamiento');
    const espesor = document.querySelector('#id_espesor_aislante');
    const material_aislacion = document.querySelector('#id_material_aislamiento');
    const costo_combustible = document.querySelector('#id_costo_combustible');
    const precio_colector = document.querySelector('#id_precio_colector');
    const unidad_costo_combustible = document.querySelector('#id_unidad_costo_combustible');
    const costo_tanque = document.querySelector('#id_costo_tanque');
    const balance = document.querySelector('#id_balance');
    const instalacion = document.querySelector('#id_instalacion');
    const operacion = document.querySelector('#id_operacion');
    const impuesto = document.querySelector('#id_impuesto');
    const descuento = document.querySelector('#id_descuento');
    const inflacion = document.querySelector('#id_inflacion');

    document.querySelector('#nomb_sim_res').textContent = nombreSimulacion;
    document.querySelector('#sector_res').textContent = sector;
    document.querySelector('#aplicacion_res').textContent = aplicacion;
    //document.querySelector('#ubicacion_res').textContent = ubicacion;
    document.querySelector('#latitud_res').textContent = latitud;
    document.querySelector('#longitud_res').textContent = longitud;
    document.querySelector('#combustible_res').textContent = combustible.value;
    document.querySelector('#unidad_demanda_res').textContent = unidad_demanda.value;
    document.querySelector('#ini_jornada_res').textContent = ini_jornada.value;
    document.querySelector('#term_jornada_res').textContent = term_jornada.value;
    document.querySelector('#potencia_res').textContent = potencia_caldera.value;
    document.querySelector('#presion_res').textContent = presion_caldera.value;
    document.querySelector('#tipo_caldera_res').textContent = tipo_caldera.value;
    document.querySelector('#eficiencia_res').textContent = eficiencia_caldera.value;
    document.querySelector('#unidad_potencia_res').textContent = unidad_potencia.value;
    document.querySelector('#unidad_presion_res').textContent = unidad_presion.value;
    document.querySelector('#t_salida_res').textContent = temperatura_salida.value;
    document.querySelector('#efectividad_res').textContent = efectividad.value;
    document.querySelector('#esquema_res').textContent = esquema;
    document.querySelector('#siglas_esquema_res').textContent = siglasEsquema;
    document.querySelector('#imagen_esquema_res').innerHTML = `<img src="${imagenEsquema}" class="w-100 h-100" alt="${esquema}">`;
    document.querySelector('#flujo_prueba_res').textContent = flujo_prueba.value;
    document.querySelector('#area_apertura_res').textContent = area_apertura.value;
    document.querySelector('#eficiencia_optica_res').textContent = eficiencia_optica.value;
    document.querySelector('#coef_per_lineales_res').textContent = coef_per_lineales.value;
    document.querySelector('#coef_per_cuadraticas_res').textContent = coef_per_cuadraticas.value;
    document.querySelector('#iam_res').textContent = iam.value;
    document.querySelector('#iam_longi_res').textContent = iam_longitudinal.value;
    document.querySelector('#inclinacion_res').textContent = inclinacion_col.value;
    document.querySelector('#azimut_res').textContent = azimut.value;
    document.querySelector('#flujo_masico_res').textContent = flujo_masico.value;
    document.querySelector('#unidad_flujo_masico_res').textContent = unidad_flujo_masico.value;
    document.querySelector('#fluido_res').textContent = tipo_fluido.value;
    document.querySelector('#volumen_res').textContent = volumen.value;
    document.querySelector('#relacion_aspecto_res').textContent = relacion_aspecto.value;
    document.querySelector('#material_almacenamiento_res').textContent = material_almacenamiento.value;
    document.querySelector('#espesor_res').textContent = espesor.value;
    document.querySelector('#material_aislacion_res').textContent = material_aislacion.value;
    document.querySelector('#costo_combustible_res').textContent = costo_combustible.value;
    document.querySelector('#precio_colector_res').textContent = precio_colector.value;
    document.querySelector('#unidad_costo_combustible_res').textContent = unidad_costo_combustible.value;
    document.querySelector('#costo_tanque_res').textContent = costo_tanque.value;
    document.querySelector('#balance_res').textContent = balance.value;
    document.querySelector('#instalacion_res').textContent = instalacion.value;
    document.querySelector('#operacion_res').textContent = operacion.value;
    document.querySelector('#impuesto_res').textContent = impuesto.value;
    document.querySelector('#descuento_res').textContent = descuento.value;
    document.querySelector('#inflacion_res').textContent = inflacion.value;
}


// Lógica de las temperaturas

// Temperatura circuito abierto o cerrado


switch_temperatura.addEventListener('change', (e)=> {

    if (e.target.checked == true) {
        //Circuito Cerrado
        t_entrada.style.display = "none";
        t_retorno.style.display = "block";
        t_retorno_variable.style.display = "block";
        
    }
    else {
        //Circuito Abierto
        t_entrada.style.display = "block";
        t_retorno.style.display = "none";
        t_retorno_variable.style.display = "none";
    }

});

// Temperaturas en circuito Cerrado constante anual o variable mensual

// crear listener por contenedor y aplicar las funciones de abajo

switch_retorno.addEventListener('change', (e)=> {

    if (e.target.checked == true) {
        //Variable mensual
        t_retorno_cte.style.display = "none";
        t_retorno_variable.style.display = "block"; // Se solicito modificar de esta forma
        t_ene.removeAttribute('readonly');
        t_feb.removeAttribute('readonly');
        t_mar.removeAttribute('readonly');
        t_abr.removeAttribute('readonly');
        t_may.removeAttribute('readonly');
        t_jun.removeAttribute('readonly');
        t_jul.removeAttribute('readonly');
        t_ago.removeAttribute('readonly');
        t_sep.removeAttribute('readonly');
        t_oct.removeAttribute('readonly');
        t_nov.removeAttribute('readonly');
        t_dic.removeAttribute('readonly');
        $V = true;
    }
    else {
        //Constante anual
        t_retorno_cte.style.display = "block";
        t_retorno_variable.style.display = "none";
        t_ene.readOnly = "true";
        t_feb.readOnly = "true";
        t_mar.readOnly = "true";
        t_abr.readOnly = "true";
        t_may.readOnly = "true";
        t_jun.readOnly = "true";
        t_jul.readOnly = "true";
        t_ago.readOnly = "true";
        t_sep.readOnly = "true";
        t_oct.readOnly = "true";
        t_nov.readOnly = "true";
        t_dic.readOnly = "true";
       $V = false;
    }
    return $V;
});


// Corrección entre temperaturas constantes y VARIABLES

temp_retorno.addEventListener('change', (e) => {
    const temperatura = e.target.value;
    
    t_anual_res.textContent = temperatura;
  
    [t_ene, t_feb, t_mar, t_abr, t_may, t_jun, t_jul, t_ago, t_sep, t_oct, t_nov, t_dic].forEach(el => el.value = temperatura);
  
    const meses = {
      'Enero': t_enero_res,
      'Febrero': t_febrero_res,
      'Marzo': t_marzo_res,
      'Abril': t_abril_res,
      'Mayo': t_mayo_res,
      'Junio': t_junio_res,
      'Julio': t_julio_res,
      'Agosto': t_agosto_res,
      'Septiembre': t_septiembre_res,
      'Octubre': t_octubre_res,
      'Noviembre': t_noviembre_res,
      'Diciembre': t_diciembre_res,
    };
  
    for (const mes in meses) {
      meses[mes].textContent = temperatura;
    }
});
          

t_retorno_variable.addEventListener('change',(e) => {
    if (e.target && e.target.tagName === 'INPUT'){
        if (e.target.id == 'id_t_enero'){
            return t_enero_res.textContent = e.target.value;
        }
        if (e.target.id == 'id_t_febrero'){
            return t_febrero_res.textContent = e.target.value;
        }
        if (e.target.id == 'id_t_marzo'){
            return t_marzo_res.textContent = e.target.value;
        }
        if (e.target.id == 'id_t_abril'){
            return t_abril_res.textContent = e.target.value;
        }
        if (e.target.id == 'id_t_mayo'){
            return t_mayo_res.textContent = e.target.value;
        }
        if (e.target.id == 'id_t_junio'){
            return t_junio_res.textContent = e.target.value;
        }
        if (e.target.id == 'id_t_julio'){
            return t_julio_res.textContent = e.target.value;
        }
        if (e.target.id == 'id_t_agosto'){
            return t_agosto_res.textContent = e.target.value;
        }
        if (e.target.id == 'id_t_septiembre'){
            return t_septiembre_res.textContent = e.target.value;
        }
        if (e.target.id == 'id_t_octubre'){
            return t_octubre_res.textContent = e.target.value;
        }
        if (e.target.id == 'id_t_noviembre'){
            return t_noviembre_res.textContent = e.target.value;
        }
        if (e.target.id == 'id_t_diciembre'){
            return t_diciembre_res.textContent = e.target.value;
        }
    }
});


/* Cálculo Demanda Anual  y Renderización de resultados*/

let demanda_mes = [];

cont_demanda_mensual.addEventListener('change', (e)=> {
    
    if (e.target && e.target.tagName === 'INPUT'){
        
        if (e.target.id == 'id_demanda_enero'){
            let d_enero = parseFloat(demanda_enero.value); //Valor demanda enero
            d_enero_res.innerText = demanda_enero.value;
            demanda_mes.push(d_enero);
        }
        if (e.target.id == 'id_demanda_febrero'){
            let d_febrero = parseFloat(demanda_febrero.value); //Valor demanda febrero
            d_febrero_res.innerText = demanda_febrero.value;
            demanda_mes.push(d_febrero);
        }
        if (e.target.id == 'id_demanda_marzo'){
            let d_marzo = parseFloat(demanda_marzo.value); //Valor demanda marzo
            d_marzo_res.innerText = demanda_marzo.value;
            demanda_mes.push(d_marzo);
        }
        if (e.target.id == 'id_demanda_abril'){
            let d_abril = parseFloat(demanda_abril.value); //Valor demanda abril
            d_abril_res.innerText = demanda_abril.value;
            demanda_mes.push(d_abril);
        }
        if (e.target.id == 'id_demanda_mayo'){
            let d_mayo = parseFloat(demanda_mayo.value); //Valor demanda mayo
            d_mayo_res.innerText = demanda_mayo.value;
            demanda_mes.push(d_mayo);
        }
        if (e.target.id == 'id_demanda_junio'){
            let d_junio = parseFloat(demanda_junio.value); //Valor demanda junio
            d_junio_res.innerText = demanda_junio.value;
            demanda_mes.push(d_junio);
        }
        if (e.target.id == 'id_demanda_julio'){
            let d_julio = parseFloat(demanda_julio.value); //Valor demanda julio
            d_julio_res.innerText = demanda_julio.value;
            demanda_mes.push(d_julio);
        }
        if (e.target.id == 'id_demanda_agosto'){
            let d_agosto = parseFloat(demanda_agosto.value); //Valor demanda agosto
            d_agosto_res.innerText = demanda_agosto.value;
            demanda_mes.push(d_agosto);
        }
        if (e.target.id == 'id_demanda_septiembre'){
            let d_septiembre = parseFloat(demanda_septiembre.value); //Valor demanda septiembre
            d_septiembre_res.innerText = demanda_septiembre.value;
            demanda_mes.push(d_septiembre);
        }
        if (e.target.id == 'id_demanda_octubre'){
            let d_octubre = parseFloat(demanda_octubre.value); //Valor demanda octubre
            d_octubre_res.innerText = demanda_octubre.value;
            demanda_mes.push(d_octubre);
        }
        if (e.target.id == 'id_demanda_noviembre'){
            let d_noviembre = parseFloat(demanda_noviembre.value); //Valor demanda noviembre
            d_noviembre_res.innerText = demanda_noviembre.value;
            demanda_mes.push(d_noviembre);
        }
        if (e.target.id == 'id_demanda_diciembre'){
            let d_diciembre = parseFloat(demanda_diciembre.value); //Valor demanda diciembre
            d_diciembre_res.innerText = demanda_diciembre.value;
            demanda_mes.push(d_diciembre);
        }
        calculo_demanda_anual(demanda_mes);
    }
});

function calculo_demanda_anual(demanda_mes) {
    try {                      
        d_anual = 0; // Sumatoria de demandas inicializada en 0
        demanda_mes.forEach(function(a){d_anual +=a;});
        
        return  ((demanda_anual.value = d_anual),(d_anual_res.innerText = d_anual));
    } catch (e) {     
        console.log(e.message);  
    }
}


// Ubicacion

function ubicacionPredefinida() {
    const select = document.getElementById("ubicaciones");
    const selectedValue = select.options[select.selectedIndex].value;
    const url = "{% url 'cargar_mapa' %}";
    const csrf_token = document.getElementsByName("csrfmiddlewaretoken")[0].value;
  
    const data = {
      csrfmiddlewaretoken: csrf_token,
      ubicacion: selectedValue,
    };
  
    fetch(url, {
      method: "POST",
      headers: {
        "Content-type": "application/json",
        "X-CSRFToken": csrf_token,
      },
      body: JSON.stringify(data),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.result) {
          const latitud = parseFloat(data.latitud);
          const longitud = parseFloat(data.longitud);
          const latLng = new google.maps.LatLng(latitud, longitud);
          map.setCenter(latLng);
          marker.setPosition(latLng);
          document.getElementById("id_latitud").value = latitud.toFixed(2);
          document.getElementById("id_longitud").value = longitud.toFixed(2);
        } else {
          alert("Error al cargar la ubicación predefinida.");
        }
      })
      .catch((error) => console.error(error));
  }
  

cont_ubica.addEventListener('change', (e)=> {
    //console.log(e.target.tagName);
    //console.log(e.target.value);
    if (e.target && e.target.tagName === 'INPUT'){
        
        if (e.target.id == 'id_latitud'){
            //console.log(e.target.value);
            return (latitud_res.value = e.target.value);
        }
        if (e.target.id == 'id_longitud'){
           // console.log(e.target.value);
            return (longitud_res.value = e.target.value);
        }   
    }
    if (e.target && e.target.tagName === 'SELECT'){
        if (e.target.id == 'id_nombre_ubicacion'){
            if (e.target.value === 'predefinida') { // Si se selecciona la opción "Predefinida"
                ubicacionPredefinida(); // Llama a la función para mostrar la ubicación predefinida *
            } else {
                return (ubicacion_res.value = e.target.value);
            }
        }
    }
});


// Layout campo solar

cont_layout.addEventListener('change', (e)=> {
    //console.log(e.target);
    if (e.target && e.target.tagName === 'INPUT'){
 
        if (e.target.id == 'id_cant_bat'){
            cant_bat_res.innerText = e.target.value;
        }
        if (e.target.id == 'id_col_bat'){
            col_bat_res.innerHTML = e.target.value;
        }
        if (e.target.id == 'id_total_colectores'){
            total_colectores_res.innerText = e.target.value;// verificar si esto lo deja en cero
        }
        if (e.target.id == 'id_cantidad_bat'){
            cant_bat_res.innerText = e.target.value;
        }
        //aca
    }
});


// Perfil demanda semanal y diaria

const diasSemana = {
    'id_demanda_lun': d_lunes_res,
    'id_demanda_mar': d_martes_res,
    'id_demanda_mie': d_miercoles_res,
    'id_demanda_jue': d_jueves_res,
    'id_demanda_vie': d_viernes_res,
    'id_demanda_sab': d_sabado_res,
    'id_demanda_dom': d_domingo_res,
  };
  
  // Comprobar el estado inicial de los checkboxes
  for (const checkboxId in diasSemana) {
    const checkbox = document.querySelector(`#${checkboxId}`);
    const elementoResumen = diasSemana[checkboxId];
  
    if (checkbox.checked) {
      elementoResumen.innerHTML = 'Si';
    } else {
      elementoResumen.innerHTML = 'No';
    }
  }
  
  // Agregar el listener de cambio a los checkboxes
  cont_perfil_de.addEventListener('change', (e) => {
    const checkboxId = e.target.id;
    const checkboxChecked = e.target.checked;
  
    if (diasSemana.hasOwnProperty(checkboxId)) {
      const elementoResumen = diasSemana[checkboxId];
  
      if (checkboxChecked) {
        elementoResumen.innerHTML = 'Si';
      } else {
        elementoResumen.innerHTML = 'No';
      }
    }
  });


/* Descargar Resumen */

async function downloadResume() {

    const pdfModal = M.Modal.init(document.getElementById('pdfModal'));
    pdfModal.open();
    const resumen = document.querySelector('.resumen');
    const clone = resumen.cloneNode(true);
    clone.style.width = resumen.scrollWidth + 'px';
    clone.style.height = resumen.scrollHeight + 'px';
    clone.style.position = 'absolute';
    clone.style.left = '-9999px';
    clone.style.overflow = 'visible';
    document.body.appendChild(clone);
  
    // Copia estilos
    const styles = Array.from(document.querySelectorAll('link[rel="stylesheet"], style'));
    styles.forEach((style) => {
      if (style.tagName === 'LINK') {
        const newLink = document.createElement('link');
        newLink.href = style.href;
        newLink.rel = 'stylesheet';
        clone.appendChild(newLink);
      } else {
        const newStyle = document.createElement('style');
        newStyle.innerHTML = `
        .page-break {
          display: block;
          page-break-before: always;
        }
        .step-actions {
          display: none;
        }
        .marginTop {
            margin-top: 250px;
          }
        `;
        clone.appendChild(newStyle);
      }

    });



  
    const options = {
      scale: 2,
      width: clone.scrollWidth,
      height: clone.scrollHeight,
      windowWidth: clone.scrollWidth,
      windowHeight: clone.scrollHeight,
      scrollY: 0,
      scrollX: 0,
      useCORS: true,
    };
  
    await new Promise((resolve) => setTimeout(resolve, 1000));
    html2canvas(clone, options).then((canvas) => {
      document.body.removeChild(clone);
      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF('p', 'mm', 'a4');
      const imgProps = pdf.getImageProperties(imgData);
      const pdfWidth = pdf.internal.pageSize.getWidth() - 20; // Resta 20 para agregar un margen
      const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;
      const pageHeight = pdf.internal.pageSize.getHeight() - 20; // Resta 20 para agregar un margen inferior
  
      let currentPage = 1;
      let yPos = 10;
  
      while (yPos < pdfHeight) {
        const cropHeight = pageHeight * (imgProps.width / pdfWidth);
        const croppedCanvas = document.createElement('canvas');
        croppedCanvas.width = imgProps.width;
        croppedCanvas.height = cropHeight;
        croppedCanvas.getContext('2d').drawImage(canvas, 0, (pageHeight * (currentPage - 1)) * (imgProps.width / pdfWidth), imgProps.width, cropHeight, 0, 0, imgProps.width, cropHeight);
  
        const croppedImgData = croppedCanvas.toDataURL('image/png');
  
        pdf.addImage(croppedImgData, 'PNG', 10, yPos - (pageHeight * (currentPage - 1)), pdfWidth, pageHeight);
  
        yPos += pageHeight;
  
        if (yPos < pdfHeight) {
          pdf.addPage();
          currentPage++;
        }
      }
      
      pdf.save('Resumen.pdf');
      pdfModal.close();
    });
  }
  
  
  
    
  



