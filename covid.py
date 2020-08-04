# -*- coding: utf-8 -*-

# import tools
import pandas as pd
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# read data for cases and deaths
cases = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv")
deaths = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv")

# include only US Mainland
cases = cases[cases['iso2'] == 'US']
deaths = deaths[deaths['iso2'] == 'US']

# create distribution maps
cases_map = px.scatter_mapbox(cases, lat="Lat", lon="Long_", hover_name="Admin2", hover_data=["Province_State"], size=cases.iloc[:,-1], labels={"size":"Confirmed"}, zoom=3.5, center={"lat": 38.0902, "lon": -95.7129}, title="Current Distribution of Confirmed Cases", height=800)
cases_map.update_layout(mapbox_style="carto-darkmatter")

death_map = px.scatter_mapbox(deaths, lat="Lat", lon="Long_", hover_name="Admin2", hover_data=["Province_State"], size=deaths.iloc[:,-1], labels={"size":"Deaths"}, zoom=3.5, color_discrete_sequence=["red"], center={"lat": 38.0902, "lon": -95.7129}, title="Current Distribution of Confirmed Deaths", height=800)
death_map.update_layout(mapbox_style="carto-darkmatter")

# create a dataframe with any state's cases
def state_cases(state):
    state_df = cases[cases['Province_State']==state]
    state_df = state_df.iloc[:,11:len(cases.columns)]
    state_df = state_df.sum(axis=0)
    return state_df
    

# create a dataframe with any state's deaths
def state_deaths(state):
    deaths_df = deaths[deaths['Province_State']==state]
    deaths_df = deaths_df.iloc[:,12:len(cases.columns)]
    deaths_df = deaths_df.sum(axis=0)
    return deaths_df

# create a dataframe with every state's daily case count total
cases_df = state_cases("Alabama").to_frame(name="Arizona")
for state in cases['Province_State'].unique().tolist():
    cases_df[state] = state_cases(state)
cases_df['United States'] =  cases_df.sum(axis=1)

# get daily change in cases
delta_cases = cases_df.diff()

# create a dataframe with every state's daily death count total
deaths_df = state_deaths("Alabama").to_frame(name="Arizona")
for state in deaths['Province_State'].unique().tolist():
    deaths_df[state] = state_deaths(state)
deaths_df['United States'] = deaths_df.sum(axis=1)

# get daily change in deaths
delta_deaths = deaths_df.diff()

# get 3 day rolling averages
rolling_cases = delta_cases.rolling(7).mean()
rolling_deaths = delta_deaths.rolling(7).mean()


states = cases_df.columns.tolist()

app=dash.Dash()
app.layout=html.Div([
                html.H1("COVID-19 Dashboard"),
                html.Div([
                    html.P("Choose State: "),
                    dcc.Dropdown(
                        id='dropdown',
                        options=[{'label':state, 'value':state} for state in states],
                        value='United States',
                        multi=True
                    ),
                    dcc.RadioItems(
                        id='radio',
                        options=[{'label':i, 'value':i} for i in ['Cases','Deaths']],
                        value='Cases'
                    )
                ]),
                html.Div([
                    dcc.Graph(id='the_line')
                ]),
                html.Div([
                    html.P("Choose State: "),
                    dcc.Dropdown(
                        id='dropdown1',
                        options=[{'label':state, 'value':state} for state in states],
                        value='United States',
                        multi=True
                    ),
                    dcc.RadioItems(
                        id='radio1',
                        options=[{'label':i, 'value':i} for i in ['Daily Change in Cases', 'Daily Change in Deaths']],
                        value='Daily Change in Cases'
                    )
                ]),
                html.Div([
                    dcc.Graph(id='delta_line')
                ]),
                html.Div([
                    dcc.Graph(
                        id='cases_map',
                        figure=cases_map
                    )
                ]),
                html.Div([
                    dcc.Graph(
                        id='deaths_map',
                        figure=death_map
                    )
                ])
            ])

@app.callback(
    Output(component_id='the_line', component_property='figure'),
    [Input(component_id='dropdown', component_property='value'),
    Input(component_id='radio', component_property='value')])
def update_graph(dropdown, radio):
    cases_copy = cases_df
    deaths_copy = deaths_df
    
    if radio=='Cases':
        state_line = px.line(cases_df[dropdown], labels={"index":"Date","value":"Confirmed Cases"}, title="COVID-19 Progression")
        return state_line
    else:
        death_line = px.line(deaths_df[dropdown], labels={"index":"Date","value":"Confirmed Deaths"}, title="COVID-19 Progression")
        return death_line
    
@app.callback(
    Output(component_id='delta_line', component_property='figure'),
    [Input(component_id='dropdown1', component_property='value'),
     Input(component_id='radio1', component_property='value')])
def update_graph1(dropdown1, radio1):
    cases_copy = cases_df
    deaths_copy = deaths_df
    
    if radio1=='Daily Change in Cases':
        delta_case_line = px.line(rolling_cases[dropdown1], labels={"index":"Date","value":"Daily Change in Cases"}, title="7-Day Rolling Average of Daily Change in Cases")
        return delta_case_line
    else:
        delta_death_line = px.line(rolling_deaths[dropdown1], labels={"index":"Date","value":"Daily Change in Deaths"}, title="7-Day Rolling Average of Daily Change in Deaths")
        return delta_death_line
        
    
app.run_server(debug=True, use_reloader=False)