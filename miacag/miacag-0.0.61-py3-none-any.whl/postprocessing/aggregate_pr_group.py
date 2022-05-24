import pandas as pd
from dataclasses import dataclass
from miacag.plots.plotter import convertConfFloats
from miacag.utils.sql_utils import getDataFromDatabase, \
    update_cols, add_columns
import psycopg2
import numpy
from psycopg2.extensions import register_adapter, AsIs
def addapt_numpy_float64(numpy_float64):
    return AsIs(numpy_float64)
def addapt_numpy_int64(numpy_int64):
    return AsIs(numpy_int64)
register_adapter(numpy.float64, addapt_numpy_float64)
register_adapter(numpy.int64, addapt_numpy_int64)


@dataclass
class Aggregator:
    sql_config: dict
    fields_to_aggregate: list

    def get_df_from_query(self) -> None:
        # return df with data
        self.df, self.conn = getDataFromDatabase(self.sql_config)
        self.conn.close()

    def compute_mean_confidence(self, aggregated_cols_list):
        # return records from dataframe to update
        count = 0
        df_frames = []
        for field in self.fields_to_aggregate:
            agg_field = aggregated_cols_list[count]
            confidences = self.df[field]
            confidences = convertConfFloats(confidences)
            df_new = self.df.copy()
           # self.df[agg_field] = confidences
            df_new[agg_field] = confidences
            df_new = df_new.groupby(
                ['PatientID', 'StudyInstanceUID'])[agg_field].mean()
            df_new = df_new.to_frame()
            df_new.reset_index(inplace=True)
            df2 = self.df.merge(df_new, left_on=['PatientID', 'StudyInstanceUID'],
                          right_on=['PatientID', 'StudyInstanceUID'],
                          how='right')[['rowid', agg_field]]
            df_frames.append(df2)
            count += 1
        dfs = [df.set_index('rowid') for df in df_frames]
        result_df = pd.concat(dfs, axis=1)
        result_df.reset_index(inplace=True)
        result_df['rowid'].values.astype(int)
        records = result_df.to_records()
        return records

    def update_colum_wrap(self, records, cols) -> None:
        self.conn = psycopg2.connect(
            host=self.sql_config['host'],
            database=self.sql_config['database'],
            user=self.sql_config['username'],
            password=self.sql_config['password'])
        update_cols(self.conn, records, self.sql_config, cols, page_size=2)

    def __call__(self):
        self.get_df_from_query()
        aggregated_cols_list = [
            i + "_aggregated" for i in self.fields_to_aggregate]
        data_types = ["float8"] * len(aggregated_cols_list)
        add_columns(self.sql_config, aggregated_cols_list, data_types)
        records = self.compute_mean_confidence(aggregated_cols_list)
        self.update_colum_wrap(records, aggregated_cols_list)


if __name__ == '__main__':
    sql_config = {'database':
                  'mydb',
                  'username':
                  "sauroman",
                  'password':
                  "123qweasd",
                  'host':
                  "localhost",
                  'port':
                  "5432",
                  'table_name':
                  "classification_config_angio_SEP_May20_18-20-38_sauromanPC_dicom",
                  'query':
                  "SELECT * FROM ?table_name WHERE (\"sten_procent_2_midt_rca_transformed_confidences\" IS NOT NULL) AND (\"sten_procent_3_prox_rca_transformed_confidences\" IS NOT NULL);"
                  }
    fields_to_aggregate = [
        "sten_procent_3_prox_rca_transformed_confidences",
        "sten_procent_2_midt_rca_transformed_confidences"]
    agg = Aggregator(sql_config, fields_to_aggregate)
    agg()
