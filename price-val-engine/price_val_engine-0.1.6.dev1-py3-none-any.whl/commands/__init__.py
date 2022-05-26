import os, sys
from argparse import ArgumentParser


ENV_VAR = 'PRICE_VAL_ENG_SETTINGS_MODULE'

def handle_default_options(options):
    """
    Include any default options to the all commands 
    """
    if options.settings:
        os.environ[ENV_VAR] = options.settings
    

class BaseCommand:
    
    def get_version(self):
        import price_val_engine
        return price_val_engine.get_version()

    def short_desc(self):
        return ""
    
    def long_desc(self):
        return self.short_desc()
    
    def help(self):
        return self.long_desc()
    
    def create_parser(self, prog_name, subcommand, **kwargs):
        """
        Create and return the ``ArgumentParser`` which will be used to
        parse the arguments to this command.
        """
        parser = ArgumentParser(
            prog='%s %s' % (os.path.basename(prog_name), subcommand),
            description=self.help() or None,
            **kwargs
        )
        parser.add_argument('--version', action='version', version=self.get_version())
        parser.add_argument(
            '--settings',
            help=(
                'project path to a settings module, e.g. '
                '"myproject.settings.py". If this isn\'t provided, the '
                f'{ENV_VAR} environment variable will be used.'
            ),
        )
        self.add_arguments(parser)
        return parser

    def add_arguments(self, parser):
        """
        add custom arguments to the parser.
        """
        pass

    def print_help(self, prog_name, subcommand):
        """
        Print the help message for this command.
        """
        parser = self.create_parser(prog_name, subcommand)
        parser.print_help()

    def run_from_argv(self, argv):
        """
        Set up any environment changes requested.
        """
        parser = self.create_parser(argv[0], argv[1])
        options = parser.parse_args(argv[2:])
        
        cmdline_options = vars(options)
        # Move positional args out of options to mimic legacy optparse
        args = cmdline_options.pop('args', ())
        handle_default_options(options)
        
        self.execute(*args, **cmdline_options)
    
    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement this method.
        """
        raise NotImplementedError('subclasses of BaseCommand must provide a handle() method')
    
    def execute(self, *args, **options):
        output = self.handle(*args, **options)
        if output:
            sys.stdout.write(output)
        return output
