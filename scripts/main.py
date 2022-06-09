import requests
import bs4
import json
import re
import time
import sys

number_of_requests = 0

def print_rate_limit_info(current_url, requests_start_time):
    requests_end_time = time.time()
    elapsed_time = requests_end_time - requests_start_time
    average_requests_per_second = number_of_requests / elapsed_time
    print(f"**** Rate limited ****\n{current_url}\nscript started at {requests_start_time}\nscript ended at {requests_end_time}\ntotal elapsed time {elapsed_time}\nnumber of requests for session = {number_of_requests}\naverage requests per second = {average_requests_per_second}")


def request_page(url, request_start_time):
    global number_of_requests
    number_of_requests += 1
    page = requests.get(url)
    if page.status_code == 429:
        print_rate_limit_info(url, request_start_time)

    return page


def scrape_hltv():
    player_database = {}
    # load player list
    with open('../data/player-db.json') as json_file:
        player_database = json.load(json_file)

    request_start_time = time.time()

    # iterate through players and scrape their data
    for player_id, player_data in player_database.items():
        # build base url for the current player
        player_url = f"https://www.hltv.org/player/{player_id}/{player_data.get('nick_name')}"

        #### scrape tab-infoBox page
        page = request_page(f"{player_url}#tab-infoBox", request_start_time)
        soup = bs4.BeautifulSoup(page.content, 'html.parser')

        if is_player_a_coach(soup):
            # mark player for deletion later
            player_database[player_id]['coach'] = True
            continue
        else:
            current_team = scrape_players_current_team(soup)
            player_database[player_id]['team'] = current_team

        # REAL NAME
        # This lambda enables soup to search for classes that ~only~ have the class name we're looking for.  
        # In this case we're looking for a tag with the class 'playerRealname' XOR 'player-realname'
        real_name_element = soup.find(lambda tag: tag.get('class') == ['playerRealname'] or tag.get('class') == ['player-realname'])
        player_database[player_id]['name'] = real_name_element.getText().strip()

        # AGE
        # this lambda only finds the first element with ~only~ the class 'playerAge'
        player_age_class_element = soup.find(lambda tag: tag.get('class') == ['playerAge'] or tag.get('class') == ['profile-player-stat'])
        if player_age_class_element is not None:
            age = player_age_class_element.getText().strip()
            parsed_age = re.findall(r'\d+', age)[0]
            player_database[player_id]['age'] = parsed_age

        
        #### scrape teamBox tab
        # PAST TEAMS
        page = request_page(f"{player_url}#tab-teamsBox", request_start_time)
        soup = bs4.BeautifulSoup(page.content, 'html.parser')

        past_teams = set()
        past_teams_elements = soup.find_all(lambda tag: tag.name == 'tr' and tag.get('class') == ['team', 'past-team'])
        if len(past_teams_elements) > 0:
            for e in past_teams_elements:
                past_teams.add(e.select('td > a > span')[0].getText())
        # save player's past teams in temp dictionary
        past_teams_list = list(past_teams)
        player_database[player_id]['past_teams'] = past_teams_list


        ### scrape achievementBox tab
        # MAJORS
        page = request_page(f"{player_url}#tab-achievementBox", request_start_time)
        soup = bs4.BeautifulSoup(page.content, 'html.parser')
        achievement_element = soup.find(lambda tag: tag.name == 'div' and tag.get('id') == 'majorAchievement')
        number_of_majors_won = "0"
        if achievement_element is not None:
            number_of_majors_won = achievement_element.select_one('.stat').getText()
        player_database[player_id]['majors'] = number_of_majors_won


        ### scrape weapons page
        # WEAPON
        page = request_page(f"https://www.hltv.org/stats/players/weapon/{player_id}/{player_data.get('nick_name')}", request_start_time)
        soup = bs4.BeautifulSoup(page.content, 'html.parser')

        favorite_weapon_element = soup.select_one('.stats-row')
        favorite_weapon = favorite_weapon_element.select('span')[1].getText().strip()
        player_database[player_id]['weapon'] = favorite_weapon

        # append new player data to file
        with open("../data/player-db-second-pass.json", "a") as outfile:
            json.dump(player_database, outfile)

        # sleep to prevent rate limiting from the hltv.org
        time.sleep(0.5)
        

# return True is player is a coach
def is_player_a_coach(soup):
    # extract the player's current team name if it exists, otherwise it'll have the default value
    current_team_element = soup.find(lambda tag: tag.get('class') == ['profile-player-stats-container'])

    # Soup failed to find the element || team name DOES NOT contain '(coach)'
    if current_team_element is None or '(coach)' not in current_team_element.select('span')[-1].getText():
        return False
    
    # Team name contains '(coach)'
    return True


def scrape_players_current_team(soup):
    current_team_element = soup.find(lambda tag: tag.get('class') == ['playerTeam'])
    if current_team_element is None:
        return 'No team'
    # getText() returns "Current teamTeamFURIA". [16:] removes "Current teamTeam" and leaves just the actual team name
    return current_team_element.getText().strip()[16:] 

if __name__ == '__main__':
    scrape_hltv()

