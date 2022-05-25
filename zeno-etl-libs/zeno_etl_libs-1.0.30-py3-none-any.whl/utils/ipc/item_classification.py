'''classification of a drug at store: ABC-XYZ '''
import numpy as np


def abc_xyz_classification(cal_drug_sales_monthly, logger=None):
    cut_cov = (0.3, 1.0)
    cut_sales = (4, 30)

    # taking last 12 months data only for classification
    n = 12
    prev_n_month_dt = cal_drug_sales_monthly[
        ['month_begin_dt']].drop_duplicates().\
        sort_values('month_begin_dt', ascending=False)['month_begin_dt'].\
        head(n)
    cal_drug_sales_classification = cal_drug_sales_monthly[
        cal_drug_sales_monthly.month_begin_dt.isin(prev_n_month_dt)]
    print(len(cal_drug_sales_classification))

    # monthly averages for classification
    drug_class = cal_drug_sales_classification.\
        groupby('drug_id').agg({'net_sales_quantity': [np.mean, np.std]}).\
        reset_index()
    drug_class.columns = ['drug_id', 'net_sales', 'sales_std_dev']
    drug_class = drug_class[drug_class['net_sales'] >= 0]
    drug_class['sales_cov'] = (
        drug_class['sales_std_dev'] /
        drug_class['net_sales'])

    # assertion error to check all sales positive
    assert len(drug_class[
        drug_class['net_sales'] < 0]) == 0

    # handling infs
    drug_class['sales_cov'] = np.where(
        drug_class['sales_cov'] == np.inf,
        drug_class['sales_std_dev'],
        drug_class['sales_cov']
    )

    # assigning buckets
    drug_class['bucket_abc'] = np.select(
        [(drug_class['net_sales'] <= cut_sales[0]),
         (drug_class['net_sales'] > cut_sales[0]) &
         (drug_class['net_sales'] <= cut_sales[1]),
         (drug_class['net_sales'] > cut_sales[1])],
        ['C', 'B', 'A'],
        default='NA')
    drug_class['bucket_xyz'] = np.select(
        [drug_class['sales_cov'] <= cut_cov[0],
         (drug_class['sales_cov'] > cut_cov[0]) &
         (drug_class['sales_cov'] <= cut_cov[1]),
         drug_class['sales_cov'] > cut_cov[1]],
        ['X', 'Y', 'Z'],
        default='NA')
    print(drug_class.drug_id.nunique())

    # summary
    bucket_sales = drug_class.groupby(
        ['bucket_abc', 'bucket_xyz']).agg(
            {'drug_id': 'count', 'net_sales': ['sum', 'mean'],
             'sales_cov': 'mean'}).reset_index()
    bucket_sales.columns = ['bucket_abc', 'bucket_xyz', 'drug_id', 'net_sales',
                            'avg_sales_per_drug', 'sales_cov']
    bucket_sales['net_sales_frac'] = round(
        100*bucket_sales['net_sales']/drug_class.net_sales.sum(), 2)
    bucket_sales['drug_frac'] = round(
        100*bucket_sales['drug_id']/drug_class.drug_id.nunique(), 2)
    bucket_sales['avg_sales_per_drug'] = (
        bucket_sales['net_sales']/bucket_sales['drug_id'])
    print(bucket_sales)

    return drug_class, bucket_sales
