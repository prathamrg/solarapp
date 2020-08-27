from pvgeneration import *

if __name__ == '__main__':
    poa_irrad, pvtemp, dc_out, ac_out = get_forecasts(latitude=39.7423,longitude=105.1785,
                                                      surface_tilt=30,surface_azimuth=180,albedo=0.2,
                                                      pvmoduledata={'pvmanf':'SandiaMod', 'pvmodel':'Canadian_Solar_CS5P_220M___2009_'},
                                                      inverterdata={'invmanf':'sandiainverter','invmodel':'ABB__MICRO_0_25_I_OUTD_US_208__208V_'},
                                                      fm='GFS',daysahead=1)
    
    df = dc_out
    df2 = ac_out
    df3 = poa_irrad
    df4 = pvtemp

    df.to_csv('.\\initial_data\\dc_out.csv')
    df2.to_csv('.\\initial_data\\ac_out.csv')
    df3.to_csv('.\\initial_data\\poa_irrad.csv')
    df4.to_csv('.\\initial_data\\pvtemp.csv')

'''
        
'''