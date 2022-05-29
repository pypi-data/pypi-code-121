import sqlite3
conn = sqlite3.connect(":memory:")

def now():
        return conn.execute("select julianday('now','localtime') + 0.5").fetchone()[0]
def today():
        return int(now())

class JulianDate(float):
        
        def __str__(self):
            return conn.execute("select datetime(? - 0.5)", (float(self),)).fetchone()[0][:10]

