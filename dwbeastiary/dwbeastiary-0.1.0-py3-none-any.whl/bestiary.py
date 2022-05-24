
# standard libraries
import json
from random import randrange
import sys

# third-party libraries
import requests 


def pretty_print_monster(monster):
    return \
f'''{monster.get('name')} [{monster.get('monster_tags')}]
-----------------------------------------------------
HP: {monster["hp"]}
Armor: {monster["armor"]}
Attack: {monster["attack"]}
Damage: {monster["damage"]}
-----------------------------------------------------
{monster.get('description')}

Instinct: {monster["instinct"]}
-----------------------------------------------------
Moves: {monster["moves"]}
Special Qualities: {monster["special_qualities"]}
Attack Tags: {monster["attack_tags"]}
'''

def main():
    resp: requests.Response = requests.get('https://raw.githubusercontent.com/mileszs/dungeon-world-data/master/monsters.json')
    if not resp.ok:
        print('Error:', resp.status_code)
        sys.exit(1)
    
    original_monster_data = resp.json()

    monster_categories = list(original_monster_data.keys())

    print('What kind of monster would you like?')
    print('[0] Random')
    
    # original_monster_data.keys() ==> ['Cavern Dwellers', 'Dark Woods', 'Folk of the Realm', 'Lower Depths', 'Planar Powers', 'Ravenous Hordes', 'Swamp Denizens', 'Twisted Experiments', 'Undead Legion']
    for num, category in enumerate(monster_categories, start=1):
        print(f'[{num}] {category}')

    choice = int(input('Pick a category: '))
    if choice == 0:
        # random
        pass
    else:
        # specific category
        category = monster_categories[choice - 1]
        monsters = original_monster_data.get(category)
        rand_index = randrange(0, len(monsters))
        print(pretty_print_monster(monsters[rand_index]))

if __name__ == '__main__':
    main()