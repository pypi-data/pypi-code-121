#   Copyright 2015-2016, 2022 University of Lancaster
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import cherrypy

import psycopg2.pool

COMMITTABLE_HANDLER_EXCEPTIONS = (
    cherrypy.HTTPRedirect,
    cherrypy.InternalRedirect,
    cherrypy.NotFound
)


class Psycopg2Tool(cherrypy.Tool):
    def __init__(self):
        super().__init__('before_handler', self.execute, priority=20)

        self._pools = {}

    def execute(self, minconn, maxconn, dsn, cursor_factory=None):
        dsn = f"fallback_application_name='cherrypy_psycopg2' {dsn}"

        if dsn not in self._pools:
            self._pools[dsn] = psycopg2.pool.ThreadedConnectionPool(minconn, maxconn, dsn=dsn)

        pool = self._pools[dsn]

        inner_handler = cherrypy.serving.request.handler

        def wrapper(*args, **kwargs):
            connection = None
            connection_attempt = 0

            while not connection:
                connection_attempt += 1
                connection = pool.getconn()

                try:
                    connection.reset()
                except Exception:
                    pool.putconn(connection, close=True)
                    connection = None

                    # After a PostgreSQL server restart all connections in the
                    # pool will be broken, so try up to maxconn+1 times to get a
                    # working connection
                    if connection_attempt <= maxconn:
                        msg = f"Database connection failed (attempt {connection_attempt} of {maxconn+1})"
                        cherrypy.log.error(msg, traceback=True)
                    else:
                        msg = "No working database connections"
                        cherrypy.log.error(msg, traceback=True)
                        raise cherrypy.HTTPError(message="psycopg2 connection failure")

            cherrypy.request.psycopg2_cursor = connection.cursor(cursor_factory=cursor_factory)

            try:
                response = inner_handler(*args, **kwargs)
            except COMMITTABLE_HANDLER_EXCEPTIONS:
                connection.commit()
                raise
            except Exception:
                connection.rollback()
                raise
            else:
                connection.commit()
            finally:
                cherrypy.request.psycopg2_cursor.close()
                pool.putconn(connection)

            return response

        cherrypy.serving.request.handler = wrapper


cherrypy.tools.psycopg2 = Psycopg2Tool()
