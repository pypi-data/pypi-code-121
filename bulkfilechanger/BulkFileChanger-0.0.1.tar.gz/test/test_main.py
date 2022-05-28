#!/usr/bin/python3 -B
from bulkfilechanger import *

def test_main():
	bulkfilechanger = BulkFileChanger()
	bulkfilechanger.run()

if __name__ == '__main__':
	raise SystemExit(test_main())