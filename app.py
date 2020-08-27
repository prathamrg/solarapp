import dash
import dash_core_components as dcc
import dash_table as dt
import dash_html_components as html
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
import pandas as pd

from pvgeneration import *

app = dash.Dash(__name__)
server = app.server
app.css.config.serve_locally = False
app.css.append_css({'external_url': 'https://codepen.io/amyoshino/pen/jzXypZ.css'})

    
app.layout = html.Div([
    html.Div([
        html.H1('Solar PV Generation Forecaster Dashboard', className = 'seven columns')
        ], 
        className = 'row'),
    html.Div([
        html.Div([
            html.Div(dcc.Input(id='lat', placeholder='Latitude (Ex: 39.7423)', 
                    className = 'two columns')),
            html.Div(dcc.Dropdown(id='pvmanf', options=[
                                                                    {'label': 'Sandia', 'value': 'SandiaMod'}
                                                               ], placeholder='PV Module Manufacturer: (Ex: Sandia)'), 
                    className = 'five columns')
            ], 
            className = 'row'),
        html.Div([
            html.Div(dcc.Input(id='lon', placeholder='Longitude (Ex: 105.1785)', 
                    className = 'two columns')),
            html.Div(dcc.Dropdown(id='pvmodel', options=[
                                                                    {'label': 'Canadian_Solar_CS5P_220M___2009_', 'value': 'Canadian_Solar_CS5P_220M___2009_'}
                                                               ], placeholder='PV Module Model: (Ex: Canadian_Solar_CS5P_220M___2009_)'), 
                    className = 'five columns'),
            
            ], 
            className = 'row'),
       html.Div([
            html.Div(dcc.Input(id='surface_tilt', placeholder='Surface Tilt (Ex: 30)', 
                    className = 'two columns')),
            html.Div(dcc.Dropdown(id='invmanf', options=[
                                                                    {'label': 'Sandia', 'value': 'sandiainverter'}
                                                               ], placeholder='Inverter Manufacturer: (Ex: Sandia)'), 
                    className = 'five columns'),
            
            ], 
            className = 'row'),
       html.Div([
            html.Div(dcc.Input(id='surface_azimuth', placeholder='Surface Azimuth (Ex: 180)', 
                    className = 'two columns')),
            html.Div(dcc.Dropdown(id='invmodel', options=[
                                                                    {'label': 'ABB__MICRO_0_25_I_OUTD_US_208__208V_', 'value': 'ABB__MICRO_0_25_I_OUTD_US_208__208V_'}
                                                               ], placeholder='Inverter Model: (Ex: ABB__MICRO_0_25_I_OUTD_US_208__208V_)'), 
                    className = 'five columns'),
            
            ], 
            className = 'row'),
       html.Div([
            html.Div(dcc.Input(id='albedo', placeholder='Albedo (Ex: 0.2)', 
                    className = 'two columns')),
            html.Div(dcc.Dropdown(id='fm', options=[
                                                                    {'label': 'GFS', 'value': 'GFS'},
                                                                    {'label': 'NAM', 'value': 'NAM'},
                                                                    {'label': 'NDFD', 'value': 'NDFD'},
                                                                    {'label': 'RAP', 'value': 'RAP'},
                                                                    {'label': 'HRRR', 'value': 'HRRR'},
                                                               ], placeholder='NWP Forecasting Model (Ex: GFS)'), 
                    className = 'five columns'),
            
            ], 
            className = 'row'),
       html.Div([html.Div(id='id',title='')],className = 'row'),
       html.Div([
               #html.H6(children='Days ahead:', 
               #     className = 'one columns'),
               html.Div([
                    html.Button('Run/Clear Forecasts', id='run_forecasts'),
                
                ],className = 'two columns'),
               html.Div([
                    dcc.Slider(
                                id='daysahead',
                                min=1,
                                max=21,
                                step=1,
                                value=7,
                                marks={
                                1: '1-day ahead',
                                7: '7=days ahead',
                                14: '14-days ahead',
                                21: '21-days ahead'
                            },
                            ),
                    ], 
                    className = 'five columns')
                
            ], className = 'row'
              ),
       
       #html.Div([html.Button('Clear', id='clear', className='one column')], className='row'),
       html.H4(id='op1', className='row'),
       
        
        
       
       
       ], className = 'row'),
       
       
    html.Div([
        dcc.Graph(id='graph1', className='seven columns'),#, figure=initial_render(1)),
        dcc.Graph(id='graph2', className='five columns' ),#, figure=initial_render(2)),
    ], className = 'row'),                                #
    html.Div([                                            #
        dcc.Graph(id='graph3', className='four columns' ),#, figure=initial_render(3)),                                            
        dcc.Graph(id='graph4', className='four columns' ),#, figure=initial_render(4)), 
        dcc.Graph(id='graph5', className='four columns' )#, figure=initial_render(5)),
    ], className = 'row')
       
], id='container')


def initial_render():
    df  = pd.read_csv('data_dc_out.csv')
    df2 = pd.read_csv('data_ac_out.csv')
    df3 = pd.read_csv('data_poa_irrad.csv')
    df4 = pd.read_csv('data_pvtemp.csv')
    
    df.rename(columns={'Unnamed: 0':'date'},inplace=True)
    df2.rename(columns={'Unnamed: 0':'date', '0':'p_ac'},inplace=True)
    df3.rename(columns={'Unnamed: 0':'date'},inplace=True)
    df4.rename(columns={'Unnamed: 0':'date', '0':'pvtemp'},inplace=True)

    fig1 = go.Figure(layout = {'title': 'Irradiance (Wm^-2)'}, 
                                        data=[go.Scatter(x=df3.index, y=df3['poa_global'], name='poa_global'), 
                                              go.Scatter(x=df3.index, y=df3['poa_direct'], name='poa_direct'),
                                              go.Scatter(x=df3.index, y=df3['poa_diffuse'], name='poa_diffuse'),
                                              go.Scatter(x=df3.index, y=df3['poa_sky_diffuse'], name='poa_sky_diffuse'),
                                              go.Scatter(x=df3.index, y=df3['poa_ground_diffuse'], name='poa_ground_diffuse'),
                                              ])
    fig2 = go.Figure(layout = {'title': 'PV Module Temperature (degree Celcius)'}, 
                                data=[go.Scatter(x=df4.index, y=df4['pvtemp'])  
                                      ])                                  
                                      
    fig3 = go.Figure(layout = {'title': 'Open-Circuit & MPP Voltages (V)'}, 
                                data=[go.Scatter(x=df.index, y=df['v_oc'], name='v_oc'), 
                                      go.Scatter(x=df.index, y=df['v_mp'], name='v_mp')
                                      ])
    fig4 = go.Figure(layout = {'title': 'Short-Circuit & MPP Currents (A)'}, 
                                data=[go.Scatter(x=df.index, y=df['i_sc'], name='i_sc'), 
                                      go.Scatter(x=df.index, y=df['i_mp'], name='i_mp')
                                      ])
    fig5 = go.Figure(layout = {'title': 'DC and AC MPP Power (W)'}, 
                                data=[go.Scatter(x=df.index, y=df['p_mp'], name='DC p_mp'), 
                                      go.Scatter(x=df2.index, y=df2, name='AC p_mp')
                                      ])
    #return_object = {1:fig1, 2:fig2, 3:fig3, 4:fig4, 5:fig5}                                
    #return return_object[graph_id]
    return fig1, fig2, fig3, fig4, fig5



@app.callback(
    [
        Output('op1','children'),
        Output('graph1','figure'),
        Output('graph2','figure'),
        Output('graph3','figure'),
        Output('graph4','figure'),
        Output('graph5','figure')
    ],
    [
        Input('run_forecasts', 'n_clicks')
    ],
    [
        State('lat', 'value'),
        State('lon', 'value'),
        State('surface_tilt', 'value'),
        State('surface_azimuth', 'value'),
        State('albedo', 'value'),
        State('pvmanf', 'value'),
        State('pvmodel', 'value'),
        State('invmanf', 'value'),
        State('invmodel', 'value'),
        State('fm', 'value'),
        State('daysahead', 'value'),
        
    ])

def update_output(n_clicks, lat, lon, surface_tilt, surface_azimuth, albedo, 
                    pvmanf, pvmodel, invmanf, invmodel, fm, daysahead):
    
    fig1 = go.Figure(layout = {'title': 'Irradiance (Wm^-2)'})
    fig2 = go.Figure(layout = {'title': 'PV Module Temperature (degree Celcius)'}) 
    fig3 = go.Figure(layout = {'title': 'Open Circuit & MPP Voltages (V)' })
    fig4 = go.Figure(layout = {'title': 'Short-Circuit & MPP Currents (A)'})
    fig5 = go.Figure(layout = {'title': 'DC and AC MPP Power (W)'})
    
    if not n_clicks:
        #return 'Solar pv-generation forecasts', fig1, fig2, fig3, fig4, fig5
        fig1, fig2, fig3, fig4, fig5 = initial_render()
        return '1-day ahead solar pv-generation forecasts for NREL - Boulder, Colorado (39.7423N, 105.1785W)', fig1, fig2, fig3, fig4, fig5
    elif n_clicks%2 == 0:
        return 'Solar pv-generation forecasts', fig1, fig2, fig3, fig4, fig5
    
    else:
        poa_irrad, pvtemp, dc_out, ac_out = get_forecasts(float(lat),float(lon),float(surface_tilt),float(surface_azimuth),float(albedo),
                                                          {'pvmanf':pvmanf,
                                                          'pvmodel':pvmodel},
                                                          {'invmanf':invmanf,
                                                          'invmodel':invmodel},
                                                          fm,int(daysahead))

        
        df = dc_out
        df2 = ac_out
        df3 = poa_irrad
        df4 = pvtemp
        
        '''
        df = pd.read_csv('dc_out.csv')
        df2 = pd.read_csv('ac_out.csv')
        df3 = pd.read_csv('poa_irrad.csv')
        df4 = pd.read_csv('pvtemp.csv')
        
        df.rename(columns={'Unnamed: 0':'date'},inplace=True)
        df2.rename(columns={'Unnamed: 0':'date', '0':'p_ac'},inplace=True)
        df3.rename(columns={'Unnamed: 0':'date'},inplace=True)
        df4.rename(columns={'Unnamed: 0':'date', '0':'pvtemp'},inplace=True)
        '''
        fig1 = go.Figure(layout = {'title': 'Irradiance (Wm^-2)'}, 
                                    data=[go.Scatter(x=df3.index, y=df3['poa_global'], name='poa_global'), 
                                          go.Scatter(x=df3.index, y=df3['poa_direct'], name='poa_direct'),
                                          go.Scatter(x=df3.index, y=df3['poa_diffuse'], name='poa_diffuse'),
                                          go.Scatter(x=df3.index, y=df3['poa_sky_diffuse'], name='poa_sky_diffuse'),
                                          go.Scatter(x=df3.index, y=df3['poa_ground_diffuse'], name='poa_ground_diffuse'),
                                          ])
        fig2 = go.Figure(layout = {'title': 'PV Module Temperature (degree Celcius)'}, 
                                    data=[go.Scatter(x=df4.index, y=df4)  
                                          ])                                  
                                          
        fig3 = go.Figure(layout = {'title': 'Open-Circuit & MPP Voltages (V)'}, 
                                    data=[go.Scatter(x=df.index, y=df['v_oc'], name='v_oc'), 
                                          go.Scatter(x=df.index, y=df['v_mp'], name='v_mp')
                                          ])
        fig4 = go.Figure(layout = {'title': 'Short-Circuit & MPP Currents (A)'}, 
                                    data=[go.Scatter(x=df.index, y=df['i_sc'], name='i_sc'), 
                                          go.Scatter(x=df.index, y=df['i_mp'], name='i_mp')
                                          ])
        fig5 = go.Figure(layout = {'title': 'DC and AC MPP Power (W)'}, 
                                    data=[go.Scatter(x=df.index, y=df['p_mp'], name='DC p_mp'), 
                                          go.Scatter(x=df2.index, y=df2, name='AC p_mp')
                                          ])                                  
        return '{}-day(s) ahead solar pv-generation forecasts:'.format(daysahead), fig1, fig2, fig3, fig4, fig5 
      
        
        

if __name__ == '__main__':
    app.run_server(debug=True)