"""
Invoke cli interface when puft executed as a script:
```py
python -m puft
```
"""
try:
    from .tools import cli
except ImportError:
    from tools import cli


if __name__ == "__main__":
    cli.main()