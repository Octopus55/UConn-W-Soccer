import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings('ignore')

def clean_col_names(data):
    clean_cols = data.rename(columns={'Shots / on target': 'Shots',
                                    'Unnamed: 9': 'Shots On Target',
                                    'Unnamed: 10': 'Shots On Target Percentage',
                                    'Passes / accurate': 'Passes Attempted',
                                    'Unnamed: 12': 'Accurate Passes',
                                    'Unnamed: 13': 'Pass Accuracy Percentage',
                                    'Possession, %': 'Possession Percentage',
                                    'Losses / Low / Medium / High': 'Total Losses',
                                    'Unnamed: 16': 'Low Losses',
                                    'Unnamed: 17': 'Medium Losses',
                                    'Unnamed: 18': 'High Losses',
                                    'Recoveries / Low / Medium / High': 'Total Recoveries',
                                    'Unnamed: 20': 'Low Recoveries',
                                    'Unnamed: 21': 'Medium Recoveries',
                                    'Unnamed: 22': 'High Recoveries',
                                    'Duels / won': 'Total Duels',
                                    'Unnamed: 24': 'Duels Won',
                                    'Unnamed: 25': 'Duels Win Percentage',
                                    'Shots from outside penalty area / on target': 'Shots from outside penalty area',
                                    'Unnamed: 27': 'Shots from outside penalty area on target',
                                    'Unnamed: 28': 'Shots from outside penalty area on target Percentage',
                                    'Positional attacks / with shots': 'Total Postional attacks',
                                    'Unnamed: 30': 'Positional attacks with shots',
                                    'Unnamed: 31': 'Positional attacks with shots Percentage',
                                    'Counterattacks / with shots': 'Total Counterattacks',
                                    'Unnamed: 33': 'Counterattacks with shots',
                                    'Unnamed: 34': 'Counterattacks with shots Percentage',
                                    'Set pieces / with shots': 'Total Set pieces',
                                    'Unnamed: 36': 'Set pieces with shots',
                                    'Unnamed: 37': 'Set pieces with shots Percentage',
                                    'Corners / with shots': 'Total Corners',
                                    'Unnamed: 39': 'Corners with shots',
                                    'Unnamed: 40': 'Coners with shots Percentage',
                                    'Free kicks / with shots': 'Total Free kicks',
                                    'Unnamed: 42': 'Free kicks with shots',
                                    'Unnamed: 43': 'Free kicks with shots Percentage',
                                    'Penalties / converted': 'Total Penalties',
                                    'Unnamed: 45': 'Penalties converted',
                                    'Unnamed: 46': 'Penalties converted Percentage',
                                    'Crosses / accurate': 'Total Crosses',
                                    'Unnamed: 48': 'Crosses accurate',
                                    'Unnamed: 49': 'Crosses accurate Percentage',
                                    'Penalty area entries (runs / crosses)': 'Total Penalty area entries',
                                    'Unnamed: 53': 'Penalty area entries (runs)',
                                    'Unnamed: 54': 'Penalty area entries (crosses)',
                                    'Offensive duels / won': 'Total Offensive duels',
                                    'Unnamed: 57': 'Offensive duels won',
                                    'Unnamed: 58': 'Offensive duels win Percentage',
                                    'Shots against / on target': 'Total Shots against',
                                    'Unnamed: 62': 'Shots against on target',
                                    'Unnamed: 63': 'Shots against on target Percentage',
                                    'Defensive duels / won': 'Total Defensive duels',
                                    'Unnamed: 65': 'Defensive duels won',
                                    'Unnamed: 66': 'Defensive duels win Percentage',
                                    'Aerial duels / won': 'Total Aerial duels',
                                    'Unnamed: 68': 'Aerial duels won',
                                    'Unnamed: 69': 'Aerial duels win Percentage',
                                    'Sliding tackles / successful': 'Total Sliding tackles',
                                    'Unnamed: 71': 'Sliding tackles successful',
                                    'Unnamed: 72': 'Sliding tackles successful Percentage',
                                    'Forward passes / accurate': 'Total Forward passes',
                                    'Unnamed: 79': 'Forward passes accurate',
                                    'Unnamed: 80': 'Forward passes accurate Percentage',
                                    'Back passes / accurate': 'Total Back passes',
                                    'Unnamed: 82': 'Back passes accurate',
                                    'Unnamed: 83': 'Back passes accurate Percentage',
                                    'Lateral passes / accurate': 'Total Lateral passes',
                                    'Unnamed: 85': 'Lateral passes accurate',
                                    'Unnamed: 86': 'Lateral passes accurate Percentage',
                                    'Long passes / accurate': 'Total Long passes',
                                    'Unnamed: 88': 'Long passes accurate',
                                    'Unnamed: 89': 'Long passes accurate Percentage',
                                    'Passes to final third / accurate': 'Total Passes to final third',
                                    'Unnamed: 91': 'Passes to final third accurate',
                                    'Unnamed: 92': 'Passes to final third accurate Percentage',
                                    'Progressive passes / accurate': 'Total Progressive passes',
                                    'Unnamed: 94': 'Progressive passes accurate',
                                    'Unnamed: 95': 'Progressive passes accurate Percentage',
                                    'Smart passes / accurate': 'Total Smart passes',
                                    'Unnamed: 97': 'Smart passes accurate',
                                    'Unnamed: 98': 'Smart passes accurate Percentage',
                                    'Throw ins / accurate': 'Total Throw ins',
                                    'Unnamed: 100': 'Throw ins accurate',
                                    'Unnamed: 101': 'Throw ins accurate Percentage'
    })
    return clean_cols

def filter_team(data, team_name = 'UCONN Huskies'):
    return data[data['Team'] == team_name]

def numeric_cols(data):
    return data.iloc[:, 6:]

def better_add_opp(data):
    # Define the slice of columns to be mirrored
    target_cols = data.columns[6:109]
    
    # Create a copy of the target slice shifted by one position
    shifted = data[target_cols].shift(-1)
    
    # Alternate the shift for odd-indexed rows (so it's symmetrical)
    opp_data = shifted.copy()
    opp_data.iloc[1::2] = data[target_cols].shift(1).iloc[1::2]
    
    # Rename columns and assign
    opp_data.columns = ['opp_' + col for col in opp_data.columns]

    # Match original dtypes
    for orig_col, opp_col in zip(target_cols, opp_data.columns):
        opp_data[opp_col] = opp_data[opp_col].astype(data[orig_col].dtype)

    return pd.concat([data, opp_data], axis=1)

def snake_columns(data):
    data.columns = data.columns.str.lower().str.replace(' ', '_')

