'''
Created on Apr 15, 2015

@author: scott
'''

__version__ = '0.1.1'


import numpy as np
# import matplotlib.pyplot as plt
# from isnobal import ipw



def mkprecip(precipitation, temperature):
    '''
    Follows the IPW command mkprecip
    
    The precipitation phase, or the amount of precipitation falling as rain or snow, can significantly
    alter the energy and mass balance of the snowpack, either leading to snow accumulation or inducing
    melt :cite:`Marks&al:1998` :cite:`Kormos&al:2014`. The precipitation phase and initial snow density are
    based on the precipitation temperature (the distributed dew point temperature) and are estimated 
    after Susong et al (1999) :cite:`Susong&al:1999`. The table below shows the relationship to
    precipitation temperature:
    
    ========= ======== ============ ===============
    Min Temp  Max Temp Percent snow Snow density
    [deg C]   [deg C]  [%]          [kg/m^3]
    ========= ======== ============ ===============
    -Inf      -5       100          75
    -5        -3       100          100
    -3        -1.5     100          150 
    -1.5      -0.5     100          175 
    -0.5      0        75           200 
    0         0.5      25           250 
    0.5       Inf      0            0 
    ========= ======== ============ ===============
    
    Args:
    precipitation - array of precipitation values [mm]
    temperature - array of temperature values, use dew point temperature
        if available [degree C]
        
    Output:
    - returns the percent snow and estimated snow density
    '''
    
    # convert the inputs to numpy arrays
    precipitation = np.array(precipitation)
    temperature = np.array(temperature)
    
    # create a list from the table above
    t = []
    t.append( {'temp_min': -1e309,  'temp_max': -5,     'snow': 1,    'density':75} )
    t.append( {'temp_min': -5,      'temp_max': -3,     'snow': 1,    'density':100} )
    t.append( {'temp_min': -3,      'temp_max': -1.5,    'snow': 1,    'density':150} )
    t.append( {'temp_min': -1.5,    'temp_max': -0.5,   'snow': 1,    'density':175} )
    t.append( {'temp_min': -0.5,    'temp_max': 0.0,    'snow': 0.75, 'density':200} )
    t.append( {'temp_min': 0.0,     'temp_max': 0.5,    'snow': 0.25, 'density':250} )
    t.append( {'temp_min': 0.5,     'temp_max': 1e309,  'snow': 0,    'density':0} )
        
    
    # preallocate the percent snow (ps) and snow density (sd)
    ps = np.zeros(precipitation.shape)
    sd = np.zeros(ps.shape)
    
    # if no precipitation return all zeros
    if np.sum(precipitation) == 0:
        return ps, sd
    
    # determine the indicies and allocate based on the table above
    for row in t:
        
        # get the values between the temperature ranges that have precip
        ind = [(temperature >= row['temp_min']) & (temperature < row['temp_max'])]
        
        # set the percent snow
        ps[ind] = row['snow']
        
        # set the density
        sd[ind] = row['density']
        
    
    # if there is no precipitation at a pixel, don't report a value
    # this may make isnobal crash, I'm not really sure
    ps[precipitation == 0] = 0
    sd[precipitation == 0] = 0
    
    return ps, sd
    
    
def storms(precipitation, perc_snow, mass=1, time=4, 
           stormDays=None, stormPrecip=None, ps_thresh=0.5):
    '''
    Calculate the decimal days since the last storm given a precip time series,
    percent snow, mass threshold, and time threshold
    
     - Will look for pixels where perc_snow > 50% as storm locations
     - A new storm will start if the mass at the pixel has exceeded the mass
         limit, this ensures that the enough has accumulated
    
    Args:
    precipitation - precipitation values
    perc_snow - precent of precipitation that was snow
    mass - threshold for the mass to start a new storm
    time - threshold for the time to start a new storm
    stormDays - if specified, this is the output from a previous run of storms
    stormPrecip - keeps track of the total storm precip
    
    Created April 17, 2015
    @author: Scott Havens
    '''
    
    # either preallocate or use the input
    if stormDays is None:
        stormDays = np.zeros(precipitation.shape)
        
    if stormPrecip is None:
        stormPrecip = np.zeros(precipitation.shape)
        
    # if there is no snow, don't reset the counter
    # This ensures that the albedo won't be reset
    stormDays += 1
    if np.sum(perc_snow) == 0:
#         stormDays = np.add(stormDays, 1)
        stormPrecip = np.zeros(precipitation.shape)
        return stormDays, stormPrecip
    
    
    # determine locations where it has snowed
    idx = perc_snow >= ps_thresh
    
    # determine locations where the time threshold has passed
    # these areas, the stormPrecip will be set back to zero
    idx_time = stormDays >= time
    stormPrecip[idx_time] = 0
    
    # add the values to the stormPrecip
    stormPrecip[idx] =+ precipitation[idx]
    
    # see if the mass threshold has been passed
    idx_mass = stormPrecip >= mass
    
    # reset the stormDays to zero where the storm is present
    stormDays[idx_mass] = 0
    
    
    return stormDays, stormPrecip
    
    
def storms_time(precipitation, perc_snow, time_step=1/24, mass=1, time=4,
                stormDays=None, stormPrecip=None, ps_thresh=0.5):
    '''
    Calculate the decimal days since the last storm given a precip time series,
    percent snow, mass threshold, and time threshold
    
     - Will look for pixels where perc_snow > 50% as storm locations
     - A new storm will start if the mass at the pixel has exceeded the mass
         limit, this ensures that the enough has accumulated
    
    Args:
        precipitation - precipitation values
        perc_snow - precent of precipitation that was snow
        time_step: step in days of the model run
        mass - threshold for the mass to start a new storm
        time - threshold for the time to start a new storm
        stormDays - if specified, this is the output from a previous run of storms
            else it will be set to the date_time value
        stormPrecip - keeps track of the total storm precip

    Created Janurary 5, 2016
    @author: Scott Havens
    '''
      
    # either preallocate or use the input
    if stormDays is None:
        stormDays = np.zeros(precipitation.shape)
        
    if stormPrecip is None:
        stormPrecip = np.zeros(precipitation.shape)
        
    
    # if there is no snow, don't reset the counter
    # This ensures that the albedo won't be reset
    stormDays += time_step
    if np.sum(perc_snow) == 0:
#         stormDays = np.add(stormDays, 1)
        stormPrecip = np.zeros(precipitation.shape)
        return stormDays, stormPrecip
    
    
    # determine locations where it has snowed
    idx = perc_snow >= ps_thresh
    
    # determine locations where the time threshold has passed
    # these areas, the stormPrecip will be set back to zero
    idx_time = stormDays >= time
    stormPrecip[idx_time] = 0
    
    # add the values to the stormPrecip
    stormPrecip[idx] =+ precipitation[idx]
    
    # see if the mass threshold has been passed
    idx_mass = stormPrecip >= mass
    
    # reset the stormDays to zero where the storm is present
    stormDays[idx_mass] = 0
    
    
    return stormDays, stormPrecip
      
    