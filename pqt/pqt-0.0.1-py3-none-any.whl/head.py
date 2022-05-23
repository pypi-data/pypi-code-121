import argparse
from .summary import Summary


class Head(Summary):

    def __init__(self, **kwargs):
        Summary.__init__(self, **kwargs)
        self.cursor.execute(
            f"""
                SELECT * FROM "{self.file}" LIMIT ?
            """, [self.lines]
        )
        self.data = self.cursor.fetchall()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'file',
        help='The filename of the parquet file to analyze'
    )
    parser.add_argument(
        '-n',
        '--lines',
        default=10,
        type=int,
        help='Number of entries to show'
    )
    Head(**vars(parser.parse_args())).print()


if __name__ == '__main__':
    main()
