from datetime import date
f = lambda x, d='/': f'{x.day:02d}{d}{x.month:02d}{d}{x.year}'
t = lambda: all([f(date(2020, 3, 2)) == '02/03/2020'])
