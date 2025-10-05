# app_dynamic_fix.py
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd

# Load dataset
df = px.data.gapminder()
df = df.sort_values(['country','year'])
df['gdp_growth'] = df.groupby('country')['gdpPercap'].pct_change() * 100

# Initialize Dash
app = dash.Dash(__name__)
app.title = "🌍 Multi-Metric Dashboard (Dynamic Fix)"

# Layout
app.layout = html.Div([
    html.H1("🌍 Multi-Metric Dashboard", style={'textAlign':'center'}),

    html.Div([
        html.Label("Select Continent:"),
        dcc.Dropdown(
            id='continent-dropdown',
            options=[{'label': c,'value': c} for c in sorted(df['continent'].unique())],
            value='Asia', clearable=False
        ),
    ], style={'margin':'20px'}),

    html.Div([
        html.Label("Select Countries:"),
        dcc.Dropdown(id='country-dropdown', multi=True)
    ], style={'margin':'20px'}),

    html.Div([
        html.Label("Select Year:"),
        dcc.Slider(
            id='year-slider',
            min=df['year'].min(),
            max=df['year'].max(),
            value=df['year'].min(),
            marks={str(year): str(year) for year in df['year'].unique()},
            step=None
        )
    ], style={'margin':'20px'}),

    html.Div([
        html.Label("Select Chart Type:"),
        dcc.Dropdown(
            id='chart-type-dropdown',
            options=[
                {'label':'Scatter','value':'scatter'},
                {'label':'Bubble','value':'bubble'},
                {'label':'Bar','value':'bar'},
                {'label':'Histogram','value':'histogram'},
                {'label':'Line','value':'line'},
                {'label':'Choropleth','value':'choropleth'},
                {'label':'Box','value':'box'}
            ],
            value='scatter',
            clearable=False
        )
    ], style={'margin':'20px'}),

    html.Div([
        html.Label("Select X-axis Metric:"),
        dcc.Dropdown(
            id='x-metric-dropdown',
            options=[
                {'label':'GDP per Capita','value':'gdpPercap'},
                {'label':'Life Expectancy','value':'lifeExp'},
                {'label':'Population','value':'pop'},
                {'label':'GDP Growth (%)','value':'gdp_growth'}
            ],
            value='gdpPercap',
            clearable=False
        )
    ], style={'margin':'20px'}),

    html.Div([
        html.Label("Select Y-axis Metric:"),
        dcc.Dropdown(
            id='y-metric-dropdown',
            options=[
                {'label':'GDP per Capita','value':'gdpPercap'},
                {'label':'Life Expectancy','value':'lifeExp'},
                {'label':'Population','value':'pop'},
                {'label':'GDP Growth (%)','value':'gdp_growth'}
            ],
            value='lifeExp',
            clearable=False
        )
    ], style={'margin':'20px'}),

    html.Div([dcc.Graph(id='main-graph', style={'height':'700px'})])
])

# Update countries based on continent
@app.callback(
    Output('country-dropdown','options'),
    Output('country-dropdown','value'),
    Input('continent-dropdown','value')
)
def update_countries(continent):
    countries = df[df.continent==continent]['country'].unique()
    options = [{'label': c, 'value': c} for c in sorted(countries)]
    value = sorted(countries)[:3]  # default select first 3 countries
    return options, value

# Update main graph
@app.callback(
    Output('main-graph','figure'),
    Input('year-slider','value'),
    Input('continent-dropdown','value'),
    Input('country-dropdown','value'),
    Input('chart-type-dropdown','value'),
    Input('x-metric-dropdown','value'),
    Input('y-metric-dropdown','value')
)
def update_graph(year, continent, countries, chart_type, x_metric, y_metric):
    # Filter by continent, year, and selected countries
    dff = df[(df.continent==continent) & (df.year==year)]
    if countries:
        dff = dff[dff.country.isin(countries)]

    title = f"{chart_type.title()} - {year} ({continent})"

    if chart_type=='scatter':
        fig = px.scatter(dff, x=x_metric, y=y_metric, size='pop', color='country',
                         hover_name='country', log_x=(x_metric=='gdpPercap'), title=title)
    elif chart_type=='bubble':
        fig = px.scatter(dff, x='country', y=y_metric, size='pop', color=x_metric,
                         hover_name='country', title=title)
    elif chart_type=='bar':
        fig = px.bar(dff, x='country', y=y_metric, color=x_metric, title=title)
    elif chart_type=='histogram':
        fig = px.histogram(dff, x=y_metric, nbins=20, color='country', title=title)
    elif chart_type=='line':
        trend_df = df[df.continent==continent]
        if countries:
            trend_df = trend_df[trend_df.country.isin(countries)]
        fig = px.line(trend_df, x='year', y=y_metric, color='country', markers=True,
                      title=f"Line Chart - {y_metric} Trend ({continent})")
    elif chart_type=='choropleth':
        fig = px.choropleth(dff, locations='iso_alpha', color=y_metric,
                            hover_name='country', projection='natural earth', title=title)
    elif chart_type=='box':
        fig = px.box(dff, x='country', y=y_metric, color='country', title=title)
    else:
        fig = px.scatter(dff, x=x_metric, y=y_metric)
    return fig

# Run app
if __name__ == '__main__':
    app.run(debug=True)
