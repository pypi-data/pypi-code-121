from get_auth import current_request

employees_list = current_request.employees_list_request()
find_employees_list = current_request.employees_list_request('Егор Максимов')
print(f'All Employees: {employees_list}')
print(f'Filter Employees: {find_employees_list}')
