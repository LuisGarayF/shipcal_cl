#!/usr/bin/env python
# coding: utf-8



import numpy as np
import pandas as pd
import pvlib as pv
from scipy import interpolate
import datetime
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def corr_exp_solar(FILENAME=f'{BASE_DIR}\Simulacion\DHTMY_SAM_E_9H23YU.csv'):

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
    DATA=pd.read_csv(FILENAME,nrows=1)
    latitude=DATA.iloc[0][5]
    longitude=DATA.iloc[0][6]
    UTC=-DATA.iloc[0][7]

    # get meteorological variables
    DATA=pd.read_csv(FILENAME,header=2)
    GHI=DATA['GHI'].values
    DHI=DATA['DHI'].values


    # get cloud coverage variabilty
    # load coordinate matrices, X=LONG;Y=LAT

    XCF=pd.read_csv(f'{BASE_DIR}\Simulacion\XCF.csv').values
    YCF=pd.read_csv(f'{BASE_DIR}\Simulacion\YCF.csv').values

    # load cloud coverage variability layer
    CF=pd.read_csv(f'{BASE_DIR}\Simulacion\CF.csv').values

    # calculate by interpolation the effective variability of cloud coverage
    # for the target location

    # Se reajustan las dimensiones de las matrices a arreglos de una dimensión
    YCF=YCF.reshape(-1)
    XCF=XCF.reshape(-1)
    CF=np.array([CF.reshape(-1)]).T

    # Se crea un arreglo de dos dimensiones donde cada entrada incluye latitud y longitud
    XYCF=np.vstack((YCF,XCF)).T

    # Se realiza una interpolación 
    CFSTD=interpolate.griddata(XYCF, CF,(latitude,longitude),method='nearest')

    # Calculate solar geometry
    tz = f'Etc/GMT+{UTC}'
    times = pd.date_range('2021-01-01 00:00:00', '2022-01-01', closed='left',
                          freq='H', tz=tz)
    solpos = pv.solarposition.ephemeris(times, latitude, longitude)
    elevationangle=solpos['elevation']


    ast=solpos['solar_time']


    # Extraterrestrial irradiance
    epsilon=pv.solarposition.pyephem_earthsun_distance(times)
    Io=np.maximum(0,1367*epsilon*np.sin(elevationangle*np.pi/180))


    # Calculate clearness index and diffuse fraction

    GHI=np.minimum(Io,GHI) #% limit GHI to under Io
    Kt=GHI/Io
    Kt[np.where(Io<=0)[0]]=0
    DHI=np.minimum(DHI,GHI)# limit DHI to under GHI
    K=np.minimum(1,DHI/GHI)
    K[np.where(GHI<=0)[0]]=1
    K[np.where(Io<=0)[0]]=1

    # Load coefficients for BRL predictor generation

    P=[[275.614845282659  ,-84.0341464533378  ,-1.86015047743254   ],
       [-123.987004786273 ,44.2818520840966   ,6.59582239895984    ],
       [-5.10707452673121 ,1.72451283166942   ,-0.163934905299144  ],
       [-1.06584246650315 ,0.243994275140034  ,-0.0184549284117407 ],
       [-81.5719886815895 ,20.4764911164922   ,2.22797398848424    ],
       [26.9296725403115  ,-6.13579726686233  ,0.360110809734099   ]]

    # Calculate BRL predictors

    B=[]
    for i in range(0,6):
        B.append(P[i][0]*CFSTD**2+P[i][1]*CFSTD+P[i][2])

    #Apply BRL model
    # Calculate persistence

    per=[]
    UTCc=0

    for counter in range(len(Kt)):
        if counter>=1 and counter<=(len(Kt)-2):
            if elevationangle[counter-1]<=0 and elevationangle[counter]>0:
                per.append(Kt[counter+1-UTCc])

            elif elevationangle[counter-1]>0 and elevationangle[counter]<=0:
                per.append(Kt[counter-1-UTCc])

            else:
                per.append(0.5*(Kt[counter+1-UTCc]+Kt[counter-1-UTCc]))

        else:
            per.append(0)


    per=np.array(per)

    # Calculate daily KT
    KT=sum(GHI.values.reshape(24,int(len(GHI)/24)))/sum(Io.values.reshape(24,int(len(Io)/24)))
    KT_aux=[]
    for i in range(len(KT)):
        KT_aux.append(KT[i]*np.ones([24,1]))
    KT_aux=np.array(KT_aux)
    KT=KT_aux.reshape(-1)


    #Apply model
    Kbrl=(1/(1+np.exp(B[0]+B[1]*Kt+B[2]*ast+B[3]*elevationangle+B[4]*KT+B[5]*per)))

    # Reconstruct irradiance
    DHIbrl=Kbrl*Kt*Io # DHI by BRL reconstruction
    DNIbrl=(GHI-DHIbrl)/np.sin(elevationangle*np.pi/180) # % DNI by BRL reconstruction
    DNIbrl[np.where(elevationangle<=1)[0]]=0 # for very low solar elevations, make DNI=0 and GHI=DHI
    DHIbrl[np.where(elevationangle<=1)[0]]=GHI[np.where(elevationangle<=1)[0]]

    DATA['DNI']=DNIbrl.values
    DATA['DHI']=DHIbrl.values
    
    return latitude,longitude,UTC,DATA




def Irradiance_2(latitude,longitude,UTC,DATA,tilt=35,azimuth=354,albedo=0.2): 
    
    '''
    Función que calcula la irradiancia total sobre un plano inclinado con intervalo horario 
    a lo largo de un año. La función utiliza funciones de la librería pvlib para calcular 
    independientemente: Radiación directa, radiación difusa y radiación reflejada en
    el suelo por sobre una superficie inclinada. Posteriormente, se entrega un vector de 8760*1,
    donde cada componente es la suma de las tres radiaciones mencionadas anteriormente por hora.
    
    Parámetros:
    ----------
        -latitude : Latitud en grados. Positivo para el norte del ecuador, negativo para el sur. 
        -longitude: Longitud en grados. Positivo para el este del meridiano cero, negativo para el oeste.
        -UTC      : UTC de la zona horaria a analizar.
        -GHI      : 
        -DNI      :
        -DHI      : Vector de irradiacia difusa, W/m2
        -tilt     : Ángulo de inclinación de la superficie a analizar con respecto a la horizontal, °
        -azimuth  : Azimut de la superficie a analizar, °
        -albedo   : Albedo de la superficie que se desea analizar.
        
    Outputs:
    --------
        -Vector de 8760*1 donde se entrega la irradiancia total sobre el plano inclinado, W/m2
        
    '''
    GHI=DATA['GHI'].values
    DNI=DATA['DNI'].values
    DHI=DATA['DHI'].values
    
    tz = f'Etc/GMT+{UTC}'  #Se establece la zona horaria por medio de UTC
    
    times = pd.date_range('2021-01-01 00:00:00', '2022-01-01', closed='left',freq='H', tz=tz) # Se genera un dataframe 
                                                                                              # con con un time-step horario
                                                                                              # de todo un año
    
    solpos = pv.solarposition.ephemeris(times, latitude, longitude) #Se obtiene la posición solar para la locación a analizar
    
    solar_azimuth=solpos['azimuth']           # Vector de azimuth de la posición solar anual, °
    solar_zenith=solpos['zenith']             # Vector de zenith de la posición solar anual, °
    
    diff=pv.irradiance.isotropic(tilt,DHI)                                        # Vector de radiación difusa sobre la superficie inclinada, W/m2
    diff_ground=pv.irradiance.get_ground_diffuse(tilt,GHI,albedo)                 # Vector de radiación difusa reflejada en el suelo en la superficie inclinada, W/m2
    dni=pv.irradiance.beam_component(tilt,azimuth,solar_zenith,solar_azimuth,DNI) # Vector de radiación directa en la superficie inclinada, W/m2
    
    return dni,diff,diff_ground
