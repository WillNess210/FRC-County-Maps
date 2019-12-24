import pandas as pd

class RoboColor:
    def __init__(self, color_override_loc):
        colordf = pd.read_csv(color_override_loc)
        self.teamcolors = {}
        for index, row in colordf.iterrows():
            self.teamcolors[str(row["Team Number"])] = row["Color"]
    
    def getTeamRGB(self, teamnum):
        if str(teamnum) in self.teamcolors:
            return self.teamcolors[str(teamnum)]
        teamhash = hash(str(teamnum) * 100)
        R = ((teamhash // (256 * 256)) % 161) + 75
        G = ((teamhash // (256)) % 161) + 75
        B = ((teamhash // 1) % 161) + 75
        return "rgb(" + str(R) + "," + str(G) + "," + str(B) + ")"
    
    def getContestedRGB(self):
        return "rgb(255,255,255)"