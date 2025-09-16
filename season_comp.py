import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
import warnings
from soccer_functions import (clean_col_names, filter_team, numeric_cols,
                              better_add_opp, snake_columns)

warnings.filterwarnings('ignore')

app = dash.Dash(__name__)
server = app.server

# read in data and clean column names
fall_2024_stats = pd.read_csv('data/team_stats_uconn_huskies_fall_2024.csv')
fall_2024_stats = clean_col_names(fall_2024_stats)
fall_2024_stats = better_add_opp(fall_2024_stats)

fall_2025_stats = pd.read_csv('data/team_stats_uconn_huskies_fall_2025.csv')
fall_2025_stats = clean_col_names(fall_2025_stats)
fall_2025_stats = better_add_opp(fall_2025_stats)

# Concatanate 2024 and 2025 together
season_comp = pd.concat([fall_2025_stats, fall_2024_stats]).reset_index(drop=True)

# Filter to only UConn rows
season_comp = filter_team(season_comp)

# columns to snake case
snake_columns(season_comp)

season_comp = season_comp.reset_index(drop=True)

# Engineer year variable
season_comp['date'] = pd.to_datetime(season_comp['date'])
season_comp.insert(4, 'year', season_comp['date'].dt.year)


# derive result if game is in 2025, else evualuate to '2024'
season_comp['result'] = np.where(
    season_comp['goals'] > season_comp['conceded_goals'], 'win',
    np.where(season_comp['goals'] == season_comp['conceded_goals'], 'draw', 'loss')
)
season_comp['result_2025'] = np.where(season_comp['year'] == 2025, season_comp['result'], '2024')

# derive opponent from match column
my_team = "UCONN Huskies"

# Split match into components
season_comp[['home_team', 'rest']] = season_comp['match'].str.split(' - ', expand=True)
season_comp[['away_team', 'score']] = season_comp['rest'].str.extract(r'(.+?) (\d+:\d+)$')
season_comp.drop(columns='rest', inplace=True)

# Determine opponent
season_comp['opponent'] = season_comp.apply(
    lambda row: row['away_team'] if row['home_team'] == my_team else (
                row['home_team'] if row['away_team'] == my_team else None),
    axis=1
)

# Back to title case and rename specific columns
season_comp.columns = season_comp.columns.str.replace('_', ' ').str.title()
mapper = {'Passes To Final Third Accurate': 'Final Third Entries',
          'Ppda': 'PPDA', 'Xg': 'xG', 'Crosses Accurate': 'Completed Crosses',
          'Accurate Passes': 'Completed Passes'}
mapper_opp = {}
for key, value in mapper.items():
    mapper_opp['Opp ' + key] = 'Opp ' + value

season_comp = season_comp.rename(columns=mapper, inplace=False)
season_comp = season_comp.rename(columns=mapper_opp, inplace=False)

app.layout = html.Div(className = 'wrapper', children = [
    html.H1('Game Comparison Tool', className = 'main-title'),
    html.H3('How to use:'),
    html.Ul(children=[html.Li('Select variables for the x and y axis using the dropdowns'),
                      html.Li('Hover over the individual points for more detailed information'),
                      html.Li('Games in light gray are from the 2024 season'),
                      html.Li('Click on criterias in the legend to filter out such points')]),
    html.Label('Select X Variable', className = 'label'),
    dcc.Dropdown(season_comp.columns[7:213], id='x-axis', value='Final Third Entries',
                 style={'width': '50%'}),
    html.Br(),
    html.Label('Select Y Variable', className = 'label'),
    dcc.Dropdown(season_comp.columns[7:213], id='y-axis', value='PPDA',
                 style={'width': '50%'}),
    dcc.Graph(id='scatter-plot')
])

@app.callback(
    Output('scatter-plot', 'figure'),
    Input('x-axis', 'value'),
    Input('y-axis', 'value')
)
def update_plot(x_var, y_var):
    # Define color mapping
    color_map = {
        '2024': '#DDDDDD',
        'win': 'green',
        'draw': 'gray',
        'loss': 'red'
    }

    # Apply color mapping
    season_comp['color'] = season_comp['Result 2025'].map(color_map)

    # Create label column only for year == 2025
    season_comp['label'] = season_comp.apply(
        lambda row: row['Opponent'][:3] if row['Year'] == 2025 and pd.notnull(row['Opponent']) else '',
        axis=1
    )

    # Create tooltip text
    season_comp['tooltip_text'] = season_comp.apply(
        lambda row: f"{row['Home Team']} {str(row['Score'])[0]} - {row['Away Team']} {str(row['Score'])[2]}",
        axis=1
    )


    # Create scatter plot
    fig = px.scatter(
        season_comp,
        x=x_var,
        y=y_var,
        color=season_comp['Result 2025'],  # for legend grouping
        color_discrete_map=color_map,
        text='label',  # this will show labels on hover and optionally on plot
        hover_name='tooltip_text',
        hover_data={
            x_var:True,
            y_var:True,
            'label':False,
            'Result 2025':False
        },
        category_orders={'Result 2025': ['win', 'draw', 'loss', '2024']}
    )

    # Customize label display
    fig.update_traces(
        textposition='top center',
        textfont=dict(size=12),
        marker=dict(size=12, line=dict(width=0.5, color='black'))
    )

    # Add axis labels
    fig.update_layout(
        xaxis_title=x_var,
        yaxis_title=y_var,
        xaxis=dict(
            showgrid=False,
            gridcolor='black',
            ticks='outside',
            showline=True,
            linecolor='black'
        ),
        yaxis=dict(
            showgrid=False,
            gridcolor='black',
            ticks='outside',
            showline=True,
            linecolor='black'
        ),
        showlegend=True,
        legend_title_text='Match Result',
        plot_bgcolor='#EFEFEF',
        paper_bgcolor='#FFFFFF',
        height=500,
        width=1200
    )
    return fig

if __name__ == '__main__':
    app.run(debug = False)