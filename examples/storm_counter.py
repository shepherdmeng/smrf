'''
Version = 0.2.5

20151222 Scott Havens

run_smrf.py is a command line program meant to take a single
argument for the config file.  From this program, smrf.framework
will be loaded to run the full program.

Users can also run the model as they want by using the smrf.framework.SMRF
class to change things or whatever
'''

import smrf
from datetime import datetime
import sys
from smrf import distribute
from smrf.envphys.storms import tracking_by_station
start = datetime.now()
import os

# read config file
# create a new model instance
# initialize the model
# run the model
# output if necessary

configFile = './BRB_long_term_storm_count.ini'
if len(sys.argv) > 1:
    configFile = sys.argv[1]
print os.path.abspath(os.path.expanduser(configFile))


#===============================================================================
# Model setup and initialize
#===============================================================================
#
# These are steps that will load the necessary data and initialize the framework
# Once loaded, this shouldn't need to be re-ran except if something major changes

# 1. initialize
# try:
s = smrf.framework.SMRF(configFile)

# 2. load topo data
s.loadTopo()

# 3. initialize the distribution
s.initializeDistribution()

# 5. load weather data  and station metadata
s.loadData()

d = s.data

print "{:<25}{:<25}{:<25}{:<25}".format('mass thresh', 'num storms','avg duration',"avg_mass")
for i in [0.1,0.5,1.0]:
    storms,storm_count = tracking_by_station(d.precip, mass_thresh = i)
    print "{:<25}{:<25}{:<25}{:<25}".format(i,storm_count,storms['duration'].mean(), storms['avg_mass'].mean())
