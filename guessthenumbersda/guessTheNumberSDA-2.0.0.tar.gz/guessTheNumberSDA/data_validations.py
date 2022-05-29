def validate_input(var):
    val = input(f'Please insert {var}: ')

    while True:
        if val.isnumeric():
            return int(val)
        else:
            val = input(f'Not valid number. Please insert again {var}: ')
