import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import timedelta
import warnings
from soccer_functions import (clean_col_names, filter_team, numeric_cols,
                              better_add_opp, snake_columns)

warnings.filterwarnings('ignore')

app = dash.Dash(__name__)
server = app.server
app.title = "UConn Women's Soccer | Game Comparison Tool"

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
                      html.Li('Select whether to show mean lines and what season(s) to take the average of'),
                      html.Li('See game boxes below the graph for game comparison purposes'),
                      html.Li('Click on criterias in the legend to filter out such points')]),
    html.Label('Select X Variable', className = 'label'),
    dcc.Dropdown(season_comp.columns[7:213], id='x-axis', value='Final Third Entries',
                 style={'width': '50%'}),
    html.Br(),
    html.Label('Select Y Variable', className = 'label'),
    dcc.Dropdown(season_comp.columns[7:213], id='y-axis', value='PPDA',
                 style={'width': '50%'}),
    html.Br(),
    html.Div([html.Label('Select Mean Lines'),
        dcc.RadioItems(id='mean-line-mode',
        options=[
            {'label': 'None', 'value': 'none'},
            {'label': '2024 and 2025 Games', 'value': 'all'},
            {'label': '2025 Games Only', 'value': 'filtered'},
        ],
        value='none',  # default selection
        labelStyle={'display': 'inline-block', 'margin-right': '30px'}  # horizontal layout
    )], style={'width': '34%'}),
    dcc.Graph(id='scatter-plot'),
    html.Br(),
    html.Div(id = 'gbs', className = 'gbsection', children = [
        html.Div(className = 'box ' + str(season_comp.loc[season_comp['Result 2025'] != '2025', 'Result 2025'][i]), children = [
            html.H4(season_comp.loc[i, 'Opponent'], className='oppteamname')
            ] + [
            html.H4((season_comp.loc[i, 'Date'] - timedelta(days=1)).strftime("%m/%d/%y"), className='gamedate')
            ] + [
            html.P('x', id = 'game' + str(i) + str(j)) for j in range(2)
        ])
    for i in range(len(fall_2025_stats)//2)])
])

@app.callback(
    Output('scatter-plot', 'figure'),
    Input('x-axis', 'value'),
    Input('y-axis', 'value'),
    Input('mean-line-mode', 'value')
)
def update_plot(x_var, y_var, mean_line_mode):
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

    # add mean lines (conditionally)
    if mean_line_mode != 'none':

        if mean_line_mode == 'all':
            x_mean = season_comp[x_var].mean()
            y_mean = season_comp[y_var].mean()
        elif mean_line_mode == 'filtered':
            x_mean = season_comp.loc[season_comp['Year'] == 2025, x_var].mean()
            y_mean = season_comp.loc[season_comp['Year'] == 2025, y_var].mean()

        fig.add_shape(
            type='line',
            x0=x_mean, x1=x_mean,
            y0=season_comp[y_var].min(), y1=season_comp[y_var].max(),
            line=dict(color='black', width=1, dash='dash'),
            name='Mean X'
        )

        fig.add_shape(
            type='line',
            x0=season_comp[x_var].min(), x1=season_comp[x_var].max(),
            y0=y_mean, y1=y_mean,
            line=dict(color='black', width=1, dash='dash'),
            name='Mean Y'
        )

        fig.add_annotation(
            x=x_mean,
            y=season_comp[y_var].max(),
            text=f"Mean {x_var}: {x_mean:.2f}",
            showarrow=False,
            yshift=10,
            font=dict(size=10, color='black')
        )

        fig.add_annotation(
            x=season_comp[x_var].max(),
            y=y_mean*1.1,
            text=f"Mean {y_var}: {y_mean:.2f}",
            showarrow=False,
            xshift=-10,
            font=dict(size=10, color='black')
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


# Game Boxes
@app.callback(
    [Output('game' + str(i) + str(j), 'children') for i in range(len(fall_2025_stats)//2) for j in range(2)],
    Input('x-axis', 'value'),
    Input('y-axis', 'value')
)
def update_boxes(x_var, y_var):
    '''if intercept is None:
        intercept = 0
    if slope is None:
        slope = 0'''
    #points = pd.DataFrame({'x': range(1, 11), 'y': [intercept + (slope*x) for x in range(1, 11)]})
    x = [x_var + ' = ' + str(x) for x in season_comp.loc[season_comp['Year'] == 2025, x_var]]
    y = [y_var + ' = ' + str(y) for y in season_comp.loc[season_comp['Year'] == 2025, y_var]]
    in_order = [item for pair in zip(x, y) for item in pair]
    return tuple(in_order)

if __name__ == '__main__':
    app.run(debug = False)