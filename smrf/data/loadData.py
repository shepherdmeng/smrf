'''
20121229 Scott Havens
'''

# from smrf import ipw
from smrf.data import mysql_data
import numpy as np
import logging
import pandas as pd

# logging message start
# logmsg = 'loadData: %s'

class wxdata():
    '''
    Class for loading and storing the data, either from 
    - CSV file
    - MySQL database
    - Add other sources here
        
    Inputs to data() are:
    - dataConfig, either the [csv] or [mysql] section
    - start_date, datetime object
    - end_date, datetime object
    - dataType, either 'csv' or 'mysql'
    
    The data will be loaded into a Pandas dataframe
    
    '''
    
    def __init__(self, dataConfig, start_date, end_date, time_zone='UTC', stations=None, dataType=None):
        
        if dataType is None:
            raise Exception('loadData.data() must have a specified dataType of "csv" or "mysql"')
        
        self.dataConfig = dataConfig
        self.dataType = dataType
        self.start_date = start_date
        self.end_date = end_date
        self.time_zone = time_zone
        self.stations = stations
        self.variables = ['air_temp', 'vapor_pressure', 'precip', 'solar', 'wind_speed', 'wind_direction']
        
        
        self._logger = logging.getLogger(__name__)


        # load the data        
        if dataType == 'csv':
            self.load_from_csv()
            
        elif dataType == 'mysql':
            self.load_from_mysql()
        else:
            raise Exception('Could not resolve dataType')
        
        # correct for the timezone
        for v in self.variables:
            d = getattr(self, v)
            setattr(self, v, d.tz_localize(tz=self.time_zone))
        
        
     
    def load_from_csv(self):
        '''
        Load the data from a csv file
        Fields:
        - metadata -> dictionary, one for each station, must have at least the following
            - primary_id, X, Y, elevation
        - csv data files -> dictionary, one for each time step, must have at least the
            following columns:
            - date_time, column names matching metadata.primary_id
        '''
        
        self._logger.info('Reading data coming from CSV files')
        
        sta = None
        if self.stations is not None:
            if 'stations' in self.stations:
                sta = self.stations['stations'].split(',')
                self._logger.debug('Using only stations %s' % self.stations['stations'])
                
        # load the data
        v = list(self.variables)
        v.append('metadata')
        for i in v:
            if i in self.dataConfig:
                
                if i == 'metadata':
                    dp = pd.read_csv(self.dataConfig[i], index_col='primary_id')
                elif self.dataConfig[i]:
                    dp = pd.read_csv(self.dataConfig[i], index_col='date_time', parse_dates=[0])
                    
                    if sta is not None:
                        dp = dp[sta]
                    dp = dp[self.start_date : self.end_date]    # only get the desired dates
                    
                setattr(self, i, dp)
            
        # check that metadata is there    
        try:
            self.metadata
        except:
            raise AttributeError('Metadata missing from configuration file')
        
        
        
    def load_from_mysql(self):
        '''
        Load the data from a mysql database
        '''
        
        self._logger.info('Reading data from MySQL database')
        
        # open the database connection
        data = mysql_data.database(self.dataConfig['user'], self.dataConfig['password'], 
                          self.dataConfig['host'], self.dataConfig['database'])
        
        #------------------------------------------------------------------------------ 
        # determine if it's stations or client
        sta = None
        if 'stations' in self.stations:
            sta = self.stations['stations'].split(',')
            
        c = None
        stable = None
        if 'client' in self.stations:
            c = self.stations['client']
            stable = self.dataConfig['station_table']
            
          
        # determine what table for the metadata
        mtable = self.dataConfig['metadata']  
        
        if (sta is None) & (c is None):
            raise Exception('Error in configuration file for [mysql], must specify either "stations" or "client"')
        self._logger.debug('Loading metadata from table %s' % mtable)
        
        #------------------------------------------------------------------------------ 
        # load the metadata
        self.metadata = data.metadata(mtable, station_ids=sta, client=c, station_table=stable)
            
        self._logger.debug('%i stations loaded' % self.metadata.shape[0])
            
        #------------------------------------------------------------------------------ 
        # get a list of the stations
        station_ids = self.metadata.index.tolist()
        
        # get the correct column names if specified        
        variables = []
        for i in self.variables:
            if i in self.dataConfig:
                i = self.dataConfig[i]
            variables.append(i)
        
        dp = data.get_data(self.dataConfig['data_table'], station_ids, self.start_date, self.end_date, variables)
        
        # go through and extract the data
        for i,v in enumerate(self.variables):
            setattr(self, v, dp[self.dataConfig[v]])
                            

            
            
           
        
        
        
        