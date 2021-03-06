=======
History
=======

0.1.0 (2015-12-13)
------------------

* First release on PyPI.

0.2.0 (2017-05-09)
------------------

* SMRF can run with Python 3
* Fixed indexing issue in wind
* Minor Config file improvements.

0.3.0 (2017-09-08)
------------------

* New feature for backing up the input data for a run in csv.
* Major update to config file, enabling checking and default adding
* Updated C file prototypes.

0.4.0 (2017-11-14)
------------------

* Small improvements to our config file code including: types checking, relative paths to config, auto documentation
* Fixed bugs related to precip undercatch
* Improvements to ti station data backup
* Various adjustments for better collaboration with AWSM
* Moved to a new station database format


0.5.0 (2018-04-18)
------------------

* Removed inicheck to make its own package.
* Added in HRRR input data for new gridded type
* Fixed various bugs associated with precip
* Modularized some functions for easiuer use scripting
* Added netcdf functionality to gen_maxus
* Added first integration test


0.6.0 (2018-07-13)
------------------

* Added a new feature allowing wet bulb to be used to determine the phase of the precip.
* Added a new feature to redistribute precip due to wind.
* Added in kriging as a new distribution option all distributable variables.

