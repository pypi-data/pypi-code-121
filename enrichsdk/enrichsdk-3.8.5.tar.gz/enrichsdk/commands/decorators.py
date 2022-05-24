import traceback
from functools import update_wrapper
import click
import logging

logger = logging.getLogger("app")


def log_activity(runfunc):
    """
    This is a decorator that wraps around a click command.

    This decorator captures run metadata, initiates logging,
    and handles exceptions during execution of the command.

    Example::

        @click.command('compare')
        @log_activity
        @click.pass_obj
        def _compare(config):
          "Compares the data"
           ....

    """

    @click.pass_context
    def logged_run(ctx, *args, **kwargs):
        """
        Make note of what is going in and out...
        """

        config = ctx.obj
        config.start_run(ctx.command.name)
        try:
            try:
                config.state["command"]["name"] = ctx.command_path
                config.state["command"]["description"] = ctx.command.help
            except:
                traceback.print_exc()
                pass

            response = ctx.invoke(runfunc, *args, **kwargs)
            config.set_status("success")
            config.end_run()
            return response
        except Exception as e:
            config.set_message(str(e))
            config.set_status("failure")
            logger.exception("Failure in execution")
            config.end_run()
            print("Command failed. Please see the log")

    return update_wrapper(logged_run, runfunc)
