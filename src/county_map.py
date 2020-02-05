from lxml import etree
import pandas as pd
from helper import genCSSRGB, teamListToCommaSepString, RoboColor, expandTeamsInCountyIntoBlankByClosest
from tba_data_fetcher import getUndefeatedTeams, getEventsInOrder, getWinnerPartersLosersAtEvent, getTeamsParticipating

class CountyMap:
    def __init__(self, blank_map_loc, dest_map_loc, team_custom_colors_loc = None):
        self.blank_map_loc = blank_map_loc
        self.dest_map_loc = dest_map_loc
        self.team_custom_colors_loc = team_custom_colors_loc
    
    # county_colors is a dictionary storing (county key -> color)
    # county_labels is a dictionary storing (county key -> label)
    def writeSVG(self, county_colors = {}, county_labels = {}):
        tree = etree.parse(self.blank_map_loc)
        root = tree.getroot()
        colors_loaded = 0
        labels_loaded = 0
        for path in root[3]:
            path_county_id = path.attrib["id"]
            if path_county_id in county_colors:
                path.attrib["style"] = "fill: " + county_colors[path_county_id] + ";"
                colors_loaded += 1
            if path_county_id in county_labels:
                path[0].text += " - " + county_labels[path_county_id]
                labels_loaded += 1
        etree.ElementTree(root).write(self.dest_map_loc, pretty_print=True)
        print("Map written to: " + self.dest_map_loc + ". Loaded " + str(colors_loaded) + "/" + str(len(county_colors)) + " colors and " + str(labels_loaded) + "/" + str(len(county_labels)) + " labels.")
    
    def genSVG(self):
        self.writeSVG()

    # teams_in_county is a dictionary storing (county key -> [teams])
    def genSVGWithTeamColors(self, teams_in_county):
        self.genCSVWithRankedTeamCountyOwnership(teams_in_county)
        if self.team_custom_colors_loc == None:
            print("No custom colors loaded. Can't generate.")
            return
        roboColor = RoboColor(self.team_custom_colors_loc)
        county_colors = {}
        county_labels = {}
        for county in teams_in_county:
            county_teams = teams_in_county[county]
            if len(county_teams) == 0:
                continue
            county_labels[county] = teamListToCommaSepString(county_teams)
            county_colors[county] = roboColor.getTeamRGBFromTeamList(county_teams)
        self.writeSVG(county_colors, county_labels)

    def genCSVWithRankedTeamCountyOwnership(self, teams_in_county):
        dest_csv_loc = self.dest_map_loc[:-4] + "_ownership.csv"
        # create dictionary (team number -> # counties owned)
        team_county_counts = {}
        for county in teams_in_county:
            for team in teams_in_county[county]:
                if team in team_county_counts:
                    team_county_counts[team] += 1
                else:
                    team_county_counts[team] = 1
        # sort, ordered list of tuples [(team, team_count)] w/ top ranked team first and last ranked team last
        team_county_counts = {(team, team_count) for team, team_count in sorted(team_county_counts.items(), key = lambda item: item[1], reverse=True)}
        # create string to write to file
        file_str = "Team,# Counties\n"
        for team, team_count in team_county_counts:
            file_str += str(team) + "," + str(team_count) + "\n"
        # writing out to file
        writer = open(dest_csv_loc, "w")
        writer.write(file_str)
        writer.close()

class DensityCountyMap(CountyMap):
    def __init__(self, blank_map_loc, dest_map_loc, frc_county_data_loc):
        super().__init__(blank_map_loc,dest_map_loc)
        self.frc_county_data_loc = frc_county_data_loc
        self.min_color_val = 30
    
    def genSVG(self):
        print("Generating density map.")
        frc_counties = pd.read_csv(self.frc_county_data_loc)
        # create dictionary with list of teams by county
        teams_in_county = {}
        for index, row in frc_counties.iterrows():
            county_list_for_team = row["fips"].split(",")
            for county in county_list_for_team:
                if county in teams_in_county:
                    teams_in_county[county].append(row["Team Number"])
                else:
                    teams_in_county[county] = [row["Team Number"]]
        # convert teams_in_county into county_labels
        county_labels = {}
        max_teams_in_one_county = -1
        for county_id in teams_in_county:
            max_teams_in_one_county = max([max_teams_in_one_county, len(teams_in_county[county_id])])
            county_labels[county_id] = teamListToCommaSepString(teams_in_county[county_id])
        # convert teams in county into county_colors
        county_colors = {}
        for county_id in teams_in_county:
            num_teams = len(teams_in_county[county_id])
            colorDef = self.min_color_val + int(((255.0 - self.min_color_val)) * float(num_teams/max_teams_in_one_county))
            county_colors[county_id] = genCSSRGB(255 - colorDef, 255 - colorDef, 255)
        # writing svg
        self.writeSVG(county_colors, county_labels)

class UndefeatedCountyMap(CountyMap):
    def __init__(self, blank_map_loc, dest_map_loc, frc_county_data_loc, county_location_info_loc, team_custom_colors_loc = None):
        super().__init__(blank_map_loc,dest_map_loc, team_custom_colors_loc=team_custom_colors_loc)
        self.frc_county_data_loc = frc_county_data_loc
        self.county_location_info_loc = county_location_info_loc
    
    def genSVG(self):
        print("Generating undefeated map.")
        frc_counties = pd.read_csv(self.frc_county_data_loc)
        # create dictionary with list of teams by county
        teams_in_county = {}
        for index, row in frc_counties.iterrows():
            county_list_for_team = row["fips"].split(",")
            for county in county_list_for_team:
                if county in teams_in_county:
                    teams_in_county[county].append(row["Team Number"])
                else:
                    teams_in_county[county] = [row["Team Number"]]
        # get undefeated teams
        #undefeated_teams = [254, 4944, 1332, 5254]
        undefeated_teams = getUndefeatedTeams(2020, quiet=False)
        undef_teams_in_county = {}
        for county in teams_in_county:
            county_teams = teams_in_county[county]
            undef_teams_in_county[county] = [team for team in county_teams if team in undefeated_teams]
        undef_teams_in_county_expanded = expandTeamsInCountyIntoBlankByClosest(undef_teams_in_county, self.county_location_info_loc)
        self.genSVGWithTeamColors(undef_teams_in_county_expanded)

class ImperialismCountyMap(CountyMap):
    def __init__(self, blank_map_loc, dest_map_loc, frc_county_data_loc, county_location_info_loc, team_custom_colors_loc = None):
        super().__init__(blank_map_loc,dest_map_loc, team_custom_colors_loc=team_custom_colors_loc)
        self.frc_county_data_loc = frc_county_data_loc
        self.county_location_info_loc = county_location_info_loc
        self.teams_in_county = {}
    
    def genSVG(self):
        print("Generating imperialism map.")
        frc_counties = pd.read_csv(self.frc_county_data_loc)
        # create dictionary with list of teams by county
        self.teams_in_county = {}
        for index, row in frc_counties.iterrows():
            county_list_for_team = row["fips"].split(",")
            for county in county_list_for_team:
                if county in self.teams_in_county:
                    self.teams_in_county[county].append(row["Team Number"])
                else:
                    self.teams_in_county[county] = [row["Team Number"]]
        # grab all teams active in this year
        active_teams = getTeamsParticipating(year=2020)
        tic_next = {}
        for county in self.teams_in_county:
            tic_next[county] = [team for team in self.teams_in_county[county] if team in active_teams]
        self.teams_in_county = tic_next
        # expand outwards to fill map
        self.teams_in_county = expandTeamsInCountyIntoBlankByClosest(self.teams_in_county, self.county_location_info_loc)
        # load in all events, sort, and filter
        events = getEventsInOrder(year=2020)
        num_event = 1
        for event in events:
            winner, partners, losers = getWinnerPartersLosersAtEvent(event)
            self.landClaim(winner, losers)
            if num_event <= 5 or num_event % 5 == 0:
                print(str(num_event) + "/" + str(len(events)) + " processed so far.")
            num_event += 1
        self.genSVGWithTeamColors(self.teams_in_county)

    def landClaim(self, winner, losers):
        for county in self.teams_in_county:
            countyOwners = self.teams_in_county[county]
            for loser in [loser for loser in losers if loser in countyOwners]:
                if winner not in countyOwners:
                    self.teams_in_county[county].append(winner)
                self.teams_in_county[county].remove(loser)