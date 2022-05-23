import argparse
import os
import sys

sys.path.append('../../../..')

from zeno_etl_libs.db.db import DB


def main(db):
    table_name = "retention-master"

    db.execute(query="begin ;")
    db.execute(query=f""" delete from "prod2-generico"."{table_name}"; """)
    query = f"""
    insert
        into
        "prod2-generico"."{table_name}" ( "id",
        "created-by",
        "created-at",
        "updated-by",
        "updated-at",
        "patient-id",
        "store-id",
        "doctor-id",
        "promo-code-id",
        "promo-discount",
        "payment-method",
        "redeemed-points",
        "bill-date",
        "bill-year",
        "bill-month",
        "bill-day",
        "bill-month-diff",
        "doctor-name",
        "total-spend",
        "spend-generic",
        "spend-goodaid",
        "spend-ethical",
        "spend-others-type",
        "num-drugs",
        "quantity-generic",
        "quantity-goodaid",
        "quantity-ethical",
        "quantity-chronic",
        "quantity-repeatable",
        "quantity-others-type",
        "is-generic",
        "is-goodaid",
        "is-ethical",
        "is-chronic",
        "is-repeatable",
        "is-others-type",
        "is-rx",
        "total-quantity",
        "zippin-serial",
        "total-mrp-value",
        "pr-flag",
        "hd-flag",
        "ecom-flag",
        "promo-flag",
        "digital-payment-flag",
        "total-purchase-rate-value",
        "total-ptr-value",
        "month-bill-rank",
        "min-bill-date-in-month",
        "store-id-month",
        "normalized-date",
        "p-first-bill-date",
        "p-last-bill-date",
        "p-average-bill-value",
        "p-total-quantity",
        "p-quantity-generic",
        "p-quantity-chronic",
        "p-quantity-ethical",
        "p-quantity-repeatable",
        "p-quantity-goodaid",
        "p-quantity-rx",
        "p-quantity-others-type",
        "p-number-of-bills",
        "p-hd-bills",
        "p-is-repeatable",
        "p-is-generic",
        "p-is-chronic",
        "p-is-goodaid",
        "p-is-ethical",
        "p-is-rx",
        "p-is-others-type",
        "p-hd-flag",
        "p-ecom-flag",
        "p-pr-flag",
        "p-total-spend",
        "p-spend-generic",
        "p-promo-min-bill-date",
        "p-hd-min-bill-date",
        "p-ecom-min-bill-date",
        "p-pr-min-bill-date",
        "p-generic-min-bill-date",
        "p-goodaid-min-bill-date",
        "p-ethical-min-bill-date",
        "p-chronic-min-bill-date",
        "p-repeatable-min-bill-date",
        "p-others-type-min-bill-date",
        "p-rx-min-bill-date",
        "p-digital-payment-min-bill-date",
        "p-first-bill-id",
        "p-last-bill-id",
        "p-digital-payment-flag",
        "p-total-mrp-value",
        "is-nps",
        "latest-nps-rating",
        "latest-nps-rating-comment",
        "latest-nps-rating-store-id",
        "latest-nps-rating-store-name",
        "latest-nps-rating-date",
        "referred-count",
        "primary-store-id",
        "p-num-drugs",
        "p-primary-disease",
        "recency-customer-days",
        "system-age-days",
        "avg-purchase-interval",
        "std-purchase-interval",
        "quantity-generic-pc",
        "quantity-chronic-pc",
        "quantity-ethical-pc",
        "quantity-repeatable-pc",
        "quantity-goodaid-pc",
        "quantity-others-type-pc",
        "spend-generic-pc",
        "previous-bill-date",
        "previous-store-id",
        "value-segment-calculation-date",
        "value-segment",
        "behaviour-segment-calculation-date",
        "behaviour-segment",
        "promo-code",
        "promo-code-type",
        "promo-eligibility",
        "promo-discount-type",
        "promo-min-purchase",
        "campaign-id",
        "campaign-name",
        "store",
        "line-manager",
        "abo",
        "store-manager",
        "store-type",
        "store-opened-at",
        "date-diff",
        "month-diff",
        "latitude",
        "longitude",
        "store-contact-1",
        "store-contact-2",
        "store-address",
        "store-city",
        "store-b2b",
        "line",
        "landmark",
        "store-group-id",
        "franchisee-id",
        "franchisee-name",
        "old-new",
        "bill-quarter",
        "previous-normalized-date",
        "cum-spend",
        "cum-nob",
        "cum-abv",
        "prev-cum-spend",
        "prev-cum-nob",
        "prev-cum-abv",
        "acquired" ,
        "old-new-static")
    select
        bm."id",
        bm."created-by" ,
        bm."created-at" ,
        'etl-automation',
        bm."updated-at" ,
        bm."patient-id",
        bm."store-id",
        bm."doctor-id",
        bm."promo-code-id",
        bm."promo-discount",
        bm."payment-method",
        bm."redeemed-points",
        bm."bill-date",
        bm."bill-year",
        bm."bill-month",
        bm."bill-day",
        bm."month-diff" as "bill-month-diff",
        bm."doctor-name",
        bm."total-spend",
        bm."spend-generic",
        bm."spend-goodaid",
        bm."spend-ethical",
        bm."spend-others-type",
        bm."num-drugs",
        bm."quantity-generic",
        bm."quantity-goodaid",
        bm."quantity-ethical",
        bm."quantity-chronic",
        bm."quantity-repeatable",
        bm."quantity-others-type",
        bm."is-generic",
        bm."is-goodaid",
        bm."is-ethical",
        bm."is-chronic",
        bm."is-repeatable",
        bm."is-others-type",
        bm."is-rx",
        bm."total-quantity",
        bm."zippin-serial",
        bm."total-mrp-value",
        bm."pr-flag",
        bm."hd-flag",
        bm."ecom-flag",
        bm."promo-flag",
        bm."digital-payment-flag",
        bm."total-purchase-rate-value",
        bm."total-ptr-value",
        bm."month-bill-rank",
        bm."min-bill-date-in-month",
        bm."store-id-month",
        bm."normalized-date",
        pm."first-bill-date" as "p-first-bill-date",
        pm."last-bill-date" as "p-last-bill-date",
        pm."average-bill-value" as "p-average-bill-value",
        pm."total-quantity" as "p-total-quantity",
        pm."quantity-generic" as "p-quantity-generic",
        pm."quantity-chronic" as "p-quantity-chronic",
        pm."quantity-ethical" as "p-quantity-ethical",
        pm."quantity-repeatable" as "p-quantity-repeatable",
        pm."quantity-goodaid" as "p-quantity-goodaid",
        pm."quantity-rx" as "p-quantity-rx",
        pm."quantity-others-type" as "p-quantity-others-type",
        pm."number-of-bills" as "p-number-of-bills",
        pm."hd-bills" as "p-hd-bills",
        pm."is-repeatable" as "p-is-repeatable",
        pm."is-generic" as "p-is-generic",
        pm."is-chronic" as "p-is-chronic",
        pm."is-goodaid" as "p-is-goodaid",
        pm."is-ethical" as "p-is-ethical",
        pm."is-rx" as "p-is-rx",
        pm."is-others-type" as "p-is-others-type",
        pm."hd-flag" as "p-hd-flag",
        pm."ecom-flag" as "p-ecom-flag",
        pm."pr-flag" as "p-pr-flag",
        pm."total-spend" as "p-total-spend",
        pm."spend-generic" as "p-spend-generic",
        pm."promo-min-bill-date" as "p-promo-min-bill-date",
        pm."hd-min-bill-date" as "p-hd-min-bill-date",
        pm."ecom-min-bill-date" as "p-ecom-min-bill-date",
        pm."pr-min-bill-date" as "p-pr-min-bill-date",
        pm."generic-min-bill-date" as "p-generic-min-bill-date",
        pm."goodaid-min-bill-date" as "p-goodaid-min-bill-date",
        pm."ethical-min-bill-date" as "p-ethical-min-bill-date",
        pm."chronic-min-bill-date" as "p-chronic-min-bill-date",
        pm."repeatable-min-bill-date" as "p-repeatable-min-bill-date",
        pm."others-type-min-bill-date" as "p-others-type-min-bill-date",
        pm."rx-min-bill-date" as "p-rx-min-bill-date",
        pm."digital-payment-min-bill-date" as "p-digital-payment-min-bill-date",
        pm."first-bill-id" as "p-first-bill-id",
        pm."last-bill-id" as "p-last-bill-id",
        pm."digital-payment-flag" as "p-digital-payment-flag",
        pm."total-mrp-value" as "p-total-mrp-value",
        pm."is-nps",
        pm."latest-nps-rating",
        pm."latest-nps-rating-comment",
        pm."latest-nps-rating-store-id",
        pm."latest-nps-rating-store-name",
        pm."latest-nps-rating-date",
        pm."referred-count",
        pm."primary-store-id",
        pm."num-drugs" as "p-num-drugs",
        pm."primary-disease" as "p-primary-disease",
        pm."recency-customer-days",
        pm."system-age-days",
        pm."avg-purchase-interval",
        pm."std-purchase-interval",
        pm."quantity-generic-pc",
        pm."quantity-chronic-pc",
        pm."quantity-ethical-pc",
        pm."quantity-repeatable-pc",
        pm."quantity-goodaid-pc",
        pm."quantity-others-type-pc",
        pm."spend-generic-pc",
        lead(bm."bill-date" , 1)
          OVER( 
          PARTITION BY bm."patient-id"
          ORDER BY bm."created-at" desc) AS "previous-bill-date",
        lead(bm."store-id" , 1)
          OVER( 
          PARTITION BY bm."patient-id"
          ORDER BY bm."created-at" desc) AS "previous-store-id",
        cvs."segment-calculation-date" as "value-segment-calculation-date",
        cvs."value-segment",
        cbs."segment-calculation-date" as "behaviour-segment-calculation-date",
        cbs."behaviour-segment",
        p."promo-code",
        p."promo-code-type",
        p."promo-eligibility",
        p."promo-discount-type",
        p."promo-min-purchase",
        p."campaign-id",
        p."campaign-name",
        sm."store",
        sm."line-manager",
        sm."abo",
        sm."store-manager",
        sm."store-type",
        sm."opened-at" as "store-opened-at",
        sm."date-diff",
        sm."month-diff",
        sm."latitude",
        sm."longitude",
        sm."store-contact-1",
        sm."store-contact-2",
        sm."store-address",
        sm."city" as "store-city",
        sm."store-b2b",
        sm."line",
        sm."landmark",
        sm."store-group-id",
        sm."franchisee-id",
        sm."franchisee-name",
        case 
            when (12 * (extract (year from bm."created-at") - extract (year from pm."first-bill-date")) + (extract (month from bm."created-at") - extract (month from pm."first-bill-date")))>= 1 then 'old'
            else 'new'
        end as "old-new",
        extract('year' from bm."bill-date")||'Q'||extract('quarter' from bm."bill-date") as "bill-quarter",
        ppnd."previous-normalized-date",
        sum(bm."total-spend") over( partition by bm."patient-id"
        order by
        bm."created-at" asc rows unbounded preceding) as "cum-spend",
        count(bm."id") over( partition by bm."patient-id"
        order by
        bm."created-at" asc rows unbounded preceding) as "cum-nob",
        sum(bm."total-spend") over( partition by bm."patient-id"
        order by
        bm."created-at" asc rows unbounded preceding)/ count(bm."id") over( partition by bm."patient-id"
        order by
        bm."created-at" asc rows unbounded preceding) as "cum-abv",
        (sum(bm."total-spend") over( partition by bm."patient-id"
        order by
        bm."created-at" asc rows unbounded preceding))-bm."total-spend" as "prev-cum-spend",
        (count(bm."id") over( partition by bm."patient-id"
        order by
        bm."created-at" asc rows unbounded preceding))-1 as "prev-cum-nob",
        sum(bm."total-spend") over( partition by bm."patient-id"
        order by
        bm."created-at" asc rows between unbounded preceding and 1 preceding)/ count(bm."id") over( partition by bm."patient-id"
        order by
        bm."created-at" asc rows between unbounded preceding and 1 preceding) as "prev-cum-abv",
        sm."acquired" ,
        sm."old-new-static"
    from
        "prod2-generico"."bills-1-metadata" bm
    left join "prod2-generico"."patients-metadata-2" pm on
        pm.id = bm."patient-id"
    left join "prod2-generico"."customer-value-segment" cvs on
        bm."patient-id" = cvs."patient-id"
        and bm."normalized-date" = cvs."segment-calculation-date"
    left join "prod2-generico"."customer-behaviour-segment" cbs on
        bm."patient-id" = cbs."patient-id"
        and bm."normalized-date" = cbs."segment-calculation-date"
    left join "prod2-generico".promo p on
        bm."promo-code-id" = p.id
    inner join "prod2-generico"."stores-master" sm on
        bm."store-id" = sm."id"
    inner join "prod2-generico"."patient-previous-normalized-date" ppnd on
        bm."patient-id" = ppnd."patient-id"
        and bm."normalized-date" = ppnd."normalized-date"
    """
    db.execute(query=query)

    """ committing the transaction """
    db.execute(query=" end; ")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="This is ETL script.")
    parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                        help="This is env(dev, stag, prod)")
    args, unknown = parser.parse_known_args()
    env = args.env
    os.environ['env'] = env

    print(f"env: {env}")
    rs_db = DB()
    rs_db.open_connection()

    """ For single transaction  """
    rs_db.connection.autocommit = False

    """ calling the main function """
    main(db=rs_db)

    # Closing the DB Connection
    rs_db.close_connection()
