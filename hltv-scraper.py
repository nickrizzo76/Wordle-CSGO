import requests
import bs4
import json
import re
import time

#res = requests.get('https://www.hltv.org/stats/players')
file = open('hltv.html')
soup = bs4.BeautifulSoup(file.read(), 'html.parser')

players = soup.select('.playerCol')  # '.playerCol > a'
del players[0]  # first index is not a player

nationalities = ['No Team']
playerDataBase = {}

# Download data for players
# - nationality
# - playerURL
# - hltvId
# - playerNickName
for player in players:
    nationality = player.contents[0].attrs['title']
    playerURL = player.contents[1].attrs['href']
    hltvId = re.findall(r'\d+', playerURL)[0]
    playerNickName = player.contents[1].getText()
    
    # update db with data
    playerDataBase.update({hltvId: {
        'nick_name': playerNickName,
        'nationality': nationality,
        'player_url': playerURL,
    }})

    # add nationality to nationalities list if its not in there already
    if nationality not in nationalities:
        nationalities.append(nationality)

nationalities.sort()

# iterate through player list and go to each player page using their player_url
count = 0
for key, value in playerDataBase.items():
    print(f"count: {count}\n{key}\n{value.get('nick_name')}")
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
    playerDataBase[key]['name'] = real_name.strip()

    # extract age
    # this lambda only finds the first element with ~only~ the class 'playerAge'
    player_age = soup.find(lambda tag: tag.get('class') == ['playerAge'])
    age = player_age.contents[1].getText()
    parsed_age = re.findall(r'\d+', age)[0]
    # save player's rating in temp dictionary
    playerDataBase[key]['age'] = parsed_age

    # extract rating
    # this lambda only finds the first element with ~only~ the class 'player-stat'
    # player_stat_element = soup.find(lambda tag: tag.get('class') == ['player-stat'])
    # if player_stat_element is not None:
    #     rating = player_stat_element.contents[1].getText() ######## if none then find Rating 1.0 at https://www.hltv.org/stats/players/7592/device
    # else:
    #     player_page = requests.get('https://www.hltv.org/stats/players/' + key + value.get('nick_name'))
    #     soup = bs4.BeautifulSoup(info_box_page.content, 'html.parser')

    # # save player's rating in temp dictionary
    # playerDataBase[key]['rating'] = rating

    # navigate to teamBox tab
    teams_box_url = base_url + '#tab-teamsBox'
    teams_box_page = requests.get(teams_box_url)
    soup = bs4.BeautifulSoup(teams_box_page.content, 'html.parser')

    # extract the player's current team name if it exists, otherwise it'll have the default value: 'No Team'
    current_team = 'No Team'
    current_team_element = soup.find(lambda tag: tag.name == 'tr' and tag.get('class') == ['team'])
    if len(current_team_element) > 0:
        current_team = current_team_element.select('td > a > span')[0].getText()
    # save player's current team in temp dictionary
    playerDataBase[key]['current_team'] = current_team
    
    # extract the player's past teams
    past_teams = []
    past_teams_elements = soup.find_all(lambda tag: tag.name == 'tr' and tag.get('class') == ['team', 'past-team'])
    if len(past_teams_elements) > 0:
        for e in past_teams_elements:
            past_teams.append(e.select('td > a > span')[0].getText())
    # save player's past teams in temp dictionary
    playerDataBase[key]['past_teams'] = past_teams

    achievement_box_url = base_url + '#tab-achievementBox'
    achievement_page = requests.get(achievement_box_url)
    soup = bs4.BeautifulSoup(achievement_page.content, 'html.parser')
    achievement_element = soup.find(lambda tag: tag.name == 'div' and tag.get('id') == 'majorAchievement')
    number_of_majors_won = "0"
    if achievement_element is not None:
        number_of_majors_won = achievement_element.select_one('.stat').getText()
    playerDataBase[key]['majors'] = number_of_majors_won

    player_weapons_url = 'https://www.hltv.org/stats/players/weapon/' + player_params_url
    weapons_page = requests.get(player_weapons_url)
    soup = bs4.BeautifulSoup(weapons_page.content, 'html.parser')
    favorite_weapon_element = soup.select_one('.stats-row')
    favorite_weapon = favorite_weapon_element.select('span')[1].getText().strip()
    playerDataBase[key]['weapon'] = favorite_weapon

    if count > 4:
        break
    time.sleep(0.5)



# live code =======>
with open("player-db.json", "w") as outfile:
    json.dump(playerDataBase, outfile)
# <========

# json_object = json.dumps(playerDataBase, indent = 4)
# print(json_object)
# print(playerDataBase)










# # iterate through player list and go to each player page using their player_url
# for key, value in playerDataBase.items():
    
#     # load player page
#     player_url = value.get('player_url')
#     player_page = requests.get(player_url)
#     # build soup
#     soup = bs4.BeautifulSoup(player_page.content, 'html.parser')
#     # extract rating
#     rating = soup.select('.statistics span')[-1].getText()
#     playerDataBase.update({key: {
#         'rating': rating
#     }})
#     time.sleep(0.5)
# #     #current_team = soup.select('.SummaryTeamname > a')[0].getText()
# #     #print(value.get('nick_name'), current_team)
