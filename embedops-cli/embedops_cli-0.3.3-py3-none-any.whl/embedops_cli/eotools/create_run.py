#!/usr/bin/env python
"""
`create_run.py`
=======================================================================
A small script to create an EmbedOps CI run record and return the new ID
* Author(s): Bryan Siepert
"""
from embedops_cli.eotools.ci_run import CIRun

if __name__ == "__main__":
    ci_run = CIRun()
    ci_run.main()
