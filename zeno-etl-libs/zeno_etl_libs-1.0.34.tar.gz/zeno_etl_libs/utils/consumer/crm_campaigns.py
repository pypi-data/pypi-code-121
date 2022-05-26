#!/usr/bin/env python
# coding: utf-8

"""
# Author - shubham.jangir@zeno.health
# Purpose - utility module with crm campaigns (multiple) functions
# Todo evaluate RS/MySQL read-write connections later
"""

from zeno_etl_libs.db.db import DB, MySQL
from zeno_etl_libs.logger import get_logger

from datetime import timedelta

import pandas as pd

# Common utility functions for crm-campaigns listed in this class
# Connections also inititated in the class, to be closed when the script is closed.


class CrmCampaigns:
    """
    # Sequence
    # Data prep
    # no_bill_in_last_n_days(data, run_date, last_n_days_param = 15)
    # no_call_in_last_n_days(data, run_date, last_n_days_param = 30)
    # patient_latest_store(data)
    # remove_dnd(data)
    # db_write()
    """

    def __init__(self):
        self.logger = get_logger()

        self.ms_connection_read = MySQL()
        self.ms_connection_read.open_connection()

        # ALERT: read_only=False, if you want connection which writes
        self.ms_connection_write = MySQL(read_only=False)
        self.ms_connection_write.open_connection()

        self.rs_db = DB()
        self.rs_db.open_connection()

    ##############################
    # Utility functions
    ##############################
    def patient_latest_store(self, data_pass):

        data_base_c_grp = data_pass.copy()
        patients = tuple(data_base_c_grp['patient_id'].to_list())

        self.logger.info("Length of patients tuple is - {}".format(len(patients)))

        ##########################################
        # Latest store-id
        ##########################################
        store_q = """
            select
                `patient-id`,
                `store-id`,
                `created-at`
            from
                (
                select
                    `patient-id`,
                    `store-id`,
                    `created-at`,
                    ROW_NUMBER() OVER (partition by `patient-id`
                order by
                    `created-at` desc) as bill_rank_desc
                from
                    `bills-1` b
                where `patient-id` in {}
            ) sub
            where
                bill_rank_desc = 1
        """.format(patients)

        data_store = pd.read_sql_query(store_q, self.ms_connection_read.connection)
        data_store.columns = [c.replace('-', '_') for c in data_store.columns]

        self.logger.info("Length of data store is {}".format(len(data_store)))

        # Already unique, but still check
        data_store['created_at'] = pd.to_datetime(data_store['created_at'])
        data_store = data_store.sort_values(by=['patient_id', 'created_at'],
                                            ascending=[True, False])

        # Keep latest store-id
        data_store = data_store.drop_duplicates(subset='patient_id')
        data_store = data_store[['patient_id', 'store_id']].copy()

        self.logger.info("Length of data store after dropping duplicates - is "
                         "{}".format(len(data_store)))

        return data_store

    def no_bill_in_last_n_days(self, data_pass, run_date, last_n_days_param=15):
        ##########################################
        # No bills in last 15 days
        ##########################################
        data_base_c_grp = data_pass.copy()
        patients = tuple(data_base_c_grp['patient_id'].to_list())

        self.logger.info("Length of patients tuple is - {}".format(len(patients)))

        # Take parameter input, default is 15
        last_n_days_cutoff = last_n_days_param
        self.logger.info("Last n days cutoff is {}".format(last_n_days_cutoff))

        run_date_minus_n_days = (pd.to_datetime(run_date) - timedelta(days=last_n_days_cutoff)).strftime("%Y-%m-%d")
        self.logger.info("Run date minus n days is {}".format(run_date_minus_n_days))

        lb_q = """
                SELECT
                    `patient-id`
                FROM
                    `bills-1`
                WHERE
                    `created-at` >= '{0} 00:00:00'
                    and `patient-id` in {1}
                GROUP BY
                    `patient-id`
        """.format(run_date_minus_n_days, patients)

        already_billed = pd.read_sql_query(lb_q, self.ms_connection_read.connection)
        already_billed.columns = [c.replace('-', '_') for c in already_billed.columns]

        already_billed_list = already_billed['patient_id'].to_list()

        self.logger.info("Length of Already billed last 15 days (List)- "
                         "fetched is {}".format(len(already_billed_list)))

        data_base_c_grp = data_base_c_grp.query("patient_id not in @already_billed_list")
        self.logger.info("Length of data base after filtering already billed - "
                         "length is {}".format(len(data_base_c_grp)))

        return data_base_c_grp

    def no_call_in_last_n_days(self, data_pass, run_date, last_n_days_param=30):
        ##########################################
        # No calls in last 30 days period
        ##########################################
        data_base_c_grp = data_pass.copy()
        patients = tuple(data_base_c_grp['patient_id'].to_list())

        self.logger.info("Length of patients tuple is - {}".format(len(patients)))

        # Take parameter input, default is 15
        last_n_days_cutoff = last_n_days_param
        self.logger.info("Last n days cutoff is {}".format(last_n_days_cutoff))

        run_date_minus_n_days = (pd.to_datetime(run_date) -
                                 timedelta(days=last_n_days_cutoff)).strftime("%Y-%m-%d")
        self.logger.info("Run date minus n days is {}".format(run_date_minus_n_days))

        calling_q = """
                    SELECT
                        `patient-id`
                    FROM
                        `calling-dashboard`
                    WHERE
                        (`list-date` >= '{0}'
                        OR `call-date` >= '{0}')
                        and `patient-id` in {1}
                    GROUP BY
                        `patient-id`
        """.format(run_date_minus_n_days, patients)

        data_c = pd.read_sql_query(calling_q, self.ms_connection_read.connection)
        data_c.columns = [c.replace('-', '_') for c in data_c.columns]

        already_p = data_c['patient_id'].drop_duplicates().to_list()
        self.logger.info("Length of Calling last {0} days (List)- "
                         "fetched is {1}".format(last_n_days_cutoff, len(already_p)))

        data_base_c_grp = data_base_c_grp.query("patient_id not in @already_p")
        self.logger.info("Length of data base after filtering already called - "
                         "length is {}".format(len(data_base_c_grp)))

        return data_base_c_grp

    def remove_dnd(self, data_pass):
        data_base_c_grp = data_pass.copy()

        read_schema = 'prod2-generico'
        self.rs_db.execute(f"set search_path to '{read_schema}'", params=None)

        # Read DND list
        dnd_q = """
            select
                (case
                    when a."patient-id" is not null then a."patient-id"
                    else b."id"
                end) as "patient-id"
            from
                "dnd-list" a
            left join "prod2-generico"."patients" b on
                a."phone" = b."phone"
            where a."call-dnd" = 1
            """
        self.logger.info(dnd_q)

        self.rs_db.execute(dnd_q, params=None)
        dnd: pd.DataFrame = self.rs_db.cursor.fetch_dataframe()
        if dnd is None:
            dnd = pd.DataFrame(columns=['patient_id'])
        dnd.columns = [c.replace('-', '_') for c in dnd.columns]

        self.logger.info("dnd data length is : {}".format(len(dnd)))

        dnd_list = dnd['patient_id'].drop_duplicates().to_list()

        # Remove those already covered
        data_base_c_grp = data_base_c_grp.query("patient_id not in @dnd_list")

        self.logger.info("Net list after removing DND - length is : {}".format(len(data_base_c_grp)))

        return data_base_c_grp

    def db_write(self, data_pass, run_date_str,
                 campaign_id_param, callback_reason_str_param,
                 store_daily_limit_param=5, default_sort_needed=True):

        self.logger.info("Running for run date {}".format(run_date_str))

        data_base_c_grp = data_pass.copy()
        # If default_sort then default sort on ABV descending, for each store
        if default_sort_needed:
            data_base_c_grp = data_base_c_grp.sort_values(by=['store_id', 'average_bill_value'],
                                                          ascending=[True, False])
            data_base_c_grp['priority'] = data_base_c_grp.groupby(['store_id']).cumcount() + 1
        else:
            # assumes that sorting is already done, with priority column present
            pass
        ##########################################
        # Filter on Ranking
        ##########################################
        # Take parameter input, default is 5
        store_daily_limit = store_daily_limit_param

        self.logger.info("Store level daily call limit is {}".format(store_daily_limit))

        read_schema = 'prod2-generico'
        self.rs_db.execute(f"set search_path to '{read_schema}'", params=None)

        store_limit_q = f"""select
                                "store-id" as "store_id",
                                "store-daily-limit" 
                            from
                                "{read_schema}"."store-calling-exceptions" sce
                            where
                                "campaign-id" = {campaign_id_param}
                                and current_date between "start-date" and "end-date";
                        """
        store_limit = self.rs_db.get_df(query=store_limit_q)

        data_base_c_grp = pd.merge(data_base_c_grp, store_limit, on='store_id', how='left')
        data_base_c_grp["store-daily-limit"] = data_base_c_grp["store-daily-limit"].fillna(store_daily_limit_param)
        data_base_c_grp = data_base_c_grp[data_base_c_grp['priority'] <= data_base_c_grp["store-daily-limit"]]
        data_base_c_grp = data_base_c_grp.drop(columns=["store-daily-limit"])

        self.logger.info("Length of data base after Rank filtering - "
                         "length is {}".format(len(data_base_c_grp)))

        ##########################################
        # WRITE to calling dashboard
        ##########################################
        data_export = data_base_c_grp[['store_id', 'patient_id', 'priority']].copy()
        data_export['list_date'] = run_date_str
        data_export['call_date'] = data_export['list_date']

        data_export['campaign_id'] = campaign_id_param  # integer
        data_export['callback_reason'] = callback_reason_str_param  # string
        data_export.columns = [c.replace('_', '-') for c in data_export.columns]

        ##########################################
        # DANGER ZONE
        ##########################################

        self.logger.info("Insert started for length {}".format(len(data_export)))

        data_export.to_sql(name='calling-dashboard', con=self.ms_connection_write.engine,
                           if_exists='append', index=False,
                           chunksize=500, method='multi')

        self.logger.info("Insert done")

    def close_connections(self):
        # Closing the DB Connection
        self.ms_connection_read.close()
        self.ms_connection_write.close()
        self.rs_db.close_connection()
