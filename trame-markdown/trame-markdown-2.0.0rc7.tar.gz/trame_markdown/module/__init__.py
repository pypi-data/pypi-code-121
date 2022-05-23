from pathlib import Path

# Compute local path to serve
serve_path = str((Path(__file__).with_name("serve") / "dist").resolve())

# Serve directory for JS/CSS files
serve = {"__trame_markdown": serve_path}

# List of JS files to load (usually from the serve path above)
scripts = ["__trame_markdown/markdown-it-vue.umd.min.js"]
styles = ["__trame_markdown/markdown-it-vue.css"]
