"""

Mixin to implement checks. Light weight flexible version of the

"""
import inspect
import sys
import json
from collections import defaultdict


class ReconMixin(object):
    def check_all_columns_match(self, spec, segment, frames, params):
        """
        Check whether all columns match...
        """

        status = {"check": "Match columns", "status": True, "message": ""}

        columns = set()
        for df in frames.values():
            columns.update(list(df.columns))

        for name, df in frames.items():
            if columns != set(df.columns):
                status["message"] += f"[{name}] Mismatch\n"

        return status

    def check_shapes_match(self, spec, segment, frames, params):
        """
        Check whether shapes match...
        """
        status = {"check": "Match Shapes", "status": True, "message": "", "details": ""}

        shapes = set()
        for df in frames.values():
            shapes.add(df.shape)

        if len(shapes) > 1:
            status["status"] = False
            status["message"] = f"Found {len(shapes)}. Expected 1"
            for name, df in frames.items():
                status["details"] += f"[{name}] {df.shape}\n"

        return status

    def default_checker(self, spec, data, checkspec, summary):

        sources = spec["sources"]

        # Collect segments
        segments = set()
        for s in sources:
            segments.update(list(data.get(s, {}).keys()))

        # For each segment..
        for segment in segments:

            frames = {}
            status = {
                "checker": "default_checker",
                "check": "Data Availability",
                "status": True,
                "message": "",
            }
            for s in sources:
                if segment not in data.get(s, {}):
                    status["status"] = False
                    status["message"] += f"[{s}] Missing\n"
                    continue
                df = data[s][segment]
                if df is None:
                    status["status"] = False
                    status["message"] += f"[{s}] Null\n"
                    continue
                frames[s] = df

            summary["segments"][segment].append(status)
            if not status["status"]:
                continue

            def get_func(cls, name):

                func = getattr(cls, name, getattr(cls, "check_" + name, None))
                if func is not None:
                    return func

                # Check the caller module
                callermod = sys.modules[cls.__module__]
                func = getattr(
                    callermod, name, getattr(callermod, "check_" + name, None)
                )
                if func is not None:
                    return func
                if name in globals():
                    handler = globals()[name]
                    return handler

                raise Exception(f"Handler {name} could not be found")

            for c in checkspec["checks"]:
                if isinstance(c, str):
                    handler = get_func(self, c)
                    params = {}
                elif isinstance(c, dict):
                    handler = c.get("handler", c.get("check"))
                    handler = get_func(self, handler)
                    params = c.get("params", {})
                else:
                    raise Exception("Unknown check format")

                if not callable(handler):
                    raise Exception("Handler not a valid method")

                status = handler(spec, segment, frames, params)
                if isinstance(status, dict):
                    summary["segments"][segment].append(status)
                elif isinstance(status, list):
                    summary["segments"][segment].extend(status)
                else:
                    raise Exception(f"Invalid response from checker method {handler}")

    def get_check_specs(self):
        raise Exception("To be overridden by parent of this mixin")

    def run_recon(self, data):

        # Get the checking specification...
        specs = self.get_check_specs()

        specsummary = []
        for spec in specs:

            name = spec["name"]

            # Get the checker specification.
            checks = spec["checks"]
            if isinstance(checks, list) and isinstance(checks[0], str):
                checks = [
                    {
                        "checks": checks,
                    }
                ]

            # Summary per-spec
            summary = {"spec": spec, "segments": defaultdict(list)}

            # Go through each checker specification. There could be
            # potentially multiple strategies to check...
            for checkspec in checks:
                checker = checkspec.get("checker", "default_checker")

                if not callable(checker):
                    checker = getattr(self, checker)

                if not callable(checker):
                    continue

                checker(spec, data, checkspec, summary)

            specsummary.append(summary)

        return specsummary
