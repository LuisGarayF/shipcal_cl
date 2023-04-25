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

const combustible = document.getElementById('id_combustible');
const unidad_demanda = document.getElementById('id_unidad_demanda');
const ini_jornada = document.getElementById('id_ini_jornada');
const term_jornada = document.getElementById('id_term_jornada');

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

let t_salida = document.getElementById('id_t_salida');
let efectividad = document.getElementById('id_efectividad');
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

// Resumen campo perfil de demanda

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

/* Cálculo Superficie estimada y total de colectores */

colector.addEventListener('change', (e)=> {
    if (e.target && e.target.tagName === 'INPUT'){
        
        if ((e.target.id == 'id_area_apertura') || (e.target.id == 'id_col_bat') || (e.target.id == 'id_cantidad_bat')){
            
            let area = parseFloat($area.value); //Area Apertura
            let colb = parseFloat($col_b.value); //Colectores por bateria
            let cbat = parseFloat($cant_bat.value); //n° baterias*/
            
            calc_sup_tcol(area,colb,cbat);
        }
    }
});

function calc_sup_tcol(area,colb,cbat) {
    try {

        let a = area || 0;
        let b = colb || 0;
        let c = cbat || 0;       
        superficie = a * b * c * 1.3 ; // Superficie Estimada = Area Apertura x n° baterias x Colectores por bateria x 1.3
        total = b * c ; // Total de colectores = n° baterias x Colectores por bateria

        return  (sup_col.value = superficie), (tot_col.value = total), (sup_colectores_res.innerHTML = superficie), (total_colectores_res.innerText = total);//ver por que retorna cero
    } catch (e) {       
    }
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

/*id_temperatura_red.addEventListener('change', (e) => {
    return t_entrada_res.innerText = e.target.value;
});*/
        
temp_retorno.addEventListener('change', (e)=> {
    t_anual_res.innerText = e.target.value; // Arroja la temperatura anual
    return ((t_ene.value = e.target.value ),(t_feb.value = e.target.value),(t_mar.value = e.target.value),(t_abr.value = e.target.value),(t_may.value = e.target.value),
            (t_jun.value = e.target.value),(t_jul.value = e.target.value),(t_ago.value = e.target.value),(t_sep.value = e.target.value),(t_oct.value = e.target.value),
            (t_nov.value = e.target.value),(t_dic.value = e.target.value), (t_enero_res.textContent = e.target.value),(t_febrero_res.textContent = e.target.value),
            (t_marzo_res.textContent = e.target.value),(t_abril_res.textContent = e.target.value),(t_mayo_res.textContent = e.target.value),(t_junio_res.textContent = e.target.value),
            (t_julio_res.innerHTML = e.target.value),(t_agosto_res.innerHTML = e.target.value),(t_septiembre_res.innerHTML = e.target.value),(t_octubre_res.innerHTML = e.target.value),
            (t_noviembre_res.innerHTML = e.target.value),(t_diciembre_res.innerHTML = e.target.value));
});

// Temperatura variable

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

// Temperatura salida

t_salida.addEventListener('change', (e) =>{
    return t_salida_res.textContent = e.target.value;
});


// Listener de campo Esquema de Integración

esq_int.addEventListener('change', (e)=> {
    let sigla_esq = document.getElementById("id_siglas_esquema");
    let siglas_ocultas = document.getElementById("siglas_ocultas");

    console.log(e.target.checked);
    console.log(e.target.tagName);
    console.log(e.target.value);
    if (e.target && e.target.tagName === 'INPUT'){

        console.log(siglas_ocultas.value);
        return (siglas_ocultas.value = sigla_esq.value);
        
    }
    else {
        
    }

});

/* Cálculo Demanda Anual  y Renderización de resultados*/

let demanda_mes = [];

cont_demanda_mensual.addEventListener('change', (e)=> {
    
    if (e.target && e.target.tagName === 'INPUT'){
        
        if (e.target.id == 'id_demanda_enero'){
            let d_enero = parseFloat(demanda_enero.value); //Valor demanda enero
            //d_enero_res.innerText = demanda_enero.value;
            demanda_mes.push(d_enero);
        }
        if (e.target.id == 'id_demanda_febrero'){
            let d_febrero = parseFloat(demanda_febrero.value); //Valor demanda febrero
            //d_febrero_res.innerText = demanda_febrero.value;
            demanda_mes.push(d_febrero);
        }
        if (e.target.id == 'id_demanda_marzo'){
            let d_marzo = parseFloat(demanda_marzo.value); //Valor demanda marzo
            //d_marzo_res.innerText = demanda_marzo.value;
            demanda_mes.push(d_marzo);
        }
        if (e.target.id == 'id_demanda_abril'){
            let d_abril = parseFloat(demanda_abril.value); //Valor demanda abril
            //d_abril_res.innerText = demanda_abril.value;
            demanda_mes.push(d_abril);
        }
        if (e.target.id == 'id_demanda_mayo'){
            let d_mayo = parseFloat(demanda_mayo.value); //Valor demanda mayo
            //d_mayo_res.innerText = demanda_mayo.value;
            demanda_mes.push(d_mayo);
        }
        if (e.target.id == 'id_demanda_junio'){
            let d_junio = parseFloat(demanda_junio.value); //Valor demanda junio
            //d_junio_res.innerText = demanda_junio.value;
            demanda_mes.push(d_junio);
        }
        if (e.target.id == 'id_demanda_julio'){
            let d_julio = parseFloat(demanda_julio.value); //Valor demanda julio
            //d_julio_res.innerText = demanda_julio.value;
            demanda_mes.push(d_julio);
        }
        if (e.target.id == 'id_demanda_agosto'){
            let d_agosto = parseFloat(demanda_agosto.value); //Valor demanda agosto
            //d_agosto_res.innerText = demanda_agosto.value;
            demanda_mes.push(d_agosto);
        }
        if (e.target.id == 'id_demanda_septiembre'){
            let d_septiembre = parseFloat(demanda_septiembre.value); //Valor demanda septiembre
            //d_septiembre_res.innerText = demanda_septiembre.value;
            demanda_mes.push(d_septiembre);
        }
        if (e.target.id == 'id_demanda_octubre'){
            let d_octubre = parseFloat(demanda_octubre.value); //Valor demanda octubre
            //d_octubre_res.innerText = demanda_octubre.value;
            demanda_mes.push(d_octubre);
        }
        if (e.target.id == 'id_demanda_noviembre'){
            let d_noviembre = parseFloat(demanda_noviembre.value); //Valor demanda noviembre
            //d_noviembre_res.innerText = demanda_noviembre.value;
            demanda_mes.push(d_noviembre);
        }
        if (e.target.id == 'id_demanda_diciembre'){
            let d_diciembre = parseFloat(demanda_diciembre.value); //Valor demanda diciembre
            //d_diciembre_res.innerText = demanda_diciembre.value;
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
    console.log(e.target.tagName);
    console.log(e.target.value);
    if (e.target && e.target.tagName === 'INPUT'){
        
        if (e.target.id == 'id_latitud'){
            console.log(e.target.value);
            return (latitud_res.value = e.target.value);
        }
        if (e.target.id == 'id_longitud'){
            console.log(e.target.value);
            return (longitud_res.value = e.target.value);
        }   
    }
    if (e.target && e.target.tagName === 'SELECT'){
        if (e.target.id == 'id_nombre_ubicacion'){
            if (e.target.value === 'predefinida') { // Si se selecciona la opción "Predefinida"
                ubicacionPredefinida(); // Llama a la función para mostrar la ubicación predefinida
            } else {
                return (ubicacion_res.value = e.target.value);
            }
        }
    }
});

// Campo solar

colector.addEventListener('change', (e)=> {
    
    if (e.target && e.target.tagName === 'INPUT'){
 
        if (e.target.id == 'id_area_apertura'){
            area_apertura_res.innerText = e.target.value;
        }
        if (e.target.id == 'id_eficiencia_optica'){
            eficiencia_optica_res.innerHTML = e.target.value;
        }
        if (e.target.id == 'id_rango_flujo_prueba'){
            rango_flujo_prueba_res.innerText = e.target.value;
        }
        if (e.target.id == 'id_coef_per_lineales'){
            coef_per_lineales_res.innerText = e.target.value;
        }
        if (e.target.id == 'id_coef_per_cuadraticas'){
            coef_per_cuadraticas_res.innerText = e.target.value;
        }
        if (e.target.id == 'id_iam'){
            iam_res.innerText = e.target.value;
        }
        if (e.target.id == 'id_iam_longitudinal'){
            iam_longi_res.innerText = e.target.value;
        }
    }
});

// Layout campo solar

cont_layout.addEventListener('change', (e)=> {
    console.log(e.target);
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
        if (e.target.id == 'id_inclinacion_col'){
            inclinacion_res.innerText = e.target.value;
        }
        if (e.target.id == 'id_azimut'){
            azimut_res.innerText = e.target.value;
        }
        if (e.target.id == 'id_flujo_masico'){
            flujo_masico_res.innerText = e.target.value;
        }
        if (e.target.id == 'id_unidad_flujo_masico'){
            unidad_flujo_masico_res.innerText = e.target.value;
        }
    }
    if (e.target && e.target.tagName === 'SELECT'){

        if (e.target.id == 'id_tipo_fluido'){
            console.log(e.target.value);
            fluido_res.innerText = e.target.value;
        }
    }
});


// Perfil demanda semanal y diaria

cont_perfil_de.addEventListener('change', (e) => {

    if (e.target && e.target.type === 'checkbox') {

        if ((e.target.id == 'id_demanda_lun')&&(e.target.checked)){
            if (e.target.value == 'on'){
                return (d_lunes_res.innerHTML = 'Si');    
            }
            else{
                return (d_lunes_res.innerHTML = 'No');    
            }   
        }
        if ((e.target.id == 'id_demanda_mar')&&(e.target.checked)){
            if (e.target.checked){
                return (d_martes_res.innerHTML = 'Si');    
            }
            else{
                return (d_martes_res.innerHTML = 'No');    
            }   
        }
        if ((e.target.id == 'id_demanda_mie')&&(e.target.checked)){
            if (e.target.value == 'on'){
                return (d_miercoles_res.innerHTML = 'Si');    
            }
            else{
                return (d_miercoles_res.innerHTML = 'No');    
            }   
        }
        if ((e.target.id == 'id_demanda_jue')&&(e.target.checked)){
            if (e.target.value == 'on'){
                return (d_jueves_res.innerHTML = 'Si');    
            }
            else{
                return (d_jueves_res.innerHTML = 'No');    
            }   
        }
        if ((e.target.id == 'id_demanda_vie')&&(e.target.checked)){
            if (e.target.value == 'on'){
                return (d_viernes_res.innerHTML = 'Si');    
            }
            else{
                return (d_viernes_res.innerHTML = 'No');    
            }   
        }
        if ((e.target.id == 'id_demanda_sab')&&(e.target.checked)){
            if (e.target.value == 'on'){
                return (d_sabado_res.innerHTML = 'Si');    
            }
            else{
                return (d_sabado_res.innerHTML = 'No');    
            }   
        }
        if ((e.target.id == 'id_demanda_dom')&&(e.target.checked)){
            if (e.target.value == 'on'){
                return (d_domingo_res.innerHTML = 'Si');    
            }
            else{
                return (d_domingo_res.innerHTML = 'No');    
            }   
        }
    }    
    if (e.target && e.target.tagName === 'SELECT'){
        if (e.target.id == 'id_combustible'){
            console.log(e.target.value);
            return (combustible_res.value = e.target.value);
        }

    }
 
});

// Parametros caldera

cont_param_caldera.addEventListener('change', (e)=>{
    if (e.target && e.target.tagName === 'INPUT'){
 
        if (e.target.id == 'id_potencia_caldera'){
            potencia_res.innerText = e.target.value;
        }
        if (e.target.id == 'id_presion_caldera'){
            presion_res.innerText = e.target.value;
        }
        if (e.target.id == 'id_eficiencia_caldera'){
            eficiencia_res.innerText = e.target.value;
        }
    }
    if (e.target && e.target.tagName === 'SELECT'){

        if (e.target.id == 'id_unidad_potencia'){
            unidad_potencia_res.innerText = e.target.value;
        }
        if (e.target.id == 'id_unidad_presion'){
            unidad_presion_res.innerText = e.target.value;
        }
        if (e.target.id == 'id_tipo_caldera'){
            tipo_caldera_res.innerText = e.target.value;
        }
    }
});

cont_almacenamiento.addEventListener('change',(e)=>{
    if (e.target && e.target.tagName === 'INPUT'){
        if (e.target.id == 'id_volumen'){
            volumen_res.innerText = e.target.value;
        }
        if (e.target.id == 'id_espesor_aislante'){
            espesor_res.innerText = e.target.value;
        }
    }
    if (e.target && e.target.tagName === 'SELECT'){
        if (e.target.id == 'id_relacion_aspecto'){
            relacion_aspecto_res.innerText = e.target.value;
        }
        if (e.target.id == 'id_material_almacenamiento'){
            material_almacenamiento_res.innerText = e.target.value;
        }
        if (e.target.id == 'id_material_aislamiento'){
            material_aislacion_res.innerText = e.target.value;
        }
    }
});

efectividad.addEventListener('change', (e)=>{
    return efectividad_res.innerText = e.target.value;
});

cont_param_financiero.addEventListener('change', (e)=>{
    if (e.target && e.target.tagName === 'INPUT'){
        if (e.target.id == 'id_costo_combustible'){
            costo_combustible_res.innerText = e.target.value;
        }
        if (e.target.id == 'id_precio_colector'){
            precio_colector_res.innerText = e.target.value;
        }
    }
    if (e.target && e.target.tagName === 'SELECT'){
        if (e.target.id == 'id_unidad_costo_combustible'){
            unidad_costo_combustible_res.innerText = e.target.value;
        }
    }
});

