# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

site_dropdown_options = [
    {'label': 'All Sites', 'value': 'All'},
    {'label': 'Cape Canaveral AFS SLC-40', 'value': 'CCAFS SLC-40'},
    {'label': 'Cape Canaveral AFS LC-40', 'value': 'CCAFS LC-40'},
    {'label': 'Kennedy SC LC-39A', 'value': 'KSC LC-39A'},
    {'label': 'Vandenberg AFB SLC-4E', 'value': 'VAFB SLC-4E'}
]

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=site_dropdown_options,
                                    value='All',
                                    placeholder='Select a Launch Site',
                                    searchable=True
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0,
                                    max=10000,
                                    step=1000,
                                    value=[0, 10000]
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output

@app.callback(
    Output(component_id='success-pie', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(launch_site):
    if launch_site == 'All':
        fig = px.pie(spacex_df, values='class', names='Launch Site',
            title='Successful booster landings by Launch Site'
        )

    else:
        # Get the right data
        pie_data = spacex_df[spacex_df['Launch Site'] == launch_site]
        pie_numbers = pie_data['class'].value_counts().reset_index()
        # Make the labels readable
        pie_numbers['class'] = pie_numbers['class'].replace({0: 'Failure', 1: 'Success'})
        # Make sure Failure is always red!
        pie_numbers.sort_values(by='class', ascending=False, inplace=True)
        fig = px.pie(pie_numbers, values='count', names='class',
            title=f'Successful booster landings for {launch_site}'
        )
        # plotly sorts pie charts, screwing up the red color!
        fig.update_traces(sort=False)
    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output

@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def get_scatter_plot(launch_site, payload_slider):
    payload_select = ((spacex_df['Payload Mass (kg)'] > payload_slider[0]) & (spacex_df['Payload Mass (kg)'] < payload_slider[1]))
    if launch_site == 'All':
        scatter_data = spacex_df[payload_select]
        title = 'Landing success vs Payload Mass for all launch sites'
    else:
        scatter_data = spacex_df[spacex_df['Launch Site'] == launch_site & payload_select]
        title = f'Landing success vs Payload Mass for {launch_site}'
    fig = px.scatter(scatter_data, x='Payload Mass (kg)', y='class', color='Booster Version Category', title=title)
    return fig
    

# Run the app
if __name__ == '__main__':
    app.run_server()
