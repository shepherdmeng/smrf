"""
Functions to output as a netCDF
"""

import numpy as np
# from scipy import stats
import logging
import os
from datetime import datetime
from smrf.utils import utils
import pandas as pd
import pytz

from smrf import __version__

class output_point():
    """
    Class output_point() to output values to a csv file
    """

    #type = 'netcdf'
    fmt = '%Y-%m-%d %H:%M:%S'

    def __init__(self, variable_list, time, outConfig):
        """
        Initialize the output_netcdf() class

        Args:
        variable_list: dictionary of variable information
        time: numpy array of datetimes
        outConfig: output section dictionary of smrf config

        """

        self._logger = logging.getLogger(__name__)

        # go through the variable list and make full file names
        for v in variable_list:
            variable_list[v]['file_name'] = \
                variable_list[v]['out_location'] + '.csv'
            # open file
            variable_list[v]['fp'] = open(variable_list[v]['file_name'], 'w')
            #write first line
            variable_list[v]['fp'].write('date_time,{}\n'.format(v))

        self.variable_list = variable_list

        # process the time section
        self.out_frequency = int(outConfig['frequency'])
        self.outConfig = outConfig

        for v in self.variable_list:

            f = self.variable_list[v]
            self.variable_list[v]['df'] = pd.DataFrame(columns=['date_time', v])
            self.variable_list[v]['values'] = np.zeros((len(time)))
            self.variable_list[v]['df']['date_time'] = time
            if os.path.isfile(f['file_name']):
                self._logger.warning('Opening {}, data may be overwritten!'
                                  .format(f['file_name']))

            else:
                self._logger.debug('Will create %s' % f['file_name'])

    def output(self, variable, data, date_time):
        """
        Output a time step

        Args:
            variable: variable name that will index into variable list
            data: the variable data
            date_time: the date time object for the time step
        """

        self._logger.debug('{0} Storing variable {1}'
                           .format(date_time, variable))

        data = np.array(data)

        time = self.variable_list[variable]['df']['date_time'].values
        tzinfo = pytz.timezone('UTC')
        date_time = np.datetime64(date_time.replace(tzinfo=tzinfo))

        data = np.array(data)
        datatype = type(data)
        # print(variable)
        # print(data)
        try:
            data = data[0][0]
        except:
            # print('Nope')
            pass

        if variable == 'net_solar' and np.any(np.isnan(data)):
            data = np.array(0.0)*np.ones((1,1))

        #print(self.variable_list[variable]['values'])
        self.variable_list[variable]['values'][time == date_time] = data
        # output csv
        wl = '{},{}\n'.format(pd.to_datetime(date_time).strftime(self.fmt),
                              data)
        self.variable_list[variable]['fp'].write(wl)
        # output csv if this is the last time step
        if date_time == time[-1]:
            self.variable_list[variable]['fp'].close()
        #     fp = self.variable_list[variable]['file_name']
        #     self.variable_list[variable]['df'][variable] = self.variable_list[variable]['values']
        #     self.variable_list[variable]['df'].to_csv(fp, index=False)
