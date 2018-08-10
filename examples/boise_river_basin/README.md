# Boise River Basin Example (BRB)
The Boise River Basin is the watershed just outside of Boise Idaho. The
watershed is populated with many weather stations which makes it a great testing
ground for watershed models. 

## Setting up

SMRF needs a maxus file which describes how the wind will roughly behave over
the DEM. Then SMRF uses this file to distribute the wind field. To generate the
maxus file first, simply run the following command:

```
gen_maxus --out_maxus ./common_data/maxus.nc ./common_data/dem100m.ipw
```
## Running

To run the example simply enter:

```
run_smrf brb_config.ini
```

## Viewing the Data

Using ncview is an easy way to view the outputs from SMRF. For example, to look
at the precip data simply use the command:

```
ncview output/precip.nc
```

## Extended Excercises

The configuration file (```./brb_wy2017.ini```) controls everything in the
simulation. To get more familiar with how the system works try some of the
variations below:

* Open with a text editor the ```./output/config.ini``` to see all the options
that were used on this run. SMRF uses inicheck to reduces the amount of
information in a config file for options that are not changed very often.
* The data provided is for the whole water year 2017, try changing the dates to
find different weather events.
* Change the distribution scheme in the precipitation section from
```distribution: dk``` vs ```distribution: kriging``` to see what effect it has
on the data.
