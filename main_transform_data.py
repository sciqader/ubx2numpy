#---------------------------------------------
# this progarm transform the ublox data 
# measured by a gps antenna to a numpy array
#
# a run example:
# python main_transform_data.py -i Messung_Galileo_GPS.ubx  
#
# author: Qader Dorosti
# email: qader.dorosti@uni-siegen.de
# time: 10:50 21.06.2022
#---------------------------------------------

import os
from optparse import OptionParser
import sys
import datacontainer as dc
import time


script_name = 'main_transform_data.py'
script_version = '1'


# Get paarameters
#---------------------------------------------
parser = OptionParser(usage = "%prog [options]", prog = script_name)
parser.set_description('a script to transform gps data into a ndarray')

parser.add_option('-i', '--input', 
					dest='input', default = '', help = 'input ubx data')

parser.add_option('-d', '--dump_raw_data', type=int,
					dest='dump_raw_data', default = 0, help = 'save the raw parsed data')


(options, args) = parser.parse_args()
input = options.input
save_raw_data = options.dump_raw_data

# check i/o 
#---------------------------------------------
if len(args) != 0:
    crap = "ERROR: Got undefined options:"
    for a in args:
            crap += a
            crap += " "
    parser.error(crap)
if input == "":
    parser.print_help()
    print ("ERROR: Please specify an ubx input file")
    sys.exit(1)
if not os.path.exists(input):
    print ("ERROR: Input file '%s' not found." % input)
    sys.exit(1)

if save_raw_data != 0 and save_raw_data != 1:
	parser.print_help()
	print("ERROR: this entry must be 0 or 1!")
	sys.exit()

# let's do it!
#---------------------------------------------
start =time.time()
dc.transform_data(input_file=input, dump_raw_data=bool(save_raw_data))
end =time.time()
total_time = end - start
print("total run time: "+ str(total_time) + ' seconds')