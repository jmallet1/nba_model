import datetime
import time

from nba_api.stats.endpoints import leagueleaders
from nba_api.stats.endpoints import playergamelogs
from nba_api.stats.endpoints import teamestimatedmetrics
from nba_api.stats.endpoints import playerestimatedmetrics
from nba_api.stats.endpoints import leaguedashteamstats
from nba_api.stats.static import teams
import pandas as pd

# team pace
def pace_mapping(row):
    team_id = row['TEAM_ID']
    for team in team_metrics:
        if team[1] == team_id:
            return team[10]

# offensive rating
def offrtg_mapping(row):
    team_id = row['TEAM_ID']
    for team in team_metrics:
        if team[1] == team_id:
            return team[7]

# usage rating
def usgrtg_mapping(row):
    pid = row['PLAYER_ID']
    for player in player_metrics:
        if player[0] == pid:
            return player[15]

# defensive rating
def defrtg_mapping(row):
    # substr opp team abbrev
    opp_team_abbrev = row['MATCHUP'][-3:]

    # translate team abrev to team id
    opp_team = teams.find_team_by_abbreviation(opp_team_abbrev)
    opp_team_id = opp_team.get('id')

    # select the row with the right team id, then get the value of the defensive rating
    return team_stats.loc[team_stats['TEAM_ID'] == opp_team_id]['DEF_RATING'].values[0]

# second chance points
def sc_mapping(row):
    # substr opp team abbrev
    opp_team_abbrev = row['MATCHUP'][-3:]

    # translate team abrev to team id
    opp_team = teams.find_team_by_abbreviation(opp_team_abbrev)
    opp_team_id = opp_team.get('id')

    # select the row with the right team id, then get the value of the defensive rating
    return team_stats.loc[team_stats['TEAM_ID'] == opp_team_id]['OPP_PTS_2ND_CHANCE'].values[0]

# fast break points
def fbp_mapping(row):
    # substr opp team abbrev
    opp_team_abbrev = row['MATCHUP'][-3:]

    # translate team abrev to team id
    opp_team = teams.find_team_by_abbreviation(opp_team_abbrev)
    opp_team_id = opp_team.get('id')

    # select the row with the right team id, then get the value of the defensive rating
    return team_stats.loc[team_stats['TEAM_ID'] == opp_team_id]['OPP_PTS_FB'].values[0]

# points in the paint
def pinp_mapping(row):
    # substr opp team abbrev
    opp_team_abbrev = row['MATCHUP'][-3:]

    # translate team abrev to team id
    opp_team = teams.find_team_by_abbreviation(opp_team_abbrev)
    opp_team_id = opp_team.get('id')

    # select the row with the right team id, then get the value of the defensive rating
    return team_stats.loc[team_stats['TEAM_ID'] == opp_team_id]['OPP_PTS_PAINT'].values[0]

# seasons to get player data for
master_df = pd.DataFrame()
seasons = ['2014-15', '2015-16', '2016-17', '2017-18', '2018-19', '2019-20', '2020-21', '2021-22', '2022-23']

for season in seasons:
    print("On season: ", season)
    print("Current Time: ", datetime.datetime.now())

    # Pull data for the top 150 scorers
    top_200 = leagueleaders.LeagueLeaders(
        season=season,
        season_type_all_star='Regular Season',
        stat_category_abbreviation='PTS'
    ).get_data_frames()[0][:150]

    team_stats = leaguedashteamstats.LeagueDashTeamStats(
        season=season,
        per_mode_detailed='PerGame',
        measure_type_detailed_defense='Defense',
        season_type_all_star='Regular Season'
    ).get_data_frames()[0]

    team_metrics = teamestimatedmetrics.TeamEstimatedMetrics(
        season=season,
        season_type='Regular Season'
    ).get_dict().get('resultSet')['rowSet']

    player_metrics = playerestimatedmetrics.PlayerEstimatedMetrics(
        season=season,
        season_type='Regular Season'
    ).get_dict().get('resultSet')['rowSet']

    # Inspect the first few rows of the averaged stats
    player_ids = top_200.PLAYER_ID.values.tolist()

    for player_id in player_ids:

        # sleep to not overload the server
        time.sleep(5)
        game_log = playergamelogs.PlayerGameLogs(
            player_id_nullable=player_id,
            season_type_nullable='Regular Season',
            season_nullable=season).get_data_frames()[0]

        game_log['SEASON AVG FG_PCT'] = game_log['FG_PCT'].mean()
        game_log['SEASON AVG FG3_PCT'] = game_log['FG3_PCT'].mean()
        game_log['SEASON AVG FT_PCT'] = game_log['FT_PCT'].mean()
        game_log['SEASON AVG OREB'] = game_log['OREB'].mean()
        game_log['SEASON AVG REB'] = game_log['REB'].mean()
        game_log['SEASON AVG AST'] = game_log['AST'].mean()
        game_log['SEASON AVG TOV'] = game_log['TOV'].mean()
        game_log['SEASON AVG STL'] = game_log['STL'].mean()
        game_log['SEASON AVG PF'] = game_log['PF'].mean()
        game_log['SEASON AVG PFD'] = game_log['PFD'].mean()
        game_log['SEASON AVG PLUS_MINUS'] = game_log['PLUS_MINUS'].mean()

        # gets rolling averages for 5 games, 10 games, and the season average
        game_log['5 GM PTS'] = game_log['PTS'].rolling(window=5, min_periods=1, closed='left').mean()
        game_log['10 GM PTS'] = game_log['PTS'].rolling(window=10, min_periods=1, closed='left').mean()
        game_log['SEASON AVG PTS'] = game_log['PTS'].mean()

        game_log['5 GM MIN'] = game_log['MIN'].rolling(window=5, min_periods=1, closed='left').mean()
        game_log['10 GM MIN'] = game_log['MIN'].rolling(window=10, min_periods=1, closed='left').mean()
        game_log['SEASON AVG MIN'] = game_log['MIN'].mean()

        game_log['USG'] = game_log.apply(usgrtg_mapping, axis=1)
        game_log['PACE'] = game_log.apply(pace_mapping, axis=1)
        game_log['TEAM OFF RTG'] = game_log.apply(offrtg_mapping, axis=1)
        game_log['OPP DEF RTG'] = game_log.apply(defrtg_mapping, axis=1)
        game_log['OPP 2nd CHANCE'] = game_log.apply(sc_mapping, axis=1)
        game_log['OPP FB POINTS'] = game_log.apply(fbp_mapping, axis=1)
        game_log['OPP PinP'] = game_log.apply(pinp_mapping, axis=1)

        # caluclates true shooting percentage
        game_log = game_log.assign(TS=lambda x: x['PTS'] / (2 * (x['FGA'] + (0.44 * x['FTA']))))
        game_log['SEASON AVG TS'] = game_log['TS'].mean()

        # effective field goal percentage
        game_log = game_log.assign(eFG=lambda x: (x['FGM'] + 0.5 * x['FG3M']) / x['FGA'])
        game_log['SEASON AVG EFG'] = game_log['eFG'].mean()


        game_log['SEASON AVG PFD'] = game_log['PFD'].mean()
        game_log['SEASON AVG PLUS_MINUS'] = game_log['PLUS_MINUS'].mean()

        # removes unneccessary columns
        game_log = game_log[
            ['PTS', 'SEASON AVG FG_PCT', 'SEASON AVG FG3_PCT', 'SEASON AVG FT_PCT', 'SEASON AVG OREB',
             'SEASON AVG REB', 'SEASON AVG AST', 'SEASON AVG TOV', 'SEASON AVG STL', 'SEASON AVG PF', 'SEASON AVG PFD',
             'SEASON AVG PLUS_MINUS', '5 GM PTS', '10 GM PTS', 'SEASON AVG PTS', '5 GM MIN', '10 GM MIN',
             'SEASON AVG MIN', 'USG', 'PACE', 'TEAM OFF RTG',
             'OPP DEF RTG', 'OPP 2nd CHANCE', 'OPP FB POINTS', 'OPP PinP',
             'SEASON AVG TS', 'SEASON AVG EFG'
             ]]

        master_df = pd.concat([master_df, game_log], axis=0)

master_df.to_csv('player_data.csv')
