try:
    from .app import app
except ImportError:
    print(
        "Run `pip install fastapi prometheus_client` to install missing dependencies."
    )
