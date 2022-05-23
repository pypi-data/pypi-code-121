#!/usr/bin/env python
# coding: utf-8
import argparse
import sys
import os
import datetime

sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper import helper
import numpy as np
import pandas as pd

status = {
    "updated": "updated",
    "pending": "pending",
    "updating": "updating",
}

patients_metadata_table = "patients-metadata-2"
bill_metadata_table = "bills-1-metadata"


def insert_new_patients(db):
    limit_str = f" limit {limit}; " if limit else ""
    query = f'''
        insert
            into
            "prod2-generico"."{patients_metadata_table}" (id,
            "created-at",
            "updated-at",
            "created-by",
            "etl-status"
            )
        select
            p.id,
            p."created-at",
            convert_timezone('Asia/Calcutta', GETDATE()),
            'etl-job',
            '{status['pending']}'
        from
            "prod2-generico"."patients" p
        inner join (
            select
                "patient-id"
            from
                "prod2-generico"."{bill_metadata_table}" bm
            group by
                "patient-id"
            ) bm1 on
            bm1."patient-id" = p.id
        left join "prod2-generico"."{patients_metadata_table}" pm on
            pm.id = p.id
        where
            pm.id is null
            -- and date(p."updated-at") between '2021-06-01' and '2021-11-30'
            and (pm."etl-status" != '{status['updated']}'
            or pm."etl-status" is null)
    {limit_str}
    '''
    db.execute(query, params=None)


def mark_old_patients_pending(db):
    # mark old patients etl-status pending if they have transacted
    query = f"""
            update
                "prod2-generico"."{patients_metadata_table}" pm2
            set
                "etl-status" = '{status['pending']}',
                "updated-at" = convert_timezone('Asia/Calcutta', GETDATE())
            from
                (
                select
                    pm.id
                from
                    "prod2-generico"."{patients_metadata_table}" pm
                inner join
                    "prod2-generico"."{bill_metadata_table}" bm on
                    pm.id = bm."patient-id"
                where
                    pm."updated-at" < bm."updated-at" ) ab
            where 
                pm2.id = ab.id;
        """
    db.execute(query, params=None)


def mark_pending_patients_updating(db):
    limit_str = f"limit {batch_size} " if batch_size else ""

    query = f"""
        update
            "prod2-generico"."{patients_metadata_table}" pm2
        set
            "etl-status" = '{status['updating']}'
        from
            (
            select
                pm.id
            from
                "prod2-generico"."{patients_metadata_table}" pm
            where
                "etl-status" = '{status['pending']}'
            {limit_str}
            ) ab
        where 
            pm2.id = ab.id;
    """
    db.execute(query, params=None)


def get_to_be_updated_patients(db):
    # ## Considering only changed patients
    query = f'''
     select
        id,
        "created-at",
        "updated-at",
        "created-by",
        "etl-status"
    from
        "prod2-generico"."{patients_metadata_table}" pm
    where
        "etl-status" = '{status['updating']}'
    '''
    db.execute(query, params=None)
    _changed_patients: pd.DataFrame = db.cursor.fetch_dataframe()
    return _changed_patients


def update_bill_agg_fields(db):
    query = f"""
        update
            "prod2-generico"."{patients_metadata_table}" t
        set
            "first-bill-date" = s."first-bill-date",
            "last-bill-date" = s."last-bill-date",
            "first-bill-id" = s."first-bill-id",
            "last-bill-id" = s."last-bill-id",
            "average-bill-value" = s."average-bill-value",
            "total-quantity" = s."total-quantity",
            "quantity-generic" = s."quantity-generic",
            "quantity-chronic" = s."quantity-chronic",
            "quantity-ethical" = s."quantity-ethical",
            "quantity-rx" = s."quantity-rx",
            "quantity-repeatable" = s."quantity-repeatable",
            "quantity-goodaid" = s."quantity-goodaid",
            "quantity-others-type" = s."quantity-others-type",
            "number-of-bills" = s."number-of-bills",
            "hd-bills" = s."hd-bills",
            "is-repeatable" = s."is-repeatable",
            "is-generic" = s."is-generic",
            "is-chronic" = s."is-chronic",
            "is-goodaid" = s."is-goodaid",
            "is-ethical" = s."is-ethical",
            "is-rx" = s."is-rx",
            "is-others-type" = s."is-others-type",
            "hd-flag" = s."hd-flag",
            "ecom-flag" = s."ecom-flag",
            "pr-flag" = s."pr-flag",
            "total-spend" = s."total-spend",
            "spend-generic" = s."spend-generic",
            "promo-min-bill-date" = s."promo-min-bill-date",
            "hd-min-bill-date" = s."hd-min-bill-date",
            "ecom-min-bill-date" = s."ecom-min-bill-date",
            "pr-min-bill-date" = s."pr-min-bill-date",
            "generic-min-bill-date" = s."generic-min-bill-date",
            "goodaid-min-bill-date" = s."goodaid-min-bill-date",
            "ethical-min-bill-date" = s."ethical-min-bill-date",
            "chronic-min-bill-date" = s."chronic-min-bill-date",
            "repeatable-min-bill-date" = s."repeatable-min-bill-date",
            "others-type-min-bill-date" = s."others-type-min-bill-date",
            "digital-payment-min-bill-date" = s."digital-payment-min-bill-date",
            "rx-min-bill-date" = s."rx-min-bill-date",
            "digital-payment-flag" = s."digital-payment-flag",
            "total-mrp-value" = s."total-mrp-value",
            "recency-customer-days" = s."recency-customer-days",
            "system-age-days" = s."system-age-days",
            "quantity-generic-pc" = s."quantity-generic-pc",
            "quantity-chronic-pc" = s."quantity-chronic-pc",
            "quantity-ethical-pc" = s."quantity-ethical-pc",
            "quantity-repeatable-pc" = s."quantity-repeatable-pc",
            "quantity-goodaid-pc" = s."quantity-goodaid-pc",
            "quantity-others-type-pc" = s."quantity-others-type-pc",
            "spend-generic-pc" = s."spend-generic-pc"
        from
            (
            select
                pm.id ,
                min(bm."created-at") as "first-bill-date",
                max(bm."created-at") as "last-bill-date",
                min(bm.id) as "first-bill-id",
                max(bm.id) as "last-bill-id",
                round(sum(bm."total-spend")/ count(distinct bm.id), 4) as "average-bill-value",
                sum(bm."total-quantity") as "total-quantity",
                sum(bm."quantity-generic") as "quantity-generic",
                case when sum(bm."total-quantity") in (0, null) then -1 else round(100.0 * sum(bm."quantity-generic")/ 
                sum(bm."total-quantity"), 4) end as "quantity-generic-pc",
                sum(bm."quantity-chronic") as "quantity-chronic",
                case when sum(bm."total-quantity") in (0, null) then -1 else round(100.0 * sum(bm."quantity-chronic")/ 
                sum(bm."total-quantity"), 4) end as "quantity-chronic-pc",
                sum(bm."quantity-ethical") as "quantity-ethical",
                case when sum(bm."total-quantity") in (0, null) then -1 else round(100.0 * sum(bm."quantity-ethical")/ 
                sum(bm."total-quantity"), 4) end as "quantity-ethical-pc",
                sum(bm."quantity-repeatable") as "quantity-repeatable",
                case when sum(bm."total-quantity") in (0, null) then -1 else round(100.0 * sum(bm."quantity-repeatable")
                / sum(bm."total-quantity"), 4) end as "quantity-repeatable-pc",
                sum(bm."quantity-goodaid") as "quantity-goodaid",
                case when sum(bm."total-quantity") in (0, null) then -1 else round(100.0 * sum(bm."quantity-goodaid")/ 
                sum(bm."total-quantity"), 4) end as "quantity-goodaid-pc",
                sum(bm."quantity-others-type") as "quantity-others-type",
                case when sum(bm."total-quantity") in (0, null) then -1 else round(100.0 * 
                sum(bm."quantity-others-type")/ sum(bm."total-quantity"), 4) end as "quantity-others-type-pc",
                sum(bm."quantity-generic" + bm."quantity-ethical") as "quantity-rx",
                case when sum(bm."total-quantity") in (0, null) then -1 else round(100.0 * sum(bm."quantity-generic" + 
                bm."quantity-ethical")/ sum(bm."total-quantity"), 4) end as "quantity-rx-pc",
                count(distinct bm.id) as "number-of-bills",
                count(distinct (case when bm."hd-flag" is true then bm.id else null end)) as "hd-bills",
                case when count(distinct bm.id) in (0, null) then -1 else round(100.0 * count(distinct (case when 
                bm."hd-flag" is true then bm.id else null end))/ count(distinct bm.id), 4) end  as "hd-bills-pc",
                bool_or(bm."is-repeatable") as "is-repeatable",
                bool_or(bm."is-generic") as "is-generic",
                bool_or(bm."is-chronic") as "is-chronic",
                bool_or(bm."is-goodaid") as "is-goodaid",
                bool_or(bm."is-ethical") as "is-ethical",
                bool_or(bm."is-rx") as "is-rx",
                bool_or(bm."is-others-type") as "is-others-type",
                bool_or(bm."hd-flag") as "hd-flag",
                bool_or(bm."ecom-flag") as "ecom-flag",
                bool_or(bm."pr-flag") as "pr-flag",
                bool_or(bm."digital-payment-flag") as "digital-payment-flag",
                sum(bm."total-spend") as "total-spend",
                sum(bm."spend-generic") as "spend-generic",
                case when sum(bm."total-spend") in (0, null) then -1 else round(100.0 * sum(bm."spend-generic")/ 
                sum(bm."total-spend")) end as "spend-generic-pc",
                min(case when bm."promo-code-id" is not null then bm."created-at" else null end) as 
                "promo-min-bill-date",
                min(case when bm."hd-flag" is true then bm."created-at" else null end) as "hd-min-bill-date",
                min(case when bm."ecom-flag" is true then bm."created-at" else null end) as "ecom-min-bill-date",
                min(case when bm."pr-flag" is true then bm."created-at" else null end) as "pr-min-bill-date",
                min(case when bm."is-generic" is true then bm."created-at" else null end) as "generic-min-bill-date",
                min(case when bm."is-goodaid" is true then bm."created-at" else null end) as "goodaid-min-bill-date",
                min(case when bm."is-ethical" is true then bm."created-at" else null end) as "ethical-min-bill-date",
                min(case when bm."is-chronic" is true then bm."created-at" else null end) as "chronic-min-bill-date",
                min(case when bm."is-repeatable" is true then bm."created-at" else null end) as 
                "repeatable-min-bill-date",
                min(case when bm."is-others-type" is true then bm."created-at" else null end) as 
                "others-type-min-bill-date",
                min(case when bm."digital-payment-flag" is true then bm."created-at" else null end) as 
                "digital-payment-min-bill-date",
                min(case when bm."is-rx" is true then bm."created-at" else null end) as "rx-min-bill-date",
                sum(bm."total-mrp-value") as "total-mrp-value",
                case
                    when max(bm."created-at") = '0101-01-01' then null
                    else datediff(day,
                    max(bm."created-at"),
                    current_date)
                end as "recency-customer-days",
                case
                    when min(bm."created-at") = '0101-01-01' then null
                    else datediff(day,
                    min(bm."created-at"),
                    current_date)
                end as "system-age-days"
            from
                "prod2-generico"."{patients_metadata_table}" pm
            inner join "prod2-generico"."{bill_metadata_table}" bm on
                pm.id = bm."patient-id"
            where
                pm."etl-status" = '{status['updating']}'
            group by
                pm.id
        ) s
        where
            t.id = s.id;
    """
    db.execute(query, params=None)


def get_customer_feedback(db):
    # get customer feedback data (nps)
    query = f"""
        select
            p.id,
            f.rating,
            f.suggestion,
            f."store-id",
            s."name" as "store-name",
            f."created-at"
        from
            "prod2-generico"."{patients_metadata_table}" pm
        inner join "prod2-generico".patients p on
             p.id = pm.id
        inner join "prod2-generico".feedback f on
            f.phone = p.phone
        inner join "prod2-generico".stores s on
            f."store-id" = s."id"
        where pm."etl-status" = '{status['updating']}'
    """
    db.execute(query, params=None)
    nps: pd.DataFrame = db.cursor.fetch_dataframe()

    if not isinstance(nps, type(None)) and len(nps):
        nps.head(2)
        nps['created-at'] = pd.to_datetime(nps['created-at'])
        nps['nps-rating-date'] = nps['created-at'].dt.strftime("%Y-%m-%d")
        nps['is-nps'] = True
        nps = nps.sort_values(by=['id', 'created-at'], ascending=[True, False])

        # Keep only latest entry
        nps['rank'] = nps.groupby(['id']).cumcount() + 1
        nps = nps[nps['rank'] == 1]
        nps.drop('rank', axis='columns', inplace=True)
        nps = nps.rename(
            columns={
                'rating': 'latest-nps-rating',
                'suggestion': 'latest-nps-rating-comment',
                'nps-rating-date': 'latest-nps-rating-date',
                'store-id': 'latest-nps-rating-store-id',
                'store-name': 'latest-nps-rating-store-name'
            }
        )
    else:
        nps = pd.DataFrame(
            columns=['id', 'created-at', 'nps-rating-date', 'is-nps', 'latest-nps-rating', 'latest-nps-rating-comment',
                     'latest-nps-rating-date', 'latest-nps-rating-store-id', 'latest-nps-rating-store-name'])

    return nps


def get_referral_count(db):
    # Referral count
    query = f"""
        select
            a."patient-id" as id,
            SUM(b."total-used") as "referred-count"
        from
            "prod2-generico"."{patients_metadata_table}" pm
        left join 
            "prod2-generico"."patients-promo-codes" a on
            pm.id = a."patient-id"
        left join "prod2-generico"."promo-codes" b on
            a."promo-code-id" = b."id"
        where
            b."code-type" = 'referral'
            and pm."etl-status" = '{status['updating']}'
        group by
            a."patient-id"
    """
    db.execute(query=query)
    _referral: pd.DataFrame = db.cursor.fetch_dataframe()
    return _referral


def get_patient_bills(db):
    # ## Primary Store, System Age Days and Recency Customer Days
    query = f"""
        select
            pm.id,
            bm."store-id",
            bm.id as "bill-id",
            bm."bill-year",
            bm."bill-month",
            bm."bill-date",
            bm."created-at",
            bm."total-spend"
        from
            "prod2-generico"."{patients_metadata_table}" pm
        inner join 
            "prod2-generico"."{bill_metadata_table}" bm on
            pm.id = bm."patient-id"
        where
            pm."etl-status" = '{status['updating']}'
    """
    db.execute(query=query)
    _patient_bills: pd.DataFrame = db.cursor.fetch_dataframe()
    return _patient_bills


def get_patient_drugs(db):
    # ## Number of drug and primary disease
    query = f"""
        select
            b."patient-id" ,
            b.id as "bill-id",
            bi."inventory-id",
            i."drug-id"
        from
            "prod2-generico"."{patients_metadata_table}" pm
        inner join "prod2-generico"."bills-1" b on
            pm.id = b."patient-id"
        inner join "prod2-generico"."bill-items-1" bi on
            b.id = bi."bill-id"
        inner join "prod2-generico"."inventory-1" i on
            bi."inventory-id" = i.id
        inner join "prod2-generico".drugs d on
            i."drug-id" = d.id
        where
            pm."etl-status" = '{status['updating']}';
    """
    db.execute(query=query)
    _patient_drugs: pd.DataFrame = db.cursor.fetch_dataframe()

    return _patient_drugs


def get_drug_subgroup(db):
    # primary disease calculation
    query = """
        select
            b."drug-id",
            a.subgroup
        from
            "prod2-generico".molecules a
        inner join "prod2-generico".composition b on
            a.name = b.molecule
        group by
            b."drug-id",
            a.subgroup;
    """
    db.execute(query=query)
    _drug_subgroup: pd.DataFrame = db.cursor.fetch_dataframe()
    return _drug_subgroup


def get_patient_value_segment(db):
    # ## Value segment calculation
    query = f"""
        select
            pm.id,
            COUNT(distinct bm."id") as "total-bills",
            SUM(bm."total-spend") as "total-spend",
            current_date as "value-segment-calculation-date"
        from
            "prod2-generico"."{patients_metadata_table}" pm
        inner join "prod2-generico"."{bill_metadata_table}" bm on
            pm.id = bm."patient-id"
        where
            pm."etl-status" = '{status['updating']}'
    --        and datediff(day, current_date, bm."created-at") between -2 and -1
        group by
            pm.id;
    """
    db.execute(query=query)
    patient_agg_bill: pd.DataFrame = db.cursor.fetch_dataframe()
    patient_agg_bill['abv'] = np.round(
        patient_agg_bill['total-spend'].astype('float') / patient_agg_bill['total-bills'].astype('float'), 2)
    patient_value_segment = patient_agg_bill.sort_values(['total-spend'], ascending=False)
    patient_value_segment['rank'] = patient_value_segment['total-spend'].rank(method='dense', ascending=False)
    patient_value_segment['cumm-sales'] = patient_value_segment.sort_values(['total-spend'], ascending=False)[
        'total-spend'].cumsum()
    len_data = len(patient_value_segment)

    def assign_value_segment(row):
        if row['rank'] <= 0.05 * len_data:
            return 'platinum'
        elif (row['rank'] > 0.05 * len_data) & (row['rank'] <= 0.1 * len_data):
            return 'gold'
        elif (row['rank'] > 0.1 * len_data) & (row['rank'] <= 0.2 * len_data):
            return 'silver'
        else:
            return 'others'

    patient_value_segment['value-segment'] = patient_value_segment.apply(lambda row: assign_value_segment(row), axis=1)
    return patient_value_segment


def get_referral_code(db):
    # Get referral code for patient
    query = f"""
                SELECT
                    "patient-id" as "id",
                    "promo-code" as "referral-code"
                FROM
                (
                    SELECT
                        ppc."patient-id",
                        row_number() over (partition by ppc."patient-id" order by ppc."id" ASC) as rank_entry,
                        pc."promo-code"
                    FROM
                        "prod2-generico"."patients-promo-codes" ppc
                    INNER JOIN 
                        "prod2-generico"."promo-codes" pc 
                    ON
                        ppc."promo-code-id" = pc."id"
                    WHERE
                        pc."code-type" = 'referral') sub
                left join
                    "prod2-generico"."{patients_metadata_table}" pm 
                    on 
                    pm.id = sub."patient-id"
                where
                    sub.rank_entry = 1
                    and
                    pm."etl-status" = '{status['updating']}'"""
    db.execute(query=query)
    referral_code: pd.DataFrame = db.cursor.fetch_dataframe()
    return referral_code


def get_value_segment_anytime(db):
    q1 = f"""
            select
                value."patient-id" as "patient-id",
                value."value-segment" as "value-segment"
            from
                "prod2-generico"."customer-value-segment" value
                left join 
                "prod2-generico"."{patients_metadata_table}" pm 
                on
                pm.id = value."patient-id"
            where 
                pm."etl-status" = '{status['updating']}'
            group by
                value."patient-id",
                value."value-segment"
        """
    data_vs = db.get_df(q1)
    data_vs.columns = [c.replace('-', '_') for c in data_vs.columns]
    data_vs['value_segment_rank'] = data_vs['value_segment'].map({'platinum': 3, 'gold': 2,  'silver': 1, 'others': 0})
    data_vs = data_vs.sort_values(by=['patient_id', 'value_segment_rank'], ascending=[True, False])
    data_vs['rank'] = data_vs.groupby(['patient_id']).cumcount() + 1
    data_vs_r1 = data_vs[data_vs['rank'] == 1]
    data_vs_f = data_vs_r1[['patient_id', 'value_segment']]
    data_vs_f.columns = ['id', 'value-segment-anytime']
    return data_vs_f


def get_behaviour_segment_anytime(db):
    q1 = f"""
            select
                behaviour."patient-id" as "patient-id",
                behaviour."behaviour-segment" as "behaviour-segment" 
            from
                "prod2-generico"."customer-behaviour-segment" behaviour
                left join 
                "prod2-generico"."{patients_metadata_table}" pm 
                on
                pm.id = behaviour."patient-id"
            where 
                pm."etl-status" = '{status['updating']}'
            group by
                behaviour."patient-id",
                behaviour."behaviour-segment"
        """

    data_bs = db.get_df(q1)
    data_bs.columns = [c.replace('-', '_') for c in data_bs.columns]

    data_bs['behaviour_segment_rank'] = data_bs['behaviour_segment'].map({'super': 7,
                                                                          'regular': 6,
                                                                          'generic_heavy': 5,
                                                                          'ethical_heavy': 4,
                                                                          'other_type': 3,
                                                                          'singletripper': 2,
                                                                          'newcomer_repeat': 1,
                                                                          'newcomer_singletripper': 0
                                                                          })
    data_bs = data_bs.sort_values(by=['patient_id', 'behaviour_segment_rank'], ascending=[True, False])

    data_bs['rank'] = data_bs.groupby(['patient_id']).cumcount() + 1

    data_bs_r1 = data_bs[data_bs['rank'] == 1]

    data_bs_f = data_bs_r1[['patient_id', 'behaviour_segment']]
    data_bs_f.columns = ['id', 'behaviour-segment-anytime']
    return data_bs_f


def get_patient_behaviour_segment(changed_patients, pg_db):
    patients_ids = [str(i) for i in list(changed_patients['id'].values)]
    csv_patients_ids = ",".join(patients_ids)
    query = f"""
        SELECT
            patient_id as id,
            segment_calculation_date as "behaviour-segment-calculation-date" ,
            segment_name as "behaviour-segment"
        FROM
            customer_behaviour_segment
        WHERE
            patient_id in ({csv_patients_ids})
    """
    patient_behaviour_segment = pd.read_sql_query(query, pg_db.connection)

    patient_behaviour_segment["behaviour-segment-calculation-date"] = pd.to_datetime(
        patient_behaviour_segment["behaviour-segment-calculation-date"])
    return patient_behaviour_segment


def update_data_in_patients_metadata_table(db, s3, patient_data):
    # ## Create temp table and update (nps and other) from that
    patient_temp_table = patients_metadata_table.replace("-", "_") + "_temp"
    db.execute(query=f"DROP table IF EXISTS {patient_temp_table};")
    query = f"""
        CREATE TEMP TABLE {patient_temp_table}
        (
            id INTEGER ENCODE az64
            ,"is-nps" bool
            ,"latest-nps-rating" INTEGER  ENCODE az64
            ,"latest-nps-rating-comment" VARCHAR(1500)   ENCODE lzo
            ,"latest-nps-rating-store-id" INTEGER ENCODE az64
            ,"latest-nps-rating-store-name" VARCHAR(765)   ENCODE lzo
            ,"latest-nps-rating-date" date  ENCODE az64
            ,"referred-count" int  ENCODE az64
            ,"primary-store-id" INTEGER ENCODE az64
            ,"num-drugs" INTEGER ENCODE az64
            ,"primary-disease" VARCHAR(100)   ENCODE lzo
            ,"avg-purchase-interval" numeric
            ,"std-purchase-interval" numeric
            -- ,"value-segment-calculation-date" date
            -- ,"value-segment" VARCHAR(50)
            ,"previous-bill-date" DATE   ENCODE az64
            ,"previous-store-id" INTEGER   ENCODE az64
            -- ,"min-bill-date-in-month" DATE   ENCODE az64
            -- ,"store-id-month" INTEGER   ENCODE az64
            ,"referral-code" VARCHAR(765) ENCODE lzo
            ,"value-segment-anytime" varchar(255) ENCODE lzo
            ,"behaviour-segment-anytime" varchar(255) ENCODE lzo
            ,PRIMARY KEY (id)
        );
    """
    db.execute(query=query)
    patient_temp_table_info = helper.get_table_info(db=db, table_name=patient_temp_table, schema=None)

    # ### Fixing the data types
    patient_data['latest-nps-rating'] = patient_data['latest-nps-rating'].fillna(-1).astype('int64')
    patient_data['latest-nps-rating-store-id'] = patient_data['latest-nps-rating-store-id'].fillna(-1).astype('int64')
    patient_data['referred-count'] = patient_data['referred-count'].fillna(-1).astype('int64')
    patient_data['num-drugs'] = patient_data['num-drugs'].fillna(-1).astype('int64')
    patient_data['previous-store-id'] = patient_data['previous-store-id'].fillna(-1).astype('int64')

    s3.write_df_to_db(
        df=patient_data[list(dict.fromkeys(patient_temp_table_info['column_name']))],
        db=db, table_name=patient_temp_table, schema=None
    )

    # ## Updating the data in patient-metadata-2 table
    query = f"""
        update
            "prod2-generico"."{patients_metadata_table}" t
        set
            "is-nps" = s."is-nps",
            "latest-nps-rating" = s."latest-nps-rating",
            "latest-nps-rating-comment" = s."latest-nps-rating-comment",
            "latest-nps-rating-store-id" = s."latest-nps-rating-store-id",
            "latest-nps-rating-store-name" = s."latest-nps-rating-store-name",
            "latest-nps-rating-date" = s."latest-nps-rating-date",
            "referred-count" = s."referred-count",
            "primary-store-id" = s."primary-store-id",
            "num-drugs" = s."num-drugs",
            "primary-disease" = s."primary-disease",
            "avg-purchase-interval" = s."avg-purchase-interval",
            "std-purchase-interval" = s."std-purchase-interval",
            -- "value-segment-calculation-date" = s."value-segment-calculation-date",
            -- "value-segment" = s."value-segment",
            "previous-bill-date" = s."previous-bill-date",
            "previous-store-id" = s."previous-store-id",
            -- "min-bill-date-in-month" = s."min-bill-date-in-month",
            -- "store-id-month" = s."store-id-month",
            "referral-code" = s."referral-code",
            "value-segment-anytime" = s."value-segment-anytime",
            "behaviour-segment-anytime" = s."behaviour-segment-anytime",
            "etl-status" = 'updated'
        from
             {patient_temp_table} s
        where
            t.id = s.id;
    """
    db.execute(query=query)


def process_batch(changed_patients, db, s3, pg_db):
    update_bill_agg_fields(db=db)
    nps = get_customer_feedback(db=db)
    referral = get_referral_count(db=db)
    patient_bills = get_patient_bills(db=db)
    referral_code = get_referral_code(db=db)
    value_segment_anytime = get_value_segment_anytime(db=db)
    behaviour_segment_anytime = get_behaviour_segment_anytime(db=db)

    # purchase interval calculation
    patient_bills_2 = patient_bills.sort_values(by=["id", "created-at"])
    # Fetch previous bill date, against every bill
    patient_bills_2['previous-bill-date'] = patient_bills_2.groupby("id")['bill-date'].shift(1)
    patient_bills_2['previous-bill-date'] = pd.to_datetime(patient_bills_2['previous-bill-date'], errors='coerce')
    patient_bills_2['bill-date'] = pd.to_datetime(patient_bills_2['bill-date'], errors='coerce')
    patient_bills_2['purchase-interval'] = (
            patient_bills_2['bill-date'] - patient_bills_2['previous-bill-date']).dt.days
    patient_bills_avg_std = patient_bills_2.groupby(['id']).agg({'purchase-interval': ['mean', 'std']})
    patient_bills_avg_std = patient_bills_avg_std.reset_index(col_level=1)
    patient_bills_avg_std.columns = patient_bills_avg_std.columns.droplevel(0)
    patient_bills_avg_std.columns = ['id', 'avg-purchase-interval', 'std-purchase-interval']

    # ### Primary Store
    # Patient store wise, NOB and Total spend
    patient_store_agg = patient_bills.groupby(
        ['id', 'store-id']).agg({'bill-id': 'nunique', 'total-spend': 'sum'}).reset_index()
    patient_store_agg = patient_store_agg.rename(columns={'bill-id': 'store-bills', 'total-spend': 'store-spend'})
    patient_store_agg['rank'] = patient_store_agg.sort_values(
        ['store-bills', 'store-spend'], ascending=[False, False]).groupby(['id']).cumcount() + 1
    # Shortlist 1 store per patient
    patient_primary_store = patient_store_agg[patient_store_agg['rank'] == 1]
    patient_primary_store = patient_primary_store.rename(columns={'store-id': 'primary-store-id'})

    # ### Previous Bill Date and Store id
    previous_store_bill = patient_bills_2.sort_values(
        by=["id", "created-at"], ascending=[True, False]).drop_duplicates(subset='id')
    previous_store_bill = previous_store_bill.rename(columns={'store-id': 'previous-store-id'})

    # # Store month calculation
    # patient_bills_3 = patient_bills.sort_values(by=['id', 'bill-year', 'bill-month', 'bill-date'])
    # patient_bills_3['month_bill_rank'] = patient_bills_3.groupby(['id', 'bill-year', 'bill-month']).cumcount() + 1
    #
    # patient_bills_month_min = patient_bills_3[patient_bills_3['month_bill_rank'] == 1].copy()
    #
    # patient_bills_month_min = patient_bills_month_min.rename(
    #     columns={'bill-date': 'min-bill-date-in-month', 'store-id': 'store-id-month'})

    # Number of drug calculation
    patient_drugs = get_patient_drugs(db=db)

    patient_drug_agg = patient_drugs.groupby(['patient-id']).agg({'drug-id': "nunique"}).reset_index().rename(
        columns={'drug-id': 'num-drugs', 'patient-id': 'id'})

    drug_subgroup = get_drug_subgroup(db=db)

    # Merge subgroups, take only relevant columns
    patient_drugs_count = patient_drugs.groupby(
        ['patient-id', 'drug-id'])['inventory-id'].count().reset_index().rename(columns={'inventory-id': 'count'})
    patient_drugs_subgroup_count = patient_drugs_count.merge(drug_subgroup, how='left', on=['drug-id'])
    # Sub subgroup instances in each patient
    patient_subgroup = patient_drugs_subgroup_count.groupby(
        ['patient-id', 'subgroup'])['count'].sum().reset_index().rename(columns={'count': 'drug-count'})
    # Rank on use
    patient_subgroup = patient_subgroup.sort_values(by=['patient-id', 'drug-count'], ascending=[True, False])
    patient_subgroup['rank'] = patient_subgroup.groupby(['patient-id']).cumcount() + 1
    # keep top2 subgroups
    patient_subgroup_top_2 = patient_subgroup[patient_subgroup['rank'] <= 2]
    # Make 2 columns, first for rank1, other for rank2
    patient_subgroup_top_2_pivot = patient_subgroup_top_2.pivot(index='patient-id', columns='rank',
                                                                values='subgroup').reset_index()
    patient_subgroup_top_2_pivot = patient_subgroup_top_2_pivot.reset_index(drop=True)

    patient_subgroup_top_2_pivot.columns = ['patient-id', 'disease-rank1', 'disease-rank2']

    # Assignment of primary disease
    # If rank1 is not others, then rank1 as it is
    # If rank1 is others, and rank2 is null, then rank1 as it is
    # If rank1 is others, and rank2 is something, then rank2
    patient_subgroup_top_2_pivot['primary-disease'] = np.where(
        (
                (patient_subgroup_top_2_pivot['disease-rank1'] == 'others') &
                (patient_subgroup_top_2_pivot['disease-rank2'].isnull() is False)
        ),
        patient_subgroup_top_2_pivot['disease-rank2'],
        patient_subgroup_top_2_pivot['disease-rank1']
    )
    patient_subgroup_top_2_pivot.head(2)
    patient_primary_disease = patient_subgroup_top_2_pivot[['patient-id', 'primary-disease']].rename(
        columns={'patient-id': 'id'})

    # patient_value_segment = get_patient_value_segment(db=db)

    # patient_behaviour_segment = get_patient_behaviour_segment(changed_patients=changed_patients, pg_db=pg_db)

    # Merging all data points
    patient_data = changed_patients[['id']]

    # ### Feedback (nps)
    patient_data = patient_data.merge(nps, how='left', on=['id'])

    # ### Referral
    patient_data = patient_data.merge(referral, how='left', on=['id'])

    # ### Referral Primary Store
    patient_data = patient_data.merge(patient_primary_store[['id', 'primary-store-id']], how='left', on='id')

    # ### Primary Disease
    patient_data = patient_data.merge(patient_primary_disease, how='left', on='id')

    # ### Drug count
    patient_data = patient_data.merge(patient_drug_agg, how='left', on='id')

    # ### Average and Standard Purchase Interval
    patient_data = patient_data.merge(patient_bills_avg_std, how='left', on='id')

    # ### Value Segment
    # patient_data = patient_data.merge(patient_value_segment[['id',
    # 'value-segment-calculation-date', 'value-segment']],
    #                                   how='left', on='id')

    # # ### Behaviour Segment patient_behaviour_segment
    # patient_data = patient_data.merge(patient_behaviour_segment[['id',
    # 'value-segment-calculation-date', 'value-segment']],
    #                                   how='left', on='id')

    # ### Previous store id
    patient_data = patient_data.merge(previous_store_bill[['id', 'previous-bill-date', 'previous-store-id']],
                                      how='left', on='id')

    patient_data = patient_data.merge(referral_code, how='left', on='id')

    patient_data = patient_data.merge(value_segment_anytime, how='left', on='id')

    patient_data = patient_data.merge(behaviour_segment_anytime, how='left', on='id')

    patient_data['is-nps'] = patient_data['is-nps'].fillna(False)
    # # ### Month store id and month min bill date
    # patient_data = patient_data.merge(patient_bills_month_min[['id', 'min-bill-date-in-month', 'store-id-month']],
    #                                   how='left', on='id')

    update_data_in_patients_metadata_table(db, s3, patient_data)
    # Extracting max date from customer behaviour segment

    cust_seg = '''
                 select
        	    max("segment-calculation-date") as max_date
            from
        	    "prod2-generico"."customer-behaviour-segment"
                             '''

    rs_db.execute(query=cust_seg, params=None)
    f_data: pd.DataFrame = rs_db.cursor.fetch_dataframe()

    # Extracting max date from patients metadata for behaviour_seg

    patient_beh = '''
                select
        	    max("behaviour-segment-calculation-date") as max_date
            from
        	    "prod2-generico"."patients-metadata-2"
                             '''
    rs_db.execute(query=patient_beh, params=None)
    b_data: pd.DataFrame = rs_db.cursor.fetch_dataframe()

    # Extracting max date from patients metadata for value_seg

    patient_val = '''
                select
        	    max("value-segment-calculation-date") as max_date
            from
        	    "prod2-generico"."patients-metadata-2"
                             '''
    rs_db.execute(query=patient_val, params=None)
    c_data: pd.DataFrame = rs_db.cursor.fetch_dataframe()

    # Extracting max date from customer value segment

    cust_val = '''

              select
                max("segment-calculation-date") as max_date
              from
                "prod2-generico"."customer-value-segment"
                             '''
    rs_db.execute(query=cust_val, params=None)
    d_data: pd.DataFrame = rs_db.cursor.fetch_dataframe()

    beh_max_date = f_data['max_date'][0]  # max date from customer value segment
    patient_beh_max_date = b_data['max_date'][0]  # max behaviour segment date in patients metadata
    value_max_date = c_data['max_date'][0]  # max value segment date in patients metadata
    patient_val_max_dt = d_data['max_date'][0]  # max value segment date in patients metadata
    cur_nmz_date = (datetime.datetime.today()).replace(day=1).strftime('%Y-%m-%d')  # current date

    if str(beh_max_date) == str(cur_nmz_date):
        if str(cur_nmz_date) != str(patient_beh_max_date):
            logger.info('Condition passed for update')
            rs_db.execute('Begin;')
            update_q1 = '''
                update "prod2-generico"."patients-metadata-2"
                set "behaviour-segment"=cbs."behaviour-segment",
                "behaviour-segment-calculation-date"=cbs."segment-calculation-date"
                from "prod2-generico"."patients-metadata-2" pm2
                inner join "prod2-generico"."customer-behaviour-segment" cbs
                on pm2."id"=cbs."patient-id"
                where cbs."segment-calculation-date" = DATE_TRUNC('month',CURRENT_DATE);
                '''
            update_q2 = '''
                update "prod2-generico"."patients-metadata-2"
                set "behaviour-segment"= null,
                "behaviour-segment-calculation-date"= null 
                from "prod2-generico"."patients-metadata-2" pm2
                where pm2."behaviour-segment-calculation-date" != DATE_TRUNC('month',CURRENT_DATE);
                '''
            rs_db.execute(query=update_q1, params=None)
            rs_db.execute(query=update_q2, params=None)
            rs_db.execute('commit;')

            logger.info('Update Successful')

    if str(value_max_date) == str(cur_nmz_date):
        if str(cur_nmz_date) != str(patient_val_max_dt):
            logger.info('Condition passed for update')
            rs_db.execute('Begin;')
            update_q1 = '''
                update "prod2-generico"."patients-metadata-2"
                set "value-segment"=cbs."value-segment",
                "value-segment-calculation-date"=cbs."segment-calculation-date"
                from "prod2-generico"."patients-metadata-2" pm2
                inner join "prod2-generico"."customer-value-segment"  cbs
                on pm2."id"=cbs."patient-id"
                where cbs."segment-calculation-date" = DATE_TRUNC('month',CURRENT_DATE);
                '''
            update_q2 = '''
                update "prod2-generico"."patients-metadata-2"
                set "value-segment"=null,
                "value-segment-calculation-date"=null
                from "prod2-generico"."patients-metadata-2" pm2
                where pm2."value-segment-calculation-date" != DATE_TRUNC('month',CURRENT_DATE);
                '''
            rs_db.execute(query=update_q1, params=None)
            rs_db.execute(query=update_q2, params=None)
            rs_db.execute('commit;')
            logger.info('Update Succesful')


def main(db, s3, pg_db):
    insert_new_patients(db)
    mark_old_patients_pending(db)

    is_still_pending = True
    count = 1
    while is_still_pending:
        mark_pending_patients_updating(db=db)
        logger.info(f"batch: {count}, mark_pending_patients_updating done.")
        changed_patients = get_to_be_updated_patients(db=db)
        if isinstance(changed_patients, type(None)) or changed_patients.empty:
            is_still_pending = False
            logger.info("Completed all batches.")
        else:
            process_batch(changed_patients=changed_patients, db=db, s3=s3, pg_db=pg_db)
            logger.info(f"batch: {count}, process_batch done.")
            count += 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="This is ETL script.")
    parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                        help="This is env(dev, stag, prod)")
    parser.add_argument('-b', '--batch_size', default=500000, type=int, required=False, help="batch size")
    parser.add_argument('-l', '--limit', default=None, type=int, required=False, help="Total patients to process")
    args, unknown = parser.parse_known_args()
    env = args.env
    os.environ['env'] = env
    logger = get_logger()
    batch_size = args.batch_size
    limit = args.limit
    logger.info(f"env: {env}, limit: {limit}, batch_size: {batch_size}")

    rs_db = DB()
    rs_db.open_connection()

    pg_db = None
    _s3 = S3()

    """ calling the main function """
    main(db=rs_db, s3=_s3, pg_db=pg_db)

    # Closing the DB Connection
    rs_db.close_connection()
