from datetime import date, timedelta

from .config_helper import ConfigHelper
from .soozaccess import SoozAccess

# root
# yt0QlYIQXS7xH6KDyn4M8Vcq


def daterange(start_date: date, n_dates: int):
    for n in range(n_dates):
        yield start_date + timedelta(n)


def main():
    users = ["test1", "test2"]
    group = "group test"
    start_date = date(2020, 1, 1)
    n_dates = 5

    ConfigHelper.host = "http://localhost:3000"
    ConfigHelper.verbose = True

    SoozAccess.prepare_users(group, users)

    # create data
    for name in users:
        with SoozAccess(name, name) as user:
            for day in daterange(start_date, n_dates):
                user.responses.put_response(2, 21, 3, day.strftime("%Y-%m-%d"))


if __name__ == "__main__":
    main()
