import re

from ...models.logger._colorations import colored_term


class WerkzeugColorFilter:
    P_REQUEST_LOG = re.compile(r'^(.*?) - - \[(.*?)\] "(.*?)" (\d+) (\d+|-)$')
    method_colors = {
        "GET": "green",
        "POST": "yellow",
        "PUT": "blue",
        "DELETE": "red",
    }
    routes_exceptions = []

    def filter(self, record):
        match = self.P_REQUEST_LOG.match(record.msg)
        if match:
            try:
                ip, date, request_line, status_code, size = match.groups()
                method = request_line.split(" ")[0]  # key 0 always exists
                route = request_line.split()[1]

                if route.strip() == "/":
                    return False

                for pattern in WerkzeugColorFilter.routes_exceptions:
                    match = re.match(pattern, route)
                    if match:
                        return False

                fmt = self.method_colors.get(method.upper(), "white")
                request_line = colored_term(request_line, fmt)
                ip = colored_term(ip, "blue")
                date = colored_term(date, "yellow")
                try:
                    status_code_value = int(status_code)
                    if status_code_value >= 500:
                        status_code = colored_term(status_code, back="red")
                    elif status_code_value >= 400:
                        status_code = colored_term(status_code, "red")
                    elif status_code_value >= 300:
                        status_code = colored_term(status_code, "black", "yellow")
                    elif status_code_value >= 200:
                        status_code = colored_term(status_code, "green")
                    else:
                        status_code = colored_term(status_code, bold=True)
                except ValueError:
                    pass
                record.msg = '%s - - [%s] "%s" %s %s' % (
                    ip,
                    date,
                    request_line,
                    status_code,
                    size,
                )
            except ValueError:
                pass
        return record
