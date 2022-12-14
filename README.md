# ubx2numpy

This progarm transforms the Ublox data measured by a GPS antenna into a Numpy array. The Python modules required to run this programme are:
~~~
numpy
~~~

~~~
pyubx2
~~~

# a run example:
``` sh
python main_transform_data.py -i GA_GP_SBAS.ubx
```

This can take some time depending on the size of the file. 

At the end, the programm converts the ubx data into a numpy array arranging them in a data container defined as shown in [this](https://github.com/sciqader/ubx2numpy/blob/main/diagram.jpeg) diagram. The output file will be formated dc_inputfilename.npy, for the example here it is called:

```
dc_GA_GP_SBAS.ubx.npy
```

As shown in the diagram, not all the information from the ublox file is converted to Numpy, but only the information I find useful. The user can follow the code in data_container.py and add the information they need.

# An analysis example


``` python
import numpy as np

data = np.load('dc_GA_GP_SBAS.ubx.npy') # load gps measurements from the data container

lat = data['pos']['lat'] # get the measured latitudes
lon = data['pos']['lon'] # get the measured longitudes

# If you have a zero measurement in your data, 
#  e.g. due to premature completion of the measurement, rectify this by:
lat = lat[lat != 0]

pfilter_data = data[data['dop']['pdop'] < 2] # select a subset of data with a pdop value < 2

pf_lat = pfilter_data['pos']['lat'] # get latitudes for pdop < 2

# lets apply a cut on satellite elevation angle > 10 degrees
l = []
for d in data:
	if (d['sat'][:d['nvsat']]['elv'] > 10).all():
		l.append(d)

elvfilter_data = np.asarray(l)

elvf_lat = elvfilter_data['pos']['lat'] # get latitudes for elv > 10°

# Here, too, you can ensure that the incomplete messages are 
# are rejected by discarding the 0 measurement.
elvf_lat = elvf_lat[elvf_lat ! = 0]


#####
# this part is for education
# list of satellites which send SBAS correction signal in an event (e.g. event #10)
svID_corrSource = data[10]['sig']['svid'][data[10]['sig']['corrsource'] == 1]
# now list all the satellites which contributed in the solution
used_svID = data[10]['used_sat'][:data[10]['nsat']]
# to check if all satellites which contributed in the solution
# and belong to satellite with correction signal
print(np.in1d(used_svID, svID_corrSource).all() )
# to check if any satellites which contributed in the solution
# and belong to satellite with correction signal
print(np.in1d(used_svID, svID_corrSource).any() )
# to sum the satellites which contributed in the solution
# and belong to satellite with correction signal
print(np.in1d(used_svID, svID_corrSource).sum() )
####

# now we want to use this information
# to filter out events where there are 
# less than 5 correction satellites 
# for the solutions
l = []
for d in data:
	svID_corrSource = d['sig']['svid'][d['sig']['corrsource'] == 1 ]
	used_svID = d['used_sat'][:d['nsat']]
	NCorrSat = np.in1d(used_svID, svID_corrSource).sum()
	if NCorrSat >= 5:
		l.append(d)

corrsat_filter = np.asarray(l)
```

