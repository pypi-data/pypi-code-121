from askdata import human2query
import pandas as pd

if __name__ == "__main__":
    df = pd.DataFrame()
    df = df.append({'player': 'Cristiano Ronaldo', 'goals': '10', 'team': 'Juventus'}, ignore_index=True)
    df = df.append({'player': 'Roberto Baggio', 'goals': '2', 'team': 'Milan'}, ignore_index=True)
    res = human2query.data2nl(df=df, base_sentence="{{player}} score {{goals}} for team {{team}}")
    print(res.head())
