
## import pvlib library

# In[24]:

import sys
import os
sys.path.append(os.path.abspath('../')) #append the parent directory to the system path
sys.path.append(os.path.abspath('../pvlib')) #append the parent directory to the system path
import pvlib
import pandas as pd 


## Import TMY data

### Use Sandia standard data 

# In[26]:


fname='723650TY.csv' #Use absolute path if the file is not in the local directory
TMY, meta=pvlib.tmy.readtmy3(filename=fname)


# In[6]:

meta['longitude']=-79.2
meta['latitude']=43.42
meta['TZ']=-5
meta['SurfTilt']=30
meta['SurfAz']=0
meta['Albedo']=0.2


# In[7]:

print meta['State']
print meta['longitude']


# Out[7]:

#     NM
#     -79.2
# 

### Define date range of interest for graphing

# In[8]:

month=3
day=26
hour=0
periods=24
freq='H'
rng=pd.date_range(datetime.datetime(year=min(TMY.index.year),month=month,day=day,hour=hour),periods=periods,freq=freq)
rng                


# Out[8]:

#     <class 'pandas.tseries.index.DatetimeIndex'>
#     [1981-03-26 00:00:00, ..., 1981-03-26 23:00:00]
#     Length: 24, Freq: H, Timezone: None

## Get solar angles

# In[9]:

import pvl_ephemeris
reload(pvl_ephemeris)
#Using Ephemeris Calculations
TMY['SunAz'],TMY['SunEl'],TMY['ApparentSunEl'],TMY['SolarTime'], TMY['SunZen']=pvl_ephemeris.pvl_ephemeris(Time=TMY.index,Location=meta)
#Using NRELS SPA Calculations
import pvl_spa
reload (pvl_spa)
TMY['SunAz_spa'],TMY['SunEl_spa'],TMY['SunZen_spa']=pvl_spa.pvl_spa(Time=TMY.index,Location=meta)



# In[10]:

clf()
plot(TMY.index,TMY.SunAz)
plot(TMY.index,TMY.SunAz_spa)
plot(TMY.index,TMY.SunEl,label='eph')
plot(TMY.index,TMY.SunEl_spa,label='spa')
legend()


# Out[10]:

#     <matplotlib.legend.Legend at 0x107e16ad0>

## Calculate Extraterrestrial Irradiaion and AirMass

# In[11]:


TMY['HExtra']=pvlib.pvl_extraradiation(doy=TMY.index.dayofyear)

TMY['AM']=pvlib.pvl_relativeairmass(z=TMY.SunZen)


## Generate Clear Sky and DNI

# In[12]:


DFOut=pvlib.pvl_disc(Time=TMY.index,GHI=TMY.GHI, SunZen=TMY.SunZen)

TMY['DNI_gen_DISC']=DFOut['DNI_gen_DISC']
TMY['Kt_gen_DISC']=DFOut['Kt_gen_DISC']
TMY['AM']=DFOut['AM']
TMY['Ztemp']=DFOut['Ztemp']


## Plane Transformation

# In[13]:


TMY['In_Plane_SkyDiffuse']=pvlib.pvl_perez(SurfTilt=meta['SurfTilt'],
                                            SurfAz=meta['SurfAz'],
                                            DHI=TMY.DHI,
                                            DNI=TMY.DNI,
                                            HExtra=TMY.HExtra,
                                            SunZen=TMY.SunZen,
                                            SunAz=TMY.SunAz,
                                            AM=TMY.AM)


## Ground Diffuse reflection

# In[14]:


TMY['GR']=pvlib.pvl_grounddiffuse(GHI=TMY.GHI,Albedo=meta['Albedo'],SurfTilt=meta['SurfTilt'])


## Get AOI

# In[15]:


TMY['AOI']=pvlib.pvl_getaoi(SunAz=TMY.SunAz,SunZen=TMY.SunZen,SurfTilt=meta['SurfTilt'],SurfAz=meta['SurfAz'])


## Calculate Global in-plane

# In[16]:


TMY['E'],TMY['Eb'],TMY['EDiff']=pvlib.pvl_globalinplane(AOI=TMY.AOI,
                                DNI=TMY.DNI,
                                In_Plane_SkyDiffuse=TMY.In_Plane_SkyDiffuse,
                                GR=TMY.GR,
                                SurfTilt=meta['SurfTilt'],
                                SurfAz=meta['SurfAz'])



## Calculate Cell Temperature

# In[17]:


TMY['Tcell'],TMY['Tmodule']=pvlib.pvl_sapmcelltemp(E=TMY.E,
                            Wspd=TMY.Wspd,
                            Tamb=TMY.DryBulb)





## Import module coefficients

# In[18]:


moddb=pvlib.pvl_retreiveSAM(name='SandiaMod')
module=moddb.Canadian_Solar_CS5P_220M___2009_
module


# Out[18]:

#     Vintage                                                   2009
#     Area                                                     1.701
#     Material                                                  c-Si
#     #Series                                                     96
#     #Parallel                                                    1
#     Isco                                                   5.09115
#     Voco                                                   59.2608
#     Impo                                                   4.54629
#     Vmpo                                                   48.3156
#     Aisc                                                  0.000397
#     Aimp                                                  0.000181
#     C0                                                     1.01284
#     C1                                                  -0.0128398
#     Bvoco                                                 -0.21696
#     Mbvoc                                                        0
#     Bvmpo                                                -0.235488
#     Mbvmp                                                        0
#     N                                                       1.4032
#     C2                                                    0.279317
#     C3                                                    -7.24463
#     A0                                                    0.928385
#     A1                                                    0.068093
#     A2                                                  -0.0157738
#     A3                                                   0.0016606
#     A4                                                -6.93035e-05
#     B0                                                           1
#     B1                                                   -0.002438
#     B2                                                   0.0003103
#     B3                                                  -1.246e-05
#     B4                                                   2.112e-07
#     B5                                                  -1.359e-09
#     DTC                                                          3
#     FD                                                           1
#     A                                                     -3.40641
#     B                                                   -0.0842075
#     C4                                                    0.996446
#     C5                                                    0.003554
#     IXO                                                    4.97599
#     IXXO                                                   3.18803
#     C6                                                     1.15535
#     C7                                                   -0.155353
#     Notes        Source: Sandia National Laboratories Updated 9...
#     Name: Canadian_Solar_CS5P_220M___2009_, dtype: object

##  import inverter coefficients

# In[19]:

Invdb=pvlib.pvl_retreiveSAM(name='SandiaInverter')
inverter=Invdb.Advanced_Energy__Solaron_333_3159000_105_480V__CEC_2008_
inverter


# Out[19]:

#     Vac          4.800000e+02
#     Paco         3.330000e+05
#     Pdco         3.432510e+05
#     Vdco         3.700880e+02
#     Pso          1.427750e+03
#     C0          -5.768090e-08
#     C1           7.192230e-05
#     C2           2.075400e-03
#     C3           5.956110e-05
#     Pnt          1.033000e+02
#     Vdcmax       6.000000e+02
#     Idcmax       5.000000e+02
#     Mppt_low     3.300000e+02
#     Mppt_high    6.000000e+02
#     Name: Advanced_Energy__Solaron_333_3159000_105_480V__CEC_2008_, dtype: float64

## Sandia Model

# In[20]:


DFOut=pvlib.pvl_sapm(Eb=TMY['Eb'],
                    Ediff=TMY['EDiff'],
                    Tcell=TMY['Tcell'],
                    AM=TMY['AM'],
                    AOI=TMY['AOI'],
                    Module=module)

TMY['Imp']=DFOut['Imp']
TMY['Voc']=DFOut['Voc']
TMY['Vmp']=DFOut['Vmp']
TMY['Pmp']=DFOut['Pmp']
TMY['Ix']=DFOut['Ix']
TMY['Ixx']=DFOut['Ixx']


## Single Diode Model

# In[21]:


moddb=pvlib.pvl_retreiveSAM(name='CECMod')
module=moddb.Canadian_Solar_CS5P_220P

IL,I0,Rs,Rsh,nNsVth=pvlib.pvl_calcparams_desoto(S=TMY.GHI,
                                               Tcell=TMY.DryBulb,
                                               alpha_isc=.003,
                                               ModuleParameters=module,
                                               EgRef=1.121,
                                               dEgdT= -0.0002677)


DFout= pvlib.pvl_singlediode(Module=module,
                               IL=IL,
                               I0=I0,
                               Rs=Rs,
                               Rsh=Rsh,
                               nNsVth=nNsVth)


TMY['sd_Imp']=DFOut['Imp']
TMY['sd_Voc']=DFOut['Voc']
TMY['sd_Vmp']=DFOut['Vmp']
TMY['sd_Pmp']=DFOut['Pmp']
TMY['sd_Ix']=DFOut['Ix']
TMY['sd_Ixx']=DFOut['Ixx']           


## Inverter Model

# In[22]:


TMY['ACPower']=pvlib.pvl_snlinverter(Vmp=TMY.Vmp,Pmp=TMY.Pmp,Inverter=inverter)



# In[ ]:




# In[ ]:



