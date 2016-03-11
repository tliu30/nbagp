import json
import pandas as pd
import os

__DATA_PATH__ = "data/%s.json"
player_info_a = [
    'playeridsid',
    'playerfirstname',
    'playerlastname',
    'playernumber',
    'p',
    'teamidsid',
    'teamname',
    'teamnameabbreviation',
    'teamshortname',
    'gp'
]

player_info_b = [
    'player_id',
    'player_name',
    'team_id',
    'team_abbreviation',
    'gp',
    'w',
    'l'
]

# player_info_shared = ['player_id', 'player_name', 'team_id', 'team_abbreviation', 'gp']
player_info_shared = ['player_id']

# FIX THIS - too lazy on the error handling
def transform_to_fix_playerid(df):
    transform = transform_to_fix_playerid_a if ('playeridsid' in df.columns) else transform_to_fix_playerid_b

    return transform(df)

def transform_to_fix_playerid_a(df):
    keep_columns = []
    for column in df.columns:
        if column not in player_info_a:
            keep_columns.append(column)
    
    new_df = pd.DataFrame(df[keep_columns])

    new_df['player_id'] = df['playeridsid']
    # new_df['player_name'] = df['playerfirstname'] + ' ' + df['playerlastname']
    # new_df['team_id'] = df['teamidsid']
    # new_df['team_abbreviation'] = df['teamnameabbreviation']
    # new_df['gp'] = df['gp']

    return new_df

def transform_to_fix_playerid_b(df):
    keep_columns = []
    for column in df.columns:
        if column not in player_info_b:
            keep_columns.append(column)

    new_df = pd.DataFrame(df[keep_columns])

    for b in player_info_shared:
        new_df[b] = df[b]

    return new_df

simple_name = {
    "CatchShoot_2015_16" : "catchshoot",
    "cut" : "cut",
    "Defense_2015_16" : "defense",
    "Drives_2015_16" : "drives",
    "Efficiency_2015_16" : "efficiency",
    "ElbowTouch_2015_16" : "elbowtouch",
    "handoff" : "handoff",
    "isolation" : "isolation",
    "misc" : "misc",
    "offscreen" : "offscreen",
    "PaintTouch_2015_16" : "painttouch",
    "Passing_2015_16" : "passing",
    "pnr" : "pnr",
    "Possessions_2015_16" : "possessions",
    "PostTouch_2015_16" : "posttouch",
    "postup" : "postup",
    "PullUpShot_2015_16" : "pullup",
    "putback" : "putback",
    "Rebounding_2015_16" : "rebounding",
    "rollman" : "rollman",
    "SpeedDistance_2015_16" : "speed",
    "spotup" : "spotup",
    "transition" : "transition"
}

def load_all():
    dfs = []
    for name in simple_name:
        dfs.append( transform_to_fix_playerid(load_pd(name)) )

    df = reduce(lambda x,y: pd.merge(x,y,'outer',player_info_shared), dfs)
    return df

def load_all_df():
    df = {}
    for name in simple_name:
        df[simple_name[name]] = transform_to_fix_playerid(load_pd(name))

    return df

def load_pd(name):
    sname = simple_name[name]
    fname = __DATA_PATH__%(name)

    json_obj = json.load(open(fname))

    array = json_obj['resultSets'][0]['rowSet']
    hdr   = [x.lower() for x in json_obj['resultSets'][0]['headers']]
    new_hdr = map(lambda x : x if (x in player_info_a or x in player_info_b) else x + '_' + sname, hdr)

    df = pd.DataFrame(array, columns = new_hdr)
    return df

def load(fname):
    data = json.load(open(fname))
    keys = data['resultSets'][0]['headers']

    returnVal = []
    for row in data['resultSets'][0]['rowSet']:
        d = {}
        for i in range(len(keys)):
            d[keys[i]] = row[i]
        returnVal.append(d)

    return returnVal

def toDict(d):
    new_d = {}
    for key in d:
        fname = "data/%s.json"%(d[key])
        data = load(fname)
        new_d[key] = data
    return new_d

def byPlayer(d):
    new_d = {}
    for (key, val) in d.items():
        for rowDict in val:
            rowKey = None
            if 'PLAYER_NAME' in rowDict:
                rowKey = rowDict['PLAYER_NAME']
            else:
                rowKey = "%s %s"%(rowDict['PlayerFirstName'], rowDict['PlayerLastName'])
            
            if rowKey not in new_d:
                new_d[rowKey] = {}
            
            new_d[rowKey][key] = rowDict
    return new_d
