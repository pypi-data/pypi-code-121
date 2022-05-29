from get_auth import current_request


waiter_list = current_request.waiter_list_request()
print(f'All waiters: {waiter_list}')
