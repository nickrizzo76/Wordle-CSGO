import json

weapons = set()
player_database = {}
with open('../data/complete-player-db.json') as json_file:
        player_database = json.load(json_file)

for player in player_database:
    weapon = player_database[player]['weapon']
    weapons.add(weapon)

weaponsList = list(weapons)
print(weaponsList)
