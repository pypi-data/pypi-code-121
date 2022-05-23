import typer
from typer import Option
from typing import Optional
from thingsmatrix import apis
from thingsmatrix import __version__
from rich.console import Console

app_help = \
f'''
ThingsMatrix API TOOL
version: {__version__}
'''
app = typer.Typer(help=app_help)

console = Console()

api = apis.ThingsMatrix()


@app.command()
def reports(sn: Optional[str] = typer.Argument(..., help='imei'),
            starttime: Optional[str] = typer.Option(
                None, help='Format as YYYY-mm-dd HH:mm:ss'),
            endtime: Optional[str] = typer.Option(
                None, help='Format as YYYY-mm-dd HH:mm:ss')):
    '''
    Get reports by imei and datetime
    '''
    response, reports = api.get_devices_reports(sn=sn,
                                                startTime=starttime,
                                                endTime=endtime)
    if response != None or reports != None:
        console.print(reports.json)


# @app.command()
# def devices(sn:Optional[str],model:Optional[str],group:Optional[str],status:Optional[str]):
#     api.get_devices()


@app.command()
def device(sn: str,
           status: bool = Option(
               False,
               "--status",
               "-s",
               help="show status",
           ),
           model: bool = Option(
               False,
               "--model",
               "-m",
               help="show model name",
           ),
           group: bool = Option(
               False,
               "--group",
               "-g",
               help="show group name",
           ),
           location_mode: bool = Option(
               False,
               "--location_mode",
               "-lm",
               help="show location mode",
           ),
           heartbeat: bool = Option(
               False,
               "--heatbeat",
               "-hb",
               help="show heartbeat timer setting",
           ),
           ac_report_interval: bool = Option(
               False,
               "--ac_report_interval",
               "-ari",
               help="show ac report interval",
           ),
           dc_report_interval: bool = Option(
               False,
               "--dc_report_interval",
               "-dri",
               help="show dc report interval",
           ),
           gps_report_interval: bool = Option(
               False,
               "--gps_report_interval",
               "-gri",
               help="show gps report interval",
           )):
    '''
    Get device info by imei
    '''
    device = api.get_device(sn)
    if device:
        if status:
            console.print(device.status.name)
        elif model:
            console.print(device.model.name)
        elif group:
            console.print(device.group.name)
        elif location_mode:
            console.print(device.latest.gpsLocating.name)
        elif heartbeat:
            console.print(device.template.heartbeat_timer)
        elif ac_report_interval:
            console.print(device.template.ac_report_interval)
        elif dc_report_interval:
            console.print(device.template.dc_report_interval)
        elif gps_report_interval:
            console.print(device.template.gps_report_interval)
        else:
            console.print(device.json)


@app.command()
def events(sn: str,
           starttime: Optional[str] = typer.Option(
               None, help='Format as YYYY-mm-dd HH:mm:ss'),
           endtime: Optional[str] = typer.Option(
               None, help='Format as YYYY-mm-dd HH:mm:ss')):
    """Get events by imei and datetime
    """
    response, events = api.get_devices_events(sn, starttime, endtime)
    if response != None or events != None:
        console.print(events.json)

def run():
    try:
        app()
        typer.Exit(0)
    except ConnectionError as e:
        console.log(e, log_locals=True)
    except Exception as e:
        console.print_exception(show_locals=True)
        typer.Exit(-1)


if __name__ == "__main__":
    run()
