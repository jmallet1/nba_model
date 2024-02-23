import csv
import pickle
from datetime import datetime
import time

from nba_api.stats.endpoints import playergamelogs
from nba_api.stats.endpoints import teamestimatedmetrics
from nba_api.stats.endpoints import playerestimatedmetrics
from nba_api.stats.endpoints import leaguedashteamstats
from nba_api.stats.static import players
from nba_api.stats.endpoints import playerprofilev2
import pandas as pd

data_file = 'lines.csv'
df = pd.read_csv(data_file, header=0)

df = df[df.Type == 'points']
# get the names of the players for the day
names = df.Name.values.tolist()

current_season = '2023-24'

# load endpoints
team_stats = leaguedashteamstats.LeagueDashTeamStats(
    season=current_season,
    per_mode_detailed='PerGame',
    measure_type_detailed_defense='Defense',
    season_type_all_star='Regular Season'
).get_data_frames()[0]

team_metrics = teamestimatedmetrics.TeamEstimatedMetrics(
    season=current_season,
    season_type='Regular Season'
).get_data_frames()[0]

player_metrics = playerestimatedmetrics.PlayerEstimatedMetrics(
    season=current_season,
    season_type='Regular Season'
).get_data_frames()[0]

timestr = time.strftime("%Y%m%d")

f = open('projections\\todays_player_data'+timestr+'.csv', 'w', newline='')
data = csv.writer(f)

# write column names
data.writerow(['SEASON AVG FG_PCT', 'SEASON AVG FG3_PCT', 'SEASON AVG FT_PCT', 'SEASON AVG OREB',
               'SEASON AVG REB', 'SEASON AVG AST', 'SEASON AVG TOV', 'SEASON AVG STL', 'SEASON AVG PF',
               'SEASON AVG PFD', 'SEASON AVG PLUS_MINUS', '5 GM PTS', '10 GM PTS', 'SEASON AVG PTS',
               '5 GM MIN', '10 GM MIN', 'SEASON AVG MIN', 'USG', 'PACE', 'TEAM OFF RTG',
               'OPP DEF RTG', 'OPP 2nd CHANCE', 'OPP FB POINTS', 'OPP PinP',
               'SEASON AVG TS', 'SEASON AVG EFG'])
row = []

# iterate through the names to load the current season data through endpoints
for name in names:
    time.sleep(1)

    try:
        player = players.find_players_by_full_name(name)[0]
    except:
        print('Name not found: ', name)
        continue

    player_id = player.get('id')

    game_log = playergamelogs.PlayerGameLogs(
        player_id_nullable=player_id,
        season_type_nullable='Regular Season',
        season_nullable=current_season).get_data_frames()[0]

    row.append(game_log[['FG_PCT']].mean().values[0])
    row.append(game_log[['FG3_PCT']].mean().values[0])
    row.append(game_log[['FT_PCT']].mean().values[0])
    row.append(game_log[['OREB']].mean().values[0])
    row.append(game_log[['REB']].mean().values[0])
    row.append(game_log[['AST']].mean().values[0])
    row.append(game_log[['TOV']].mean().values[0])
    row.append(game_log[['STL']].mean().values[0])
    row.append(game_log[['PF']].mean().values[0])
    row.append(game_log[['PFD']].mean().values[0])
    row.append(game_log[['PLUS_MINUS']].mean().values[0])

    row.append(game_log[['PTS']].tail(5).mean().values[0])
    row.append(game_log[['PTS']].tail(10).mean().values[0])
    row.append(game_log[['PTS']].mean().values[0])

    row.append(game_log[['MIN']].tail(5).mean().values[0])
    row.append(game_log[['MIN']].tail(10).mean().values[0])
    row.append(game_log[['MIN']].mean().values[0])

    next_games = playerprofilev2.PlayerProfileV2(
        player_id=player_id
    ).next_game.get_data_frame()

    vs_team_id = next_games['VS_TEAM_ID'].values[0]
    team_id = next_games['PLAYER_TEAM_ID'].values[0]

    usg = player_metrics.loc[player_metrics['PLAYER_ID'] == player_id]['E_USG_PCT'].values[0]
    row.append(usg)

    pace = team_metrics.loc[team_metrics['TEAM_ID'] == team_id]['E_PACE'].values[0]
    row.append(pace)

    off_rtg = team_metrics.loc[team_metrics['TEAM_ID'] == team_id]['E_OFF_RATING'].values[0]
    row.append(off_rtg)

    def_rtg = team_stats.loc[team_stats['TEAM_ID'] == vs_team_id]['DEF_RATING'].values[0]
    row.append(def_rtg)

    sc = team_stats.loc[team_stats['TEAM_ID'] == vs_team_id]['OPP_PTS_2ND_CHANCE'].values[0]
    row.append(sc)

    fbp = team_stats.loc[team_stats['TEAM_ID'] == vs_team_id]['OPP_PTS_FB'].values[0]
    row.append(fbp)

    pinp = team_stats.loc[team_stats['TEAM_ID'] == vs_team_id]['OPP_PTS_PAINT'].values[0]
    row.append(pinp)

    # true shooting percentage
    game_log = game_log.assign(TS=lambda x: x['PTS'] / (2 * (x['FGA'] + (0.44 * x['FTA']))))
    game_log['SEASON AVG TS'] = game_log['TS'].mean()
    row.append(game_log['SEASON AVG TS'].iloc[0])

    # calculate effective field goal range this year
    game_log = game_log.assign(eFG=lambda x: (x['FGM'] + 0.5 * x['FG3M']) / x['FGA'])
    game_log['SEASON AVG EFG'] = game_log['eFG'].mean()
    row.append(game_log['SEASON AVG EFG'].iloc[0])

    # if enough data is in the row
    if (len(row) > 5):
        data.writerow(row)
    row = []
