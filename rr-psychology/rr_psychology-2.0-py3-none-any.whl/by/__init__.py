from rr_psychology.by import unconditional_situations as us
from rr_psychology.by.common import utilities
from rr_psychology.by.pressure import Pressure


# pre condition = set main data
def get_pressure_data(tour_id: int, team_id: int, team_name: str, season='21/22'):
    main_data = utilities.initiate_main_data_dict(tour_id=tour_id, team_id=team_id, team_name=team_name, season=season)
    # step 1 - export basic data
    export = us.ExportData(main_data=main_data, current_pressure=False)
    games_df = export.get_all_history_data
    # step 2 - export pressure data
    return Pressure(main_data=main_data, pressure_view=True, psy_games_df=games_df).calculate_pressure()
