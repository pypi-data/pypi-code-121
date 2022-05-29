from get_auth import current_request


waiter_list = current_request.get_waiter()
print(f'All waiters: {waiter_list}')
