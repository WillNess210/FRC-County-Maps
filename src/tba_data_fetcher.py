import tbapy
from datetime import datetime

tba = tbapy.TBA('kuosW2jPtJ4Lj0m3HxcDr9mLTI7JHSzimVTYvBrbZdtFdMKqPwzDpnE4jTZy9G6G')
champ_types = ["District Championship", "Championship Finals"]

def getTeamsParticipating(year):
    acceptable_event_types = ["Regional", "Championship Division", "District Championship", "Championship Finals", "District", "District Championship Division"]#, "Offseason"]
    blacklisted_teams = [] # put teams in this list to auto-disqualify (incase of registrations that don't show up, possible bugs, etc..)
    init_events = tba.events(year=year)

    teamsParticipating = []
    # filter only applicable events
    events = [event for event in init_events if event.event_type_string in acceptable_event_types]
    print(str(len(events)) + " events loaded.")
    for idx, event in enumerate(events):
        teams = [int(team[3:]) for team in tba.event_teams(event.key, keys=True)]
        teamsParticipating.extend(teams)
        if idx + 1 <= 5 or (idx + 1) % 5 == 0:
            print(str(idx + 1) + "/" + str(len(events)) + " events loaded.")
    
    teamsParticipating = list(set(teamsParticipating))
    print("Found " + str(len(teamsParticipating)) + " active teams for " + str(year) + ".")
    return teamsParticipating

def getUndefeatedTeams(year, curdate=datetime.today().strftime('%Y-%m-%d'), quiet = True):
    acceptable_event_types = ["Regional", "Championship Division", "District Championship", "Championship Finals", "District", "District Championship Division"]#, "Offseason"]
    blacklisted_teams = [] # put teams in this list to auto-disqualify (incase of registrations that don't show up, possible bugs, etc..)
    # get a list of all regular season events
    init_events = tba.events(year=year)
    # filter only applicable events
    events = [event for event in init_events if event.event_type_string in acceptable_event_types]
    print(str(len(events)) + " events loaded.")
    # count down losses
    team_losses = {}
    num_event = 1
    if not quiet:
        print("Starting to count losses.")
    for event in events:
        # add qual losses
        if curdate >= event.start_date:
            event_rankings = tba.event_rankings(event.key)
            if event_rankings.rankings != None:
                rankings = event_rankings.rankings
                for indiv_team_ranking in rankings:
                    team_num = int(indiv_team_ranking["team_key"][3:])
                    if team_num in team_losses:
                        team_losses[team_num] += indiv_team_ranking["record"]["losses"]
                    else:
                        team_losses[team_num] = indiv_team_ranking["record"]["losses"]
                # add elim losses
                alliances = tba.event_alliances(event.key)
                for alliance in alliances:
                    teams = alliance["picks"]
                    for i in range(len(teams)):
                        teams[i] = int(teams[i][3:])
                    for team_num in teams:
                        if alliance["status"] != 'unknown':
                            if team_num not in team_losses:
                                team_losses[team_num] = alliance["status"]["record"]["losses"]
                            else:
                                try:
                                    team_losses[team_num] += alliance["status"]["record"]["losses"]
                                except TypeError:
                                    print(alliance)
                                    print(team_num)
        else: # add teams from event that hasn't started w 0 losses if not in
            for teamfull in tba.event_teams(event.key, keys=True):
                team_num = int(teamfull[3:])
                if team_num not in team_losses:
                    team_losses[team_num] = 0
            
        # if event is over, add loss to any team who was registered but didn't play
        if curdate > event.end_date:
            for teamfull in tba.event_teams(event.key, keys=True):
                team_num = int(teamfull[3:])
                if team_num not in team_losses:
                    team_losses[team_num] = 1
        # load
        if not quiet:
            if num_event <= 5 or num_event % 5 == 0:
                print(str(num_event) + "/" + str(len(events)) + " events completed.")
            num_event += 1
    # generate list of undefeated teams
    undefeated_teams = [team for team in team_losses.keys() if team_losses[team] == 0 and team not in blacklisted_teams]
    if not quiet:
        print("Undefeated teams: " + str(undefeated_teams))
    return undefeated_teams

def extract_enddate(event): # used for sorting
    return event.end_date

def extract_champtype(event):  # used for sorting
    return event.event_type_string in champ_types

def getEventsInOrder(year, curdate=datetime.today().strftime('%Y-%m-%d'), quiet=False):
    acceptable_event_types = ["Regional", "Championship Division", "District Championship", "Championship Finals", "District", "District Championship Division"]#, "Offseason"]

    init_events = tba.events(year=year)
    init_events.sort(key=extract_champtype)
    init_events.sort(key=extract_enddate)
    events = [event for event in init_events if event.event_type_string in acceptable_event_types and event.end_date < curdate]
    if not quiet:
        print(str(len(events)) + " events loaded.")
    return events
    
# returns winner, [partners], [losers]
def getWinnerPartersLosersAtEvent(event):
    event_alliances = tba.event_alliances(event.key)
    event_teams = tba.event_teams(event.key, keys=True)

    winner = None
    partners = []
    losers = []

    #convert team keys to team numbers
    for i in range(len(event_teams)):
        event_teams[i] = int(event_teams[i][3:])
    for alliance in event_alliances:
        for i in range(len(alliance.picks)):
            alliance.picks[i] = int(alliance.picks[i][3:])

    # find winning alliance and fill winner/partners
    for alliance in event_alliances: 
        # if the alliance wins
        if (event.event_type_string not in champ_types and alliance.status["status"] == 'won') or (event.event_type_string in champ_types and alliance.status["status"] == 'won' and alliance.status["level"] == 'f'):
            winner = alliance.picks[0]
            for partner in alliance.picks[1:]:
                partners.append(partner)
            break
    
    ## add all other teams as losers
    # if the event is normal, add all non-winners
    if event.event_type_string not in champ_types or event.playoff_type == None or event.playoff_type == 0:
        losers = [team for team in event_teams if team != winner and team not in partners]
    else: # championship finals event alliances & mark losers
        for alliance in event_alliances:
            if winner not in alliance.picks: # if not winning alliance
                for loser in alliance.picks:
                    losers.append(loser)
    return winner, partners, losers