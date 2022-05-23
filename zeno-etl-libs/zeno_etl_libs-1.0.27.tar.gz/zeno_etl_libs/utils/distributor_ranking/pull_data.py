Q_FEATURES = """
select
    sb.id as "short-book-1-id" ,
	sb."ordered-distributor-id" as "short-book-distributor-id",
	sb."drug-id",
	coalesce(sb.quantity, 0) as "original-order",
	sb."required-quantity" as "final-unfulfilled",
	sb."created-at" as "original-created-at",
	sb."re-ordered-at" as "original-created-at-2",
	sbi."quantity" as "partial-quantity",
	i.id as "invoice-id",
	i."dc-id" as "partial-dc-id",
	i."distributor-id" as "partial-distributor-id",
	i."created-at" as "partial-created-at",
	i."approved-at" as "partial-invoiced-at",
	ii.id as "invoice-item-id",
	ii."drug-id" as "invoice-items-drug-id",
	inv.id as "inventory-id",
	inv."invoice-item-id" as "inv-invoice-item-id",
	inv."purchase-rate" as "distributor-rate",
	inv."selling-rate",
	d."drug-name",
	d.type as "drug_type",
	sdm."forward-dc-id",
	s.name as "dc-name"
from
	"{read_schema}"."short-book-1" sb
left join "{read_schema}"."short-book-invoices" sbi on
	sbi."short-book-id" = sb.id
left join "{read_schema}".invoices i on
	sbi."invoice-id" = i.id
left join "{read_schema}"."short-book-invoice-items" sbii on
	sb.id = sbii."short-book-id"
left join "{read_schema}"."invoice-items" ii on
	ii.id = sbii."invoice-item-id"
left join "{read_schema}"."invoice-items-1" ii1 on
	ii1."invoice-item-reference" = ii.id
left join "{read_schema}"."inventory-1" inv on
	inv."invoice-item-id" = ii1.id
left join "{read_schema}".drugs d on
	sb."drug-id" = d.id
left join "{read_schema}".distributors dis on
	dis.id = sb."ordered-distributor-id"
left join "{read_schema}"."store-dc-mapping" sdm on
	sb."store-id" = sdm."store-id"
	and dis.type = sdm."drug-type"
left join "{read_schema}".stores s on
	i."dc-id" = s.id
where
	DATEDIFF(day, date(sb."created-at"), current_date) <= {0} 
	and DATEDIFF(day, date(sb."created-at"), current_date) >= 7
	and sb."quantity" > 0
	and sb."ordered-distributor-id" != 76
	and sb."ordered-distributor-id" != 5000
	and sb."ordered-distributor-id" != 8105
	and i."distributor-id" != 8105
	and sb.status != 'deleted'
"""

Q_FEATURES_FRANCHISEE = """
select
    sb.id as "short-book-1-id" ,
    sb."ordered-distributor-id" as "short-book-distributor-id",
    sb."store-id",
    ss."franchisee-id",
    sb."drug-id",
    coalesce(sb.quantity, 0) as "original-order",
    sb."required-quantity" as "final-unfulfilled",
    sb."created-at" as "original-created-at",
    sb."re-ordered-at" as "original-created-at-2",
	sbi."quantity" as "partial-quantity",
	i.id as "invoice-id",
	i."distributor-id" as "partial-distributor-id",
	i."created-at" as "partial-created-at",
	i."approved-at" as "partial-invoiced-at",
	ii.id as "invoice-item-id",
	ii."drug-id" as "invoice-items-drug-id",
	inv.id as "inventory-id",
	inv."invoice-item-id" as "inv-invoice-item-id",
	inv."purchase-rate" as "distributor-rate",
	inv."selling-rate",
	d."drug-name",
	d.type as "drug_type",
    ss."name" as "store-name"
from
	"{read_schema}"."short-book-1" sb
left join "{read_schema}"."short-book-invoices" sbi on
	sbi."short-book-id" = sb.id
left join "{read_schema}".invoices i on
	sbi."invoice-id" = i.id
left join "{read_schema}"."short-book-invoice-items" sbii on
	sb.id = sbii."short-book-id"
left join "{read_schema}"."invoice-items" ii on
	ii.id = sbii."invoice-item-id"
left join "{read_schema}"."invoice-items-1" ii1 on
	ii1."invoice-item-reference" = ii.id
left join "{read_schema}"."inventory-1" inv on
	inv."invoice-item-id" = ii1.id
left join "{read_schema}".drugs d on
	sb."drug-id" = d.id
left join "{read_schema}".distributors dis on
	dis.id = sb."ordered-distributor-id"
left join "{read_schema}".stores s on
    i."dc-id" = s.id
left join "{read_schema}".stores ss on
    sb."store-id" = ss.id 
where
    DATEDIFF(day, date(sb."created-at"), current_date) <= {0} 
	and DATEDIFF(day, date(sb."created-at"), current_date) >= 7
	and sb."quantity" > 0
	and sb."ordered-distributor-id" != 76
	and sb."ordered-distributor-id" != 5000
	and sb."ordered-distributor-id" != 8105
	and i."distributor-id" != 8105
    and sb.status != 'deleted' 
    and ss."franchisee-id" != 1
"""

Q_DISTRIBUTORS = """
select id as "partial-distributor-id", 
name as "partial-distributor-name", 
type as "partial-distributor-type" 
from "{read_schema}".distributors
"""


def pull_data(time_interval, db, read_schema):
    ''' time interval is the buffer cutoff after which data isn't taken. 7 days in our case'''

    df_features = db.get_df(Q_FEATURES.format(time_interval,
                                              read_schema=read_schema))
    df_features.columns = [c.replace('-', '_') for c in df_features.columns]

    df_distributors = db.get_df(Q_DISTRIBUTORS.format(read_schema=read_schema))
    df_distributors.columns = [c.replace('-', '_') for c in df_distributors.columns]

    # ensure data types
    df_features["distributor_rate"] = df_features["distributor_rate"].astype(float)
    df_features["selling_rate"] = df_features["selling_rate"].astype(float)

    return df_features, df_distributors


def pull_data_franchisee(time_interval, db, read_schema):
    ''' time interval is the buffer cutoff after which data isn't taken. 7 days in our case'''

    df_features = db.get_df(Q_FEATURES_FRANCHISEE.format(time_interval,
                                                         read_schema=read_schema))
    df_features.columns = [c.replace('-', '_') for c in df_features.columns]

    df_distributors = db.get_df(Q_DISTRIBUTORS.format(read_schema=read_schema))
    df_distributors.columns = [c.replace('-', '_') for c in df_distributors.columns]

    # ensure data types
    df_features["distributor_rate"] = df_features["distributor_rate"].astype(float)
    df_features["selling_rate"] = df_features["selling_rate"].astype(float)

    return df_features, df_distributors

