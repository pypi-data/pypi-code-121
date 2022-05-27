#!/usr/bin/env python
import sys
import subprocess

subprocess.call(['itkdb', 'add-comment'] + sys.argv[1:])
