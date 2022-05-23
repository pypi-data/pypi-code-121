import sys
import os
import sentry_sdk

os.environ['QT_MAC_WANTS_LAYER'] = '1'

from kabaret.app.ui.gui.styles.gray import GrayStyle
from libreflow.resources.icons import libreflow, status
from libreflow.resources import file_templates

from .session import SessionGUI
from .resources.gui.styles.custom_style import CustomStyle

CustomStyle()


def main(argv):
    if 'SENTRY_DSN' in os.environ:
        print('SENTRY_DSN found!')
        sentry_sdk.init(os.environ['SENTRY_DSN'], traces_sample_rate=1.0)
    
    (
        session_name,
        host,
        port,
        cluster_name,
        db,
        password,
        debug,
        user,
        site,
        jobs_filter,
        uri,
        remaining_args,
    ) = SessionGUI.parse_command_line_args(argv)

    if site:
        os.environ['KABARET_SITE_NAME'] = site
    if user:
        os.environ['USER_NAME'] = user
    if jobs_filter:
        os.environ['JOBS_DEFAULT_FILTER'] = jobs_filter
    else:
        os.environ['JOBS_DEFAULT_FILTER'] = site

    session = SessionGUI(session_name=session_name, debug=debug, search_index_uri=uri)
    session.cmds.Cluster.connect(host, port, cluster_name, db, password)

    session.start()
    session.close()


if __name__ == '__main__':
    main(sys.argv[1:])