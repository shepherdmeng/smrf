'''
20121224 Scott Havens
'''

from smrf import ipw
import numpy as np
import subprocess as sp
# import threading
from multiprocessing import Process
import os
import logging

class topo():
    '''
    Class for topo images and processing those images
    Images are:
    - DEM
    - Mask
    - veg type
    - veg height
    - veg k
    - veg tau
    
    Inputs to topo() are the [topo] section of the config file
    topo() will guess the location of the TMPDIR env variable
    and should work for *nix systems
    
    Attributes:
        topoConfig: configuration for topo
        tempDir: location of temporary working directory
        dem: smrf.ipw.IPW instance for the DEM
        mask: smrf.ipw.IPW instance for the mask
        vegType: smrf.ipw.IPW instance for the veg type
        vegHeight: smrf.ipw.IPW instance for the veg height
        vegK: smrf.ipw.IPW instance for the veg K
        vegTau: smrf.ipw.IPW instance for the veg transmissivity
        ny: number of columns in DEM
        nx: number of rows in DEM
        u,v: UTM location of upper left corner
        du, dv: step size of grid
        unit: geo header units of grid
        coord_sys_ID: coordinate syste,
        x,y: position vectors
        X,Y: position grid
        stoporad_in: smrf.ipw.IPW instance for the input for stoporad
    
    '''
    
    def __init__(self, topoConfig, tempDir=None):
        self.topoConfig = topoConfig
        
        if (tempDir is None) | (tempDir == 'TMPDIR'):
            tempDir = os.environ['TMPDIR']
        self.tempDir = tempDir
        
        self._logger = logging.getLogger(__name__)
        self._logger.info('Reading [topo] and making stoporad input')
        
        # read images
        self.readImages()
        
        # calculate the necessary images for stoporad
        self.stoporadInput()
        
    def readImages(self):
        '''
        Read in the images from the config file
        '''
        
        # read in the images
        for v in self.topoConfig:
            setattr(self, v, ipw.IPW(self.topoConfig[v]))
            
        # get some general information about the model domain from the dem
        self.ny = self.dem.nlines
        self.nx = self.dem.nsamps
        self.u = self.dem.bands[0].bline
        self.v = self.dem.bands[0].bsamp
        self.du = self.dem.bands[0].dline
        self.dv = self.dem.bands[0].dsamp
        self.units = self.dem.bands[0].geounits
        self.coord_sys_ID = self.dem.bands[0].coord_sys_ID
        
        # create the x,y vectors
        self.x = self.v + self.dv*np.arange(self.nx)
        self.y = self.u + self.du*np.arange(self.ny)
        [self.X, self.Y] = np.meshgrid(self.x, self.y)
        
    def stoporadInput(self):
        '''
        Calculate the necessary input file for stoporad
        The IPW and TMPDIR environment variables must be set
        '''
            
        # calculate the skyview
        svfile = os.path.join(self.tempDir, 'sky_view.ipw')
        self._logger.debug('sky view file - %s' % svfile)
        
#         _viewf(self.topoConfig['dem'], svfile)
        ts = Process(target=_viewf, args=(self.topoConfig['dem'], svfile))
        ts.start()
            
        # calculate the gradient
        gfile = os.path.join(self.tempDir, 'gradient.ipw')
        self._logger.debug('gradient file - %s' % gfile)
        
#         _gradient(self.topoConfig['dem'], gfile)
        tg = Process(target=_gradient, args=(self.topoConfig['dem'], gfile))
        tg.start()
        
        # wait for the processes to stop
        tg.join()
        ts.join()
        
            
        # combine into a value
        sfile = os.path.join(self.tempDir, 'stoporad_in.ipw')
        self._logger.debug('stoporad in file - %s' % sfile)
        
        cmd = 'mux %s %s %s > %s' % (self.topoConfig['dem'],
                                                  gfile,
                                                  svfile,
                                                  sfile)
        proc = sp.Popen(cmd, shell=True).wait()
        
        if proc != 0:
            raise OSError('mux for stoporad_in.ipw failed')
            
        # read in the stoporad file to store in memory
        self.stoporad_in = ipw.IPW(sfile)
        
        # clean up the TMPDIR
        os.remove(gfile)
        os.remove(svfile)
        os.remove(sfile)
        
        
        
def _gradient(demFile, gradientFile):
    # calculate the gradient
    cmd = 'gradient %s > %s' % (demFile, gradientFile)
    proc = sp.Popen(cmd, shell=True).wait()
    
    if proc != 0:
        raise OSError('gradient failed')    
    
    
def _viewf(demFile, viewfFile):
    # calculate the sky view file
    cmd = 'viewf %s > %s' % (demFile, viewfFile)
    proc = sp.Popen(cmd, shell=True).wait()
    
    if proc != 0:
        raise OSError('viewf failed')   
    
        
        
