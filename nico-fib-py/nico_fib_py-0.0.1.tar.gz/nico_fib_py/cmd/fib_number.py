import argparse

from nico_fib_py.fib_calcs.fib_number import recursive_fibonnaci_number


def fib_numb() -> None:
    parser = argparse.ArgumentParser(
        description='Calculate Fibonacci numbers'
    )
    parser.add_argument('--number', action='store', type=int, required=True, help="Fibonacci number to be calculated")

    args = parser.parse_args()

    print(f"Your Fibonacci number is: " f"{recursive_fibonnaci_number(number=args.number)}")