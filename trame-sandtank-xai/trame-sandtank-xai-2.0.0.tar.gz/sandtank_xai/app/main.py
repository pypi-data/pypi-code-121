from trame.app import get_server
from . import ui, engine


def main(server=None, **kwargs):
    # Get or create server
    if server is None:
        server = get_server()

    if isinstance(server, str):
        server = get_server(server)

    # Get CLI info into state
    server.cli.add_argument("--data", help="Path to trained AI model", dest="data")
    server.state.path_to_model = server.cli.parse_known_args()[0].data

    # Bind server to app
    ui.initialize(server)  # setup state default first
    engine.initialize(server)

    # Start server
    server.start(**kwargs)


if __name__ == "__main__":
    main()
