from argparse import ArgumentError, ArgumentParser
from importlib import import_module
import pkgutil, os, sys
from price_val_engine.commands import (
    BaseCommand, handle_default_options
)


class CommandLineUtility:

    
    def __init__(self, argv) -> None:
        self.argv = argv or sys.argv[:]
        self.prog_name = os.path.basename(self.argv[0])
        
        if self.prog_name == "__main__.py":
            self.prog_name = 'python -m price_val_engine'
            
        
    @property
    def commands(self):
        import price_val_engine
        command_dir = os.path.join(price_val_engine.__path__[0], "commands")
        return {
            name: "price_val_engine.commands" for _, name, is_pkg in pkgutil.iter_modules([command_dir])
                if not is_pkg and not str(name).startswith("_")
        }
    
    def fetch_command(self, name):
        
        commands = self.commands
        
        try:
            module = commands[name]
        except KeyError:
            if not os.environ.get('PRICE_VAL_ENG_SETTINGS_MODULE'):
                sys.stderr.write("No [price_val_engine] settings specified.\n")
                
            sys.stderr.write('Unknown command: %r' % name)
            
            sys.stderr.write("\nType '%s help' for usage.\n" % self.prog_name)
            sys.exit(1)
            
        if isinstance(module, BaseCommand):
            # If the command is already loaded, use it directly.
            return module
        else:
            module = import_module("{}.{}".format(module, name))
            return module.Command()
        
            # sys.stderr.write('Invalid command: %r' % commnd)
        
        
    def run(self):
        try:
            sub_command = self.argv[1]
        except IndexError:
            sub_command = 'help'  # Display help if no arguments were given.
        
        parser = ArgumentParser(usage='%(prog)s sub_command [options] [args]', add_help=False, allow_abbrev=False)
        parser.add_argument('--settings')
        parser.add_argument('args', nargs='*')  # catch-all
        try:
            options, args = parser.parse_known_args(self.argv[2:])
            handle_default_options(options)
        except ArgumentError:
            pass  # Ignore any option errors at this point.
        
        # _parser = self.fetch_command('run').create_parser('price_val_engine', 'runserver')
        # _options, _args = _parser.parse_known_args(self.argv[2:])
        #for _arg in _args:
        #    self.argv.remove(_arg)


        if sub_command == 'help':
            if '--commands' in args:
                sys.stdout.write("\n".join(sorted(self.commands))  + '\n')
            elif not options.args:
                sys.stdout.write("\n".join(sorted(self.commands))  + '\n')
            else:
                self.fetch_command(options.args[0]).print_help(self.prog_name, options.args[0])
        elif sub_command == 'version' or self.argv[1:] == ['--version'] or self.argv[1:] == ['-v']:
            import price_val_engine
            price_val_engine.get_version()
        else:
            self.fetch_command(sub_command).run_from_argv(self.argv)


def run_from_commandline(argv=None):
    utility = CommandLineUtility(argv)
    utility.run()