"""
Collection of functions that operate on the DEM
"""

import numpy as np
from scipy import ndimage

__author__ = "Scott Havens"
__maintainer__ = "Scott Havens"
__email__ = "scott.havens@ars.usda.gov"
__date__ = "2017-09-03"


def slope_aspect_horn1981(dem, x, y):
    """
    Calculate the slope and aspect for the DEM. The calculation of
    slope is based on Horn 1981 :cite:`Horn1981` and is similar to 
    what ArcGIS implements.
    
    Take the example 3x3 DEM, the slope and aspect at point e are
    
    | a | b | c |
    | d | e | f |
    | g | h | i | 
    
    .. math::
        \frac{dz}{dx} = \frac{(c + 2f + i) - (a + 2d + g)}{8 * cell_x}
        \frac{dz}{dy} = \frac{(g + 2h + i) - (a + 2b + c)}{8 * cell_x}
        
        slope = tan^{-1}\left( \sqrt(\frac{dz}{dx}^2 + \frac{dz}{dy}^2 \right)
        aspect = (\frac{180}{pi} * atan2 (\frac{dz}{dy}, -\frac{dz}{dx})
    
    Args:
        dem: np.ndarray of elevation data
        x: vector containing the x values cooresponding to dem
        y: vector containing the y values cooresponding to dem
        
    Returns:
        slope and aspect, slope is in degrees from horizontal
    """
    
    cell_x = np.mean(np.diff(x))
    cell_y = np.mean(np.diff(y))
    
    xKernel = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
    yKernel = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
    
    dz_dx = (ndimage.convolve(dem, xKernel)) / 8
    dz_dy = (ndimage.convolve(dem, yKernel)) / 8
    
    # divide by cell size
    dx = dz_dx / cell_x
    dy = dz_dy / cell_y
    
    # calculate the slope
    s_tangent = (np.sqrt((dx * dx) + (dy * dy)))
    
    # calculate aspect
    aspect = 180/np.pi * np.arctan2(dz_dx, (-1) * dz_dy)
    aspect[(aspect < 0.00)] = (360.00    - (90.00 - aspect[(aspect < 0.00)])) + 90
    aspect[s_tangent == 0] = -1
    
    # the slope calculated is in radians, so convert to degrees from horizontal
    s = 180/np.pi * np.arctan(s_tangent)
    
    return s, aspect

    
    