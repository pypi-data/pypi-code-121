import os
from click.decorators import pass_context

import pandas as pd
from sqlalchemy import distinct, func, select, text
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import alias

from disco.storage.db import Job, Metadata, Task, FeederHead, FeederLosses, ThermalMetrics, VoltageMetrics


METRIC_MAP = {
    "thermal": {
        "submetrics": [
            "line_max_instantaneous_loading",
            "line_max_moving_average_loading",
            "line_num_time_points_with_instantaneous_violations",
            "line_num_time_points_with_moving_average_violations",
            "transformer_max_instantaneous_loading",
            "transformer_max_moving_average_loading",
            "transformer_num_time_points_with_instantaneous_violations",
            "transformer_num_time_points_with_moving_average_violations",
        ]
    },
    "voltage": {
        "node_type": ["primaries", "secondaries"],
        "submetrics": [
            "min_voltage",
            "max_voltage",
            "num_nodes_any_outside_ansi_b",
            "num_time_points_with_ansi_b_violations",
        ],
    }
}


def build_thermal_queries(thresholds):
    for metric in METRIC_MAP["thermal"]["submetrics"]:
        if "min" in metric:
            comparison = ">="
        else:
            comparison = "<="
        query = f"{metric} {comparison} {thresholds[metric]}"



def build_queries(columns, thresholds, metric_class, on="all"):
    """Build queries for filtering metrics dataframes"""
    queries = []
    if on == "all":
        on = METRIC_MAP[metric_class]["submetrics"]
    metrics = [m for m in on if m in columns]
    for metric in metrics:
        if "min" in metric:
            comparison = ">="
        else:
            comparison = "<="
        query = f"{metric} {comparison} {thresholds[metric_class][metric]}"
        queries.append(query)
    return queries


def synthesize_voltage(results_df):
    """ Reduce voltage metrics table to one time-point like table
    where for each metric, only the worst metric value of all time-points
    is recorded
    """
    filter_cols = ["name",
                   "substation",
                   "feeder",
                   "placement",
                   "sample",
                   "penetration_level",
                   "scenario",
                   "node_type"]

    df = results_df.groupby(filter_cols)[["min_voltage"]].min().reset_index()
    df2 = results_df.groupby(filter_cols)[["max_voltage"]].max().reset_index()
    df = df.merge(df2, how="left", on=filter_cols)
    df3 = (
        results_df.groupby(filter_cols)[
            [
                "num_nodes_any_outside_ansi_b",
                "num_time_points_with_ansi_b_violations"
                ]
        ]
        .max()
        .reset_index()
    )

    df = df.merge(df3, how="left", on=filter_cols)

    return df

def synthesize_thermal(results_df):
    """ Reduce thermal metrics table to one time-point like table
    where for each metric, only the worst metric value of all time-points
    is recorded
    """

    filter_cols = ["name",
                   "substation",
                   "feeder",
                   "placement",
                   "sample",
                   "penetration_level",
                   "scenario"]
    df = (
        results_df.groupby(filter_cols)[
            [
                c for c in results_df.columns if (c not in filter_cols) and (c != "time_point")
                ]
        ]
        .max()
        .reset_index()
    )
    return df

def synthesize(metrics_df, metadata_df, metric_class):
    """ For snapshot hosting capacity analysis,
    reduce metrics and metadata tables to one time-point like tables
    where for each metric, only the worst metric value of all time-points
    is recorded
    """

    """the presence of 'time_point' in the dataframe
    indicates that we are dealing with a snapshot case"""
    if 'time_point' in metrics_df.columns:
        if metric_class == 'voltage':
            metrics_df = synthesize_voltage(metrics_df)
        if metric_class == 'thermal':
            metrics_df = synthesize_thermal(metrics_df)

    return metrics_df, metadata_df


def get_hosting_capacity(meta_df, metric_df, query_phrase, metric_class, hc_summary):
    """Return the hosting capacity summary"""
    pass_df = metric_df.query(query_phrase)
    fail_df = metric_df.query(f"~({query_phrase})")
    feeders = set(metric_df.feeder)

    for feeder in feeders:
        if not feeder in hc_summary.keys():
            hc_summary[feeder] = dict()
        temp_pass = pass_df[pass_df.feeder == feeder]
        temp_fail = fail_df[fail_df.feeder == feeder]
        if len(temp_fail) != 0 and len(temp_pass) == 0:
            min_hc = min(list(temp_fail.penetration_level.values))

        elif len(temp_fail) != 0 and len(temp_pass) != 0:
            temp_min_list = [
                p
                for p in list(temp_pass.penetration_level.values)
                if not p in list(temp_fail.penetration_level.values)
            ]
            if temp_min_list:
                min_hc = max(
                    [
                        p
                        for p in list(temp_pass.penetration_level.values)
                        if not p in list(temp_fail.penetration_level.values)
                    ]
                )
            else:
                min_hc = 0
        else:
            min_hc = max(list(temp_pass.penetration_level.values))

        if len(temp_pass) != 0:
            max_hc = max(list(temp_pass.penetration_level.values))
        else:
            max_hc = min(list(temp_fail.penetration_level.values))

        total_feeder_load = meta_df[meta_df.feeder == feeder][
            "load_capacity_kw"
        ].values[0]
        max_kW = max_hc * total_feeder_load
        min_kW = min_hc * total_feeder_load

        hc_summary[feeder][metric_class] = {
            "min_hc_pct": min_hc,
            "max_hc_pct": max_hc,
            "min_hc_kw": round(min_kW, 0),
            "max_hc_kw": round(max_kW, 0),
        }
    return hc_summary


def compute_hc(
    task_name,
    thresholds,
    metric_classes,
    scenario,
    node_types,
    on="all",
):
    """
    Compute hosting capacity

    Parameters
    ----------
    result_path: str, the output directory of metrics summary tables
    thresholds: dict, the mapping of metric thresholds
    metric_classes: list, the list of metric class
    node_types: list, the node types in voltage scenario
    on: list | str, the list of metrics of interest
        example: on = ['min_voltage', 'max_voltage']

    Returns
    -------
    dict: hc_summary
    dict: hc_overall
    list: query strings
    """
    engine = create_engine(f"postgresql://dthom@localhost/disco_db", echo=False, future=True)
    with Session(engine) as session:
        hc = HostingCapacity(session)
        hc.compute_hc(task_name, thresholds, metric_classes, scenario, node_types, on)


class HostingCapacity:
    def __init__(self, session: Session):
        self._session = session
        self._task_id = None
        self._jobs = None
        self._thermal = None
        self._voltage = None
        self._metadata = None

    def _create_tables(self, task_name, scenario):
        task_id = self._get_task_id(task_name)
        jobs = select(Job).join(Task).where(Task.id == task_id).subquery()
        self._thermal = select(ThermalMetrics).join(jobs).where(ThermalMetrics.scenario == scenario)
        self._thermal_table = self._thermal.subquery()
        self._voltage = select(VoltageMetrics).join(jobs).where(VoltageMetrics.scenario == scenario)
        self._voltage_table = self._voltage.subquery()
        self._metadata = select(Metadata).join(jobs).where(Metadata.scenario == scenario)
        self._metadata_table = self._metadata.subquery()

    def _get_task_id(self, task_name):
        stmt = select(Task).where(Task.name == task_name)
        results = self._session.execute(stmt).scalars().all()
        if len(results) == 0:
            raise ValueError(f"Did not find a task with name {task_name}")
        return results[0].id

    def _get_distinct_feeders(self, obj):
        return sorted([x.feeder for x in self._session.execute(obj.distinct("feeder")).scalars().all()])

    def compute_thermal_hc(
        self,
        thresholds,
        on,
        hc_summary,
    ):
        """
        Given the metric class, compute its hosting capacity

        Parameters
        ----------
        result_path: str, the output directory of metrics summary tables
        thresholds: dict, the mapping of metric thresholds
        metric_class: str, the metric class, 'voltage' or 'thermal'
        on: list | str, the list of metrics of interest
            example: on = ['min_voltage', 'max_voltage']
        hc_summary: dict

        """
        #thermal = self._session.execute(select(ThermalMetrics).where(ThermalMetrics.
        thermal_feeders = self._get_distinct_feeders(self._thermal)
        metadata_feeders = self._get_distinct_feeders(self._metadata)
        if thermal_feeders != metadata_feeders:
            raise ValueError(
                f"distinct feeders in tables must be identical: thermal={thermal_feeders} metadata={metadata_feeders}")
        if thermal_feeders == [None]:
            pass
            # TODO
            #meta_df.feeder = meta_df.substation
            #metric_df.feeder = metric_df.substation

        #thermal, metadata = self._synthesize_thermal(thermal, metadata)
        #queries = build_queries(metric_df.columns, thresholds, metric_class, on=on)
        #query_phrase = " & ".join(queries)
        stmt = self._thermal \
            .where(ThermalMetrics.line_max_instantaneous_loading_pct >= thresholds["line_max_instantaneous_loading"]) \
            .where(ThermalMetrics.line_max_moving_average_loading_pct >= thresholds["line_max_moving_average_loading"]) \
            .where(ThermalMetrics.line_num_time_points_with_instantaneous_violations >= thresholds["line_num_time_points_with_instantaneous_violations"]) \
            .where(ThermalMetrics.line_num_time_points_with_moving_average_violations >= thresholds["line_num_time_points_with_moving_average_violations"]) \
            .where(ThermalMetrics.transformer_max_instantaneous_loading_pct >= thresholds["transformer_max_instantaneous_loading"]) \
            .where(ThermalMetrics.transformer_max_moving_average_loading_pct >= thresholds["transformer_max_moving_average_loading"]) \
            .where(ThermalMetrics.transformer_num_time_points_with_instantaneous_violations >= thresholds["transformer_num_time_points_with_instantaneous_violations"]) \
            .where(ThermalMetrics.transformer_num_time_points_with_moving_average_violations >= thresholds["transformer_num_time_points_with_moving_average_violations"])
        
        #metric_df = metric_df.mask(metric_df.eq("None")).dropna()
        summary = self.get_thermal_hosting_capacity(stmt)
        return hc_summary

    def get_thermal_hosting_capacity(self, stmt):
        """Return the hosting capacity summary"""
        summary = {}
        #pass_table = self._session.execute(stmt).scalars().all()
        #fail_table = self._session.execute(text(query_phrase))
        feeders = self._get_distinct_feeders(self._thermal)

        for feeder in feeders:
            temp_pass = stmt.where(ThermalMetrics.feeder == feeder)
            temp_fail = fail_df[fail_df.feeder == feeder]
            if len(temp_fail) != 0 and len(temp_pass) == 0:
                min_hc = min(list(temp_fail.penetration_level.values))

            elif len(temp_fail) != 0 and len(temp_pass) != 0:
                temp_min_list = [
                    p
                    for p in list(temp_pass.penetration_level.values)
                    if not p in list(temp_fail.penetration_level.values)
                ]
                if temp_min_list:
                    min_hc = max(
                        [
                            p
                            for p in list(temp_pass.penetration_level.values)
                            if not p in list(temp_fail.penetration_level.values)
                        ]
                    )
                else:
                    min_hc = 0
            else:
                min_hc = max(list(temp_pass.penetration_level.values))

            if len(temp_pass) != 0:
                max_hc = max(list(temp_pass.penetration_level.values))
            else:
                max_hc = min(list(temp_fail.penetration_level.values))

            total_feeder_load = meta_df[meta_df.feeder == feeder][
                "load_capacity_kw"
            ].values[0]
            max_kW = max_hc * total_feeder_load
            min_kW = min_hc * total_feeder_load

            hc_summary[feeder] = {
                "min_hc_pct": min_hc,
                "max_hc_pct": max_hc,
                "min_hc_kw": round(min_kW, 0),
                "max_hc_kw": round(max_kW, 0),
            }
        return hc_summary

    def _get_table_columns(self, table_class):
        name = table_class.__tablename__
        stmt = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{name}'"
        return self._session.execute(stmt).scalars().all()

    def _is_snapshot(self):
        return "time_point" in self._get_table_columns(Metadata)

    def _synthesize_thermal(self, thermal, metadata):
        """ For snapshot hosting capacity analysis,
        reduce metrics and metadata tables to one time-point like tables
        where for each metric, only the worst metric value of all time-points
        is recorded
        """

        """the presence of 'time_point' in the dataframe
        indicates that we are dealing with a snapshot case"""
        # TODO DT: handle snapshot
        #if 'time_point' in metrics_df.columns:
        #    if metric_class == 'voltage':
        #        metrics_df = synthesize_voltage(metrics_df)
        #    if metric_class == 'thermal':
        #        metrics_df = synthesize_thermal(metrics_df)

        return thermal, metadata

    def compute_hc(
        self, 
        task_name,
        thresholds,
        metric_classes,
        scenario,
        node_types,
        on="all",
    ):
        self._create_tables(task_name, scenario)
        query_list = []
        hc_summary = {}
        hc_overall = {}
        for metric_class in metric_classes:
            if metric_class == "thermal":
                hc_summary, query_phrase = self.compute_thermal_hc(
                    thresholds["thermal"],
                    on,
                    hc_summary,
                )
            elif metric_class == "voltage":
                hc_summary, query_phrase = self.compute_voltage_hc(
                    thresholds["voltage"],
                    node_types,
                    on,
                    hc_summary,
                )
            query_list.append(query_phrase)
        for feeder, dic in hc_summary.items():
            hc_overall[feeder] = {}
            df = pd.DataFrame.from_dict(dic, "index")
            for column in df.columns:
                hc_overall[feeder][column] = min(df[column])

        return hc_summary, hc_overall, query_list
