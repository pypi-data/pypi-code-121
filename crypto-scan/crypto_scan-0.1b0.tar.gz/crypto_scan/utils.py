import ast
import pandas as pd
import swifter  # don't remove, is used as pd.Dataframe.swifter.apply(...)


def json_col_to_df(df, col_name, prefix=True, chunk_size=int(1e5)):
    assert df.index.is_unique, "index is not unique"

    def _json_col_to_df(_df, col_name, prefix=prefix):
        json_df = _df[col_name].copy()
        _df = _df.drop([col_name], axis=1)
        if len(json_df[json_df.notnull()].values) > 0 and isinstance(json_df[json_df.notnull()].values[0], str):
            json_df.loc[json_df.notnull()] = json_df.loc[json_df.notnull()].swifter.apply(ast.literal_eval)
        json_df.loc[json_df.isnull()] = [{}] * json_df.isnull().sum()
        json_df = pd.DataFrame(data=json_df.tolist())
        if prefix is True:
            json_df.columns = [f"{col_name}_{c}" for c in json_df.columns]
        json_df_len = len(json_df)
        for c in json_df.columns:
            _df[c] = json_df[c].values
        assert json_df_len == len(_df), "df length changed!"
        return _df

    my_list = []
    for start in range(0, len(df), chunk_size):
        end = min(start+chunk_size, len(df))
        my_list.append(_json_col_to_df(df.iloc[start:end, :], col_name))

    return pd.concat(my_list, axis=0)
