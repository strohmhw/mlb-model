import sqlite3
import pandas as pd
import datetime as dt
import math
import numpy as  np

# Import current date and print
date = dt.date.today
print(date)

# Import data from SQL database, sort into DataFrames, and make current
conn = sqlite3.connect('fangraphs.db')

pitchers_query = 'select * from pitchers'
pitchers = pd.read_sql(pitchers_query,conn)
pitchers.set_index('id', inplace=True)

pitcher_stats_query = 'select * from pitcher_stats'
pitcher_stats = pd.read_sql(pitcher_stats_query,conn)
pitcher_current = pitcher_stats[(pitcher_stats['date'] > '2017-04-01')]
pitcher_stats.set_index('id', inplace=True)

players_query = 'select * from players'
players = pd.read_sql(players_query,conn)

player_stats_query = 'select * from player_stats'
player_stats = pd.read_sql(player_stats_query,conn)

# Sort and sum by player, add Team Names back in
p = pitcher_current.groupby('id').sum()
p2 = pitchers.join(p, how='outer')
# Teams
teams_add = pitcher_stats['team']
teams_add = teams_add[~teams_add.index.duplicated(keep='first')]
p2 = p2.merge(teams_add.to_frame(), how='outer', left_index=True, right_index=True)

# FIP Calculation, and adding to pitching data
# cFIP = 4.35 - (((13 * int(p2['hr'].mean))+(3 * (int(p2['bb'].mean)+int(p2['hbp'].mean))) - (2 * int(p2['k'].mean)))/int(p2['ip'].mean))
cFIP = 3.158
FIP = pd.DataFrame(((13*p2['hr'])+(3*(p2['bb']+p2['hbp']))-(2*p2['so']))/p2['ip'] + 3.158)
FIP.columns = ['fip']
pitching = p2.merge(FIP, how='outer', left_index=True, right_index=True)

# Individual Teams Pitching Staff Consolidation
teams = ['NYY', 'CWS', 'MIN', 'DET', 'KCR', 'COL', 'BOS', 'TBR', 'TEX', 'PIT', 'PHI', 'SDP', 'BAL', 'WAS', 'NYM', 'MIA', 'SEA', 'CLE',
    'SFG', 'ARI', 'LAD', 'CHC', 'STL', 'MIL', 'ATL', 'TOR', 'OAK', 'HOU', 'LAA']
# for x in teams:
#    x = pitching['team'] == x
#    x_pitching = pitching[x]
#    print(x_pitching)
d = []
for x in teams:
    x_class = pitching['team'] == x
    x_pitching = pitching[x_class]
    x_fip_avg = ((x_pitching['ip'] * x_pitching['fip']) / x_pitching['ip'].sum()).sum()
    team_avg = pd.DataFrame(teams, x_fip_avg)
# currently trying to take averages of teams FIPs, for team-to-pitchers skill calcs
