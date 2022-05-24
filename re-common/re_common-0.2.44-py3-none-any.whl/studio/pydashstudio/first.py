import pydash

users = [
    {'name': 'Michelangelo', 'active': False},
    {'name': 'Donatello', 'active': False},
    {'name': 'Leonardo', 'active': True}
]
callback = lambda item: item["name"] == "Donatello"
pydash.find_index(users, callback)
