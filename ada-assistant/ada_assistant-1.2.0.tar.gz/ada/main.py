import ada.query_processor
import sys

def main():
    if len(sys.argv) < 2:
        print("What's your command?")
    else:
        ada.query_processor.process_query(sys.argv[1:])
