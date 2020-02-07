import pandas as pd
from haversine import haversine
import sys

def genCSSRGB(R, G, B):
    return "rgb(" + str(R) + "," + str(G) + "," + str(B) + ")"

# ex [1, 2, 3] -> "1, 2, 3"
def teamListToCommaSepString(teamList):
    if len(teamList) == 0:
        return ""
    elif len(teamList) == 1:
        return str(teamList[0])
    res = str(teamList[0])
    for i in range(1, len(teamList)):
        res += ", " + str(teamList[i])
    return res

def cFIP_to_int(cFIP):
    return int(cFIP[1:])
    
def int_to_cFIP(fip_int):
    res = str(fip_int)
    if len(res) < 5:
        res = ("0" * (5 - len(res))) + res
    return "c" + res

def getRowDataFromFIPS(county_locations, fip):
    return county_locations[county_locations["FIPS"] == cFIP_to_int(fip)]

def distBetweenTwoCounties(rowdata1, rowdata2): #pass in rows of data from countylocs to get distance between the two
    return haversine((rowdata1["Latitude"], rowdata1["Longitude"]), (rowdata2["Latitude"], rowdata2["Longitude"]))

def expandTeamsInCountyIntoBlankByClosest(teams_in_county, county_location_info_loc):
    print("Expanding.")
    # create dictionary of 'home counties' (county -> [teams])
    home_counties = {}
    for county in teams_in_county:
        if len(teams_in_county[county]) > 0:
            home_counties[county] = teams_in_county[county]
    
    # assign closest 'home county' to each non home county
    closest_home_county = {} # (county -> closest home county)
    county_locations = pd.read_csv(county_location_info_loc)
    for index, row in county_locations.iterrows():
        row_fips = int_to_cFIP(row["FIPS"])
        if row_fips in home_counties:
            closest_home_county[row_fips] = row_fips
        else:
            minDist = -1
            closestCountySoFar = None
            for home_county in home_counties:
                home_county_row = getRowDataFromFIPS(county_locations, home_county)
                distance_to_home_county = distBetweenTwoCounties(row, home_county_row)
                if closestCountySoFar == None or distance_to_home_county < minDist:
                    minDist = distance_to_home_county
                    closestCountySoFar = home_county
            closest_home_county[row_fips] = closestCountySoFar
        if index + 1 <= 5 or (index + 1) % 50 == 0:
            print("expanded " + str(index + 1) + "/" + str(len(county_locations.index)))
    # fill a new teams_in_county
    filled_teams_in_county = {}
    for county in closest_home_county:
        filled_teams_in_county[county] = home_counties[closest_home_county[county]]
    return filled_teams_in_county


def custom_hash(s):
    ord3 = lambda x : '%.3d' % ord(x)
    return int(''.join(map(ord3, s)))

class RoboColor:
    def __init__(self, color_override_loc):
        colordf = pd.read_csv(color_override_loc)
        self.teamcolors = {}
        for index, row in colordf.iterrows():
            self.teamcolors[str(row["Team Number"])] = row["Color"]

    def getTeamRGBFromTeamList(self, team_list):
        return self.getTeamRGB(sum(team_list), disable_teamcolors = (False if len(team_list) == 1 else True))

    def getTeamRGB(self, teamnum, disable_teamcolors = False):
        if not disable_teamcolors and str(teamnum) in self.teamcolors:
            print("Preloading color for " + str(teamnum) + " - " + self.teamcolors[str(teamnum)] + ".")
            return self.teamcolors[str(teamnum)]
        string_to_hash = str(teamnum) * 100
        if len(string_to_hash) > 50:
            string_to_hash = string_to_hash[:50]
        teamhash = custom_hash(string_to_hash)
        R = ((teamhash // (256 * 256)) % 161) + 75
        G = ((teamhash // (256)) % 161) + 75
        B = ((teamhash // 1) % 161) + 75
        return "rgb(" + str(R) + "," + str(G) + "," + str(B) + ")"
    
    def getContestedRGB(self):
        return "rgb(255,255,255)"
    
