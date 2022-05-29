from ..tools.logger import Logger

def run_profile():
    text = """
        How to use:
        1. pip install snakeviz
        2. python -m cProfile -o out.prof train.py
        3. snakeviz out.prof
    """
    Logger.info(text)
