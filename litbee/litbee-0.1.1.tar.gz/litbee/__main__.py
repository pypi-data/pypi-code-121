"""Run streamlit run app.py from __main__.py."""
import sys
from streamlit import cli

sys.argv = ["streamlit", "run", "app.py"]
sys.exit(cli.main())
