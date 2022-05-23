import time
import pandas as pd
import csv
import copy
import datetime as dt
import os

class Stellar:
    
    def __init__(self, group, treatment, con, discharge_statuses = None, days_in_outcome_period = 90, stars = False):
        '''
        

        Parameters
        ----------
        group : string
            Name of the cohort to be built. This is used throughout the pipeline to name temp tables for an instance consistently.
        treatment : boolean
            True if the cohort is a treatment cohort, False if the cohort is a control.
        con : teradatasql object
            Connection to UDW, generated using the teradatasql package.
        discharge_statuses : string, optional
            String of statuses from the Truepill discharge data, in single quotes and separated by commas. The default is None.
        days_in_outcome_period : integer, optional
            Number of days the outcome period should span. The default is 90.
        stars : boolean, optional
            True if the cohort will be used in a stars follow-up analysis. False if the cohort will be used for an affordability/utilization
            analysis. The default is False.

        Returns
        -------
        None.

        '''
        
        self.group = group
        self.treatment = treatment
        self.con = con
        self.cur = con.cursor()
        self.discharge_statuses = discharge_statuses
        self.days_in_outcome_period = days_in_outcome_period
        self.stars = stars
        
    def generate_queries(self):
        '''
        

        Returns
        -------
        steps : list
            The steps list is a list of strings. Each string is a query, and they appear in the list in the order 
            they have to be run (highly sequential pipeline). To view the SQL for a query, run `print(steps[i])`.
            To execute a single query, run `cur.execute(steps[i])`.
            To run all the queries, one can simply call the method build_cohort(), which by default uses the generate_queries()
            method to generate the default pipeline and then executes it.

        '''
        steps = []

        # Treatment pipeline
        if self.treatment:
            
            steps.append(self.create_starting_cohort(f'{self.group}_cohort'))
            steps += list(self.all_utils(input_tbl_nm = f'{self.group}_cohort')) # Get all ER & IPs from 12m prior to current date - this method returns 2 queries
            steps.append(self.remove_ineligible_er_due_to_admit(ER_tbl_nm = f'{self.group}_er_all', IP_tbl_nm = f'{self.group}_ip_all', output_tbl_nm = f'{self.group}_er_eligible')) # Remove ER visits that resulted in an admit
            steps += list(self.split_utils(cohort_tbl_nm = f'{self.group}_cohort', ER_tbl_nm = f'{self.group}_er_eligible', IP_tbl_nm = f'{self.group}_ip_all'))

            #----------------These steps are all to get follow-up rates---------------------------------
            steps.append(self.unique_er_discharges(input_tbl_nm = f'{self.group}_er_eligible', # get follow-ups for ALL ED visits so can include gap closed flag on final table
                                                   output_tbl_nm = f'{self.group}_er_unique'))


            steps.append(self.mbi_to_pty_lookup(input_tbl_nm = f'{self.group}_er_unique',
                                                output_tbl_nm = f'{self.group}_er_lookup'))


            steps.append(self.claims_after_discharge(input_tbl_nm = f'{self.group}_er_lookup',
                                                     output_tbl_nm = f'{self.group}_er_clms_after'))


            steps.append(self.ed_follow_ups(discharge_tbl = f'{self.group}_er_unique',
                                            claims_after_tbl = f'{self.group}_er_clms_after',
                                            output_tbl_nm = f'{self.group}_er_follow_ups'))

            # Make the name of this table automatic to match demos and utils
            steps.append(self.follow_up_rates(cohort_tbl_nm = f'{self.group}_cohort',
                                              follow_up_tbl = f'{self.group}_er_follow_ups',
                                              output_tbl_nm = f'{self.group}_fu_rates'))

            #-----------------------End follow-up rate section--------------------------------------------

            steps.append(self.demographics(cohort_tbl_nm = f'{self.group}_cohort'))
            steps.append(self.utilizations(cohort_tbl_nm = f'{self.group}_cohort'))
            steps.append(self.charlson_comorbidities(cohort_tbl_nm = f'{self.group}_cohort'))

            
        # Control pipeline  
        else:

            steps.append(self.remove_treatment(input_tbl_nm = 'nc_control_pool_full', output_tbl_nm = f'{self.group}_pool', truepill_tbl_nm = 'stellar_discharges')) # Input table rn is loaded from outside class
            steps.append(self.mbi_to_pty_lookup(input_tbl_nm = f'{self.group}_pool', output_tbl_nm = f'{self.group}_pool_ptys', indexed_on_discharge=False))
            steps += list(self.all_utils(input_tbl_nm = f'{self.group}_pool_ptys')) # ER, IPs from 12m prior all the way through eval period after
            steps.append(self.remove_ineligible_er_due_to_admit(ER_tbl_nm = f'{self.group}_er_all', IP_tbl_nm = f'{self.group}_ip_all', output_tbl_nm = f'{self.group}_er_eligible'))
            steps.append(self.narrow_to_observation_period(input_tbl_nm = f'{self.group}_er_eligible', output_tbl_nm = f'{self.group}_cohort_mbi'))
            steps.append(self.mbi_to_pty_lookup(input_tbl_nm = f'{self.group}_cohort_mbi', output_tbl_nm = f'{self.group}_cohort'))
            steps += list(self.split_utils(cohort_tbl_nm = f'{self.group}_cohort', ER_tbl_nm = f'{self.group}_er_eligible', IP_tbl_nm = f'{self.group}_ip_all'))

            #----------------These steps are all to get follow-up rates---------------------------------
            steps.append(self.unique_er_discharges(input_tbl_nm = f'{self.group}_er_eligible', output_tbl_nm = f'{self.group}_er_unique')) # get follow-ups for ALL ED visits so can include gap closed flag on final table
            steps.append(self.mbi_to_pty_lookup(input_tbl_nm = f'{self.group}_er_unique', output_tbl_nm = f'{self.group}_er_lookup'))
            steps.append(self.claims_after_discharge(input_tbl_nm = f'{self.group}_er_lookup', output_tbl_nm = f'{self.group}_er_clms_after'))
            steps.append(self.ed_follow_ups(discharge_tbl = f'{self.group}_er_unique',
                                            claims_after_tbl = f'{self.group}_er_clms_after',
                                            output_tbl_nm = f'{self.group}_er_follow_ups'))

            # Make the name of this table automatic to match demos and utils functions
            steps.append(self.follow_up_rates(cohort_tbl_nm = f'{self.group}_cohort',
                                              follow_up_tbl = f'{self.group}_er_follow_ups',
                                              output_tbl_nm = f'{self.group}_fu_rates'))

            #-----------------------End follow-up rate section--------------------------------------------

            steps.append(self.demographics(cohort_tbl_nm = f'{self.group}_cohort'))
            steps.append(self.utilizations(cohort_tbl_nm = f'{self.group}_cohort'))
            steps.append(self.charlson_comorbidities(cohort_tbl_nm = f'{self.group}_cohort'))

            
        return steps
    
    def build_cohort(self, steps = None):
        '''
        

        Parameters
        ----------
        steps : list, optional
            List of queries to execute in sequential order. When steps = None, the generate_queries() method is called to create the default list of queries.

        Returns
        -------
        None.

        '''
        
        if steps is None:
            steps = self.generate_queries()
            
        
        start = time.time()

        for i, ele in enumerate(steps):
            print(f'Running step {i}...')
            self.cur.execute(ele)
            
        end = time.time()
        
        # self.get_params()
        print('Time to load data was: {} min.'.format(round((end - start)/60, 1)))
        
    def build_feature_tbl(self, stars_analysis, tbls = None):
        
        if tbls is None:
            
            tbls = [f'{self.group}_utils', f'{self.group}_demographics', f'{self.group}_fu_rates', 
                    f'{self.group}_er_follow_ups', f'{self.group}_charlson_comorbidities'] 
        
        print('Building feature table...')
                
        # If doing a utilization analysis, filter discharges down to the correct observation period
        sql = self.feature_tbl(cohort_tbl_nm = f'{self.group}_cohort', stars_analysis = stars_analysis, tbls = tbls)

        start = time.time()
        self.cur.execute(sql)
        end = time.time()
        
        print('Time to load data was: {} min.'.format(round((end - start)/60, 1)))
        
    def get_feature_tbl(self, stars):
        '''
        

        Returns
        -------
        tbl : pandas dataframe
            A table containing demographic and utilization features to be used in propensity-score matching for causal inference.

        '''
        
        if self.treatment:
            
            trt = 1
            
        else:
            
            trt = 0
            
        if stars:
            
            tbl_nm = f'{self.group}_feature_tbl_stars'
            
        else:
           
            tbl_nm = f'{self.group}_feature_tbl_utils'
            
        
        tbl = pd.read_sql(f'SELECT a.*, {trt} as treatment FROM {tbl_nm} a', self.con)
        
        return tbl
    
        
    def remove_treatment(self, input_tbl_nm, output_tbl_nm, truepill_tbl_nm):
        '''
        

        Parameters
        ----------
        input_tbl_nm : string
            Name of a volatile table containing MBIs for a control pool.
        output_tbl_nm : string
            Name for the volatile table resulting from this query.
        truepill_tbl_nm : string
            Name of the volatile table containing the Truepill discharge data from the treatment cohort.

        Returns
        -------
        sql : string
            Query to remove treatment MBIs from a control pool.

        '''
        
        sql = f'''CREATE VOLATILE TABLE {output_tbl_nm} AS
        
        (SELECT * 
         FROM {input_tbl_nm}
         WHERE alt_id_val NOT IN (SELECT DISTINCT member_id FROM {truepill_tbl_nm}))
        
        WITH DATA
        ON COMMIT PRESERVE ROWS
        
        
        '''
        return sql
        
    def pty_to_mbi_lookup(self, input_tbl_nm, output_tbl_nm):
        '''
        

        Parameters
        ----------
        input_tbl_nm : string
            Name of a volatile table containing mbr_pty_id's each with an index ER discharge date.
        output_tbl_nm : string
            Name for the volatile table resulting from this query.

        Returns
        -------
        sql : string
            Query to take a table with mbr_pty_id's and index ER discharges and generate an MBI look-up table for those ID's.

        '''
        
        sql = f'''CREATE VOLATILE TABLE {output_tbl_nm} AS
        
        (SELECT DISTINCT b.alt_id_val, a.mbr_pty_id, b.orig_src_sys_cd, a.er_discharge
         FROM {input_tbl_nm} a
            
             LEFT JOIN udwbasesecureview1.mbr_alt_id b
             ON a.mbr_pty_id = b.mbr_pty_id
             
            WHERE b.alt_id_typ_cd = 'HIC'
            AND b.row_expir_dt = '9999-12-31'
            AND b.src_row_sts_cd = 'A')
        
            WITH DATA
            ON COMMIT PRESERVE ROWS;
        
        '''
        
        return sql
    
    def mbi_to_pty_lookup(self, input_tbl_nm, output_tbl_nm, indexed_on_discharge = True):
        '''
        

        Parameters
        ----------
        input_tbl_nm : string
            Name of a volatile table containing MBI's, each with an index ER discharge date.
        output_tbl_nm : string
            DESCRIPTION.
        indexed_on_discharge : boolean, optional
            Does the input volatile table have a column called 'er_discharge'? The default is True.

        Returns
        -------
        sql : string
            Query to take a table with MBI's and index ER discharges and generate an mbr_pty_id look-up table for those ID's. Most UDW claims tables are indexed on mbr_pty_id's,
            multiple of which can exist for a single person depending on their coverage. Only one unique MBI exists per person across all of their mbr_pty_id's.

        '''
        
        if indexed_on_discharge:
        
            sql = f'''CREATE VOLATILE TABLE {output_tbl_nm} AS
            
            (SELECT DISTINCT a.alt_id_val, b.mbr_pty_id, b.orig_src_sys_cd, a.er_discharge
             FROM {input_tbl_nm} a
                
                 LEFT JOIN udwbasesecureview1.mbr_alt_id b
                 ON a.alt_id_val = b.alt_id_val
    
                 
                WHERE b.alt_id_typ_cd = 'HIC'
                AND b.row_expir_dt = '9999-12-31'
                AND b.src_row_sts_cd = 'A')
            
                WITH DATA
                ON COMMIT PRESERVE ROWS;
            
            '''
            
        else:
            
            sql = f'''CREATE VOLATILE TABLE {output_tbl_nm} AS
            
            (SELECT DISTINCT a.alt_id_val, b.mbr_pty_id
             FROM {input_tbl_nm} a
                
                 LEFT JOIN udwbasesecureview1.mbr_alt_id b
                 ON a.alt_id_val = b.alt_id_val
    
                 
                WHERE b.alt_id_typ_cd = 'HIC'
                AND b.row_expir_dt = '9999-12-31'
                AND b.src_row_sts_cd = 'A')
            
                WITH DATA
                ON COMMIT PRESERVE ROWS;
            
            '''
            
        
        return sql
        
    def create_starting_cohort(self, output_tbl_nm):
        '''
        

        Parameters
        ----------
        output_tbl_nm : string
            Name for the volatile table output from this query.

        Returns
        -------
        sql : string
            Query to initialize a table of ID's and index ER discharge dates for a cohort. If the instance is a treatment instance, the query will also contain the 
            member's MBI. If it's a control instance (self.treatment = False), then the query will contain only mbr_pty_id's.

        '''
        
        if self.treatment and self.discharge_statuses is not None:
            
            where_statement_treatment = f"WHERE a.status IN ({self.discharge_statuses})"

            
        elif self.treatment and self.discharge_statuses is None:
        
            where_statement_treatment = ''
         
        
        if self.treatment and self.stars:
            
            sql = f'''CREATE VOLATILE TABLE {output_tbl_nm} AS
            
            (SELECT DISTINCT b.mbr_pty_id, b.alt_id_val, a.discharge_dt AS er_discharge
             
             FROM stellar_discharges a
             
             LEFT JOIN udwbasesecureview1.mbr_alt_id b
             ON a.member_id = b.alt_id_val

             
            {where_statement_treatment} 
            AND b.alt_id_typ_cd = 'HIC'
            AND a.member_id IS NOT NULL
            AND b.alt_id_val IS NOT NULL
            AND a.member_id NOT IN ('0', 'N/A')
            AND b.row_expir_dt = '9999-12-31'
            AND b.src_row_sts_cd = 'A'
            
            )
            
            WITH DATA
            ON COMMIT PRESERVE ROWS;
            
            '''
            
            return sql
        
        
        elif self.treatment and not self.stars:
            
            sql = f'''CREATE VOLATILE TABLE {output_tbl_nm} AS
            
            (WITH index_dts AS (SELECT a.member_id, MIN(a.discharge_dt) AS discharge_dt
                                FROM stellar_discharges a
                                
                                {where_statement_treatment}
                                GROUP BY a.member_id)
             
            SELECT DISTINCT b.mbr_pty_id, b.alt_id_val, a.discharge_dt AS er_discharge
             
             FROM index_dts a
             
             LEFT JOIN udwbasesecureview1.mbr_alt_id b
             ON a.member_id = b.alt_id_val

             
            WHERE b.alt_id_typ_cd = 'HIC'
            AND a.member_id IS NOT NULL
            AND b.alt_id_val IS NOT NULL
            AND a.member_id NOT IN ('0', 'N/A')
            AND b.row_expir_dt = '9999-12-31'
            AND b.src_row_sts_cd = 'A')
            
            WITH DATA
            ON COMMIT PRESERVE ROWS;
            
            '''
            
            return sql
        

        
        else:
            
            sql = f'''CREATE VOLATILE TABLE {output_tbl_nm} AS (                 
                     
                    /* ----------
                    UDW ADJ CLMS 
                    -------------*/
                    
                    SELECT DISTINCT b.mbr_pty_id, b.srvc_strt_dt AS er_discharge
                    
                    FROM UDWBASESECUREVIEW1.ADJD_MCE_SRVC_MAIN_F b
                    
                    LEFT JOIN udwbasesecureview1.mbr_f c
                    ON b.mbr_pty_id = c.mbr_pty_id
                    AND b.orig_src_sys_cd = c.orig_src_sys_cd
                    
                    
                    WHERE b.proc_dt BETWEEN '2021-10-01' AND CURRENT_DATE()
                    AND b.srvc_strt_dt BETWEEN '2021-11-04' AND CURRENT_DATE()
                    AND (b.adjd_plsrv_cd = '23') -- OR b.proc_cd in ('99283', 'B1001','G9752','S9960')) --ER POS or ER procedure code
                    AND b.orig_src_sys_cd IN ('COS', 'NIC', 'CSP', 'APF', 'NDB', 'FRV', 'OXF') --MA/Medicaid only
                    AND b.mbr_pty_id IS NOT NULL
                    AND b.src_row_sts_cd = 'A' --not deleted in source system
                    AND b.src_row_expir_dt = '9999-12-31'
                        
                    UNION
                    
                    /* ----------------
                    UDW PRE-ADJ CLMS 
                    -------------------*/
                    
                    SELECT DISTINCT b.mbr_pty_id, c.clm_srvc_strt_dt AS er_discharge
                    FROM udwbasesecureview1.pre_adjd_med_clm b

                    --Procedures
                    LEFT OUTER JOIN udwbasesecureview1.pre_adjd_med_clm_srvc c
                    ON b.udw_med_clm_id = c.udw_med_clm_id
                    
                    
                    WHERE c.clm_srvc_strt_dt BETWEEN '2021-11-04' AND CURRENT_DATE()
                    AND (c.plsrv_cd = '23') --OR c.bil_proc_cd IN ('99283', 'B1001','G9752','S9960')) --same date for both
                    AND b.orig_src_sys_cd IN ('COS', 'NIC', 'CSP', 'APF', 'NDB', 'FRV', 'OXF') --MA/Medicaid only
                    AND b.mbr_pty_id IS NOT NULL
                    and b.udw_med_clm_id NOT IN (SELECT DISTINCT b.udw_med_clm_id
                                                 FROM UDWBASESECUREVIEW1.ADJD_MCE b
                                                             
                                                 LEFT JOIN UDWBASESECUREVIEW1.ADJD_MCE_SRVC_MAIN_F c
                                                 ON b.udw_med_clm_id = c.udw_med_clm_id
                                                             
                                                WHERE b.orig_src_sys_cd in ('COS', 'NIC', 'CSP', 'APF', 'NDB', 'FRV', 'OXF') 
                                                AND b.proc_dt BETWEEN '2021-10-01' AND CURRENT_DATE()
                                                AND c.srvc_strt_dt BETWEEN '2021-11-04' AND CURRENT_DATE())
                    )
                    WITH DATA
                    ON COMMIT PRESERVE ROWS;
            
            '''
            
            return sql
        
    def neighboring_states(self, input_tbl_nm, output_tbl_nm):
        '''
        
    
        Parameters
        ----------
        input_tbl_nm : string
            Name of a volatile table with mbr_pty_id and index ER discharge date.
        output_tbl_nm : string
            Name for the volatile table output from this query.
    
        Returns
        -------
        sql : string
            Query to pare down an input table to only those that had active coverage with one of the following states as their state of coverage: VA, TN, GA, or SC.
            (Mainly this is used to cull a control cohort from states neighboring North Carolina, the treatment state.)
            NOTE: This query as-is is not currently usable. It returns multiple rows, sometimes with different states for a single MBI. Further work needs to be done
            to determine which row should be selected (or if a row should be selected at random) for the state attribute for a member.
        '''
        
        sql = f'''
        CREATE VOLATILE TABLE {output_tbl_nm} AS (

            SELECT DISTINCT a.mbr_pty_id, a.er_discharge, b.alt_id_val
            FROM {input_tbl_nm} a

             LEFT JOIN udwbasesecureview1.mbr_alt_id b
             ON a.mbr_pty_id = b.mbr_pty_id
             AND a.er_discharge >= b.row_eff_dt
             AND a.er_discharge <= b.row_expir_dt
             
             LEFT JOIN udwbasesecureview1.mbr_f c
             ON b.mbr_pty_id = c.mbr_pty_id
             AND b.row_eff_dt = c.row_eff_dt
             AND b.row_expir_dt = c.row_expir_dt
             AND b.orig_src_sys_cd = c.orig_src_sys_cd
             
             WHERE c.st_prvc_cd IN ('VA', 'TN', 'GA', 'SC')
             AND b.alt_id_typ_cd = 'HIC'
             AND b.orig_src_sys_cd IN ('COS', 'NIC', 'CSP', 'APF', 'NDB', 'FRV', 'OXF')
             )
        WITH DATA
        ON COMMIT PRESERVE ROWS;
        
        '''
        return sql

    
    def FMC(self, input_tbl_nm, output_tbl_nm):
            
            '''
            
        
            Parameters
            ----------
            input_tbl_nm : string
                Must contain mbr_pty_ids, MBIs, and ER discharge date for the cohort of interest.
            output_tbl_nm : string
                Name for the volatile table output from this query.
        
            Returns
            -------
            sql : string
                Query to pull flags for the 8 FMC conditions for an input table of MBI's and index ER discharges.
                NOTE: This query as-is does not match the STARS definition. Ultimately, we were unable to reproduce the SDM team's logic and didn't have time to explore
                the starsview tables. Instead, we used a data extract sent by Yuhong Tian to determine someone's FMC conditions.
        
            '''
            
            sql = f'''        CREATE VOLATILE TABLE {output_tbl_nm} AS (

                                        
                                                SELECT DISTINCT a.alt_id_val, a.er_discharge,
                                  				--AMI
                                				MAX(case when c.diag_cd IN ('i219', 'i2109', 'i228', 'i221', 'i222', 'i2129', 'i214', 'i213', 'i21a1', 'i2121', 'i2119', 'i220', 'i21a9', 'i2101', 'i2102', 'i229', 'i2111')
                                				then 1 else 0 end) as ami,
                                						
                                				--CKD
                                				MAX(case when c.diag_cd IN ('i130', 'm3215', 'n000', 'n018', 'n050', 'e1021', 'i132', 'n002', 'n022', 'n058', 'e0922', 'e1065', 'i1311', 'm10331', 'i722', 'm10339', 'n079', 'n141', 'n259', 'd4100', 'e0865', 'n052', 'q615', 'd3001', 'n020', 'e1329', 'm10349')
                                                then 1 else 0 end) as ckd,
                                				
                                  				--COPD/asthma
                                  				MAX(case when c.diag_cd IN ('j441', 'j418', 'j479', 'j42', 'j470', 'j439', 'j430', 'j432', 'j411', 'j40', 'j438', 'j440', 'j410', 'j449', 'j431', 'j471', 
                                                'j4552', 'j4531', 'j45901', 'j45902', 'j45991', 'j4521', 'j45909', 'j4541', 'j4550', 'j45998', 'j4522', 'j45990', 'j4532', 'j4542', 'j4520', 'j4530', 'j4540', 'j4551')
                                                then 1 else 0 end) as copd,
                                                
                                                --Afib
                                                MAX(case when c.diag_cd IN ('i482', 'i4820', 'i4811', 'i4891', 'i480', 'i481', 'i4821', 'i4819')
                                                then 1 else 0 end) as afib,
                                                
                                                --Depression
                                                MAX(case when c.diag_cd IN ('f3131', 'f329', 'f3340', 'f3160', 'f338', 'f3162', 'f321', 'f330',
                                                  'f3163', 'f331', 'f3175', 'f315', 'f4323', 'f320', 'f4321', 'f3181', 'f325', 'f3130', 'f3342', 'f3176', 'f324', 'f3177', 'f3178', 'f322', 'f3161', 'f333', 'f332')
                                                  then 1 else 0 end) as depr,
                                                 
                                                  --Stroke/TIA
                                                 MAX(case when c.diag_cd IN ('s0240db', 's02650b', 's02671b', 's02849g', 's062x8a', 's062x9b', 
                                                's064x3a', 's06819a', 's0242xa', 's02601a', 's02842g', 's02849d', 's06356a', 's064x0a', 's064x6a', 's069x8a', 's0240eb', 's02672a', 's060x2a', 's06314a', 's06323a')
                                                then 1 else 0 end) as stroke,
                                                
                                                --Heart failure
                                                MAX(case when c.diag_cd IN ('i501', 'i5084', 'i5089', 'i5032', 'i50811', 'i0981', 'i132', 
                                                'i50812', 'i5043', 'i5082', 'i5020', 'i5041', 'i5033', 'i5083', 'i5031', 'i5021', 'i50810', 'i50813', 'i110', 'i130', 'i5023', 'i5040', 'i5042', 'i50814', 'i509', 'i503')
                                                then 1 else 0 end) as heart,
                                                
                                                --Alzheimer's
                                                MAX(case when c.diag_cd IN ('f0150', 'f061', 'f04', 'g308', 'f0391', 'g3109', 'f0151', 'g301', 'f068', 'g3101', 'r54', 'g312', 'g311', 'r4181', 
                                                'f0280', 'g138', 'g300', 'f0281', 'f0390', 'g94', 'f05', 'g309')
                                                then 1 else 0 end) as alzh
                                                
                                                FROM {input_tbl_nm} a
                                
                                                LEFT JOIN udwbasesecureview1.ADJD_MCE_SRVC b
                                                ON a.MBR_PTY_ID = b.MBR_PTY_ID
                                
                                                LEFT JOIN udwbasesecureview1.ADJD_MCE_DIAG c
                                                ON b.UDW_MED_CLM_ID = c.UDW_MED_CLM_ID
                                                AND b.orig_src_sys_cd = c.orig_src_sys_cd
                                                and b.udw_adjd_mce_id = c.udw_adjd_mce_id
                                                and b.proc_dt = c.proc_dt
                                    
                                
                                                WHERE EXTRACT(YEAR FROM b.proc_dt) IN (2021, 2022) --Look in relevant FMC years
                                                AND b.orig_src_sys_cd IN ('COS', 'NIC', 'CSP', 'APF', 'NDB', 'FRV', 'OXF')
                                                
        
                                                GROUP BY a.alt_id_val, a.er_discharge)
                            WITH DATA 
                            ON COMMIT PRESERVE ROWS;
                    
                    
                    '''
                
                

                
            return sql
    
    def FMC2(self, input_tbl_nm, output_tbl_nm):
        '''
        

        Parameters
        ----------
        input_tbl_nm : string
            DESCRIPTION.
        output_tbl_nm : string
            DESCRIPTION.

        Returns
        -------
        sql : string
            Query to narrow a table containing members with flags for the 8 FMC conditions to only those w/ at least 2 FMC conditions.
            NOTE: Query as-is doesn't reproduce SDM logic; therefore, it isn't used in our pipeline.

        '''
        
        sql = f'''
            CREATE VOLATILE TABLE {output_tbl_nm} AS (
            SELECT a.alt_id_val, a.er_discharge, a.ami, a.alzh, a.afib, a.ckd, a.copd, a.depr, a.heart, a.stroke

            FROM {input_tbl_nm} a
            
            WHERE (a.ami + a.alzh + a.afib + a.ckd + a.copd + a.depr + a.heart + a.stroke) >= 2

             )
            WITH DATA
            ON COMMIT PRESERVE ROWS;
        
        '''
        
        return sql
    
    def all_utils(self, input_tbl_nm, start_dt = None, proc_start_dt = None):
        '''
        

        Parameters
        ----------
        input_tbl_nm : string
            Name of input volatile table, containing MBI's.
        start_dt : string, optional
            A string with the SQL for the claim service start date for the pull period (end is CURRENT_DATE()). If start_dt is None (default), the query generated will pull
            all claims with a service start date from a 12-month look-back period from Nov 4, 2021 (the North Carolina pilot start date) AND with the designated processed start date
            (see proc_start_dt parameter description for more information).
        proc_start_dt : string, optional
            A string with the SQL for the processed start date for the pull period (end is CURRENT_DATE()). Note that the processed date is an administrative date, and can often
            occur after the claim service date. If proc_start_dt is None (default), the query generated will pull all claims with a processed date from 13 months prior to Nov 4, 2021
            (North Carolina pilot start date) onwards. Note that there is a further filter on claim service start date (see start_dt parameter description for more information).

        Returns
        -------
        er_sql : string
            Query to pull ER utilization for each member in the input table for the designated period (default is claims w/ service dates from Nov 4, 2020 to current date WITH processed
            dates from Oct 4, 2020 to current).
        ip_sql : string
            Query to pull IP utilization for each member in the input table for the designated period (default is claims w/ service dates from Nov 4, 2020 to current date with processed
            dates from Oct 4, 2020 to current).

        '''
        
        # Default is to pull a 12-month look-back from Nov 4, 2021 through today
        
        if start_dt is None:
            
            start_dt = '''ADD_MONTHS('2021-11-04', -12)'''
        
        if proc_start_dt is None:
            
            proc_start_dt = '''ADD_MONTHS('2021-11-04', -13)'''
            
        
        er_sql = f''' CREATE VOLATILE TABLE {self.group}_er_all AS (
        
                                /* ----------------
                                UDW ADJ CLMS 
                                -------------------*/
     
                                SELECT DISTINCT a.alt_id_val, b.srvc_strt_dt AS er
                                FROM {input_tbl_nm} a
                            
                                LEFT JOIN UDWBASESECUREVIEW1.ADJD_MCE_SRVC_MAIN_F b
                                ON a.mbr_pty_id = b.mbr_pty_id
                              
                                WHERE b.proc_dt BETWEEN {proc_start_dt} AND CURRENT_DATE() --pad process date
                                AND b.srvc_strt_dt BETWEEN {start_dt} AND CURRENT_DATE()
                                AND b.adjd_plsrv_cd = '23'
                                AND b.orig_src_sys_cd IN ('COS', 'NIC', 'CSP', 'APF', 'NDB', 'FRV', 'OXF')
                                AND b.src_row_sts_cd = 'A' --not deleted in source system
                                AND b.src_row_expir_dt = '9999-12-31'
                        
                                UNION
                    
                                /* ----------------
                                UDW PRE-ADJ CLMS 
                                -------------------*/
                    
                                SELECT DISTINCT a.alt_id_val, c.clm_srvc_strt_dt AS er

                                FROM {input_tbl_nm} a
                                
                                LEFT OUTER JOIN udwbasesecureview1.pre_adjd_med_clm b
                                ON a.mbr_pty_id = b.mbr_pty_id
                                
                                --Procedures
                                LEFT OUTER JOIN udwbasesecureview1.pre_adjd_med_clm_srvc c
                                ON b.udw_med_clm_id = c.udw_med_clm_id
                
                    
                                WHERE c.clm_srvc_strt_dt BETWEEN (CURRENT_DATE() - INTERVAL '7' DAY) AND CURRENT_DATE()
                                AND c.plsrv_cd = '23' -- OR c.bil_proc_cd IN ('99283', 'B1001','G9752','S9960') --ER POS only, exclude ER procedures
                                AND b.orig_src_sys_cd IN ('COS', 'NIC', 'CSP', 'APF', 'NDB', 'FRV', 'OXF')
                                --Remove pre-adj claims that are already in the adj table
                                and b.udw_med_clm_id NOT IN (SELECT DISTINCT b.udw_med_clm_id
                                                             FROM {input_tbl_nm} a
                                                             
                                                             LEFT JOIN UDWBASESECUREVIEW1.ADJD_MCE b
                                                             ON a.mbr_pty_id = b.mbr_pty_id
                                                             
                                                             WHERE b.orig_src_sys_cd in ('COS', 'NIC', 'CSP', 'APF', 'NDB', 'FRV', 'OXF') 
                                                             AND b.proc_dt >= ADD_MONTHS(CURRENT_DATE(), -4)
                                                             ) 
                                )
                                WITH DATA
                                ON COMMIT PRESERVE ROWS;
                
                
                '''

        ip_sql = f'''CREATE VOLATILE TABLE {self.group}_ip_all AS

                        (
                            SELECT DISTINCT a.alt_id_val, c.admis_dt AS ip_admit
                            FROM {input_tbl_nm} a
                         
                            LEFT JOIN udwbasesecureview1.ADJD_MCE_MAIN_F c
                            ON a.mbr_pty_id = c.mbr_pty_id
                         
                            WHERE c.admis_dt BETWEEN {start_dt} AND CURRENT_DATE()
                            AND c.IPTNT_OR_OPTNT_TYP_CD = 'IP'
                            AND c.CLM_INST_OR_PROF_CD IN ('I', 'H')
                            AND c.orig_src_sys_cd IN ('COS', 'NIC', 'CSP', 'APF', 'NDB', 'FRV', 'OXF')
                            AND c.src_row_sts_cd = 'A' --not deleted in source system
                            AND c.src_row_expir_dt = '9999-12-31'

                            UNION 

                            SELECT DISTINCT a.alt_id_val, d.clm_srvc_strt_dt AS ip_admit
                            FROM {input_tbl_nm} a
                        
                            --Claims
                            LEFT OUTER JOIN udwbasesecureview1.pre_adjd_med_clm b
                            ON a.mbr_pty_id = b.mbr_pty_id
                
                            --Procedures
                            LEFT OUTER JOIN udwbasesecureview1.pre_adjd_med_clm_srvc d
                            ON b.udw_med_clm_id = d.udw_med_clm_id
                            AND b.orig_src_sys_cd = d.orig_src_sys_cd
                
                            WHERE d.clm_srvc_strt_dt BETWEEN (CURRENT_DATE() - INTERVAL '7' DAY) AND CURRENT_DATE()
                            --bil_rvnu_cd is only populated for inpatient stays per https://uhgazure.sharepoint.com/sites/A10/400/802/Collab/Lists/L022/Default.aspx
                            AND d.plsrv_cd = '21'
                            AND d.bil_rvnu_cd IS NOT NULL
                            AND b.orig_src_sys_cd IN ('COS', 'NIC', 'CSP', 'APF', 'NDB', 'FRV', 'OXF')
                            
                            and b.udw_med_clm_id NOT IN (SELECT DISTINCT udw_med_clm_id
                                                         FROM UDWBASESECUREVIEW1.ADJD_MCE
                                                         WHERE orig_src_sys_cd in ('COS', 'NIC', 'CSP', 'APF', 'NDB', 'FRV', 'OXF')
                                                         AND proc_dt >= ADD_MONTHS(CURRENT_DATE(), -4))
                            )
                        
                            WITH DATA
                            ON COMMIT PRESERVE ROWS;
            
            
            '''
            
        return er_sql, ip_sql
    
    
    # ER visits that lead to admits should be treated as admits, not ER visits
    def remove_ineligible_er_due_to_admit(self, ER_tbl_nm, IP_tbl_nm, output_tbl_nm):

        '''   

        Returns
        -------
        sql : string
            Query to remove any ER visits that resulted in an IP admission (same day or next day). These are counted purely as IP stays.

        '''
        
        sql = f'''CREATE VOLATILE TABLE {self.group}_er_eligible AS
        
                    (SELECT a.*
                    FROM {ER_tbl_nm} a
                    
                    LEFT JOIN {self.group}_ip_all b
                    ON a.alt_id_val = b.alt_id_val
                    AND b.ip_admit BETWEEN a.er AND (a.er + INTERVAL '1' DAY) --IP admit on the same day or day after will result in counting as an IP only
                    
                    WHERE b.ip_admit IS NULL)
                    
                    WITH DATA
                    ON COMMIT PRESERVE ROWS;
                    '''
                    
        return sql
    
    def remove_ineligible_due_to_ed_helper(self, input_tbl_nm, ER_col_nm = 'er'):
        
        # Pull discharges into memory
        df = pd.read_sql(f'SELECT * FROM {input_tbl_nm};', self.con)
        df[f'{ER_col_nm}'] = pd.to_datetime(df[f'{ER_col_nm}'])

        #df_test = copy.deepcopy(full_discharge_df)
        
        member_ids = df['ALT_ID_VAL'].unique()
        
        # Initialize output
        eligible_dict = {}
        
        start = time.time()
        for i in member_ids:
        
            # Get the ith mbr
            mbr_discharges = copy.deepcopy(df.loc[df['ALT_ID_VAL'] == i])
    
            # Put dates in order
            mbr_discharges.sort_values(by = f'{ER_col_nm}')
            
            # Remove ineligible discharges
            mbr_elig_discharges = self.get_mbrs_eligible_discharges(mbr_discharges[f'{ER_col_nm}'])
    
            eligible_dict.update({f'{i}': mbr_elig_discharges})
            
        end = time.time()
        print('Time to eliminate ineligible discharges due to ED was: {} min.'.format(round((end - start)/60, 3)))
        
        # Convert back to dataframe
        eligible_discharges_df = pd.DataFrame([(k, x) for k, v in eligible_dict.items() for x in v], columns = ['ALT_ID_VAL', f'{ER_col_nm}'])
        
        return eligible_discharges_df
    
    
    # Helper function for remove_ineligible_due_to_ed()
    def get_mbrs_eligible_discharges(self, discharge_list):
        
        discharge_array = copy.deepcopy(discharge_list)
    
        eligible_discharge_dts = []
    
        while len(discharge_array) > 0:
        
            # Add the index date to eligible discharges
            eligible_discharge_dts.append(min(discharge_array))
        
            # Remove index date + all dates in the 7 days following from list
            dts_to_remove = pd.date_range(min(discharge_array), min(discharge_array) + dt.timedelta(days = 7), freq = 'D')
    
            discharge_array = [x for x in discharge_array if x not in dts_to_remove]
            
        return eligible_discharge_dts
    
    # 3
    # A. Gets all ED discharges from claims + TP discharge data
    # B. Removes ED discharges that are too close to a prior discharge
    # C. Loads into a temp table in teradata
    def remove_ineligible_due_to_ed(self, input_tbl_nm, output_tbl_nm):
        
        # Remove ineligible discharges and return df of eligible discharges
        elig_discharges = self.remove_ineligible_due_to_ed_helper(input_tbl_nm = input_tbl_nm)
        
        # Load into temp table in Teradata
        elig_discharges.to_csv(f'{self.group}_ed_eligible.csv', header = False, index = False)
        
        # Load eligible discharge data into a volatile table
        with open(f'{self.group}_ed_eligible.csv', newline='') as f:
            self.cur.execute(f'''CREATE VOLATILE TABLE {output_tbl_nm}
                             
                                (ALT_ID_VAL VARCHAR(100),
                                 er DATE FORMAT 'YYYY-MM-DD'
                                 )
                                
                                ON COMMIT PRESERVE ROWS;''')
            
            self.cur.execute(f'INSERT INTO {output_tbl_nm} (?, ?)', [row for row in csv.reader(f)])
            
        os.remove(f'{self.group}_ed_eligible.csv')
    
    def narrow_to_observation_period(self, input_tbl_nm, output_tbl_nm):
        '''
        

        Parameters
        ----------
        input_tbl_nm : string
            Name of input volatile table containing MBI's and er_discharges for a control pool.
        output_tbl_nm : string
            Name for volatile table output from this query.

        Returns
        -------
        sql : string
            Query to take a pool of control-group discharges and narrow down to only discharges that occurred during the pilot window (to match the treatment group).

        '''
        
        sql = f'''CREATE VOLATILE TABLE {output_tbl_nm} AS
        
        --If the input table is coming from remove_eligible_er_due_to_admit(), the ER field will need to be renamed
        --Take the min discharge to match the treatment group
        (SELECT a.alt_id_val, MIN(a.er) AS er_discharge
         FROM {input_tbl_nm} a
         
         WHERE a.er BETWEEN '2021-11-04' AND CURRENT_DATE()
         
         GROUP BY a.alt_id_val
         )
        
        WITH DATA
        ON COMMIT PRESERVE ROWS;

        '''
        
        return sql
    

    
    def unique_er_discharges(self, input_tbl_nm, output_tbl_nm):
        '''
        

        Parameters
        ----------
        input_tbl_nm : string
            Name of input volatile table with MBI and index ER discharges.
        output_tbl_nm : string
            Name for volatile table to be output from this query.

        Returns
        -------
        sql : string
            Query to remove any duplicate ER discharges from the input table. Duplicates can occur from indexing on ER discharge.

        '''
        
        sql = f'''
        CREATE VOLATILE TABLE {output_tbl_nm} AS
        
        (SELECT DISTINCT alt_id_val, er AS er_discharge
         FROM {input_tbl_nm})
        
        WITH DATA
        ON COMMIT PRESERVE ROWS;
        
        '''
        
        return sql
    
    
    def claims_after_discharge(self, input_tbl_nm, output_tbl_nm):
        '''
        

        Parameters
        ----------
        input_tbl_nm : string
            Name of volatile table containing MBIs and all ER discharges of interest.
        output_tbl_nm : string
            Name of volatile table to be output from this query.

        Returns
        -------
        sql_udw : string
            Query to pull all claims in the 7-day period after an ER visit relevant to a Hedis follow-up for an eligible FMC member.
            Claims are filtered, so any ER discharge without a matching claim will be dropped; hence, these claims will need to get joined
            back to their respective discharges to determine if a Hedis-eligible follow-up occurred after the ER visit or not.

        '''
        
        
        sql_udw = f'''CREATE VOLATILE TABLE {output_tbl_nm} AS
        
        /*------------
        UDW pre-adj
        ------------*/
        
        (SELECT DISTINCT a.alt_id_val, a.er_discharge, d.clm_srvc_strt_dt AS srvc_dt, d.plsrv_cd, d.bil_proc_cd AS proc_cd
        --Cohort (discharges)
        FROM {input_tbl_nm} a
        
        --Claims
        LEFT OUTER JOIN udwbasesecureview1.pre_adjd_med_clm c
        ON a.mbr_pty_id = c.mbr_pty_id
        
        --Procedures
        LEFT OUTER JOIN udwbasesecureview1.pre_adjd_med_clm_srvc d
        ON c.udw_med_clm_id = d.udw_med_clm_id
        AND c.orig_src_sys_cd = d.orig_src_sys_cd
        
        WHERE d.clm_srvc_strt_dt BETWEEN a.er_discharge AND (a.er_discharge + INTERVAL '7' DAY)
        AND d.clm_srvc_strt_dt BETWEEN (CURRENT_DATE() - INTERVAL '7' DAY) AND CURRENT_DATE() --limit pre-adj to look only for most recent discharges
        AND a.er_discharge BETWEEN (CURRENT_DATE() - INTERVAL '14' DAY) AND CURRENT_DATE()
        AND c.orig_src_sys_cd IN ('COS', 'NIC', 'CSP', 'APF', 'NDB', 'FRV', 'OXF')
        AND d.bil_proc_cd IN ('99201', '99202', '99203', '99204', '99205', '99201', '99202', '99203', '99204', '99205', '99211', '99212', '99213', '99214', '99215', 
        '99241', '99242', '99243', '99244', '99245', '99341', '99342', '99343', '99344', '99345', '99347', '99348', '99349', '99350', '99381', '99382', '99383', 
        '99384', '99385', '99386', '99387', '99391', '99392', '99393', '99394', '99395', '99396', '99397', '99401', '99402', '99403', '99404', '99411', '99412', 
        '99429', '99455', '99456', '99483', 'G0402', 'G0438', 'G0439', 'G0463', 'T1015', '0510', '0511', '0512', '0513', '0514', '0515', '0516', '0517', '0519', 
        '0520', '0521', '0522', '0523', '0526', '0527', '0528', '0529', '0982', '0983', '98966', '98967', '98968', '99441', '99442', '99443', '99495', '99496',
        '99366', 'T1016', 'T1017', 'T2022', 'T2023', '99439', '99487', '99489', '99490', '99491', 'G0506', '90791', '90792', '90832', '90833', '90834', '90836', '90837', '90838', '90839', '90840', '90845', '90847', '90849', '90853', '90875', '90876', '99221', 
        '99222', '99223', '99231', '99232', '99233', '99238', '99239', '99251', '99252', '99253', '99254', '99255', '98960', '98961', '98962', '99078', '99201', '99215', '99241', '99242', '99243', '99244', '99349', '99350', '99381', 
        '99382', '99383', '99395', '99396', '99397', '99401', '99402', '99510', '99202', '99203', '99204', '99205', '99211', '99212', 
        '99213', '99214', '99245', '99341', '99342', '99343', '99344', '99345', '99347', '99348', '99384', '99385', '99386', '99387', 
        '99391', '99392', '99393', '99394', '99403', '99404', '99411', '99412', '99483', '99492', '99493', '99494', 'G0155', 'G0176', 'G0177', 
        'G0409', 'G0463', 'G0512', 'H0002', 'H0004', 'H0031', 'H0034', 'H0036', 'H0037', 'H0039', 'H0040', 'H2000', 'H2010', 'H2011', 'H2013', 'H2014', 
        'H2015', 'H2016', 'H2017', 'H2018', 'H2019', 'H2020', 'T1015', '0510', '0513', '0515', '0516', '0517', '0519', '0520', '0521', '0522', '0523', '0526', '0527', 
        '0528', '0529', '0900', '0902', '0903', '0904', '0911', '0914', '0915', '0916', '0917', '0919', '0982', '0983', '90791', '90792', '90832', '90833', '90834', '90836', '90837', '90838', '90839', '90840', '90845', '90847', '90849', '90853', '90875', 
        '90876', '99221', '99222', '99223', '99231', '99232', '99233', '99238', '99239', '99251', '99252',
        '99253', '99254', '99255', 'G0410', 'G0411', 'H0035', 'H2001', 'H2012', 'S0201', 'S9480', 'S9484', 'S9485', '0905', '0907', '0912', '0913', '90791', '90792', '90832', '90833', '90834', '90836', '90837', '90838', '90839', '90840', '90845', '90847', '90849', 
        '90853', '90875', '90876', '99221', '99222', '99223', '99231', '99232', '99233', '99238', '99239', '99251', '99252',
        '99253', '99254', '99255', '90870', 'GZB0ZZZ', 'GZB1ZZZ', 'GZB2ZZZ', 'GZB3ZZZ', 'GZB4ZZZ', '90791', '90792', '90832', '90833', '90834', '90836', '90837', '90838', '90839', '90840', '90845', '90847', '90849', '90853', '90875', 
        '90876', '99221', '99222', '99223', '99231', '99232', '99233', '99238', '99239', '99251', '99252', '99253', '99254', '99255', '99217', '99218', '99219', '99220',
        '99408', '99409', 'G0396', 'G0397', 'G0443', 'H0001', 'H0005', 'H0007', 'H0015', 'H0016', 'H0022', 'H0047', 
        'H0050', 'H2035', 'H2036', 'T1006', 'T1012', '0906', '0944', '0945', '98969', '98970', '98971', '98972', '99421', '99422', '99423', '99444', '99457', 'G0071', 'G2010', 'G2012', 'G2061', 'G2062', 'G2063'
        )
        AND c.udw_med_clm_id NOT IN (SELECT DISTINCT udw_med_clm_id
                                     FROM UDWBASESECUREVIEW1.ADJD_MCE
                                     WHERE orig_src_sys_cd in ('COS', 'NIC', 'CSP', 'APF', 'NDB', 'FRV', 'OXF')
                                     AND proc_dt >= ADD_MONTHS(CURRENT_DATE(), -4))

        UNION
        
        /*------------
        UDW adj
        ------------*/
    
        SELECT DISTINCT a.alt_id_val, a.er_discharge, d.srvc_strt_dt AS srvc_dt, e.plsrv_cd, f.proc_cd
        
        --Cohort (discharges)
        FROM {input_tbl_nm} a
        
        --Claims
        LEFT JOIN udwbasesecureview1.ADJD_MCE_SRVC d
        ON a.MBR_PTY_ID = d.MBR_PTY_ID
        
        --POS
        LEFT JOIN udwbasesecureview1.ADJD_MCE_SRVC_PLSRV e
        ON d.orig_src_sys_cd = e.orig_src_sys_cd
        and d.proc_dt = e.proc_dt
        and d.UDW_MED_CLM_ID = e.UDW_MED_CLM_ID
        and d.adjd_med_clm_srvc_ln_num = e.adjd_med_clm_srvc_ln_num
        
        --Procedures
        LEFT JOIN udwbasesecureview1.ADJD_MCE_SRVC_PROC f
        ON d.orig_src_sys_cd = f.orig_src_sys_cd
        and d.proc_dt = f.proc_dt
        and d.UDW_MED_CLM_ID = f.UDW_MED_CLM_ID
        and d.adjd_med_clm_srvc_ln_num = f.adjd_med_clm_srvc_ln_num
        
        WHERE d.srvc_strt_dt BETWEEN a.er_discharge AND (a.er_discharge + INTERVAL '7' DAY)
        AND d.orig_src_sys_cd IN ('COS', 'NIC', 'CSP', 'APF', 'NDB', 'FRV', 'OXF')
        AND f.proc_cd IN ('99201', '99202', '99203', '99204', '99205', '99201', '99202', '99203', '99204', '99205', '99211', '99212', '99213', '99214', '99215', 
        '99241', '99242', '99243', '99244', '99245', '99341', '99342', '99343', '99344', '99345', '99347', '99348', '99349', '99350', '99381', '99382', '99383', 
        '99384', '99385', '99386', '99387', '99391', '99392', '99393', '99394', '99395', '99396', '99397', '99401', '99402', '99403', '99404', '99411', '99412', 
        '99429', '99455', '99456', '99483', 'G0402', 'G0438', 'G0439', 'G0463', 'T1015', '0510', '0511', '0512', '0513', '0514', '0515', '0516', '0517', '0519', 
        '0520', '0521', '0522', '0523', '0526', '0527', '0528', '0529', '0982', '0983', '98966', '98967', '98968', '99441', '99442', '99443', '99495', '99496',
        '99366', 'T1016', 'T1017', 'T2022', 'T2023', '99439', '99487', '99489', '99490', '99491', 'G0506', '90791', '90792', '90832', '90833', '90834', '90836', '90837', '90838', '90839', '90840', '90845', '90847', '90849', '90853', '90875', '90876', '99221', 
        '99222', '99223', '99231', '99232', '99233', '99238', '99239', '99251', '99252', '99253', '99254', '99255', '98960', '98961', '98962', '99078', '99201', '99215', '99241', '99242', '99243', '99244', '99349', '99350', '99381', 
        '99382', '99383', '99395', '99396', '99397', '99401', '99402', '99510', '99202', '99203', '99204', '99205', '99211', '99212', 
        '99213', '99214', '99245', '99341', '99342', '99343', '99344', '99345', '99347', '99348', '99384', '99385', '99386', '99387', 
        '99391', '99392', '99393', '99394', '99403', '99404', '99411', '99412', '99483', '99492', '99493', '99494', 'G0155', 'G0176', 'G0177', 
        'G0409', 'G0463', 'G0512', 'H0002', 'H0004', 'H0031', 'H0034', 'H0036', 'H0037', 'H0039', 'H0040', 'H2000', 'H2010', 'H2011', 'H2013', 'H2014', 
        'H2015', 'H2016', 'H2017', 'H2018', 'H2019', 'H2020', 'T1015', '0510', '0513', '0515', '0516', '0517', '0519', '0520', '0521', '0522', '0523', '0526', '0527', 
        '0528', '0529', '0900', '0902', '0903', '0904', '0911', '0914', '0915', '0916', '0917', '0919', '0982', '0983', '90791', '90792', '90832', '90833', '90834', '90836', '90837', '90838', '90839', '90840', '90845', '90847', '90849', '90853', '90875', 
        '90876', '99221', '99222', '99223', '99231', '99232', '99233', '99238', '99239', '99251', '99252',
        '99253', '99254', '99255', 'G0410', 'G0411', 'H0035', 'H2001', 'H2012', 'S0201', 'S9480', 'S9484', 'S9485', '0905', '0907', '0912', '0913', '90791', '90792', '90832', '90833', '90834', '90836', '90837', '90838', '90839', '90840', '90845', '90847', '90849', 
        '90853', '90875', '90876', '99221', '99222', '99223', '99231', '99232', '99233', '99238', '99239', '99251', '99252',
        '99253', '99254', '99255', '90870', 'GZB0ZZZ', 'GZB1ZZZ', 'GZB2ZZZ', 'GZB3ZZZ', 'GZB4ZZZ', '90791', '90792', '90832', '90833', '90834', '90836', '90837', '90838', '90839', '90840', '90845', '90847', '90849', '90853', '90875', 
        '90876', '99221', '99222', '99223', '99231', '99232', '99233', '99238', '99239', '99251', '99252', '99253', '99254', '99255', '99217', '99218', '99219', '99220',
        '99408', '99409', 'G0396', 'G0397', 'G0443', 'H0001', 'H0005', 'H0007', 'H0015', 'H0016', 'H0022', 'H0047', 
        'H0050', 'H2035', 'H2036', 'T1006', 'T1012', '0906', '0944', '0945', '98969', '98970', '98971', '98972', '99421', '99422', '99423', '99444', '99457', 'G0071', 'G2010', 'G2012', 'G2061', 'G2062', 'G2063'
        )
        AND d.src_row_sts_cd = 'A' --not deleted in source system
        AND d.src_row_expir_dt = '9999-12-31'
        )
        
        WITH DATA
        ON COMMIT PRESERVE ROWS;
        
        '''
        
        # sql_stars = f'''CREATE VOLATILE TABLE {self.discharge_category}_stars_claims_after_discharge AS
    
        # (--Query runs 6x faster if we pull cohort first
        # WITH ids AS (SELECT DISTINCT a.member_id, b.mbr_surrg_id
        # FROM {self.discharge_category}_eligible_discharges a
        # LEFT JOIN starsview.mbr_alt_id b
        # ON a.member_id = b.alt_id_val
        
        # WHERE b.alt_id_typ_cd = 1)
        
        # --Rename columns to match other pulls so we can stack
        # SELECT DISTINCT a.member_id, a.er_discharge, /*a.status,*/ d.clm_str_srvc_dt AS srvc_dt, e.med_clm_pos_cd AS plsrv_cd, f.med_clm_proc_cd AS proc_cd
        
        # FROM {self.discharge_category} a
        # LEFT JOIN ids b
        # ON a.member_id = b.member_id
        
        # LEFT JOIN starsview.clm d
        # ON b.mbr_surrg_id = d.mbr_surrg_id
        
        # LEFT JOIN starsview.med_clm e
        # ON d.clm_surrg_id = e.clm_surrg_id
        
        # LEFT JOIN starsview.med_clm_proc f
        # ON d.clm_surrg_id = f.clm_surrg_id
        
        # WHERE d.clm_str_srvc_dt >= '2021-11-04'
        # AND d.clm_str_srvc_dt BETWEEN a.er_discharge AND (a.er_discharge + INTERVAL '7' DAY)
        # )
        
        # WITH DATA
        # ON COMMIT PRESERVE ROWS;
        
        # '''
        
        return sql_udw #, sql_stars
    
    def ed_follow_ups(self, discharge_tbl, claims_after_tbl, output_tbl_nm):
        '''
        

        Parameters
        ----------
        discharge_tbl : string
            Name of volatile table with Truepill ER discharge data. Needs to include MBI, ER discharge date, and status of the follow-up on the ER visit.
        claims_after_tbl : string
            Name of a volatile table with all Hedis-relevant claims after ER discharges. Usually this is generated using the claims_after_discharge() method.
        output_tbl_nm : string
            Name for the volatile table output from this query.

        Returns
        -------
        sql : string
            Query to create a stars_eligible_er_follow_up binary column for the input MBI's/discharges/statuses, indicating whether or not that ER discharge
            had a follow-up that met the Hedis STARS requirements.

        '''
        
        
        sql = f'''CREATE VOLATILE TABLE {output_tbl_nm} AS
    
        (
        --15 scenarios look to see if discharge was closed in claims
        --Otherwise, check to see if discharge was closed in EMR
        SELECT DISTINCT a.alt_id_val, a.er_discharge,
        
        MAX(CASE 
        --Scenario 1: outpatient visits
        WHEN b.proc_cd IN ('99201', '99202', '99203', '99204', '99205', '99201', '99202', '99203', '99204', '99205', '99211', '99212', '99213', '99214', '99215', 
        '99241', '99242', '99243', '99244', '99245', '99341', '99342', '99343', '99344', '99345', '99347', '99348', '99349', '99350', '99381', '99382', '99383', 
        '99384', '99385', '99386', '99387', '99391', '99392', '99393', '99394', '99395', '99396', '99397', '99401', '99402', '99403', '99404', '99411', '99412', 
        '99429', '99455', '99456', '99483', 'G0402', 'G0438', 'G0439', 'G0463', 'T1015', '0510', '0511', '0512', '0513', '0514', '0515', '0516', '0517', '0519', 
        '0520', '0521', '0522', '0523', '0526', '0527', '0528', '0529', '0982', '0983')
        
        --Scenario 2: telephone visits
        OR b.proc_cd IN ('98966', '98967', '98968', '99441', '99442', '99443')
        
        --Scenario 3: transitional care mgmt
        OR b.proc_cd IN ('99495', '99496')
        
        --Scenario 4: case mgmt visits
        OR b.proc_cd IN ('99366', 'T1016', 'T1017', 'T2022', 'T2023')
        
        --Scenario 5: complex care mgmt
        OR b.proc_cd IN ('99439', '99487', '99489', '99490', '99491', 'G0506')
        
        --Scenario 6: Outpatient or Telehealth Behavioral Health Visit
        OR (b.proc_cd IN ('90791', '90792', '90832', '90833', '90834', '90836', '90837', '90838', '90839', '90840', '90845', '90847', '90849', '90853', '90875', '90876', '99221', 
        '99222', '99223', '99231', '99232', '99233', '99238', '99239', '99251', '99252', '99253', '99254', '99255')
        AND b.plsrv_cd IN ('03', '05', '07', '09', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '22', '33', '49', '50', '71', '72'))
        
        --Scenario 7: Outpatient or Telehealth Behavioral Health Visit
        OR b.proc_cd IN ('98960', '98961', '98962', '99078', '99201', '99215', '99241', '99242', '99243', '99244', '99349', '99350', '99381', 
        '99382', '99383', '99395', '99396', '99397', '99401', '99402', '99510', '99202', '99203', '99204', '99205', '99211', '99212', 
        '99213', '99214', '99245', '99341', '99342', '99343', '99344', '99345', '99347', '99348', '99384', '99385', '99386', '99387', 
        '99391', '99392', '99393', '99394', '99403', '99404', '99411', '99412', '99483', '99492', '99493', '99494', 'G0155', 'G0176', 'G0177', 
        'G0409', 'G0463', 'G0512', 'H0002', 'H0004', 'H0031', 'H0034', 'H0036', 'H0037', 'H0039', 'H0040', 'H2000', 'H2010', 'H2011', 'H2013', 'H2014', 
        'H2015', 'H2016', 'H2017', 'H2018', 'H2019', 'H2020', 'T1015', '0510', '0513', '0515', '0516', '0517', '0519', '0520', '0521', '0522', '0523', '0526', '0527', 
        '0528', '0529', '0900', '0902', '0903', '0904', '0911', '0914', '0915', '0916', '0917', '0919', '0982', '0983')
        
        --Scenario 8: Intensive Outpatient Encounter or Partial Hospitalization
        OR (b.proc_cd IN ('90791', '90792', '90832', '90833', '90834', '90836', '90837', '90838', '90839', '90840', '90845', '90847', '90849', '90853', '90875', 
        '90876', '99221', '99222', '99223', '99231', '99232', '99233', '99238', '99239', '99251', '99252',
        '99253', '99254', '99255')
        AND b.plsrv_cd = '52')
        
        --Scenario 9: Intensive Outpatient Encounter or Partial Hospitalization
        OR b.proc_cd IN ('G0410', 'G0411', 'H0035', 'H2001', 'H2012', 'S0201', 'S9480', 'S9484', 'S9485', '0905', '0907', '0912', '0913')
        
        --Scenario 10: Community Mental Health Center Visit
        OR (b.proc_cd IN ('90791', '90792', '90832', '90833', '90834', '90836', '90837', '90838', '90839', '90840', '90845', '90847', '90849', 
        '90853', '90875', '90876', '99221', '99222', '99223', '99231', '99232', '99233', '99238', '99239', '99251', '99252',
        '99253', '99254', '99255')
        AND b.plsrv_cd = '53')
        
        --Scenario 11: Electroconvulsive Therapy With Any Provider Type and With Appropriate Place of Service Code
        OR (b.proc_cd IN ('90870', 'GZB0ZZZ', 'GZB1ZZZ', 'GZB2ZZZ', 'GZB3ZZZ', 'GZB4ZZZ')
        AND b.plsrv_cd IN ('03', '05', '07', '09', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '22', '24', '33', '49',
        '50', '52', '53', '71', '72') )
        
        --Scenario 12: Telehealth Visit With Any Provider Type and the appropriate pl of svc code
        OR (b.proc_cd IN ('90791', '90792', '90832', '90833', '90834', '90836', '90837', '90838', '90839', '90840', '90845', '90847', '90849', '90853', '90875', 
        '90876', '99221', '99222', '99223', '99231', '99232', '99233', '99238', '99239', '99251', '99252', '99253', '99254', '99255')
        AND b.plsrv_cd = '02' )
        
        --Scenario 13: Observation Visit
        OR b.proc_cd IN ('99217', '99218', '99219', '99220')
        
        --Scenario 14: Substance Use Disorder Services
        OR b.proc_cd IN ('99408', '99409', 'G0396', 'G0397', 'G0443', 'H0001', 'H0005', 'H0007', 'H0015', 'H0016', 'H0022', 'H0047', 
        'H0050', 'H2035', 'H2036', 'T1006', 'T1012', '0906', '0944', '0945')
        
        --Scenario 15: E-Visit or Virtual Check-In
        OR b.proc_cd IN ('98969', '98970', '98971', '98972', '99421', '99422', '99423', '99444', '99457', 'G0071', 'G2010', 'G2012', 'G2061', 'G2062', 'G2063')
        
        --Closed out in discharge data
        OR c.status = 'COMPLETED BEFORE DUE DATE' THEN 1 ELSE 0 END) AS stars_eligible_er_follow_up
        
        FROM {discharge_tbl} a
        
        LEFT JOIN {claims_after_tbl} b
        ON a.alt_id_val = b.alt_id_val
        AND a.er_discharge = b.er_discharge
        
        LEFT JOIN stellar_discharges c
        ON a.alt_id_val = c.member_id
        AND a.er_discharge = c.discharge_dt

        GROUP BY a.alt_id_val, a.er_discharge
        )
        
        WITH DATA
        ON COMMIT PRESERVE ROWS;'''
        
        return sql
    
    # def follow_up_rates(self, cohort_tbl_nm, follow_up_tbl, output_tbl_nm):
    #     '''
        

    #     Parameters
    #     ----------
    #     cohort_tbl_nm : string
    #         Name of volatile table containing cohort MBIs and index discharge dates.
    #     follow_up_tbl : string
    #         Name of volatile table containing Hedis follow-up flag. This is usually created using the claims_after_discharge() method followed by the ed_follow_ups() method.
    #     output_tbl_nm : string
    #         Name for the volatile table to be output from this query.

    #     Returns
    #     -------
    #     sql : string
    #         Query to calculate the FMC follow-up rates for MBIs in the cohort table. FMC follow-up rates are calculated for 2 different time periods (and returned 
    #          in two separate columns): (1) the 12 months prior to the member's index ER discharge date, and (2) the time between Nov 4, 2021 (the NC pilot start date) 
    #         and the member's index ER discharge date. If no visits occurred in the relevant time period, NULL is returned for the follow-up rate.

    #     '''
        
    #     sql = f'''CREATE VOLATILE TABLE {output_tbl_nm} AS 
                            
    #                         (WITH unique_mbis AS (SELECT DISTINCT alt_id_val, er_discharge
    #                                                 FROM {cohort_tbl_nm} a),
                            
    #                                 fu_12m_df AS (SELECT DISTINCT a.alt_id_val, a.er_discharge, COUNT(DISTINCT b.er_discharge) AS ed_12m, SUM(b.stars_eligible_er_follow_up) AS fu_12m
    #                                             FROM unique_mbis a
                
    #                                         -- %age of ED visits gap closed in 12 m prior to index date
    #                                             LEFT JOIN {follow_up_tbl} b
    #                                             ON a.alt_id_val = b.alt_id_val
    #                                             AND b.er_discharge BETWEEN ADD_MONTHS(a.er_discharge, -12) AND (a.er_discharge - INTERVAL '1' DAY)
                                                
    #                                             GROUP BY a.alt_id_val, a.er_discharge),

    #                                 fu_study_df AS (SELECT DISTINCT a.alt_id_val, a.er_discharge, COUNT(DISTINCT c.er_discharge) AS ed_study, SUM(c.stars_eligible_er_follow_up) as fu_study
                                            
    #                                              FROM unique_mbis a
                                            
    #                                             --%age of ED visits gap closed before index date within study period
    #                                             LEFT JOIN {follow_up_tbl} c
    #                                             ON a.alt_id_val = c.alt_id_val
    #                                             AND c.er_discharge BETWEEN '2021-11-04' AND a.er_discharge
                                                
    #                                             GROUP BY a.alt_id_val, a.er_discharge),
                            
    #                                 fu_summary AS (SELECT DISTINCT a.alt_id_val, a.er_discharge, CASE WHEN b.fu_12m IS NULL THEN 0 ELSE b.fu_12m END AS fu_12m,
    #                                                b.ed_12m, CASE WHEN c.fu_study IS NULL THEN 0 ELSE c.fu_study END AS fu_study, c.ed_study
                                    
    #                                                 FROM unique_mbis a
                                    
    #                                                 LEFT JOIN fu_12m_df b
    #                                                 ON a.alt_id_val = b.alt_id_val
    #                                                 AND a.er_discharge = b.er_discharge
                                    
    #                                                 LEFT JOIN fu_study_df c
    #                                                 ON a.alt_id_val = c.alt_id_val
    #                                                 AND a.er_discharge = c.er_discharge)
                                    
    #                                 SELECT alt_id_val, er_discharge, CASE WHEN ed_12m = 0 THEN NULL ELSE CAST(fu_12m AS FLOAT)/CAST(ed_12m AS FLOAT) END AS fu_rate_12m, 
    #                                 CASE WHEN ed_study = 0 THEN NULL ELSE CAST(fu_study AS FLOAT)/CAST(ed_study AS FLOAT) END AS fu_rate_study
    #                                 FROM fu_summary)
                            
    #                         WITH DATA
    #                         ON COMMIT PRESERVE ROWS;
                            
    #                         '''
                            
    #     return sql
    
    def follow_up_rates(self, cohort_tbl_nm, follow_up_tbl, output_tbl_nm):
        '''
        

        Parameters
        ----------
        cohort_tbl_nm : string
            Name of volatile table containing cohort MBIs and index discharge dates.
        follow_up_tbl : string
            Name of volatile table containing Hedis follow-up flag. This is usually created using the claims_after_discharge() method followed by the ed_follow_ups() method.
        output_tbl_nm : string
            Name for the volatile table to be output from this query.

        Returns
        -------
        sql : string
            Query to calculate the FMC follow-up rates for MBIs in the cohort table. FMC follow-up rates are calculated for 2 different time periods (and returned 
             in two separate columns): (1) the 12 months prior to the member's index ER discharge date, and (2) the time between Nov 4, 2021 (the NC pilot start date) 
            and the member's index ER discharge date. If no visits occurred in the relevant time period, NULL is returned for the follow-up rate.

        '''
        
        sql = f'''CREATE VOLATILE TABLE {output_tbl_nm} AS 
                            
                            (WITH unique_mbis AS (SELECT DISTINCT alt_id_val, er_discharge
                                                    FROM {cohort_tbl_nm} a),
                            
                                    fu_12m_df AS (SELECT DISTINCT a.alt_id_val, a.er_discharge, COUNT(DISTINCT b.er_discharge) AS ed_12m, SUM(b.stars_eligible_er_follow_up) AS fu_12m
                                                FROM unique_mbis a
                
                                            -- %age of ED visits gap closed in 12 m prior to index date
                                                LEFT JOIN {follow_up_tbl} b
                                                ON a.alt_id_val = b.alt_id_val
                                                AND b.er_discharge BETWEEN ADD_MONTHS(a.er_discharge, -12) AND (a.er_discharge - INTERVAL '1' DAY)
                                                
                                                GROUP BY a.alt_id_val, a.er_discharge),

                                    fu_study_df AS (SELECT DISTINCT a.alt_id_val, a.er_discharge, COUNT(DISTINCT c.er_discharge) AS ed_study, SUM(c.stars_eligible_er_follow_up) as fu_study
                                            
                                                 FROM unique_mbis a
                                            
                                                --%age of ED visits gap closed before index date within study period
                                                LEFT JOIN {follow_up_tbl} c
                                                ON a.alt_id_val = c.alt_id_val
                                                AND c.er_discharge BETWEEN '2021-11-04' AND a.er_discharge
                                                
                                                GROUP BY a.alt_id_val, a.er_discharge)
                                    
                                    SELECT a.alt_id_val, a.er_discharge, CASE WHEN a.fu_12m IS NULL THEN 0 ELSE a.fu_12m END AS fu_12m, 
                                    CASE WHEN a.ed_12m IS NULL THEN 0 ELSE a.ed_12m END AS ed_12m, 
                                    CASE WHEN b.fu_study IS NULL THEN 0 ELSE b.fu_study END AS fu_study, b.ed_study
                                    
                                    FROM fu_12m_df a
                                    
                                    LEFT JOIN fu_study_df b
                                    ON a.alt_id_val = b.alt_id_val
                                    AND a.er_discharge = b.er_discharge)
                            
                            WITH DATA
                            ON COMMIT PRESERVE ROWS;
                            
                            '''
                            
        return sql
    
    
    def split_utils(self, cohort_tbl_nm, ER_tbl_nm, IP_tbl_nm):
        '''
        

        Parameters
        ----------
        cohort_tbl_nm : string
            Name of cohort table with MBIs and index ER discharge dates

        Returns
        -------
        er_covariate : string
            Query to pull member ER discharges in the covariate period (12m prior to the index date through the day before the index date).
        er_outcome : string
            Query to pull member ER discharges in the outcome period (day after index date through +months in eval period of the instance).
        ip_covariate : string
            Query to pull member IP admissions in the covariate period (12m prior to the index date through the day before the index date).
        ip_outcome : string
            Query to pull member IP admissions in the outcome period (day after index date through +months in outcome period of the instance).

        '''
        
        er_covariate = f'''CREATE VOLATILE TABLE {self.group}_er_covariate AS
        
        (SELECT a.alt_id_val, a.er_discharge, b.er
         FROM {cohort_tbl_nm} a
                               
         LEFT JOIN {ER_tbl_nm} b
         ON a.alt_id_val = b.alt_id_val
         AND er BETWEEN ADD_MONTHS(a.er_discharge, -12) AND (a.er_discharge - INTERVAL '1' DAY))
        
        WITH DATA
        ON COMMIT PRESERVE ROWS;
        
        
        '''
        
        er_outcome = f'''CREATE VOLATILE TABLE {self.group}_er_outcome AS
        
        (SELECT a.alt_id_val, a.er_discharge, b.er
         FROM {cohort_tbl_nm} a
                       
        LEFT JOIN {ER_tbl_nm}  b
        ON a.alt_id_val = b.alt_id_val
        AND b.er BETWEEN (a.er_discharge + INTERVAL '1' DAY) AND (a.er_discharge + INTERVAL '{self.days_in_outcome_period}' DAY))

        WITH DATA
        ON COMMIT PRESERVE ROWS;
        '''
        
        ip_covariate = f'''CREATE VOLATILE TABLE {self.group}_ip_covariate AS
        
        (SELECT a.alt_id_val, a.er_discharge, b.ip_admit
        FROM {cohort_tbl_nm} a
                                              
        LEFT JOIN {IP_tbl_nm}  b
        ON a.alt_id_val = b.alt_id_val
        AND b.ip_admit BETWEEN ADD_MONTHS(a.er_discharge, -12) AND (a.er_discharge - INTERVAL '1' DAY))
        
        WITH DATA
        ON COMMIT PRESERVE ROWS;
        
        
        '''
        
        ip_outcome  = f'''CREATE VOLATILE TABLE {self.group}_ip_outcome AS
        
        (SELECT a.alt_id_val, a.er_discharge, b.ip_admit
         FROM {cohort_tbl_nm} a
                                      
        LEFT JOIN {IP_tbl_nm} b
        ON a.alt_id_val = b.alt_id_val
        AND b.ip_admit BETWEEN (a.er_discharge + INTERVAL '1' DAY) AND (a.er_discharge + INTERVAL '{self.days_in_outcome_period}' DAY))
        
        WITH DATA
        ON COMMIT PRESERVE ROWS;
        
        '''
    
        return er_covariate, er_outcome, ip_covariate, ip_outcome
    
    def utilizations(self, cohort_tbl_nm):
        '''
        

        Parameters
        ----------
        cohort_tbl_nm : string
            Name of volatile table containing cohort MBIs and index ER discharges.

        Returns
        -------
        sql : string
            Query to count distinct ER visits and IP admissions in covariate and outcome periods (raw dates are usually pulled using the split_utils() method).

        '''
        
        sql = f''' CREATE VOLATILE TABLE {self.group}_utils AS 
                 
        (SELECT a.alt_id_val, a.er_discharge, COUNT(DISTINCT b.er) AS er_12m, COUNT(DISTINCT c.er) AS er_trt, COUNT(DISTINCT d.ip_admit) AS ip_12m, COUNT(DISTINCT e.ip_admit) AS ip_trt
        FROM {cohort_tbl_nm} a
        
        LEFT JOIN {self.group}_er_covariate b
        ON a.alt_id_val = b.alt_id_val
        AND a.er_discharge = b.er_discharge
        
        LEFT JOIN {self.group}_er_outcome c
        ON a.alt_id_val = c.alt_id_val
        AND a.er_discharge = c.er_discharge
        
        LEFT JOIN {self.group}_ip_covariate d
        ON a.alt_id_val = d.alt_id_val
        AND a.er_discharge = d.er_discharge
        
        LEFT JOIN {self.group}_ip_outcome e
        ON a.alt_id_val = e.alt_id_val
        AND a.er_discharge = e.er_discharge
        
        GROUP BY a.alt_id_val, a.er_discharge)
        
        WITH DATA
        ON COMMIT PRESERVE ROWS;'''
        
        return sql
    
    
    def demographics(self, cohort_tbl_nm):
        '''
        

        Parameters
        ----------
        cohort_tbl_nm : string
            Name of volatile table containing cohort MBIs and index ER discharges.

        Returns
        -------
        sql : string
            Query to pull member's age and gender as of their index ER discharge.

        '''
        
        sql = f'''CREATE VOLATILE TABLE {self.group}_demographics AS
        
        (SELECT DISTINCT a.alt_id_val, a.er_discharge, b.mbr_pty_id, ((CURRENT_DATE() (INT)) -  (c.bth_dt (INT))) * 0.0001 AS age, c.gdr_typ_cd AS gender
         
         FROM {cohort_tbl_nm} a
         
         LEFT JOIN udwbasesecureview1.mbr_alt_id b
         ON a.alt_id_val = b.alt_id_val
         
         LEFT JOIN udwbasesecureview1.mbr_f c
         ON b.mbr_pty_id = c.mbr_pty_id
         AND b.orig_src_sys_cd = c.orig_src_sys_cd

         
        WHERE b.alt_id_typ_cd = 'HIC'
        AND b.alt_id_val IS NOT NULL
        AND b.orig_src_sys_cd IN ('COS', 'NIC', 'CSP', 'APF', 'NDB', 'FRV', 'OXF')
        AND b.src_row_sts_cd = 'A' --not deleted in source system
        AND b.row_expir_dt = '9999-12-31'
        )
        
        WITH DATA
        ON COMMIT PRESERVE ROWS;
        
        
        '''
        return sql
    
    def charlson_comorbidities(self, cohort_tbl_nm):
        
        sql = f'''CREATE VOLATILE TABLE {self.group}_charlson_comorbidities AS 
        
        (
            SELECT DISTINCT a.alt_id_val, a.er_discharge,
            --AIDS
            MAX(case when LEFT(c.diag_cd, 3) IN ('B20', 'B21', 'B22', 'B24') then 1 else 0 end) as aids,
                                						
            --Arthritis
            MAX(case when LEFT(c.diag_cd, 3) IN ('m05', 'm06', 'm32', 'm33', 'm34') OR 
            LEFT(c.diag_cd, 4) IN ('m315', 'm351', 'm353', 'm360') then 1 else 0 end) as arth,
                                				
            --Cerebrovascular disease
            MAX(case when LEFT(c.diag_cd, 3) IN ('g45', 'g46', 'i60', 'i61', 'i62', 'i63', 'i64', 'i65', 'i66', 'i67', 'i68', 'i69') OR 
            LEFT(c.diag_cd, 4) = 'h340' then 1 else 0 end) as cerebrovasc,
                                                
            --Diabetes mellitus
            MAX(case when LEFT(c.diag_cd, 4) IN ('e100', 'e101', 'e106', 'e108', 'e109', 'e110', 'e111', 'e116', 'e118', 'e119', 'e120', 'e121', 'e126', 'e128', 'e129', 'e130',
									'e131', 'e136', '138', 'e139', 'e140', 'e141', 'e146', 'e148', 'e149') then 1 else 0 end) as diab,
                                                
            --Diabetes mellitus w/ kidney complications
            MAX(case when LEFT(c.diag_cd, 4) IN ('e102', 'e103' 'e104', 'e105', 'e107', 'e112', 'e113', 'e114', 'e115', 'e117', 'e122', 'e123', 'e124', 'e125', 'e127', 'e132',
									'e133', 'e134', 'e135', 'e137', 'e142', 'e143', 'e144', 'e145', 'e147') then 1 else 0 end) as diabcx,
                                                 
            --Liver disease
            MAX(case when LEFT(c.diag_cd, 4) IN ('k700', 'k701', 'k702', 'k703', 'k709', 'k713', 'k714', 'k715', 'k717', 'k760', 'k762', 'k763', 'k764', 'k768', 'k769', 'z944')
                OR LEFT(c.diag_cd, 3) IN ('b18', 'k73', 'k74') then 1 else 0 end) as liver,
                                                
            --Liver disease w/ kidney complications
            MAX(case when LEFT(c.diag_cd, 4) IN ('i850', 'i859', 'i864', 'i982', 'k704', 'k711', 'k721', 'k729', 'k765', 'k766', 'k767') then 1 else 0 end) as livercx,
                                                
            --Malignant neoplasm
            MAX(case when LEFT(c.diag_cd, 3) IN ('c77', 'c78', 'c79', 'c80') then 1 else 0 end) as maligneo,

            --Paraplegia
            MAX(case when LEFT(c.diag_cd, 4) IN ('g041', 'g114', 'g801', 'g830', 'g831', 'g832', 'g833', 'g834', 'g839') OR 
            LEFT(c.diag_cd, 3) IN ('g81', 'g82') then 1 else 0 end) as parapleg,

            --Perivascular disease
            MAX(case when LEFT(c.diag_cd, 4) IN ('i731', 'i738', 'i739', 'i771', 'i790', 'i792', 'k551', 'k558', 'k559', 'z958', 'z959') OR 
            LEFT(c.diag_cd, 3) IN ('i70', 'i71') then 1 else 0 end) as perivasc,
	
            --Ulcers
            MAX(case when LEFT(c.diag_cd, 3) IN ('k25', 'k26', 'k27', 'k28') then 1 else 0 end) as ulcer,

            --Renal failure
            MAX(case when LEFT(c.diag_cd, 4) IN ('i120', 'i131', 'n032', 'n033', 'n034', 'n035', 'n036', 'n037', 'n052', 'n053', 'n054', 'n055', 'n056',
	         'n057', 'n250', 'z490', 'z491', 'z492', 'z940', 'z992') OR LEFT(c.diag_cd, 3) IN ('n18', 'n19') then 1 else 0 end) as renalfail,

            --Tumor
            MAX(case when LEFT(c.diag_cd, 3) IN ('c00', 'c01', 'c02', 'c03', 'c04', 'c05', 'c06', 'c07', 'c08', 'c09', 'c10', 'c11', 'c12', 'c13',
				'c14', 'c15', 'c16', 'c17', 'c18', 'c19', 'c20', 'c21', 'c22', 'c23', 'c24', 'c25', 'c26', 'c30', 'c31', 'c32', 'c33', 'c34', 'c37', 'c38', 'c39', 'c40', 'c41',
				'c43', 'c45', 'c46', 'c47', 'c48', 'c49', 'c50', 'c51', 'c52', 'c53', 'c54', 'c55', 'c56', 'c57', 'c58', 'c60', 'c61', 'c62', 'c63', 'c64', 'c65', 'c66',
				'c67', 'c68', 'c69', 'c70', 'c71', 'c72', 'c73', 'c74', 'c75', 'c76', 'c81', 'c82', 'c83', 'c84', 'c85', 'c88', 'c90', 'c91', 'c92', 'c93', 'c94', 'c95', 'c96',
				'c97') then 1 else 0 end) as tumor
                                               
            FROM {cohort_tbl_nm} a
                                        
            LEFT JOIN udwbasesecureview1.ADJD_MCE_SRVC b
            ON a.MBR_PTY_ID = b.MBR_PTY_ID
                                        
            LEFT JOIN udwbasesecureview1.ADJD_MCE_DIAG c
            ON b.UDW_MED_CLM_ID = c.UDW_MED_CLM_ID
            AND b.orig_src_sys_cd = c.orig_src_sys_cd
            and b.udw_adjd_mce_id = c.udw_adjd_mce_id
            --and b.proc_dt = c.proc_dt
                                            
                                        
            WHERE --b.proc_dt BETWEEN '2020-11-30' AND '2022-02-31'
            b.srvc_strt_dt BETWEEN ADD_MONTHS(a.er_discharge, -12) AND (a.er_discharge - INTERVAL '1' DAY)
            AND b.orig_src_sys_cd IN ('COS', 'NIC', 'CSP', 'APF', 'NDB', 'FRV', 'OXF')
            AND b.src_row_sts_cd = 'A' --not deleted in source system
            AND b.src_row_expir_dt = '9999-12-31'
                                                        
            GROUP BY a.alt_id_val, a.er_discharge
            
            )
        
            WITH DATA
            ON COMMIT PRESERVE ROWS;
        
        '''
        
        return sql
        
        
    
    def feature_tbl(self, cohort_tbl_nm, stars_analysis, tbls = None):
        
        select_statement = ''
        join_statement = ''
        
        # No way to automatically exclude index cols, so do that here 
        if tbls is not None:
            
            for i in tbls:
                join_statement += f'''
                                    LEFT JOIN {i}
                                    ON a.er_discharge = {i}.er_discharge
                                    AND a.alt_id_val = {i}.alt_id_val
                                    '''
                tbl_cols = pd.read_sql(f'SELECT * FROM {i} SAMPLE 1;', self.con)
                non_index_cols = [col for col in tbl_cols.columns if col.lower() not in ['alt_id_val', 'er_discharge', 'mbr_pty_id']]  
                
                for j in non_index_cols:
                    select_statement += f', {i}.{j}'
                 
        
        if stars_analysis:
            
            where_statement = ''
            output_tbl_nm = f'{self.group}_feature_tbl_stars'
            
            
        
        else:
            
            where_statement = f'''WHERE a.er_discharge <= (CURRENT_DATE() - INTERVAL '{self.days_in_outcome_period + 30}' DAY)''' # subtract another 30 days for the ~4week claims lag
            output_tbl_nm = f'{self.group}_feature_tbl_utils'
        
        
        
        sql = f'''CREATE VOLATILE TABLE {output_tbl_nm} AS 
            
            (SELECT a.alt_id_val, a.er_discharge, (CURRENT_DATE() - INTERVAL '{self.days_in_outcome_period + 30}' DAY) as obs_period_end_date  {select_statement}
             FROM {cohort_tbl_nm} a
             
             {join_statement}
             
             
             {where_statement} --Select only discharges that occurred w/ enough time to evaluate; additional -1 is for the lag in having FULL claims
             
                )
            
            WITH DATA
            ON COMMIT PRESERVE ROWS;
            
            
            '''
            
        return sql
        
        
    
    # def feature_tbl(self, cohort_tbl_nm, filter_to_obs_period = False, util_tbl_nm = None, demo_tbl_nm = None, fu_rate_tbl_nm = None, fu_tbl_nm = None):
    #     '''
        

    #     Parameters
    #     ----------
    #     cohort_tbl_nm : string
    #         Name of volatile table containing cohort MBI's and index ER discharges.
    #     filter_to_obs_period : boolean, optional
    #         Should the ER discharges be filtered to the observation period? If the analysis is on utilization (affordability analysis), this should be set to True so
    #         that the only discharges returned are in the observation period. If the analysis is on Hedis follow-up, then follow-up for all discharges to date should be evaluated.
    #         The default is False.
    #     util_tbl_nm : string, optional
    #         The name of the volatile table that contains the utilization counts (IP, ER) for the members in the cohort table. The default is None.
    #     demo_tbl_nm : string, optional
    #         The name of the volatile table that contains the demographics (age, gender) for the members in the cohort table. The default is None.
    #     fu_rate_tbl_nm : string, optional
    #         The name of the volatile table that contains the follow-up rates for the covariate window and pre-index study period. The default is None.
    #     fu_tbl_nm : string, optional
    #         The name of the volatile table that contains the follow-up flag for the index ER discharges in the cohort table. The default is None.

    #     Returns
    #     -------
    #     sql : TYPE
    #         Query to create the feature table for propensity-score matching for the instance's cohort.

    #     '''
        
    #     if util_tbl_nm is None:
            
    #         util_tbl_nm = f'{self.group}_utils'
            
    #     if demo_tbl_nm is None:
            
    #         demo_tbl_nm = f'{self.group}_demographics'
            
    #     if fu_rate_tbl_nm is None:
            
    #         fu_rate_tbl_nm = f'{self.group}_fu_rates'
            
    #     if fu_tbl_nm is None:
            
    #         fu_tbl_nm = f'{self.group}_er_follow_ups'
            
    #     if filter_to_obs_period:
            
    #         where_statement = f'WHERE a.er_discharge <= ADD_MONTHS(CURRENT_DATE(), -{self.months_in_eval_period}-1)'
        
    #     else:
            
    #         where_statement = ''
        
        
    #     sql = f'''CREATE VOLATILE TABLE {self.group}_feature_tbl AS 
            
    #         (SELECT DISTINCT a.alt_id_val, a.er_discharge, c.er_trt, c.ip_trt, 
    #          /*b.ami, b.afib, b.alzh, b.ckd, b.copd, b.depr, b.heart, b.stroke,*/ 
    #          c.er_12m, c.ip_12m, d.age, d.gender, e.fu_rate_12m, e.fu_rate_study, 
    #          CASE WHEN f.stars_eligible_er_follow_up IS NULL THEN 0 ELSE f.stars_eligible_er_follow_up END AS hedis_follow_up,
    #          {self.months_in_eval_period} AS months_in_outcome_period
    #          FROM {cohort_tbl_nm} a
             
    #           /*LEFT JOIN {self.group}_fmc b
    #           ON a.alt_id_val = b.alt_id_val
    #           AND a.er_discharge = b.er_discharge*/
             
    #          LEFT JOIN {util_tbl_nm} c
    #          ON a.alt_id_val = c.alt_id_val
    #          AND a.er_discharge = c.er_discharge
             
    #          LEFT JOIN {demo_tbl_nm} d
    #          ON a.alt_id_val = d.alt_id_val
    #          AND a.er_discharge = d.er_discharge
             
    #          LEFT JOIN {fu_rate_tbl_nm} e
    #          ON a.alt_id_val = e.alt_id_val
    #          AND a.er_discharge = e.er_discharge
             
    #          LEFT JOIN {fu_tbl_nm} f
    #          ON a.alt_id_val = f.alt_id_val
    #          AND a.er_discharge = f.er_discharge
             
    #          {where_statement} --Select only discharges that occurred w/ enough time to evaluate; additional -1 is for the lag in having FULL claims
             
    #             )
            
    #         WITH DATA
    #         ON COMMIT PRESERVE ROWS;
            
            
    #         '''
            
    #     return sql
