import pandas as pd
import numpy as np
import json
import time
import tqdm as tqdm

seconds_per_minute = 1

overall_offset = 0.1

def play_match(team1, team2, df):

    ovr1 = df.iloc[team1]['OVR']
    ovr2 = df.iloc[team2]['OVR']

    if ovr1 > ovr2:
        ovr1 *= 1 + overall_offset
        ovr2 *= 1 - overall_offset
    if ovr2 < ovr1:
        ovr2 *= 1 + overall_offset
        ovr1 *= 1 - overall_offset

    score1 = min(np.random.poisson(lam=ovr1/ovr2*1), 5)
    score2 = min(np.random.poisson(lam=ovr2/ovr1*1), 5)

    goals = [(np.random.randint(3, 90), team1) for i in range(0, score1)]
    goals += [(np.random.randint(3, 90), team2) for i in range(0, score2)]

    goals.sort()

    for ig, g in enumerate(goals):
        all_mins_before = {m for (ii,(m,t)) in enumerate(goals) if ii < ig}
        if ig > 0 and g[0] in all_mins_before:
            goals[ig] = (max(max(all_mins_before),g[0])+1, g[1])

    if score1 + score2 > 0:
        last_goal_min = max({m for (m,t) in goals})

    team1_name = df.iloc[team1]['Team']
    team2_name = df.iloc[team2]['Team']

    team1_current_score = 0
    team2_current_score = 0

    for i in tqdm.tqdm(range(0,max(90,last_goal_min))):
        if i == 45:
            print('HALFTIME BREAK, game will resume soon...')
            time.sleep(seconds_per_minute*15)
        if (i, team1) in goals:
            team1_current_score += 1
            print('\nGOOOAL:', team1_name, 'scored at', i, 'minutes. ', end='')
            print('[', team1_name, team1_current_score, 'x', team2_current_score, team2_name, ']')
        if (i, team2) in goals:
            team2_current_score += 1
            print('\nGOOOAL:', team2_name, 'scored at', i, 'minutes. ', end='')
            print('[', team1_name, team1_current_score, 'x', team2_current_score, team2_name, ']')

        time.sleep(seconds_per_minute)

    return score1, score2

try:
    with open('data/played_matches.json', 'r') as fp:
        played_games = json.load(fp)
except:
    played_games = {}
    played_games['matches'] = []

def create_table(played_games):
    points_col = {}
    wins_col = {}
    losses_col = {}
    draws_col = {}
    gf_col = {}
    ga_col = {}
    for game in played_games['matches']:
        team1 = list(game.keys())[0]
        team2 = list(game.keys())[1]
        score1 = game[team1]
        score2 = game[team2]
        for team in [team1, team2]:
            if team not in points_col:
                points_col[team] = 0
                wins_col[team] = 0
                losses_col[team] = 0
                draws_col[team] = 0
                gf_col[team] = 0
                ga_col[team] = 0
        if score1 > score2:
            points_col[team1] += 3
            wins_col[team1] += 1
            losses_col[team2] += 1
        if score2 > score1:
            points_col[team2] += 3
            wins_col[team2] += 1
            losses_col[team1] += 1
        if score1 == score2:
            points_col[team1] += 1
            points_col[team2] += 1
            draws_col[team1] += 1
            draws_col[team2] += 1
        gf_col[team1] += score1
        gf_col[team2] += score2
        ga_col[team1] += score2
        ga_col[team2] += score1

    table_df = pd.DataFrame.from_dict({'Team': list(points_col.keys()),
                                  'Points': list(points_col.values()),
                                  'Wins': list(wins_col.values()),
                                  'Losses': list(losses_col.values()),
                                  'Draws': list(draws_col.values()),
                                  'GF': list(gf_col.values()),
                                  'GA': list(ga_col.values())
                                  })
    table_df['GD'] = table_df['GF'] - table_df['GA']
    table_df = table_df.sort_values(['Points', 'GD', 'GF', 'Wins'], ascending=False).\
        reset_index().drop(['index'], axis=1)

    return table_df


print()
print('*'*5, 'FAMILY SOCCER LEAGUE','*'*5, '\n')
print('TABLE:\n', create_table(played_games))
print()
df = pd.read_csv('data/teams.csv')
print('TEAMS:\n', df)

while True:

    print()
    t1_idx = input('Enter Team 1 index (ENTER to stop, \'l\' to list): ')
    if t1_idx in ['l', 'L']:
        print()
        print(df)
        continue
    elif t1_idx == '':
        break
    else:
        t1_idx = int(t1_idx)
    t2_idx = input('Enter Team 2 index (ENTER to stop, \'l\' to list): ')
    if t2_idx in ['l', 'L']:
        print()
        print(df)
        continue
    elif t2_idx == '':
        break
    else:
        t2_idx = int(t2_idx)

    if t1_idx+1 > len(df) or t2_idx+1 > len(df) or t1_idx == t2_idx:
        print('ERROR - you have entered an incorrect index.')
        continue

    print('\nPlaying game [',df.iloc[t1_idx]['Team'],'x', df.iloc[t2_idx]['Team'], ']:\n')
    score1, score2 = play_match(t1_idx, t2_idx, df)
    print('\n', df.iloc[t1_idx]['Team'], score1, 'x', score2, df.iloc[t2_idx]['Team'])

    played_games['matches'].append({df.iloc[t1_idx]['Team']: score1,
                    df.iloc[t2_idx]['Team']: score2})

print('\nGame history:\n', played_games['matches'])

print('TABLE:\n', create_table(played_games))
print()

ans = input('\nDo you want to save match results (y/N): ')

if ans in {'Y','y'}:
    print('Storing scores in file \'data/played_matches.json\'...', end='', flush=True)
    with open('data/played_matches.json', 'w') as fp:
        json.dump(played_games,fp=fp)
    print(' Done.', flush=True)
