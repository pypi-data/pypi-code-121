from pathlib import Path

# Compute local path to serve
serve_path = str(Path(__file__).with_name("serve").resolve())

# Serve directory for JS/CSS files
serve = {"__trame_router": serve_path}

# List of JS files to load (usually from the serve path above)
scripts = ["__trame_router/trame-router.umd.min.js"]

# List of Vue plugins to install/load
vue_use = ["trame_router"]
