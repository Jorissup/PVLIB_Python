"""
Collection of functions used in pvlib_python
"""
import pdb
import numpy as np 
import ast
import re

import inspect
from functools import wraps

class repack():   #repack a dict as a struct
	
	'''
	Converts a dict to a struct
	
	Parameters
	----------

	dct : dict

			Dict to be converted

	Returns
	-------
	self : struct

			structure of packed dict entries
	'''

	def __init__(self,dct):
		self.__dict__.update(dct)

class Parse():		#parse complex logic
	'''
	Parses inputs to pvlib_python functions.

	Parameters
	----------

	kwargs : dict
		Input variables 

	Expect : dict
		Parsing logic for input variables, in the form of a dict. 

		Possible flags are:

		============	=======================================================================================
		string flag 	Description
		============	=======================================================================================
		num 			Ensure input is numeric
		array 			Ensure input is a numpy array. If it is not in an array, it will attempt to convert it 
		df    			Ensure input is a pandas dataframe
		str 			Ensure inpus is a string
		optional 		Input is not required
		default			Defines a default value for a parameter. Must be followed by a 'default=x' statement
		*logical* 		Can accept a range of logical arguments in the form 'x[== <= >= < >]value'
		============	=======================================================================================
	
	Returns
	-------

	var : struct

		Structure containing all input values in kwargs

	Notes
	-----

	This function will raise a descriptive exception if a variable fails any input requrements 


	'''

 	def __init__(self, dct, Expect):
 		self.__dict__.update(self.parse_fcn(dct,Expect))

	def parse_fcn(self,kwargs,Expect):

		#unpack any kwargs into a flat dict

		if 'kwargs' in kwargs:
			kwargs.update(kwargs['kwargs'])
			del kwargs['kwargs']

		#Check all inputs are defined
		try:
			for arg in kwargs:

					Expect[arg]
		except:
			raise Exception('WARNING: Unknown variable " '+arg+' " ')

		#Check that all inputs exist
		try: 
			for arg in Expect:
				if 'df' in Expect[arg]:
					df=kwargs[arg]  #locate main dataframe 
				if not(('matelement' in Expect[arg]) or ('optional' in Expect[arg]) 
						or ('default' in Expect[arg])):
					kwargs[arg]
		except:
			raise Exception('WARNING: " '+arg+' " was not input')	

		
		#Check dataframe entries
		try:
			for arg in Expect:
				if 'matelement' in Expect[arg]:
					df[arg]

		except:
			raise Exception('WARNING: " '+arg+' " in main dataframe does not exist')			
		# Assert numeric for all numeric fields
		
		try:
			for arg in kwargs:
				#add any exceptions to numeric checks (eg. string input fields)
				if not('num' in Expect[arg]):
					continue
				# Check if the value is an np.array
				if not isinstance(kwargs[arg],np.ndarray):
		 			kwargs[arg]=np.array(kwargs[arg])
		 			#print('WARNING: Numeric variable '+ arg +' not input as a numpy array. Recasting as array')
				kwargs[arg].astype(float)
		except:
			raise Exception('Error: Non-numeric value in numeric input field: '+arg)

		#Check any string inputs. 
		#pdb.set_trace()
		#print 'DEVWARNING: Fix string index dependancy'
		for arg in kwargs:
			if 'str' in Expect[arg]:
				if (not('open' in Expect[arg]) or not( 'o' in Expect[arg])) and not(kwargs[arg] in Expect[arg][1]):
					raise Exception('Error: String in input field '+ arg+' is not valid')


		#Check logical functions
		#pdb.set_trace()
		reg=re.compile('[a-z][== <= >= < >][== <= >= < >]?-?[0-9]+')
		reglogical=re.compile('.[== <= >= < >].')
		regdefault=re.compile('default=')
		regsyst=re.compile('.__.')
		for arg in Expect:
			for string in Expect[arg]:
				
				if isinstance(string,basestring): ##Python 2.x dependancy
					#Remove any potential of running system commands through eval
					if np.shape(re.findall(regsyst,string))[0]>0:		
						raise Exception("DANGER: System Command entered as constraint ' "+ string+ "' ")	
					
					#Set default value for a variable if defined
					elif np.shape(re.findall(regdefault,string))[0]>0:
						
						try: 
							kwargs[arg]
					 	except:
					 		try: 
								kwargs[arg]=np.array(float(string[8:])) #numeric defualt
							except:
								kwargs[arg]=(string[8:]) #string default

					#Excecute proper logical operations if syntax matches regex
					elif np.shape(re.findall(reg,string))[0]>0:

						lambdastring='lambda x:'+re.findall(reg,string)[0]

						#check df elements
						if ('matelement' in Expect[arg]):
							if not(eval(lambdastring)(df[arg]).any()):
								raise Exception('Error: Numeric input "'+arg+' " fails on logical test " '+ re.findall(reg,string)[0]+'"')	
						elif ('optional' in Expect[arg]):
							#pdb.set_trace()
							try: #check if the optional value exists 
								kwargs[arg]
							except:
								print 'Optional value "'+arg+'" not input'""
								continue
							if not(eval(lambdastring)(kwargs[arg])): #check its logical constraint
								raise Exception('Error: Optional input "'+arg+'" fails on logical test "'+ re.findall(reg,string)[0]+'"')	
						#check all other contraints
						elif not(eval(lambdastring)(kwargs[arg]).all()):
							raise Exception('Error: Numeric input "'+arg+' " fails on logical test " '+ re.findall(reg,string)[0]+'"')
					#Check if any string logicals are bypassed due to poor formatting
							
					elif np.shape(re.findall(reglogical,string))[0]>0:		
						raise Exception("WARNING: Logical constraint ' "+string+" ' is unused. Check syntax")
					
			 	

		return kwargs


class TypeCheck(object):
    """Decorator that sanitize function arguments using Parse
    """

    def __init__(self, **kwargs):
        self.expect = kwargs


    def __call__(self, fn):

    	# get the function names for the signature
    	arg_names = inspect.getargspec(fn).args

        @wraps(fn)
        def inner(*args, **kwargs):
    		cleaned_var = Parse(locals(), self.expect)

    		# replace the arguments with the sanitized versions, where available,
    		# if not, use the current
    		new_args = (getattr(cleaned_var, name, arg) for name, arg in zip(arg_names, args))

    		# replace the kwargs with sanitized versions where available
    		for key, val in kwargs.items():
    			kwargs[key] = getattr(cleaned_var, key, val)

    		# invoke the function with the sanitized argument
    		return fn(*new_args, **kwargs)

def cosd(angle):
	"""
	Cosine with angle input in degrees

	Parameters
	----------

	angle : float
				Angle in degrees

	Returns
	-------

	result : float
				Cosine of the angle
	"""

	res=np.cos(np.radians(angle))
	return res

def sind(angle):
	"""
	Sine with angle input in degrees

	Parameters
	----------

	angle : float
				Angle in degrees

	Returns
	-------

	result : float
				Sin of the angle
	"""

	res=np.sin(np.radians(angle))
	return res

def tand(angle):
	"""
	Tan with angle input in degrees

	Parameters
	----------

	angle : float
				Angle in degrees

	Returns
	-------

	result : float
				Tan of the angle
	"""

	res=np.tan(np.radians(angle))
	return res


def asind(number):
	"""
	Inverse Sine returning an angle in degrees

	Parameters
	----------

	number : float
			Input number

	Returns
	-------

	result : float
			arcsin result

	"""

	res=np.degrees(np.arcsin(number))
	return res

