
import numpy as np
import logging
from smrf.distribute import image_data
from smrf.utils import utils
from smrf.envphys.core import envphys_c


class vp(image_data.image_data):
    """
    The :mod:`~smrf.distribute.vapor_pressure.vp` class allows for variable
    specific distributions that go beyond the base class

    Vapor pressure is provided as an argument and is calcualted from coincident
    air temperature and relative humidity measurements using utilities such as
    IPW's ``rh2vp``. The vapor pressure is distributed instead of the relative
    humidity as it is an absolute measurement of the vapor within the
    atmosphere and will follow elevational trends (typically negative).  Were
    as relative humidity is a relative measurement which varies in complex ways
    over the topography.  From the distributed vapor pressure, the dew point is
    calculated for use by other distribution methods. The dew point temperature
    is further corrected to ensure that it does not exceed the distributed air
    temperature.

    Args:
        vpConfig: The [vapor_pressure] section of the configuration file

    Attributes:
        config: configuration from [vapor_pressure] section
        vapor_pressure: numpy matrix of the vapor pressure
        dew_point: numpy matrix of the dew point, calculated from
            vapor_pressure and corrected for dew_point greater than air_temp
        min: minimum value of vapor pressure is 10 Pa
        max: maximum value of vapor pressure is 7500 Pa
        stations: stations to be used in alphabetical order
        output_variables: Dictionary of the variables held within class
            :mod:`!smrf.distribute.vapor_pressure.vp` that specifies the
            ``units`` and ``long_name`` for creating the NetCDF output file.
        variable: 'vapor_pressure'

    """

    variable = 'vapor_pressure'

    # these are variables that can be output
    output_variables = {'vapor_pressure': {
                                  'units': 'pascal',
                                  'standard_name': 'vapor_pressure',
                                  'long_name': 'Vapor pressure'
                                  },
                        'dew_point': {
                                  'units': 'degree_Celcius',
                                  'standard_name': 'dew_point_temperature',
                                  'long_name': 'Dew point temperature'
                                  }
                        }

    # these are variables that are operate at the end only and do not need to
    # be written during main distribute loop
    post_process_variables = {}

    def __init__(self, vpConfig):

        # extend the base class
        image_data.image_data.__init__(self, self.variable)
        self._logger = logging.getLogger(__name__)

        # check and assign the configuration
        self.getConfig(vpConfig)

        self.point_model = False
        if self.config['distribution'] == 'point':
            self.point_model = True

        self._logger.debug('Created distribute.vapor_pressure')

    def initialize(self, topo, data):
        """
        Initialize the distribution, calls
        :mod:`smrf.distribute.image_data.image_data._initialize`. Preallocates
        the following class attributes to zeros:

        Args:
            topo: :mod:`smrf.data.loadTopo.topo` instance contain topographic
                data and infomation
            data: data Pandas dataframe containing the station data,
                from :mod:`smrf.data.loadData` or :mod:`smrf.data.loadGrid`

        """

        self._logger.debug('Initializing distribute.vapor_pressure')
        self._initialize(topo, data.metadata)

    def distribute(self, data, ta):
        """
        Distribute air temperature given a Panda's dataframe for a single time
        step. Calls :mod:`smrf.distribute.image_data.image_data._distribute`.

        The following steps are performed when distributing vapor pressure:

        1. Distribute the point vapor pressure measurements
        2. Calculate dew point temperature using
            :mod:`smrf.envphys.core.envphys_c.cdewpt`
        3. Adjust dew point values to not exceed the air temperature

        Args:
            data: Pandas dataframe for a single time step from precip
            ta: air temperature numpy array that will be used for calculating
                dew point temperature

        """

        self._logger.debug('%s -- Distributing vapor_pressure' % data.name)

        # calculate the vapor pressure
        self._distribute(data)

        # set the limits
        self.vapor_pressure = utils.set_min_max(self.vapor_pressure,
                                                self.min,
                                                self.max)

        # calculate the dew point
        self._logger.debug('%s -- Calculating dew point' % data.name)

        # get through the casting to c types in the cython code by
        # changing the shapes briefly
        if self.point_model:
            self.vapor_pressure = self.vapor_pressure*np.ones((2,2))

        # use the core_c to calculate the dew point
        dpt = np.zeros_like(self.vapor_pressure, dtype=np.float64)
        envphys_c.cdewpt(self.vapor_pressure,
                         dpt,
                         self.config['tolerance'],
                         self.config['nthreads'])

        # resize to 1x1 or point model
        if self.point_model:
            self.vapor_pressure = np.array(self.vapor_pressure[0,0])
            dpt = np.array(dpt[0,0])

        # find where dpt > ta
        ind = dpt >= ta

        if (np.sum(ind) > 0):  # or np.sum(indm) > 0):
            dpt[ind] = ta[ind] - 0.2

        self.dew_point = dpt

    def distribute_thread(self, queue, data):
        """
        Distribute the data using threading and queue. All data is provided and
        ``distribute_thread`` will go through each time step and call
        :mod:`smrf.distribute.vapor_pressure.vp.distribute` then puts the
        distributed data into the queue for:

        * :py:attr:`vapor_pressure`
        * :py:attr:`dew_point`

        Args:
            queue: queue dictionary for all variables
            data: pandas dataframe for all data, indexed by date time
        """

        for t in data.index:

            ta = queue['air_temp'].get(t)

            self.distribute(data.loc[t], ta)

            queue[self.variable].put([t, self.vapor_pressure])
            queue['dew_point'].put([t, self.dew_point])
