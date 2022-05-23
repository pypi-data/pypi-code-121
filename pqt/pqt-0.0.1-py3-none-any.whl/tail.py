import argparse
from .summary import Summary


class Tail(Summary):

    def __init__(self, **kwargs):
        Summary.__init__(self, **kwargs)
        self.cursor.execute(
            f"""
                SELECT COUNT(*) FROM "{self.file}"
            """
        )
        count = self.cursor.fetchone()[0]
        skip = count - self.lines
        self.cursor.execute(
            f"""
                SELECT * FROM "{self.file}" LIMIT ? OFFSET ?
            """, [self.lines, skip]
        )
        self.data = self.cursor.fetchall()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'file',
        help='The filename of the parquet file to show the last lines off.'
    )
    parser.add_argument(
        '-n',
        '--lines',
        default=10,
        type=int,
        help='Number of entries to show'
    )
    Tail(**vars(parser.parse_args())).print()


if __name__ == '__main__':
    main()
