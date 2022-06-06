import requests
import bs4
import json
import re
import time

number_of_requests = 0

def print_rate_limit_info(current_url, requests_start_time):
    script_end = time.time()
    elapsed_time = script_end - requests_start_time
    average_requests_per_second = number_of_requests / elapsed_time
    print(f"**** Rate limited ****\n{current_url}\nscript started at {requests_start_time}\nscript ended at {script_end}\ntotal elapsed time {elapsed_time}\nnumber of requests for session = {number_of_requests}\naverage requests per second = {average_requests_per_second}")


def request_page(url):
    # buffer time to prevent rate limiting from cloudflare
    #time.sleep(1)

    global number_of_requests
    number_of_requests += 1

    page = requests.get(url)
    if page.status_code == 429:
        print_rate_limit_info(url)

    return page

def scrape_hltv():
    player_database = {}
    # load player list
    with open('../data/player-db.json') as json_file:
        player_database = json.load(json_file)
    
    # iterate through players and scrape their data
    for player_id, player_data in player_database.items():
        print(f"{player_id} {player_data.get('nick_name')} ", end = '')
        # build base url for the current player
        player_url = f"https://www.hltv.org/player/{player_id}/{player_data.get('nick_name')}" # example: /11893/zywoo

        # get tab-infoBox page
        page = request_page(f"{player_url}#tab-infoBox")
        # parse page
        soup = bs4.BeautifulSoup(page.content, 'html.parser')

        if is_player_a_coach(soup):
            # remove coach from dictionary
            player_database.pop(player_id)
        else:
            current_team = scrape_players_current_team(soup)
            print(f"current_team: {current_team}")
        

# return True is player is a coach
def is_player_a_coach(soup):
    # extract the player's current team name if it exists, otherwise it'll have the default value
    current_team_element = soup.find(lambda tag: tag.get('class') == ['profile-player-stats-container'])

    # Soup failed to find the element || team name DOES NOT contain '(coach)'
    if current_team_element is None or '(coach)' not in current_team_element.select('span')[-1].getText():
        return False
    
    # Team name contains '(coach)'
    return True


# returns False if the player is a coach
# returns current_team (String) if the player is on a team
# returns default value 'Free Agent' if the player is not on a team
def scrape_players_current_team(soup):
    current_team_element = soup.find(lambda tag: tag.get('class') == ['playerTeam'])
    if current_team_element is None:
        return 'Free Agent'
    return current_team_element.select_one('a').getText().strip()

if __name__ == '__main__':
    scrape_hltv()


# iterate through player list and go to each player page using their player_url
# for key, value in player_database.items():
#     print(f"{key} {value.get('nick_name')}")
#     # build base url for the current player
#     player_params_url = key + '/' + value.get('nick_name') # /11893/zywoo
#     base_url = 'https://www.hltv.org/player/' + player_params_url

#     ### wait
#     time.sleep(sleep_time)

#     ### navigate to infoBox tab
#     info_box_url = base_url + '#tab-infoBox'
#     info_box_page = requests.get(info_box_url)
#     number_of_requests += 1
#     if info_box_page.status_code == 429:
#         print_rate_limit_info(info_box_url)
#     soup = bs4.BeautifulSoup(info_box_page.content, 'html.parser')
    
#     # extract the player's current team name if it exists, otherwise it'll have the default value: 'No Team'
#     current_team = 'Free Agent'
#     current_team_element = soup.find(lambda tag: tag.name == 'tr' and tag.get('class') == ['playerTeam'])
    

#     if current_team_element is not None:
#         current_team = current_team_element.select('td > a > span')[0].getText()
#     # save player's current team in temp dictionary
#     player_database[key]['current_team'] = current_team

#     # extract real name
#     # this lambda only finds the first element with ~only~ the class 'playerRealname'
#     real_name_element = soup.find(lambda tag: tag.get('class') == ['playerRealname'] or tag.get('class') == ['player-realname'])
#     player_database[key]['name'] = real_name_element.getText().strip()

#     # extract age
#     # this lambda only finds the first element with ~only~ the class 'playerAge'
#     player_age = soup.find(lambda tag: tag.get('class') == ['playerAge'])
#     age = player_age.contents[1].getText()
#     parsed_age = re.findall(r'\d+', age)[0]
#     player_database[key]['age'] = parsed_age

#     ### wait
#     time.sleep(sleep_time)

#     ### navigate to teamBox tab
#     teams_box_url = base_url + '#tab-teamsBox'
#     teams_box_page = requests.get(teams_box_url)
#     if teams_box_page.status_code == 429:
#         print_rate_limit_info(teams_box_url)
#     soup = bs4.BeautifulSoup(teams_box_page.content, 'html.parser')
    
#     # extract the player's past teams
#     past_teams = []
#     past_teams_elements = soup.find_all(lambda tag: tag.name == 'tr' and tag.get('class') == ['team', 'past-team'])
#     if len(past_teams_elements) > 0:
#         for e in past_teams_elements:
#             past_teams.append(e.select('td > a > span')[0].getText())
#     # save player's past teams in temp dictionary
#     player_database[key]['past_teams'] = past_teams

#     ### wait
#     time.sleep(sleep_time)

#     ### navigate to achievementBox tab
#     achievement_box_url = base_url + '#tab-achievementBox'
#     achievement_page = requests.get(achievement_box_url)
#     if achievement_page.status_code == 429:
#         print_rate_limit_info(achievement_box_url)
#     soup = bs4.BeautifulSoup(achievement_page.content, 'html.parser')
#     achievement_element = soup.find(lambda tag: tag.name == 'div' and tag.get('id') == 'majorAchievement')
#     number_of_majors_won = "0"
#     if achievement_element is not None:
#         number_of_majors_won = achievement_element.select_one('.stat').getText()
#     player_database[key]['majors'] = number_of_majors_won

#     ### wait
#     time.sleep(sleep_time)

#     ### navigate to weapons page
#     player_weapons_url = 'https://www.hltv.org/stats/players/weapon/' + player_params_url
#     weapons_page = requests.get(player_weapons_url)
#     if weapons_page.status_code == 429:
#         print_rate_limit_info(player_weapons_url)
#     soup = bs4.BeautifulSoup(weapons_page.content, 'html.parser')
#     favorite_weapon_element = soup.select_one('.stats-row')
#     favorite_weapon = favorite_weapon_element.select('span')[1].getText().strip()
#     player_database[key]['weapon'] = favorite_weapon

#     with open("../data/player-db-second-pass.json", "w") as outfile:
#         json.dump(player_database, outfile)
