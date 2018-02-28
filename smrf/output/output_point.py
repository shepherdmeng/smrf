"""
Functions to output as a netCDF
"""

import numpy as np
# from scipy import stats
import logging
import os
from datetime import datetime
from smrf.utils import utils
# import pandas as pd

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
            variable_list: list of dicts, one for each variable
            topo: loadTopo instance
        """

        self._logger = logging.getLogger(__name__)

        # go through the variable list and make full file names
        for v in variable_list:
            variable_list[v]['file_name'] = \
                variable_list[v]['out_location'] + '.csv'

        self.variable_list = variable_list

        # process the time section
        self.run_time_step = int(time['time_step'])
        self.out_frequency = int(outConfig['frequency'])
        self.outConfig = outConfig

        for v in self.variable_list:

            f = self.variable_list[v]
            self.variable_list[v]['df'] = pd.DataFrame(columns=['date_time', v])
            self.variable_list[v]['values'] = np.zeros_like((len(time),1))
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

        if len(data) > 1:
            raise ValueError('Data is not in point format, cannot store output')

        time = self.variable_list[variable]['df']['date_time']
        self.variable_list[variable]['values'][time == date_time] = data[0]

        # output csv if this is the last time step
        if date_time == time[-1]
            fp = variable_list[variable]['file_name']
            self.variable_list[variable]['df'].to_csv[fp, index = False]
