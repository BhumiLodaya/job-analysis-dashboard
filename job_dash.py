import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

# Load data
df = pd.read_csv("C:/Users/bhumi/OneDrive/Desktop/professional/internship/job/Salaries_cleaned.csv", encoding="ISO-8859-1")
df.columns = df.columns.str.strip()

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Dropdown options with 'All'
def dropdown_options(column):
    return [{'label': 'All', 'value': 'All'}] + [
        {'label': val, 'value': val} for val in sorted(df[column].dropna().unique())
    ]

# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H2("Job Analysis", style={
                'backgroundColor': '#4B0082',
                'color': 'white',
                'textAlign': 'center',
                'padding': '15px 0',
                'margin': '0',
                'width': '100%',
                'fontSize': '32px',
                'borderRadius': '0'
            })
        ], width=12)
    ], style={'marginBottom': '10px'}),

    dbc.Row([
        dbc.Col([
            html.Div([
                html.H4("Filters", style={'color': 'white', 'textAlign': 'center'}),
                html.Label("Job Category", style={'color': 'white'}),
                dcc.Dropdown(
                    id='job-filter',
                    options=dropdown_options('job_category'),
                    value='All',
                    style={'backgroundColor': 'white'}
                ),
                html.Br(),
                html.Label("Employee Residence", style={'color': 'white'}),
                dcc.Dropdown(
                    id='residence-filter',
                    options=dropdown_options('employee_residence'),
                    value='All'
                ),
                html.Br(),
                html.Label("Work Setting", style={'color': 'white'}),
                dcc.Dropdown(
                    id='setting-filter',
                    options=dropdown_options('work_setting'),
                    value='All'
                )
            ], style={'backgroundColor': '#D8BFD8', 'padding': '20px', 'borderRadius': '10px', 'marginTop': '20px'}),

            html.Br(),
            dbc.Row([
                dbc.Col(dbc.Button(id='total-jobs', className='summary-btn', color='secondary', 
                                   style={'width': '100%', 'backgroundColor': '#D8BFD8', 'color': 'white'}), width=6),
                dbc.Col(dbc.Button(id='total-job-titles', className='summary-btn', color='secondary', 
                                   style={'width': '100%', 'backgroundColor': '#D8BFD8', 'color': 'white'}), width=6),
            ], className='mb-2', style={'marginTop': '10px', 'marginLeft': '0px', 'marginRight': '0px'}),

            dbc.Row([
                dbc.Col(dbc.Button(id='total-companies', className='summary-btn', color='secondary', 
                                   style={'width': '100%', 'backgroundColor': '#D8BFD8', 'color': 'white'}), width=6),
                dbc.Col(dbc.Button(id='total-people', className='summary-btn', color='secondary', 
                                   style={'width': '100%', 'backgroundColor': '#D8BFD8', 'color': 'white'}), width=6),
            ], className='mb-2', style={'marginLeft': '0px', 'marginRight': '0px'}),

            dbc.Row([
                dbc.Col(dbc.Button(id='total-currencies', className='summary-btn', color='secondary', 
                                   style={'width': '100%', 'backgroundColor': '#D8BFD8', 'color': 'white'}), width=6),
            ], style={'marginLeft': '0px', 'marginRight': '0px'})

        ], width=3),

        dbc.Col([
            dbc.Row([
                dbc.Col(dcc.Graph(id='job-title-count'), md=6),
                dbc.Col(dcc.Graph(id='salary-currency'), md=6)
            ]),

            dbc.Row([
                dbc.Col(dcc.Graph(id='experience-dist'), md=6),
                dbc.Col(dcc.Graph(id='company-size'), md=6)
            ]),

            dbc.Row([
                dbc.Col(dcc.Graph(id='top-countries'), md=6),
                dbc.Col(dcc.Graph(id='work-setting'), md=6)
            ]),
            html.Div(id='alert-div', style={'marginTop': '10px'})
        ], width=9)
    ])
], fluid=True)

# Callback
@app.callback(
    [
        Output('job-title-count', 'figure'),
        Output('salary-currency', 'figure'),
        Output('experience-dist', 'figure'),
        Output('company-size', 'figure'),
        Output('top-countries', 'figure'),
        Output('work-setting', 'figure'),
        Output('alert-div', 'children'),
        Output('total-jobs', 'children'),
        Output('total-job-titles', 'children'),
        Output('total-companies', 'children'),
        Output('total-people', 'children'),
        Output('total-currencies', 'children')
    ],
    [
        Input('job-filter', 'value'),
        Input('residence-filter', 'value'),
        Input('setting-filter', 'value')
    ]
)
def update_graphs(job, residence, setting):
    dff = df.copy()
    if job != 'All':
        dff = dff[dff['job_category'] == job]
    if residence != 'All':
        dff = dff[dff['employee_residence'] == residence]
    if setting != 'All':
        dff = dff[dff['work_setting'] == setting]

    if dff.empty:
        alert = dbc.Alert("No such job found in that particular employee residence.", color="danger", dismissable=True, duration=4000)
        empty_fig = px.bar(title="No data")
        return empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, alert, '', '', '', '', ''

    alert = None

    total_jobs = f"Total Job Categories: {dff['job_category'].nunique()}"
    total_titles = f"Total Job Titles: {dff['job_title'].nunique()}"
    total_companies = f"Total Companies: {dff['company_location'].nunique()}"
    total_people = f"Total People Working: {len(dff)}"
    total_currencies = f"No. of Currencies: {dff['salary_currency'].nunique()}"

    job_title_data = dff['job_title'].value_counts().nlargest(10 if setting == 'All' else len(dff)).reset_index()
    job_title_data.columns = ['Job Title', 'Count']
    fig1 = px.bar(
        job_title_data,
        x='Job Title',
        y='Count',
        title='Top Job Titles',
        color_discrete_sequence=px.colors.qualitative.Set1
    )
    fig1.update_layout(xaxis_tickangle=45)

    salary_data = dff.groupby('salary_currency')['salary'].sum()
    if setting == 'All':
        salary_data = salary_data.sort_values(ascending=False).nlargest(10)
    fig2 = px.bar(x=salary_data.index, y=salary_data.values,
                  labels={'x': 'Currency', 'y': 'Total Salary'},
                  title='Total Salary by Currency', color_discrete_sequence=px.colors.qualitative.Pastel1)

    fig3 = px.histogram(dff, x='experience_level', title='Experience Level Count',
                        color_discrete_sequence=px.colors.qualitative.Prism)

    fig4 = px.histogram(dff, x='company_size', title='Company Size Count',
                        color_discrete_sequence=px.colors.qualitative.Safe)

    if residence != 'All':
        location_data = dff['company_location'].value_counts().nlargest(10)
    else:
        location_data = dff['employee_residence'].value_counts().nlargest(10)
    fig5 = px.bar(x=location_data.index, y=location_data.values,
                  title='Top 10 Company Locations' if residence != 'All' else 'Top 10 Residences',
                  labels={'x': 'Location', 'y': 'Count'},
                  color_discrete_sequence=px.colors.qualitative.Bold)
    fig5.update_layout(xaxis_tickangle=45)

    fig6 = px.histogram(dff, x='work_setting', title='Work Setting Count',
                        color_discrete_sequence=px.colors.qualitative.Vivid)

    return fig1, fig2, fig3, fig4, fig5, fig6, alert, total_jobs, total_titles, total_companies, total_people, total_currencies

if __name__ == '__main__':
    app.run(debug=True)
