from county_map import CountyMap, DensityCountyMap, UndefeatedCountyMap, ImperialismCountyMap

svg_loc = "/home/will/Documents/Projects/frc_counties/data/counties.svg"
frc_county_data_loc = "/home/will/Documents/Projects/frc_counties/data/frc_teams_counties.csv"
team_custom_colors_loc = "/home/will/Documents/Projects/frc_counties/data/team_colors.csv"
county_location_info_loc = "/home/will/Documents/Projects/frc_counties/data/counties_loc.csv"

dest_density_map_loc = "/home/will/Documents/Projects/portfolio_website/WillNess210.github.io/frc/county_maps/frc_county_density.svg"
dest_undefeated_map_loc = "/home/will/Documents/Projects/portfolio_website/WillNess210.github.io/frc/undefeated/2019/week7/frc_undefeated_map.svg"
dest_imperialism_map_loc = "/home/will/Documents/Projects/portfolio_website/WillNess210.github.io/frc/imperialism/2019/week7/frc_imperialism_map.svg"

def generateDensityCountyMap():
    densityMap = DensityCountyMap(svg_loc, dest_density_map_loc, frc_county_data_loc)
    densityMap.genSVG()

def generateUndefeatedCountyMap():
    undefeatedMap = UndefeatedCountyMap(svg_loc, dest_undefeated_map_loc, frc_county_data_loc, county_location_info_loc, team_custom_colors_loc=team_custom_colors_loc)
    undefeatedMap.genSVG()

def generateImperialismCountyMap():
    imperialismMap = ImperialismCountyMap(svg_loc, dest_imperialism_map_loc, frc_county_data_loc, county_location_info_loc, team_custom_colors_loc=team_custom_colors_loc)
    imperialismMap.genSVG()

if __name__ == '__main__':
    generateDensityCountyMap()
    #generateUndefeatedCountyMap()
    #generateImperialismCountyMap()
