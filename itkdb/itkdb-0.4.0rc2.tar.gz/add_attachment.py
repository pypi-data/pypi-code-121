#!/usr/bin/env python
import sys
import subprocess

subprocess.call(['itkdb', 'add-attachment'] + sys.argv[1:])
