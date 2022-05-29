""" vinca statistics module """

from vinca._lib.julianday import today
from vinca._lib.terminal import COLUMNS
from vinca._lib import unicode_bitmaps
from vinca._lib import ansi

from rich import console
from rich import align
print = console.Console().print

class Statistics:

    def __init__(self, cursor, interval=7):
            self.cursor = cursor
            self.interval = interval
            self.bincount = 100
            self.height = 6

    @property
    def current_week(self):
            return today() // self.interval

    def review_counts(self):
            min_week = self.current_week - self.bincount + 1
            self.cursor.execute('SELECT round(date / ?) as week, count(*) as count FROM reviews'
             ' GROUP BY week HAVING week >= ?', (self.interval, min_week))
            rows = self.cursor.fetchall()
            d = {week: 0 for week in range(min_week, self.current_week)}
            for row in rows:
                week, count = row
                d[week] = count
            return d.values()

    def create_counts(self):
            min_week = self.current_week - self.bincount + 1
            self.cursor.execute('SELECT round(create_date / ?) as week, count(*) as count FROM cards'
             ' GROUP BY week HAVING week >= ?', (self.interval, min_week))
            rows = self.cursor.fetchall()
            d = {week: 0 for week in range(min_week, self.current_week)}
            for row in rows:
                week, count = row
                d[week] = count
            return d.values()

    def counts_to_scores(self, counts):
            score_unit = max(counts) // self.height
            score_unit = max(score_unit, 1)
            return [1 if 0 < count < score_unit else count // score_unit for count in counts]

    def scores_to_bitmap(self, scores):
            l = scores                                          # 4
            l = ['1' * score for score in l]                    # 1111
            l = [f'{score:0>{self.height}s}' for score in l]    # 001111
            l = [[int(d) for d in list(score)] for score in l]  # [0,0,1,1,1,1]
            l = [list(col) for col in zip(*l)]                  # transpose matrix to be horizontal
            return unicode_bitmaps.Bitmap(l)

    def counts_to_unicode(self, counts):
            return self.scores_to_bitmap(self.counts_to_scores(counts)).to_unicode()

    def review_stats(self):
            self.cursor.execute('SELECT count(*) FROM reviews')
            total_reviews = self.cursor.fetchone()[0]
            if total_reviews is None: total_reviews = 0
            self.cursor.execute('SELECT sum(seconds) FROM reviews')
            total_time = self.cursor.fetchone()[0]
            if total_time is None: total_time = 0
            self.cursor.execute('SELECT min(date) FROM reviews')
            first_date = self.cursor.fetchone()[0]
            if first_date is None: first_date = today() - 1
            total_days = today() - first_date
            reviews_per_day = total_reviews / total_days
            time_per_review = total_time / total_reviews if total_reviews else 0
            time_per_day = total_time / total_days
            self.cursor.execute('SELECT count(*) FROM reviews WHERE date > ?',(today() - self.interval,))
            recent_reviews = self.cursor.fetchone()[0]
            self.cursor.execute('SELECT sum(seconds) FROM reviews WHERE date > ?',(today() - self.interval,))
            recent_time = self.cursor.fetchone()[0]
            if recent_time is None: recent_time = 0
            return (f'{total_reviews} reviews '
                    f'{reviews_per_day:.1f} per day '
                    f'{recent_reviews} in the past {self.interval} days\n'
                    f'{time_per_review:.1f} seconds per review {time_per_day // 60:.1f} minutes per day\n'
                    f'{total_time // 3600} hours '
                    f'{recent_time // 60} minutes in the last {self.interval} days')

    def create_stats(self):
            self.cursor.execute('SELECT count(*) FROM cards')
            total_cards = self.cursor.fetchone()[0]
            if total_cards is None: total_cards = 0
            self.cursor.execute('SELECT min(create_date) FROM cards')
            first_date = self.cursor.fetchone()[0]
            if first_date is None: first_date = today() - 1
            total_days = today() - first_date
            cards_per_day = total_cards / total_days
            self.cursor.execute('SELECT count(*) FROM cards WHERE create_date > ?',(today() - self.interval,))
            created_recent = self.cursor.fetchone()[0]
            if created_recent is None: created_recent = 0
            return (f'{total_cards} cards created '
                    f'{cards_per_day:.1f} per day '
                    f'{created_recent} in the past {self.interval} days')

    def print(self):
            review_map = self.counts_to_unicode(self.review_counts())
            create_map = self.counts_to_unicode(self.create_counts())
            print(justify='center')
            print('[underline]STATISTICS',style='bold',end='',justify='center')
            print(f'graphs show {self.bincount} intervals of {self.interval} days',justify='center')
            print(justify='center')
            print(align.Align.center(review_map), style='green')
            print('▔'*(self.bincount//2), style='red',justify='center')
            print(self.review_stats(), style='green',justify='center')
            print(justify='center')
            print(justify='center')
            print(align.Align.center(create_map), style='blue')
            print('▔'*(self.bincount//2), style='red',justify='center')
            print(self.create_stats(), style='blue',justify='center')
            print(justify='center')

