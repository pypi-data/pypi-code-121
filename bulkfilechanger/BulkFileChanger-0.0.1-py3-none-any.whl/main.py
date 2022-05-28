#!/usr/bin/python3 -B
from .bulkfilechanger import BulkFileChanger

def main():
	bulkfilechanger = BulkFileChanger()
	bulkfilechanger.run()

if __name__ == '__main__':
	raise SystemExit(main())