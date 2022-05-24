import sys
import textwrap

sys.path.append('..')

import cherrypy  # noqa: E402
import cherrypy_psycopg2  # noqa: E402,F401

import psycopg2.extras


class Root:
    @cherrypy.expose
    @cherrypy.tools.psycopg2()
    def index(self, action=None):
        cursor = cherrypy.request.psycopg2_cursor

        cursor.execute("""
            INSERT INTO log (message) VALUES (%(message)s)
        """, {
            'message': f"Viewing index with action {action!r}"
        })

        if action == "external-redirect":
            raise cherrypy.HTTPRedirect("/")
        elif action == "internal-redirect":
            raise cherrypy.InternalRedirect("/")
        elif action == "not-found":
            raise cherrypy.NotFound()
        elif action == "exception":
            raise Exception("Example exception")

        cursor.execute("""
            SELECT "timestamp", message
            FROM log
            ORDER BY "timestamp" DESC
            LIMIT 10
        """)

        output = textwrap.dedent("""\
            <html>
            <body>
            <table>
            <tr><th>Timestamp</th><th>Message</th></tr>
        """)

        for record in cursor:
            output += "<tr><td>{timestamp}</td><td>{message}</td></tr>".format(**record)

        output += textwrap.dedent("""\
            </table>
            <ul>
            <li><a href="/">Standard page</a>
            <li><a href="/?action=external-redirect">External redirect</a>
            <li><a href="/?action=internal-redirect">Internal redirect</a>
            <li><a href="/?action=not-found">Not Found page</a>
            <li><a href="/?action=exception">Exception</a>
            </ul>
            </body>
            </html>
        """)

        return output


if __name__ == '__main__':
    cherrypy.quickstart(Root(), '/', {'/': {
        'tools.psycopg2.minconn': 1,
        'tools.psycopg2.maxconn': 5,
        'tools.psycopg2.dsn': "",
        'tools.psycopg2.cursor_factory': psycopg2.extras.RealDictCursor
    }})
