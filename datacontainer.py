########################################
# Author: Qader Dorosti
########################################
import numpy as np
from pyubx2 import UBXReader
import os


def find_number_of_events(data):
	nEvt = 1;
	for d in data:
		if hasattr(d, 'msg_id'):
			pass
		else:
			if d.msgID == 'RMC':
				nEvt += 1
	return nEvt

def read_ubx(infile):
	l = []
	stream = open(infile, 'rb')
	ubr = UBXReader(stream)
	for (raw_data, parsed_data) in ubr:
		l.append(parsed_data)
	return np.asarray(l)

def clean_and_save_dc(data, infile, dt):
	nvsat_max = data['nvsat'].max()
	dt[4] = ('sat', [('id', 'uint16'), ('elv', 'f4'), ('az', 'f4')], (nvsat_max,))
	numsig_max = data['numsig'].max()
	dt[6] = ('sig', [('svid', 'uint16'), ('qualityid', 'uint16'), \
		    ('corrsource', 'uint16')],(numsig_max,))
	nsat_max = data['nsat'].max()
	dt[-1] = ('used_sat', 'uint16', (nsat_max,))
	# reject incomplete events
	dd = data[data['nvsat']!=0]
	nevent = dd.size - dd[dd['numsig']==0].size 

	# build the nd array
	cleaned_data = np.empty((nevent,), dtype=dt)

	i = 0
	for d in data:
		# reject incomplete events
		if d['nvsat'] == 0 or d['numsig'] == 0:
			pass
		else:
			cleaned_data[i]['datetime'] = d['datetime']
			cleaned_data[i]['pos'] = d['pos']
			cleaned_data[i]['dop'] = d['dop']
			cleaned_data[i]['nsat'] = d['nsat']
			cleaned_data[i]['sat'] = d['sat'][:nvsat_max]
			cleaned_data[i]['nvsat'] = d['nvsat']
			cleaned_data[i]['sig'] = d['sig'][:numsig_max]
			cleaned_data[i]['numsig'] = d['numsig']
			cleaned_data[i]['used_sat'] = d['used_sat'][:nsat_max]
			i += 1
	np.save('dc_' + os.path.basename(infile), cleaned_data)

def transform_data(input_file, dump_raw_data=False, save_datacontainer=True):
	# define the data type
	nfp = [('lat', 'f4'), ('lon', 'f4')] # define the number format for position info
	nfd = [('pdop', 'f4'), ('hdop', 'f4'), ('vdop', 'f4')] # define the number format for dop values
	nfs = [('id', 'uint16'), ('elv', 'f4'), ('az', 'f4')] # define the number format for sat info
	nfns = [('svid', 'uint16'), ('qualityid', 'uint16'), ('corrsource', 'uint16')] # define the number format for nav sig info

	dt = [('datetime', 'datetime64[s]'), ('pos', nfp), ('dop', nfd), \
		  ('nsat', 'uint16'), ('sat', nfs, (1000,)), ('nvsat', 'uint16'), \
		  ('sig', nfns, (100,)), ('numsig', 'uint16'), ('used_sat', 'uint16', (100,))]

	svid_list = ['svid_01', 'svid_02', 'svid_03', 'svid_04', 'svid_05', \
				 'svid_06', 'svid_07', 'svid_08', 'svid_09', 'svid_10', \
				 'svid_11', 'svid_12']

	ParsedData = read_ubx(infile=input_file)
	if dump_raw_data:
		np.save('parsed_data_'+input_file, ParsedData)

	NEvent = find_number_of_events(ParsedData)

	transformed_data = np.empty((NEvent,), dtype=dt)

	i = 0
	j = 0
	k = 0
	used_svid = [] #temporarily store svid
	used_sat = [] # satelites which are used in the solution
	for d in ParsedData:
		if hasattr(d, 'msg_id'):
			if d.msg_id == b'C':
				numSig = d.numSigs
				transformed_data[i]['numsig'] = numSig
				for n in range(numSig):
					num = '0'+str(n+1)
					if n+1 > 9:
						num = str(n+1)
					transformed_data[i]['sig'][n]['svid'] = getattr(d, 'svId_'+num)
					transformed_data[i]['sig'][n]['qualityid'] = getattr(d, 'qualityInd_'+num)
					transformed_data[i]['sig'][n]['corrsource'] = getattr(d, 'corrSource_'+num)

		else:
			if d.msgID == 'RMC':
				used_svid.clear()
				used_sat.clear()
				l = 0 # number of enteries in gsv message for the visible satellites
				k = 0 # resetting iterator for sat info array
				j += 1
				transformed_data[i]['datetime'] = str(d.date) + 'T' + str(d.time)
				transformed_data[i]['pos']['lat'] = d.lat
				transformed_data[i]['pos']['lon'] = d.lon

			if d.msgID == 'GSA':
				transformed_data[i]['dop']['pdop'] = d.PDOP
				transformed_data[i]['dop']['hdop'] = d.HDOP
				transformed_data[i]['dop']['vdop'] = d.VDOP
				for svid in svid_list:
					if getattr(d, svid) != '':
						used_svid.append(getattr(d, svid))

			if d.msgID == 'GSV':
				transformed_data[i]['nsat'] = len(used_svid)
				transformed_data[i]['used_sat'][:len(used_svid)] = used_svid
				for sv in used_svid:
					for svid in svid_list:
						if hasattr(d, svid):
							if sv == getattr(d, svid):
								l += 1
								elv_id = 'elv_' + svid.split('_')[1] # get elevation
								az_id = 'az_' + svid.split('_')[1] # get azimuth
								transformed_data[i]['sat'][k]['id'] = int(sv)
								if getattr(d, elv_id) != '':
									transformed_data[i]['sat'][k]['elv'] = getattr(d, elv_id)
								if getattr(d, az_id) != '':
									transformed_data[i]['sat'][k]['az'] = getattr(d, az_id)
								k +=1
			if d.msgID == 'GLL':
				transformed_data[i]['nvsat'] = l

		i = j

	if save_datacontainer:
		#np.save('dc_' + input_file, transformed_data)
		clean_and_save_dc(transformed_data, input_file, dt)

	return 'it is done'

