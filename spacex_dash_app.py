# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX launch data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # TASK 1: Dropdown for Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=[{'label': 'All Sites', 'value': 'ALL'}] + [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),

    # TASK 2: Pie chart for success vs failure
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    
    # TASK 3: Range Slider for Payload
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={0: '0 kg', 2500: '2500 kg', 5000: '5000 kg', 7500: '7500 kg', 10000: '10000 kg'},
        value=[min_payload, max_payload]
    ),

    # TASK 4: Scatter plot to show Payload vs. Launch Success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])


# TASK 2: Callback for the Pie Chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Calculate successful launches per site
        success_counts = spacex_df[spacex_df['class'] == 1].groupby('Launch Site').size().reset_index(name='counts')
        fig = px.pie(success_counts, values='counts', names='Launch Site', title='Total Successful Launches for All Sites')
    else:
        # Filter for a specific Launch Site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        outcome_counts = filtered_df['class'].value_counts().reset_index(name='counts')
        outcome_counts.columns = ['Outcome', 'counts']
        fig = px.pie(outcome_counts, values='counts', names='Outcome', title=f'Success vs. Failure for {entered_site}',
                     color='Outcome', color_discrete_map={1: 'green', 0: 'red'})
    return fig


# TASK 4: Callback for the Scatter Plot (Payload vs Launch Success)
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_plot(entered_site, payload_range):
    min_payload_range, max_payload_range = payload_range

    # Filter by payload range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= min_payload_range) &
        (spacex_df['Payload Mass (kg)'] <= max_payload_range)
    ]

    if entered_site != 'ALL':
        # Filter by selected Launch Site
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]

    # Create scatter plot
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=f'Payload vs Launch Outcome for {entered_site if entered_site != "ALL" else "All Sites"}',
        labels={'class': 'Launch Outcome'},
        color_discrete_sequence=px.colors.qualitative.Set1
    )

    return fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
