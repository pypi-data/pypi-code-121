import os
import sys
import fsspec

from price_val_engine.commands import BaseCommand


class Command(BaseCommand):
    
    def add_arguments(self, parser):
        parser.add_argument('--input', help='input file path')
        parser.add_argument('--output', nargs='?', help='output file path', default="output.csv")
    
    def _get_protocol(file_path):
        return fsspec.core.strip_protocol()
                
    def handle(self, *args, **options):
        input_file = options.pop("input")
        output_file = options.pop("output")
        
        if not str(input_file).endswith('.csv'):
            sys.stderr.write("Invalid input [file type]. Please enter csv file path \n")    
        if not str(output_file).endswith('.csv'):
            sys.stderr.write("Invalid output file type, Please enter csv file path \n")
            
        if input_file:
            from price_val_engine.core.engine import Engine
            engine = Engine(
                input_file_path=input_file,
                output_file_path=output_file
            )
            engine.validate_all()
            engine.save()
            
            
        
    
    