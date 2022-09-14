import numpy as np

data = np.load('dc_GA_GP_SBAS.ubx.npy') # load gps measurement from the data container

lat = data['pos']['lat'] # get the measured latitudes
lon = data['pos']['lon'] # get the measured longitudes

# if you have a zero measurement in your data, 
#e.g. lat due to imature completion of the measurement fix it by:
lat = lat[lat != 0]

pfilter_data = data[data['dop']['pdop'] < 2] # select the subset of data with pdop value < 2

pf_lat = pfilter_data['pos']['lat'] # get the measured latitudes with pdop < 2

# let's apply satellite elevation cut > 10 degrees
l = []
for d in data:
	if (d['sat'][:d['nvsat']]['elv'] > 10).all():
		l.append(d)

elvfilter_data = np.asarray(l)

elvf_lat = elvfilter_data['pos']['lat'] # get the measured latitudes with elv > 10°

# here also you can make sure the uncomplete messages 
# are rejected by discarding the 0 measurement
elvf_lat = elvf_lat[elvf_lat ! = 0]


#####
# this part is for education
# list of satellites which send SBAS correction signal in an event (e.g. event #10)
svID_corrSource = data[10]['sig']['svid'][data[10]['sig']['corrsource'] == 1]
# now list all the satellites which contributed in the solution
used_svID = data[10]['used_sat'][:data[10]['nsat']]
# to check if all satellites which contributed in the solution
# and belong to satellite with correcting signal
print(np.in1d(used_svID, svID_corrSource).all() )
# to check if any satellites which contributed in the solution
# and belong to satellite with correcting signal
print(np.in1d(used_svID, svID_corrSource).any() )
# to sum the satellites which contributed in the solution
# and belong to satellite with correcting signal
print(np.in1d(used_svID, svID_corrSource).sum() )
####

# now we want to use this information to filter out events where there are less than 5 correction satellites for the solutions
l = []
for d in data:
	svID_corrSource = d['sig']['svid'][d['sig']['corrsource'] == 1 ]
	used_svID = d['used_sat'][:d['nsat']]
	NCorrSat = np.in1d(used_svID, svID_corrSource).sum()
	if NCorrSat >= 5:
		l.append(d)

corrsat_filter = np.asarray(l)


