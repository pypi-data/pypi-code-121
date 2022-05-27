"""main wrapper for distributor ranking algorithm"""

import os
import sys
import argparse

import pandas as pd
import numpy as np
import datetime as dt
from dateutil.tz import gettz
from fractions import Fraction

sys.path.append('../../../..')

from zeno_etl_libs.utils.distributor_ranking.distributor_ranking_calc import ranking_calc_dc, ranking_calc_franchisee
from zeno_etl_libs.utils.distributor_ranking.ranking_intervention import ranking_override_dc, ranking_override_franchisee
from zeno_etl_libs.utils.distributor_ranking.postprocess_ranking import postprocess_ranking_dc, postprocess_ranking_franchisee

from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.db.db import DB, MySQL
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.email.email import Email


def main(debug_mode, weights_as, weights_pr, as_low_volume_cutoff,
         pr_low_volume_cutoff, low_volume_cutoff_franchisee, volume_fraction,
         time_interval, time_interval_franchisee, rank_override_dc_active,
         rank_override_franchisee_active, db_read, db_write, read_schema,
         write_schema, s3, logger):

    mysql_write = MySQL(read_only=False)
    logger.info(f"Debug Mode: {debug_mode}")
    status = 'Failed'
    reset_date = dt.date.today()

    # weights format is [lead time, margin, bounce rate, ff, lost recency, success recency]
    weights_as = [float(Fraction(i)) for i in list(weights_as.values())]
    weights_pr = [float(Fraction(i)) for i in list(weights_pr.values())]

    logger.info("Checking input weights")
    try:
        assert(sum(weights_as) == 1)
        assert(sum(weights_pr) == 1)
        logger.info("Weight inputs summing up to one")

    except:
        logger.info("Weights not summing up to one, reverting to defaults")
        weights_as = [2 / 13, 1 / 13, 4 / 13, 4 / 13, 1 / 13, 1 / 13]
        weights_pr = [6 / 15, 1 / 15, 3 / 15, 3 / 15, 1 / 15, 1 / 15]

    try:
        # calculate ranks
        logger.info("Calculating Zippin DC-level Ranking")
        features_rank_dc = ranking_calc_dc(
            time_interval=time_interval, weights_as=weights_as,
            weights_pr=weights_pr, as_low_volume_cutoff=as_low_volume_cutoff,
            pr_low_volume_cutoff=pr_low_volume_cutoff,
            volume_fraction=volume_fraction,
            db=db_read, read_schema=read_schema, logger=logger)
        logger.info("Completed Zippin DC-level Ranking")

        logger.info("Calculating Franchisee Store-level Ranking")
        features_rank_franchisee = ranking_calc_franchisee(
            time_interval=time_interval_franchisee,
            weights_as=weights_as, weights_pr=weights_pr,
            low_volume_cutoff=low_volume_cutoff_franchisee,
            volume_fraction=volume_fraction,
            db=db_read, read_schema=read_schema, logger=logger)
        logger.info("Completed Franchisee Store-level Ranking")

        logger.info('Number of dc-drug_id combinations evaluated :' +
                    str(features_rank_dc[features_rank_dc['request_type'] == 'AS/MS'].shape[0]))
        logger.info('Number of franchisee store-drug_id combinations evaluated :' +
                    str(features_rank_franchisee[features_rank_franchisee['request_type'] == 'AS/MS'].shape[0]))

        if rank_override_dc_active == 'Y':
            logger.info("Rank override DC level begins")
            features_rank_dc = ranking_override_dc(
                features_rank_dc, db_read, read_schema, logger,
                override_type_list=['AS/MS'])
            logger.info("Rank override DC level successful")

        if rank_override_franchisee_active == 'Y':
            logger.info("Rank override franchisee store level begins")
            features_rank_franchisee = ranking_override_franchisee(
                features_rank_franchisee, db_read, read_schema, logger,
                override_type_list=['AS/MS', 'PR'])
            logger.info("Rank override franchisee store level successful")

        # postprocess features for dc level ranking
        tech_input_dc_level = postprocess_ranking_dc(features_rank_dc,
                                                     volume_fraction)

        # postprocess features for franchisee store level ranking
        tech_input_franchisee_level = postprocess_ranking_franchisee(
            features_rank_franchisee, volume_fraction)

        # combine both dc-level and frachisee-level ranking
        tech_input = pd.concat([tech_input_dc_level, tech_input_franchisee_level])

        # combine volume fraction split for cases where total distributors < 3
        volume_fraction_split = tech_input['volume_fraction'].str.split(
            pat='-', expand=True).rename(
            columns={0: 'volume_fraction_1',
                     1: 'volume_fraction_2',
                     2: 'volume_fraction_3'})

        tech_input['volume_fraction_1'] = volume_fraction_split[
            'volume_fraction_1'].astype(float)
        tech_input['volume_fraction_2'] = volume_fraction_split[
            'volume_fraction_2'].astype(float)
        tech_input['volume_fraction_3'] = volume_fraction_split[
            'volume_fraction_3'].astype(float)

        tech_input['volume_fraction_2'] = np.where(
            tech_input['final_dist_3'].isna(),
            tech_input['volume_fraction_2'] +
            tech_input['volume_fraction_3'],
            tech_input['volume_fraction_2'])

        tech_input['volume_fraction_3'] = np.where(
            tech_input['final_dist_3'].isna(), 0,
            tech_input['volume_fraction_3'])

        tech_input['volume_fraction_1'] = np.where(
            tech_input['final_dist_2'].isna(),
            tech_input['volume_fraction_1'] +
            tech_input['volume_fraction_2'],
            tech_input['volume_fraction_1'])

        tech_input['volume_fraction_2'] = np.where(
            tech_input['final_dist_2'].isna(), 0,
            tech_input['volume_fraction_2'])

        tech_input['volume_fraction'] = tech_input['volume_fraction_1'].astype(
            'str') + '-' + tech_input['volume_fraction_2'].astype(
            'str') + '-' + tech_input['volume_fraction_3'].astype('str')

        tech_input = tech_input[
            ['dc_id', 'store_id', 'franchisee_id', 'drug_id',
             'drug_type', 'request_type', 'volume_fraction',
             'final_dist_1', 'final_dist_2', 'final_dist_3']]

        ############ adhoc changes by tech, table restructure ############

        tech_input = tech_input.reset_index(
            drop=True).reset_index().rename(columns={'index': 'id'})
        tech_input[['volume_fraction_1', 'volume_fraction_2',
                    'volume_fraction_3']] = tech_input[
            'volume_fraction'].str.split('-', 3, expand=True)
        tech_input.loc[tech_input['request_type'] == 'AS/MS',
                       'request_type'] = 'manual-short/auto-short'
        tech_input.loc[tech_input['request_type'] ==
                       'PR', 'request_type'] = 'patient-request'

        volume_fraction_melt = pd.melt(tech_input, id_vars=['id'],
                                   value_vars=['volume_fraction_1',
                                               'volume_fraction_2',
                                               'volume_fraction_3']).sort_values(by='id')
        distributor_melt = pd.melt(tech_input, id_vars=['id'],
                                   value_vars=['final_dist_1',
                                               'final_dist_2',
                                               'final_dist_3']).sort_values(by='id').rename(columns={'value': 'distributor_id'})
        distributor_ranking_rule_values = pd.merge(distributor_melt,
                                                   volume_fraction_melt,
                                                   left_index=True,
                                                   right_index=True,
                                                   suffixes=('', '_y'))
        distributor_ranking_rule_values = distributor_ranking_rule_values[
            ['id', 'distributor_id', 'value']].rename(
            columns={'id': 'distributor_ranking_rule_id'}).reset_index(
            drop=True)

        distributor_ranking_rule_values = distributor_ranking_rule_values.reset_index().rename(columns={'index': 'id'})

        # drop null values in distributor_id(for cases where historical distributors are < 3)
        distributor_ranking_rule_values = distributor_ranking_rule_values[
            ~distributor_ranking_rule_values['distributor_id'].isna()]
        # convert distributor_id in int format
        distributor_ranking_rule_values['distributor_id'] = \
        distributor_ranking_rule_values['distributor_id'].astype(int)

        distributor_ranking_rules = tech_input[['id', 'drug_id', 'dc_id',
                                                'store_id', 'franchisee_id',
                                                'drug_type', 'request_type']]

        # adding required fields
        distributor_ranking_rules['rule_start_date'] = reset_date
        distributor_ranking_rules['is_active'] = 1
        distributor_ranking_rules['created_at'] = dt.datetime.now(
            tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
        distributor_ranking_rules['created_by'] = 'etl-automation'

        features_rank_dc.loc[:, 'reset_date'] = reset_date
        features_rank_dc['created_at'] = dt.datetime.now(
            tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
        features_rank_dc['created_by'] = 'etl-automation'
        features_rank_franchisee.loc[:, 'reset_date'] = reset_date
        features_rank_franchisee['created_at'] = dt.datetime.now(
            tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
        features_rank_franchisee['created_by'] = 'etl-automation'

        # formatting column names
        distributor_ranking_rule_values.columns = [c.replace('_', '-') for c in distributor_ranking_rule_values.columns]
        distributor_ranking_rules.columns = [c.replace('_', '-') for c in distributor_ranking_rules.columns]
        features_rank_dc.columns = [c.replace('_', '-') for c in features_rank_dc.columns]
        features_rank_franchisee.columns = [c.replace('_', '-') for c in features_rank_franchisee.columns]

        if debug_mode == 'N':
            logger.info("Writing table to RS-DB")
            logger.info("Writing to table: distributor-features-dc")
            s3.write_df_to_db(df=features_rank_dc,
                              table_name='distributor-features-dc',
                              db=db_write, schema=write_schema)
            logger.info("Writing to table: distributor-features-franchisee")
            s3.write_df_to_db(df=features_rank_franchisee,
                              table_name='distributor-features-franchisee',
                              db=db_write, schema=write_schema)
            logger.info("Writing table to RS-DB completed!")

            mysql_write.open_connection()
            logger.info("Updating table to MySQL")
            try:
                index_increment = int(
                    pd.read_sql(
                        'select max(id) from `distributor-ranking-rules`',
                        con=mysql_write.connection).values[0]) + 1
                redundant_increment = int(
                    pd.read_sql(
                        'select max(id) from `distributor-ranking-rule-values`',
                        con=mysql_write.connection).values[0]) + 1

            except:
                index_increment = 1
                redundant_increment = 1

            logger.info(f"Incremented distributor-ranking-rules by {index_increment}")
            logger.info(f"Incremented distributor-ranking-rule-values by {redundant_increment}")

            distributor_ranking_rules['id'] = distributor_ranking_rules['id'] + index_increment
            distributor_ranking_rule_values['distributor-ranking-rule-id'] = distributor_ranking_rule_values[
                'distributor-ranking-rule-id'] + index_increment
            distributor_ranking_rule_values['id'] = distributor_ranking_rule_values['id'] + redundant_increment

            logger.info("Setting existing rules to inactive")
            mysql_write.engine.execute("UPDATE `distributor-ranking-rules` SET `is-active` = 0")

            logger.info("Writing to table: distributor-ranking-rules")
            distributor_ranking_rules.to_sql(
                name='distributor-ranking-rules',
                con=mysql_write.connection,
                if_exists='append', index=False,
                method='multi', chunksize=10000)
            logger.info("Writing to table: distributor-ranking-rule-values")
            distributor_ranking_rule_values.to_sql(
                name='distributor-ranking-rule-values',
                con=mysql_write.connection,
                if_exists='append', index=False,
                method='multi', chunksize=10000)

            logger.info("Updating table to MySQL completed!")
            mysql_write.close()

        else:
            logger.info("Writing to RS-DB & MySQL skipped")

        status = 'Success'
        logger.info(f"Distributor Ranking code execution status: {status}")

    except Exception as error:
        logger.exception(error)
        logger.info(f"Distributor Ranking code execution status: {status}")

    return status, reset_date


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="This is ETL script.")
    parser.add_argument('-e', '--env', default="dev", type=str, required=False)
    parser.add_argument('-et', '--email_to',
                        default="vivek.revi@zeno.health", type=str,
                        required=False)

    parser.add_argument('-d', '--debug_mode', default="Y", type=str, required=True)
    parser.add_argument('-ti', '--time_interval', default=90, type=int, required=False)
    parser.add_argument('-tif', '--time_interval_franchisee', default=180, type=int, required=False)
    parser.add_argument('-was', '--weights_as',
                        default={'lead_time':'2/13', 'margin':'1/13', 'bounce_rate':'4/13','ff':'4/13', 'lost_recency':'1/13', 'success_recency':'1/13' },
                        type=str, required=False)
    parser.add_argument('-wpr', '--weights_pr',
                        default={'lead_time':'6/15', 'margin':'1/15', 'bounce_rate':'3/15','ff':'3/15','lost_recency':'1/15', 'success_recency':'1/15'},
                        type=str, required=False)
    parser.add_argument('-aslvc', '--as_low_vol_cutoff', default=0.02, type=float,
                        required=False)
    parser.add_argument('-prlvc', '--pr_low_vol_cutoff', default=0.01, type=float,
                        required=False)
    parser.add_argument('-lvcf', '--low_vol_cutoff_franchisee', default=0.0, type=float,
                        required=False)
    parser.add_argument('-vf', '--vol_frac', default="0.5-0.3-0.2", type=str,
                        required=False)
    parser.add_argument('-rodc', '--rank_override_dc', default="N", type=str,
                        required=False)
    parser.add_argument('-rof', '--rank_override_franchisee', default="N", type=str,
                        required=False)

    args, unknown = parser.parse_known_args()

    env = args.env
    os.environ['env'] = env
    email_to = args.email_to

    debug_mode = args.debug_mode
    weights_as = args.weights_as
    weights_pr = args.weights_pr
    as_low_volume_cutoff = args.as_low_vol_cutoff
    pr_low_volume_cutoff = args.pr_low_vol_cutoff
    low_volume_cutoff_franchisee = args.low_vol_cutoff_franchisee
    volume_fraction = args.vol_frac
    time_interval = args.time_interval
    time_interval_franchisee = args.time_interval_franchisee
    rank_override_dc_active = args.rank_override_dc
    rank_override_franchisee_active = args.rank_override_franchisee

    logger = get_logger()
    s3 = S3()
    rs_db_read = DB(read_only=True)
    rs_db_write = DB(read_only=False)
    read_schema = 'prod2-generico'
    write_schema = 'prod2-generico'

    # open RS connection
    rs_db_read.open_connection()
    rs_db_write.open_connection()

    """ calling the main function """
    status, reset_date = main(debug_mode, weights_as, weights_pr,
        as_low_volume_cutoff, pr_low_volume_cutoff, low_volume_cutoff_franchisee,
        volume_fraction, time_interval, time_interval_franchisee,
        rank_override_dc_active, rank_override_franchisee_active, rs_db_read,
        rs_db_write, read_schema, write_schema, s3, logger)

    # close RS connection
    rs_db_read.close_connection()
    rs_db_write.close_connection()

    # SEND EMAIL ATTACHMENTS
    logger.info("Sending email attachments..")
    email = Email()
    email.send_email_file(
        subject=f"Distributor Ranking Reset (SM-{env}) {reset_date}: {status}",
        mail_body=f"""
                    Debug Mode: {debug_mode}
                    Job Params: {args}
                    """,
        to_emails=email_to)

    logger.info("Script ended")
