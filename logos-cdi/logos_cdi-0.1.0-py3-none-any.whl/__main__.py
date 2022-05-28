from asyncio import run
from logos_cdi.application import Application


def main():
    app = Application([
        'logos_cdi',
        'logos_cdi.manager',
        'logos_cdi.command'
    ])

    command = app.get('command')
    run(command.execute())


if __name__ == '__main__':
    main()
