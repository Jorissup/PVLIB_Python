
from nose.tools import *
import numpy as np
import pandas as pd 
import sys
import os
sys.path.append(os.path.abspath('../'))
from .. import pvl_singlediode 
from .. import pvl_ephemeris 
from .. import pvl_extraradiation 
from .. import pvl_relativeairmass 
from .. import pvl_getaoi 
from .. import pvl_calcparams_desoto 
from .. import pvl_tools
from .. import tmy

def test_proper_vector():

	SurfTilt=30
	SurfAz=0
	Albedo=0.2

	TMY, meta=tmy.readtmy3(filename='703165TY.csv')

	#Canadian_Solar_CS5P_220P
	module={'A_c': 1.639,
			 'A_ref': 2.3674,
			 'Adjust': 2.3,
			 'Alpha_sc': 0.0025,
			 'Beta_oc': -0.19659000000000001,
			 'Gamma_r': -0.43,
			 'I_l_ref': 5.056,
			 'I_mp_ref': 4.73,
			 'I_o_ref': 1.006e-10,
			 'I_sc_ref': 5.05,
			 'N_s': 96,
			 'R_s': 1.004,
			 'R_sh_ref': 837.51,
			 'Source': 'Multi-c-Si',
			 'T_noct': 51.4,
			 'V_mp_ref': 46.6,
			 'V_oc_ref': 58.3}

	module=pvl_tools.repack(module)

	TMY['SunAz'], TMY['SunEl'], TMY['ApparentSunEl'], TMY['SolarTime'], TMY['SunZen']=pvl_ephemeris(Time=TMY.index,Location=meta)

	TMY['HExtra']=pvl_extraradiation(doy=TMY.index.dayofyear)

	TMY['AM']=pvl_relativeairmass(z=TMY.SunZen)

	TMY['AOI']=pvl_getaoi(SunAz=TMY.SunAz,SunZen=TMY.SunZen,SurfTilt=SurfTilt,SurfAz=SurfAz)

	IL,I0,Rs,Rsh,nNsVth=pvl_calcparams_desoto(S=TMY.GHI,Tcell=TMY.DryBulb,alpha_isc=.003,ModuleParameters=module, EgRef=1.121, dEgdT= -0.0002677)
	pmp=pvl_singlediode(Module=module,IL=IL,I0=I0,Rs=Rs,Rsh=Rsh,nNsVth=nNsVth)
	assert(True==True)

def test_proper_scalar():


	#Canadian_Solar_CS5P_220P
	module={'A_c': 1.639,
	         'A_ref': 2.3674,
	         'Adjust': 2.3,
	         'Alpha_sc': 0.0025,
	         'Beta_oc': -0.19659000000000001,
	         'Gamma_r': -0.43,
	         'I_l_ref': 5.056,
	         'I_mp_ref': 4.73,
	         'I_o_ref': 1.006e-10,
	         'I_sc_ref': 5.05,
	         'N_s': 96,
	         'R_s': 1.004,
	         'R_sh_ref': 837.51,
	         'Source': 'Multi-c-Si',
	         'T_noct': 51.4,
	         'V_mp_ref': 46.6,
	         'V_oc_ref': 58.3}
	module=pvl_tools.repack(module)
	Voc=module.V_oc_ref
	Isc=module.I_sc_ref
	Rs=module.R_s
	Rsh=module.R_sh_ref
	IL=module.I_l_ref
	I0=module.I_o_ref
	nNsVth=module.A_ref

	pmp=pvl_singlediode(Module=module,IL=IL,I0=I0,Rs=Rs,Rsh=Rsh,nNsVth=nNsVth)
	assert(True==True)

def test_multiple_I_V_Points():
	assert (False)

def main():
    unittest.main()

if __name__ == '__main__':
    main()