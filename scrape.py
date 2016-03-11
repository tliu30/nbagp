import requests

url = "http://stats.nba.com/stats/commonallplayers?IsOnlyCurrentSeason=0&LeagueID=00&Season=2015-16"

__DEFAULT_DICT__ = {
    "College" : "", "Conference" : "", "Country" : "", "DateFrom" : "",
    "DateTo" : "", "Division" : "", "DraftPick" : "", "DraftYear" : "", 
    "GameScope" : "", "Height" : "", "LastNGames" : "0", "LeagueID" : "00", 
    "Location" : "", "Month" : "0", "OpponentTeamID" : "0", "Outcome" : "", 
    "PORound" : "0", "PerMode" : "PerGame", "PlayerExperience" : "", 
    "PlayerOrTeam" : "Player", "PlayerPosition" : "", "PtMeasureType" : "", 
    "Season" : "2015-16", "SeasonSegment" : "", 
    "SeasonType" : "Regular+Season", "StarterBench" : "", "TeamID" : "0", 
    "VsConference" : "", "VsDivision" : "", "Weight" : ""
}

__DEFAULT_URL__ = "http://stats.nba.com/stats/leaguedashptstats"

__VALID_PTMEASURETYPE__ = ["SpeedDistance", "Rebounding", "Possessions", 
    "CatchShoot", "PullUpShot", "Defense", "Drives", "Passing", 
    "ElbowTouch", "PostTouch", "PaintTouch", "Efficiency"
]

def url(**kwargs):
    newArgs = {}
    for key in __DEFAULT_DICT__:
        if key in kwargs:
            newArgs[key] = kwargs[key]
        else:
            newArgs[key] = __DEFAULT_DICT__[key]

    return buildUrl(__DEFAULT_URL__, **newArgs)

def buildUrl(base, **kwargs):
    suffix = "&".join(["%s=%s"%(k, v) for (k,v) in kwargs.items()])
    return "%s?%s"%(base, suffix)

def readProp(fname):
    lines = dict([line.strip().split(' = ') for line in open(fname).readlines()])
    base = lines["root"]

    playTypeDict = {}
    for key in lines:
        if key != "root":
            playTypeDict[key] = base + "/" + lines[key]

    return playTypeDict

if __name__ == '__main__':
    # playType = readProp('playtypeURLS.txt')
    # for play in playType:
        # u = playType[play]
        # open('data/' + play + '.json', 'w').write(requests.get(u).text)

    for year in ['2014-15', '2014-15']: #('2013-14', '2014-15', '2015-16'):
        for match in __VALID_PTMEASURETYPE__:
            open('data/' + match + '_' + year.replace('-', '_') + '.json', 'w').write(requests.get(url(PtMeasureType = match, Season = year)).text)
