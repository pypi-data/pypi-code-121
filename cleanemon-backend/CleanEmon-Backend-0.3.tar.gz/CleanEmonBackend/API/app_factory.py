import datetime
from typing import Optional

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse


def create_app():
    from .API import get_data
    from .API import get_range_data
    from .API import get_plot

    from CleanEmonBackend.lib.exceptions import BadDateError
    from CleanEmonBackend.lib.exceptions import BadDateRangeError

    from CleanEmonBackend.lib.validation import is_valid_date
    from CleanEmonBackend.lib.validation import is_valid_date_range

    meta_tags = [
        {
            "name": "Views",
            "description": "Essential views."
        }
    ]

    app = FastAPI(openapi_tags=meta_tags, swagger_ui_parameters={"defaultModelsExpandDepth": -1})

    @app.exception_handler(BadDateError)
    def bad_date_exception_handler(request: Request, exception: BadDateError):
        return JSONResponse(
            status_code=400,
            content={"message": f"Bad date ({exception.bad_date}), not in ISO format (YYYY-MM-DD)."}
        )

    @app.exception_handler(BadDateRangeError)
    def bad_date_range_exception_handler(request: Request, exception: BadDateRangeError):
        return JSONResponse(
            status_code=400,
            content={"message": f"Bad date range ({exception.bad_from_date} - {exception.bad_to_date}). Dates must "
                                f"be in ISO format (YYYY-MM-DD) and placed in correct order."}
        )

    @app.get("/json/date/{date}", tags=["Views"])
    def get_json_date(date: str = None, clean: bool = False, from_cache: bool = True, sensors: Optional[str] = None):
        """Returns the daily data for the supplied **{date}**. If {date} is omitted, then **{date}** is automatically
        set to today's date.

        If **to_date** parameter is used, then a range of daily data is returned starting from **{date}** up to
        **to_date**

        - **{date}**: A date in YYYY-MM-DD format
        - **to_date**: A date in YYYY-MM-DD format. If present, defines the inclusive end of date range for returned
        data
        - **clean**: If set to True, requests an on-demand disaggregation and cleaning over the returned data. This is
        only useful when dealing with today's data
        - **from_cache**: If set to False, forces data to be fetched again from the central database. If set to True,
        data will be looked up in cache and then, if they are not found, fetched from the central database.
        - **sensors**: A comma (,) separated list of sensors to be returned. If present, only sensors defined in that
        list will be returned
        """

        parsed_date: str

        if date.lower() == "today":
            parsed_date = datetime.date.today().isoformat()
        elif date.lower() == "yesterday":
            yesterday = datetime.date.today() - datetime.timedelta(days=1)
            parsed_date = yesterday.isoformat()
        elif is_valid_date(date):
            parsed_date = date
        else:
            raise BadDateError(date)

        if sensors:
            sensors = sensors.split(',')

        return get_data(parsed_date, from_cache, sensors)

    # @app.get("/json/date/", tags=["Views"])
    # def get_json_today(date: str = None, clean: bool = False, from_cache: bool = True, sensors: Optional[str] = None):
    #     return get_plot_date("today", clean, from_cache, sensors)

    @app.get("/json/range/{from_date}/{to_date}", tags=["Views"])
    def get_json_range(from_date: str, to_date: str, clean: bool = False, from_cache: bool = True,
                       sensors: Optional[str] = None):
        """Returns the daily data for the supplied **{date}**. If {date} is omitted, then **{date}** is automatically
        set to today's date.

        If **to_date** parameter is used, then a range of daily data is returned starting from **{date}** up to
        **to_date**

        - **{date}**: A date in YYYY-MM-DD format
        - **to_date**: A date in YYYY-MM-DD format. If present, defines the inclusive end of date range for returned
        data
        - **clean**: If set to True, requests an on-demand disaggregation and cleaning over the returned data. This is
        only useful when dealing with today's data
        - **from_cache**: If set to False, forces data to be fetched again from the central database. If set to True,
        data will be looked up in cache and then, if they are not found, fetched from the central database.
        - **sensors**: A comma (,) separated list of sensors to be returned. If present, only sensors defined in that
        list will be returned
        """

        if not is_valid_date_range(from_date, to_date):
            raise BadDateRangeError(from_date, to_date)

        if sensors:
            sensors = sensors.split(',')

        return get_range_data(from_date, to_date, from_cache, sensors)

    @app.get("/plot/date/{date}", tags=["Views"])
    def get_plot_date(date: str = None, clean: bool = False, from_cache: bool = True, sensors: Optional[str] = None):
        energy_data = get_json_date(date, clean, from_cache, sensors)
        # plot_path = plot(energy_data)
        # return FileResponse(plot_path, media_type="image/jpeg")
        return JSONResponse(
            status_code=501,
            content={"message": "This feature is currently not implemented"}
        )

    @app.get("/plot/range/{from_date}/{to_date}", tags=["Views"])
    def get_plot_range(from_date: str, to_date: str, clean: bool = False, from_cache: bool = True,
                       sensors: Optional[str] = None):
        data_list = get_json_range(from_date, to_date, clean, from_cache, sensors)
        # plot_path = plot(energy_data)
        # return FileResponse(plot_path, media_type="image/jpeg")
        return JSONResponse(
            status_code=501,
            content={"message": "This feature is currently not implemented"}
        )

    return app
