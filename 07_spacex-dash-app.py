# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# map dict of options for task 1
spacex_dict = [{'label': 'All Sites', 'value': 'ALL'}]
for site in spacex_df['Launch Site'].unique():
        spacex_dict.append({
        'label': site,
        'value':site
    })

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
                                    #options=spacex_dict,
                                    options=[
                                    {'label': 'All Sites', 'value': 'All Sites'},
                                    {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                    {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                    {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                    {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
                                ],
                                    value='ALL',
                                    placeholder= 'Select launch site',
                                    searchable=True
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0,
                                    max=10000,
                                    step=1000,
                                    value=[min_payload, max_payload]
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df

    if entered_site is None or entered_site == 'All Sites':
        title = 'Total successful launches by site'

        filtered_df = spacex_df[spacex_df['class'] == 1]
        pie_data = filtered_df.groupby('Launch Site').size().reset_index(name='Count')

        values = 'Count'
        names = 'Launch Site'
        data = pie_data
    else:
        title = f'Total launch outcomes for site: {entered_site}'

        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        pie_data = filtered_df['class'].value_counts().rename(index={0: 'Failed', 1: 'Successful'}).reset_index()
        pie_data.columns = ['Outcome', 'Count']

        values = 'Count'
        names = 'Outcome'
        data = pie_data

    print(f"Site selected: {entered_site}")
    print(f"Pie data:\n{data}")

    if data.empty:
        fig = px.pie()
        fig.update_layout(title="No data available for this selection.")
        return fig

    fig = px.pie(
        data,
        values=values,
        names=names,
        title=title,
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'), Input('payload-slider', 'value')]
)
def get_scatter(entered_site, slider_value):
    print(entered_site)
    print(slider_value)
# A If-Else statement to check if ALL sites were selected or just a specific launch site was selected
# If ALL sites are selected, render a scatter plot to display all values for variable Payload Mass (kg) and variable class.
# In addition, the point color needs to be set to the booster version i.e., color="Booster Version Category"
# If a specific launch site is selected, you need to filter the spacex_df first, and render a scatter chart to show
# values Payload Mass (kg) and class for the selected site, and color-label the point using Boosster Version Category likewise.
    low, high = slider_value

    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]

    if entered_site is None or entered_site == 'All Sites':
        title = 'Success by Payload for All Sites'
    else:
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        title = f'Success by Payload for Site: {entered_site}'

    # Create scatter plot
    scatter = px.scatter(
        data_frame=filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=title,
        hover_data=['Launch Site', 'Payload Mass (kg)', 'class']
    )
    
    # Update y-axis to show "Failure"/"Success"
    scatter.update_layout(
        yaxis=dict(
            tickmode='array',
            tickvals=[0, 1],
            ticktext=['Failure', 'Success']
        )
    )

    return scatter

# Run the app
if __name__ == '__main__':
    app.run()
