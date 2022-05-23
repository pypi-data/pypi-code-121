import time
import csv

def load_discharge_data(cur):
    '''
    Loads Truepill discharge data through end of Feb 2022 into a Teradata volatile table named 'stellar_discharges'.
    

    Parameters
    ----------
    cur : teradatasql cursor connected to UDW
        Created from con.cursor()

    Returns
    -------
    None.

    '''
    
    # Load Stellar discharge data into a volatile table
    with open('data/emr_02_28_22_tidy.csv', newline='') as f:
        cur.execute('''CREATE VOLATILE TABLE stellar_discharges
    (
    member_id VARCHAR(100),
    ed_facility VARCHAR(250),
    pilot_week VARCHAR(20),
    discharge_dt DATE FORMAT 'YYYY-MM-DD',
    due_dt DATE FORMAT 'YYYY-MM-DD',
    ACO VARCHAR(50),
    latest_detail VARCHAR(150),
    status VARCHAR(150),
    member_type VARCHAR(20),
    care_coordination VARCHAR(50),
    multiple_discharge_patient VARCHAR(100)
    )
    ON COMMIT PRESERVE ROWS;''')
        
        cur.execute('INSERT INTO stellar_discharges (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', [row for row in csv.reader(f)])
        
def load_control_pool(cur, output_tbl_nm):
    '''
    Loads FMC and ImpactPro scores from data extract sent by Yuhong Tian.
    Stars data/metrics are generated from a pre-defined SQL pipeline managed by the SDM team and reside on the stars schema.
    Because it'd be quite complex to learn all the nuances of the stars tables ourselves, Yuhong (stars data scientist) pulled for us.

    Parameters
    ----------
    cur : teradatasql cursor connected to UDW
        Created from con.cursor()
    output_tbl_nm : string
        Name the volatile table will be given.

    Returns
    -------
    None.

    '''
        
    start = time.time()
    # Load UHC control data into a volatile table
    with open('data/control_pool/hedis_eligible_control_pool.csv', newline='') as f:
        cur.execute(f'''CREATE VOLATILE TABLE {output_tbl_nm}
    (
    alt_id_val VARCHAR(100),
    Pred_FMC_denom BYTEINT,
    FMCs_denom_12m BYTEINT,
    afib BYTEINT,
    alzh BYTEINT,
    ami BYTEINT,
    ckd BYTEINT,
    copd BYTEINT,
    depr BYTEINT,
    heart BYTEINT,
    stroke BYTEINT,
    total_FMC_conditions BYTEINT,
    index_month_FMC BYTEINT,
    index_year_FMC SMALLINT
    )
    PRIMARY INDEX (alt_id_val)
    ON COMMIT PRESERVE ROWS;''')
        
        cur.execute(f'INSERT INTO {output_tbl_nm} (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', [row for row in csv.reader(f)])
        
    end = time.time()
    print('Time to load data was: {} min.'.format(round((end - start)/60, 1)))