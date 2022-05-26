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

    @app.get("/data", include_in_schema=False)  # Alias for /data/<today>
    @app.get("/data/{date}", tags=["Views"])
    def get_daily_data(date: Optional[str] = None, to_date: Optional[str] = None, clean: bool = False,
                       from_cache: bool = True, sensors: Optional[str] = None):
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

        if date:
            if not is_valid_date(date):
                raise BadDateError(date)
        else:  # The user provided date
            date = datetime.date.today().isoformat()

        if sensors:
            sensors = sensors.split(',')

        if to_date:
            if not is_valid_date_range(date, to_date):
                raise BadDateRangeError(date, to_date)
            else:
                return get_range_data(date, to_date, from_cache, sensors)
        else:
            return get_data(date, from_cache, sensors)

    @app.get("/plot/{date}")
    def get_daily_plot(date: Optional[str] = None, from_cache: bool = True, sensors: Optional[str] = None):
        return FileResponse(get_plot(date, from_cache), media_type="image/jpeg")

    return app
