def get_database_name(user, frequence, underlying, algo, starting_date, running_date, db_path_suffix):
    return  user + '_' + frequence + '_' + underlying + '_' + algo + '_'+ starting_date.strftime(
        '%d_%b_%Y') + '_' + running_date.strftime('%d_%b_%Y') + db_path_suffix

def get_cointegration_database_name(user, frequence, underlying_x, underlying_y, starting_date, running_date, db_path_suffix):
    return  user + '_' + frequence + '_' + underlying_x + '_' + underlying_y + '_'+ starting_date.strftime(
        '%d_%b_%Y') + '_' + running_date.strftime('%d_%b_%Y') + db_path_suffix

def get_daily_database_name(user, frequence, underlying, algo, starting_date, running_date, delay, db_path_suffix):
    return  user + '_' + frequence + '_' + underlying + '_' + algo + '_'+ starting_date.strftime(
        '%d_%b_%Y') + '_' + running_date.strftime('%d_%b_%Y')+ '_' + str(delay) + db_path_suffix