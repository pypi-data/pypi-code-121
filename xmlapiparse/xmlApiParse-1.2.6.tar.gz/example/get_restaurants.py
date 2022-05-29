from get_auth import current_request


restaurant_list = current_request.restaurants_request()
print(f'All restaurants: {restaurant_list}')
