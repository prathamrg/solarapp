#!/usr/bin/env python
# coding: utf-8

# # Forecast to Power Tutorial
# 
# This tutorial will walk through the process of going from Unidata forecast model data to AC power using the SAPM.
# 
# Table of contents:
# 1. [Setup](#Setup)
# 2. [Load Forecast data](#Load-Forecast-data)
# 2. [Calculate modeling intermediates](#Calculate-modeling-intermediates)
# 2. [DC power using SAPM](#DC-power-using-SAPM)
# 2. [AC power using SAPM](#AC-power-using-SAPM)
# 
# This tutorial requires pvlib >= 0.6.0.
# 
# Authors:
# * Derek Groenendyk (@moonraker), University of Arizona, November 2015
# * Will Holmgren (@wholmgren), University of Arizona, November 2015, January 2016, April 2016, July 2016, August 2018

# ## Setup

import datetime
import inspect
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

from pvlib import solarposition, irradiance, atmosphere, pvsystem, inverter, temperature
from pvlib.forecast import GFS, NAM, NDFD, RAP, HRRR




def get_weather_data(latitude, longitude, start, end, fm):
    # Retrieve data
    # ## Load the Forecast data
    # pvlib forecast module only includes several models. To see the full list of forecast models visit the Unidata website: 
    # http://www.unidata.ucar.edu/data/#tds
    forecast_data = fm.get_processed_data(latitude, longitude, start, end)
    forecast_data.head()
    return forecast_data



def get_solpos(forecast_data,fm):
    # Calculate the solar position for all times in the forecast data. 
    # The default solar position algorithm is based on Reda and Andreas (2004). Our implementation is pretty fast, but you can make it even faster if you install [``numba``](http://numba.pydata.org/#installing) and use add  ``method='nrel_numba'`` to the function call below.
    time = forecast_data.index
    a_point = fm.location
    solpos = a_point.get_solarposition(time)
    return solpos
    
def get_dni_extra(fm):
    # Calculate extra terrestrial radiation. This is needed for many plane of array diffuse irradiance models.
    dni_extra = irradiance.get_extra_radiation(fm.time)
    return dni_extra

def get_airmass(solpos):
    # Calculate airmass. Lots of model options here, see the ``atmosphere`` module tutorial for more details.
    airmass = atmosphere.get_relative_airmass(solpos['apparent_zenith'])
    return airmass


def get_poa_sky_diffuse(surface_tilt, surface_azimuth, forecast_data, dni_extra, solpos):
    # Use the Hay Davies model to calculate the plane of array diffuse sky radiation.
    poa_sky_diffuse = irradiance.haydavies(surface_tilt, surface_azimuth,
                                       forecast_data['dhi'], forecast_data['dni'], dni_extra,
                                       solpos['apparent_zenith'], solpos['azimuth'])
    return poa_sky_diffuse


def get_poa_ground_diffuse(surface_tilt, forecast_data, albedo):
    # Calculate ground diffuse. We specified the albedo above. You could have also provided a string to the ``surface_type`` keyword argument.
    poa_ground_diffuse = irradiance.get_ground_diffuse(surface_tilt, forecast_data['ghi'], albedo=albedo)
    return poa_ground_diffuse

def get_angle_of_incidence(surface_tilt, surface_azimuth, solpos):
    # Calculate AOI
    aoi = irradiance.aoi(surface_tilt, surface_azimuth, solpos['apparent_zenith'], solpos['azimuth'])
    return aoi

def get_total_poa(aoi, forecast_data,poa_sky_diffuse, poa_ground_diffuse):
    # Calculate Total POA irradiance
    poa_irrad = irradiance.poa_components(aoi, forecast_data['dni'], poa_sky_diffuse, poa_ground_diffuse)
    return poa_irrad

def get_cell_temp(forecast_data, poa_irrad):
    # Calculate pv cell temperature
    ambient_temperature = forecast_data['temp_air']
    wnd_spd = forecast_data['wind_speed']
    thermal_params = temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_polymer']
    pvtemp = temperature.sapm_cell(poa_irrad['poa_global'], ambient_temperature, wnd_spd, **thermal_params)
    return pvtemp

def get_pvmodule(pvmoduledata):

    # ## DC power using SAPM
    # Get module data from the web.
    pvmanf = pvmoduledata['pvmanf']
    pvmodel = pvmoduledata['pvmodel']
    modules = eval("pvsystem.retrieve_sam('{}')".format(pvmanf)) #Sandia
    # Choose a particular module
    pvmodule = eval("modules.{}".format(pvmodel)) #Canadian_Solar_CS5P_220M___2009_
    return pvmodule
    
    
def forecast_dc_power(poa_irrad, airmass, aoi, pvmodule, pvtemp):
    # Run the SAPM using the parameters we calculated above.
    effective_irradiance = pvsystem.sapm_effective_irradiance(poa_irrad.poa_direct, poa_irrad.poa_diffuse, airmass, aoi, pvmodule)
    sapm_out = pvsystem.sapm(effective_irradiance, pvtemp, pvmodule)
    return sapm_out

def get_invertermodel(inverterdata):
    # Get the inverter database from the web
    invmanf = inverterdata['invmanf']
    invmodel = inverterdata['invmodel']
    inverters = eval("pvsystem.retrieve_sam('{}')".format(invmanf)) #sandiainverter
    # Choose a particular inverter
    invertermodel = eval("inverters['{}']".format(invmodel)) #ABB__MICRO_0_25_I_OUTD_US_208__208V_
    return invertermodel
    
    
    
def forecast_ac_power(dc_out, invertermodel):
    p_ac = inverter.sandia(dc_out.v_mp, dc_out.p_mp, invertermodel)
    return p_ac



#if __name__ == '__main__':

def get_forecasts(latitude,longitude,surface_tilt,surface_azimuth,albedo,pvmoduledata,inverterdata,fm,daysahead):
 
    # Choose a location.
    # Tucson, AZ
    #latitude = 19.131347 #32.2
    #longitude = 72.918131 #-110.9
    tz = 'US/Mountain'
  
    # Define some PV system parameters.
    #surface_tilt = 30
    #surface_azimuth = 180 # pvlib uses 0=North, 90=East, 180=South, 270=West convention
    #albedo = 0.2
    
    #pv system data
    #pvmoduledata = {'pvmanf':'SandiaMod','pvmodel':'Canadian_Solar_CS5P_220M___2009_'}
    #inverterdata = {'invmanf':'sandiainverter','invmodel':'ABB__MICRO_0_25_I_OUTD_US_208__208V_'}
    
    start = pd.Timestamp(datetime.date.today(), tz=tz) # today's date
    end = start + pd.Timedelta(days=daysahead) # 7 days from today
 
    
    # Define forecast model
    fm = eval('{}()'.format(fm))
    
    forecast_data = get_weather_data(latitude, longitude, start, end, fm)
    
    # ## Calculate modeling intermediates
    # Before we can calculate power for all the forecast times, we will need to calculate:
    # * solar position 
    # * extra terrestrial radiation
    # * airmass
    # * angle of incidence
    # * POA sky and ground diffuse radiation
    # * cell and module temperatures
    
    solpos = get_solpos(forecast_data,fm)
    dni_extra = get_dni_extra(fm)
    airmass = get_airmass(solpos)
    poa_sky_diffuse = get_poa_sky_diffuse(surface_tilt, surface_azimuth, forecast_data, dni_extra, solpos)
    poa_ground_diffuse = get_poa_ground_diffuse(surface_tilt, forecast_data, albedo)
    aoi = get_angle_of_incidence(surface_tilt, surface_azimuth, solpos)
    poa_irrad = get_total_poa(aoi, forecast_data,poa_sky_diffuse, poa_ground_diffuse)
    pvtemp = get_cell_temp(forecast_data, poa_irrad)
    pvmodule = get_pvmodule(pvmoduledata)
    invertermodel = get_invertermodel(inverterdata)
    dc_out = forecast_dc_power(poa_irrad, airmass, aoi, pvmodule, pvtemp)
    ac_out = forecast_ac_power(dc_out, invertermodel)
    
    '''
    # Plots:
    
    poa_irrad.plot()
    plt.ylabel('Irradiance ($W/m^{-2}$)')
    plt.title('POA Irradiance');
    #plt.show()
    
    pvtemp.plot()
    plt.ylabel('Temperature (C)');
    #plt.show()
    
    dc_out[['p_mp']].plot()
    plt.ylabel('DC Power (W)');
    #plt.show()
    
    ac_out.plot()
    plt.ylabel('AC Power (W)')
    plt.show()
    ac_out.to_csv('ac.csv')
    '''
    return poa_irrad, pvtemp, dc_out, ac_out


