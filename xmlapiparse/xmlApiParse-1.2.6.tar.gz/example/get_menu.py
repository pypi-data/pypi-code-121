from get_auth import current_request


menu_list = current_request.menu_request(1)
print(f'All menu by code: {menu_list}')
