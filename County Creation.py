#!/usr/bin/env python
# coding: utf-8

# In[1]:


import math
import pandas as pd
import tbapy
tba = tbapy.TBA('LenYI5DMTy1bQIoP4ralqFVd5g5JvTY9YBEBAubPktLTelEdPukJZ1RVLIV1Ypfu')
not_found_string = "N/A"
state_abrvs_loc = "/home/will/Documents/Projects/frc_counties/data/state_abrvs.csv"
zip_fips_loc = "/home/will/Documents/Projects/frc_counties/data/ZIP-COUNTY-FIPS_2018-03.csv"


# In[2]:


# getting all team data
alldata = tba.teams(year=2019)


# In[3]:


# ensuring team is in USA, if so create pandas dataframe w/ it
def shouldAddTeam(team):
    return team.country == "USA"

toadd = []
for team in alldata:
    if shouldAddTeam(team):
        toadd.append([team.team_number, team.country, team.state_prov, team.city, team.postal_code])
datadf = pd.DataFrame(toadd, columns = ["Team Number", "Country", "State", "City", "Postal Code"])


# In[4]:


# pulling in state abbreviations
state_abrvs = pd.read_csv(state_abrvs_loc)
state_dict = {}
for index, row in state_abrvs.iterrows():
    state_dict[row["State"]] = row["Code"]
# adding to df. flag if no match found
abrvs = []
for index, row in datadf.iterrows():
    if row["State"] in state_dict:
        abrvs.append(state_dict[row["State"]])
    else:
        abrvs.append(not_found_string)
        #print("No state found for " + str(row["Team Number"]) + " in " + row["State"])

datadf["State Code"] = abrvs
datadf = datadf[datadf["State Code"] != not_found_string]
datadf.head()


# In[5]:


# pulling in county data - https://data.world/niccolley/us-zipcode-to-county-state
county_data = pd.read_csv(zip_fips_loc)
county_data.head()


# In[6]:


# loop through each team, and find county code
def getCountyString(fipend):
    fipend = str(fipend)
    while(len(fipend) < 5):
        fipend = "0" + fipend
    return "c" + fipend

fips = []
for index, row in datadf.iterrows():
    teamzip = row["Postal Code"]
    if teamzip == None:
        print("No zip found for "+ str(row["Team Number"]))
        fips.append(not_found_string)
        continue
    if len(teamzip) > 5:
        teamzip = teamzip[:5]
    sub_county = county_data[county_data["ZIP"] == int(teamzip)]
    if(len(sub_county.index) == 0):
        print("No county found for " + str(row["Team Number"]) + " w/ tba zip " + row["Postal Code"])
        fips.append(not_found_string)
    elif(len(sub_county.index) > 1):
        counties = ""
        for secind, secrow in sub_county.iterrows():
            counties += getCountyString(secrow["STCOUNTYFP"]) + ","
        counties = counties[:len(counties)-1] # get rid of last comma
        fips.append(counties)
    else:
        fipend = str(sub_county["STCOUNTYFP"].iloc[0])
        fips.append(getCountyString(fipend))
# add as column in dataframe
datadf["fips"] = fips
# clean up rows w/ no county or zip - can't be included in map :( 
datadf = datadf[datadf["fips"] != not_found_string]
datadf.head()


# In[7]:


writer = open("data/frc_teams_counties.csv", "w")
writer.write(datadf.to_csv(index=False))
writer.close()

