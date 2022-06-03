import requests
import bs4
import json
import re
import time

player_database = {}
with open('player-db.json') as json_file:
    player_database = json.load(json_file)

# iterate through player list and go to each player page using their player_url
for key, value in player_database.items():
    print(f"{key} {value.get('nick_name')}")
    # build base url for the current player
    player_params_url = key + '/' + value.get('nick_name') # /11893/zywoo
    base_url = 'https://www.hltv.org/player/' + player_params_url

    # navigate to infoBox tab
    info_box_url = base_url + '#tab-infoBox'
    info_box_page = requests.get(info_box_url)
    soup = bs4.BeautifulSoup(info_box_page.content, 'html.parser')
    
    # extract real name
    # this lambda only finds the first element with ~only~ the class 'playerRealname'
    
    real_name_element = soup.find(lambda tag: tag.get('class') == ['playerRealname'])

    real_name = real_name_element.getText()
    # save player's rating in temp dictionary
    player_database[key]['name'] = real_name.strip()

    # extract age
    # this lambda only finds the first element with ~only~ the class 'playerAge'
    player_age = soup.find(lambda tag: tag.get('class') == ['playerAge'])
    age = player_age.contents[1].getText()
    parsed_age = re.findall(r'\d+', age)[0]
    # save player's rating in temp dictionary
    player_database[key]['age'] = parsed_age

    ### extract rating

    # navigate to teamBox tab
    teams_box_url = base_url + '#tab-teamsBox'
    teams_box_page = requests.get(teams_box_url)
    soup = bs4.BeautifulSoup(teams_box_page.content, 'html.parser')

    # extract the player's current team name if it exists, otherwise it'll have the default value: 'No Team'
    current_team = 'Free Agent'
    current_team_element = soup.find(lambda tag: tag.name == 'tr' and tag.get('class') == ['team'])

    if current_team_element is not None:
        current_team = current_team_element.select('td > a > span')[0].getText()
    # save player's current team in temp dictionary
    player_database[key]['current_team'] = current_team
    
    # extract the player's past teams
    past_teams = []
    past_teams_elements = soup.find_all(lambda tag: tag.name == 'tr' and tag.get('class') == ['team', 'past-team'])
    if len(past_teams_elements) > 0:
        for e in past_teams_elements:
            past_teams.append(e.select('td > a > span')[0].getText())
    # save player's past teams in temp dictionary
    player_database[key]['past_teams'] = past_teams

    achievement_box_url = base_url + '#tab-achievementBox'
    achievement_page = requests.get(achievement_box_url)
    soup = bs4.BeautifulSoup(achievement_page.content, 'html.parser')
    achievement_element = soup.find(lambda tag: tag.name == 'div' and tag.get('id') == 'majorAchievement')
    number_of_majors_won = "0"
    if achievement_element is not None:
        number_of_majors_won = achievement_element.select_one('.stat').getText()
    player_database[key]['majors'] = number_of_majors_won

    player_weapons_url = 'https://www.hltv.org/stats/players/weapon/' + player_params_url
    weapons_page = requests.get(player_weapons_url)
    soup = bs4.BeautifulSoup(weapons_page.content, 'html.parser')
    favorite_weapon_element = soup.select_one('.stats-row')
    favorite_weapon = favorite_weapon_element.select('span')[1].getText().strip()
    player_database[key]['weapon'] = favorite_weapon






# # live code =======>
# with open("player-db.json", "w") as outfile:
#     json.dump(playerDataBase, outfile)
# # <========

# json_object = json.dumps(playerDataBase, indent = 4)
# print(json_object)
# print(playerDataBase)