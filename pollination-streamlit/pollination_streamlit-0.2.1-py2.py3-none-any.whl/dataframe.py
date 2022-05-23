import typing as t

import numpy as np
import pandas as pd
import streamlit as st


class ColumnMeta:

    _meta = {'job-id', 'run-id', 'run-status'}

    def __init__(self, inputs: t.List[str] = [], outputs: t.List[str] = [],
                 parameters: t.List[str] = [], artifacts: t.List[str] = []):
        self._inputs = set(inputs)
        self._outputs = set(outputs)
        self._parameters = set(parameters)
        self._artifacts = set(artifacts)

    def extend_from_run_result(self, result: t.List[dict]):
        inputs = []
        outputs = []
        parameters = []
        artifacts = []

        for res in result:
            r_type = res['type'].lower()
            name = res['name']

            if 'input' in r_type:
                if name in self._meta:
                    continue
                inputs.append(name)
            elif 'output' in r_type:
                outputs.append(name)

            if 'file' in r_type or 'folder' in r_type or 'path' in r_type:
                artifacts.append(name)
            else:
                parameters.append(name)

        self._inputs.update(set(inputs))
        self._outputs.update(set(outputs))
        self._parameters.update(set(parameters))
        self._artifacts.update(set(artifacts))

    @staticmethod
    def list(data: set) -> list:
        ls = list(data)
        ls.sort()
        return ls

    @property
    def inputs(self) -> t.List[str]:
        return self.list(self._inputs)

    @property
    def outputs(self) -> t.List[str]:
        return self.list(self._outputs)

    @property
    def meta(self) -> t.List[str]:
        return self.list(self._meta)

    @property
    def parameters(self) -> t.List[str]:
        return self.list(self._parameters)

    @property
    def artifacts(self) -> t.List[str]:
        return self.list(self._artifacts)

    @property
    def input_parameters(self) -> t.List[str]:
        return self.list(self._inputs & self._parameters)

    @property
    def output_parameters(self) -> t.List[str]:
        return self.list(self._outputs & self._parameters)

    @property
    def input_artifacts(self) -> t.List[str]:
        return self.list(self._inputs & self._artifacts)

    @property
    def output_artifacts(self) -> t.List[str]:
        return self.list(self._outputs & self._artifacts)


class RunsDataFrame:

    def __init__(self, df: pd.DataFrame, meta: ColumnMeta = ColumnMeta):
        self._df = df
        self._column_meta = meta

    @classmethod
    @st.cache(allow_output_mutation=True)
    def from_run_results(cls, data: t.List[t.List[dict]]) -> 'RunsDataFrame':
        meta = ColumnMeta()
        df = pd.DataFrame()
        for run in data:
            meta.extend_from_run_result(run)
            sub_df = pd.DataFrame(run)
            sub_df = pd.DataFrame(
                {'name': sub_df['name'], 'value': sub_df.apply(cls._get_value, axis=1)})
            job_id = sub_df[sub_df['name'] == 'job-id']['value'].iloc[0]
            run_id = sub_df[sub_df['name'] == 'run-id']['value'].iloc[0]

            sub_df['job_id'] = job_id
            sub_df['run-id'] = run_id
            sub_df.index = [0]*len(sub_df)

            pivot = sub_df.pivot(columns='name', values='value')
            df = df.append(pivot)

        df.columns.name = None
        df.set_index('run-id', inplace=True)
        df = df.infer_objects()

        return cls(df=df, meta=meta)

    @staticmethod
    def _get_value(row) -> any:
        if row['value'] is not np.NAN:
            return row['value']
        if row['source'] is not np.NAN:
            # print(row['source'])
            return row['source']['path']
        else:
            raise ValueError('No value to pick from...')

    @property
    def dataframe(self) -> pd.DataFrame:
        return self._df

    @property
    def inputs(self) -> pd.DataFrame:
        return self._df[self._column_meta.inputs]

    @property
    def outputs(self) -> pd.DataFrame:
        return self._df[self._column_meta.outputs]

    @property
    def parameters(self) -> pd.DataFrame:
        return self._df[self._column_meta.parameters]

    @property
    def artifacts(self) -> pd.DataFrame:
        return self._df[self._column_meta.artifacts]

    @property
    def input_parameters(self) -> pd.DataFrame:
        return self._df[self._column_meta.input_parameters]

    @property
    def input_artifacts(self) -> pd.DataFrame:
        return self._df[self._column_meta.input_artifacts]

    @property
    def output_parameters(self) -> pd.DataFrame:
        return self._df[self._column_meta.output_parameters]

    @property
    def output_artifacts(self) -> pd.DataFrame:
        return self._df[self._column_meta.output_artifacts]

    @property
    def meta(self) -> pd.DataFrame:
        return self._df[['job-id', 'run-status']]
