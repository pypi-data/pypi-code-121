from get_auth import current_request


menu_list = current_request.menu_items_request()
filter_name = current_request.menu_items_request('Бомба брава с ромеско и щучьей икрой')
print(f'All menu by code: {menu_list}')
print(f'Filter menu: {filter_name}')
