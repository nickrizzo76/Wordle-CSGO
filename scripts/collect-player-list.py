import requests
import bs4
import json
import re
import time
import os

print(f"executing {os.path.basename(__file__)}")

# Extract and save data for players & nationalities
# - hltv_id (database key)
# - nick_name
# - nationality
# - player_url
# - rating

# res = requests.get('https://www.hltv.org/stats/players')
file = open('../hltv.html') # parse from local copy of hltv.org website
soup = bs4.BeautifulSoup(file.read(), 'html.parser')

player_ratings_table = soup.select_one('.player-ratings-table')
rows = player_ratings_table.select('tbody > tr')

playerDataBase = {}
nationalities = []

for row in rows:
    # extract data from .playerCol
    player = row.select_one('.playerCol')
    nationality = player.select_one('img[title]').attrs['title']
    player_url_element = player.select_one('a[href]')
    player_url = player_url_element.attrs['href']
    hltv_id = re.findall(r'\d+', player_url_element.attrs['href'])[0]
    player_nick_name = player_url_element.getText()

    # extract rating from .ratingCol
    rating = row.select_one('.ratingCol').getText()

    # save player in temporary dictionary
    playerDataBase[hltv_id] = {
        'nick_name': player_nick_name,
        'nationality': nationality,
        'player_url': player_url,
        'rating': rating,
    }

    # add nationality to nationalities list if its not in there already
    if nationality not in nationalities:
        nationalities.append(nationality)

# save players in file
with open("../data/player-db.json", "w") as outfile:
    json.dump(playerDataBase, outfile)

# save nationalities in file
nationalities.sort()
with open("../data/nationalities-db.json", "w") as outfile:
    json.dump(nationalities, outfile)
