max_bill_id = """
            select
                max("bill-id") as "bill-id-max"
            from
                "prod2-generico"."{}"
            """

max_return_id = """
            select
                max("return-item-id") as "return-item-id-max"
            from
                "prod2-generico"."{}"
            """

insert_sales_record = """
    insert
        into
        "prod2-generico"."{}" (
        "updated-by",
        "updated-at",
        "bill-id",
        "patient-id",
        "store-id",
        "inventory-id",
        "drug-id",
        "drug-name",
        "type",
        "category",
        "composition",
        "company",
        "company-id",
        "composition-master-id",
        "quantity",
        "created-at",
        "year-created-at",
        "month-created-at",
        "rate",
        "net-rate",
        "net-quantity",
        "revenue-value",
        "purchase-rate",
        "ptr",
        "mrp",
        "substitution-status",
        "created-by",
        "bill-flag",
        "old-new",
        "first-bill-date",
        "p-reference",
        "patient-category",
        "lp-flag",
        "min",
        "max",
        "safe-stock",
        "promo-code-id",
        "payment-method",
        "doctor-id",
        "code-type",
        "pc-type",
        "promo-code",
        "campaign",
        "pr-flag",
        "hd-flag",
        "ecom-flag",
        "substitution-status-g",
        "substitution-status-trend",
        "goodaid-availablity-flag",
        "cgst-rate",
        "cgst-amt",
        "cgst",
        "sgst-rate",
        "sgst-amt",
        "sgst",
        "tax-rate",
        "igst-rate",
        "igst-amt",
        "utgst-rate",
        "utgst-amt",
        "serial",
        "hsncode",
        "is-repeatable",
        "store-name",
        "store-manager",
        "line-manager",
        "abo",
        "city",
        "store-b2b",
        "store-month-diff",
        "store-opened-at",
        "franchisee-id",
        "franchisee-name",
        "cluster-id",
        "cluster-name",
        "return-item-id",
        "bill-item-id",
        "promo-discount",
        "type-at-selling",
        "category-at-selling",
        "created-date",
        "invoice-item-reference",
        "distributor-id",
        "distributor-name",
        "billed-at-return-ref",
        "return-reason",
        "drug-grade",
        "acquired" ,
        "old-new-static"
        )
    select
        'etl-automation' as "updated-by",
        convert_timezone('Asia/Calcutta', GETDATE()) as "updated-at",
        a."bill-id" as "bill-id",
        f."patient-id" as "patient-id",
        f."store-id" as "store-id",
        b."id" as "inventory-id" ,
        b."drug-id" as "drug-id",
        c."drug-name" as "drug-name",
        c."type",
        c."category",
        c."composition",
        c."company",
        c."company-id" as "company-id",
        c."composition-master-id" as "composition-master-id",
        a."quantity",
        f."created-at" as "created-at" ,
        extract(year from f."created-at") as "year-created-at",
        extract(month from f."created-at") as "month-created-at",
        a."rate",
        a."rate" as "net-rate",
        a."quantity" as "net-quantity",
        (a."rate" * a."quantity") as "revenue-value",
        b."purchase-rate" as "purchase-rate",
        b."ptr",
        b."mrp",
        s."substitution-status" as "substitution-status",
        f."created-by" as "created-by",
        'gross' as "bill-flag",
        case when (12 * (extract (year from f."created-at") - extract (year from pm."first-bill-date")) + (extract (month from f."created-at") - extract (month from pm."first-bill-date")))>= 1 then 'old' else 'new' end as "old-new",
        pm."first-bill-date" as "first-bill-date",
        p."reference" as "p-reference",
        p."patient-category" as "patient-category",
        b."franchisee-inventory" as "lp-flag",
        doi."min",
        doi."max" ,
        doi."safe-stock" as "safe-stock",
        f."promo-code-id" as "promo-code-id",
        f."payment-method" as "payment-method",
        f."doctor-id" as "doctor-id",
        pc."code-type" as "code-type" ,
        pc."type" as "pc-type",
        pc."promo-code" as "promo-code",
        ca."campaign",
        NVL(pso2."pr-flag", false),
        NVL(pso2."hd-flag", false),
        NVL(pso2."ecom-flag", false),
        case
            when (s."substitution-status" = 'substituted'
            and c."company-id" = 6984
            and f."created-at" >= mca."store-first-inv-date") then 'ga-substituted'
            when (s."substitution-status" = 'substituted'
            and mca."store-first-inv-date" is null ) then 'ga-not-available'
            else s."substitution-status"
        end as "substitution-status-g",
        case
            when (s."substitution-status" = 'substituted'
            and c."company-id" = 6984
            and f."created-at" >= mca."store-first-inv-date") then 'substituted'
            else s."substitution-status"
        end as "substitution-status-trend",
        case
            when (f."created-at" >= mca."system-first-inv-date") then 'available'
            else 'not-available'
        end as "goodaid-availablity-flag",
        a."cgst-rate" as "cgst-rate" ,
        a."cgst-amt" as "cgst-amt" ,
        a."cgst" ,
        a."sgst-rate" as "sgst-rate" ,
        a."sgst-amt" as "sgst-amt" ,
        a."sgst" ,
        (a."cgst-rate" + a."sgst-rate") as "tax-rate",
        a."igst-rate" as "igst-rate" ,
        a."igst-amt" as "igst-amt" ,
        a."utgst-rate" as "utgst-rate" ,
        a."utgst-amt" as "utgst-amt" ,
        f."serial" ,
        c."hsncode",
        c."is-repeatable" as "is-repeatable",
        msm.store as "store-name",
        msm."store-manager" ,
        msm."line-manager",
        msm.abo,
        msm.city,
        msm."store-b2b",
        msm."month-diff" as "store-month-diff",
        msm."opened-at" as "store-opened-at",
        msm."franchisee-id",
        msm."franchisee-name",
        msm."cluster-id",
        msm."cluster-name",
        NULL as "return-item-id",
        a.id as "bill-item-id",
        a."promo-discount" as "promo-discount",
        c."type" as "type-at-selling",
        c."category" as "category-at-selling",
        date(f."created-at") as "created-date",
        ii1."invoice-item-reference",
        i2."distributor-id",
        ds."name" as "distributor-name",
        f."created-at" as "billed-at-return-ref",
        NULL as "return-reason",
        doi."drug-grade",
        msm."acquired" ,
        msm."old-new-static"
    from
        "prod2-generico"."bills-1" f
    left join "prod2-generico"."bill-items-1" a on 
        f."id" = a."bill-id"
    left join "prod2-generico"."inventory-1" b on
        a."inventory-id" = b."id"
    left join "prod2-generico"."invoice-items-1" ii1 on
        b."invoice-item-id" = ii1.id
    left join "prod2-generico".invoices i2 on
        ii1."invoice-id" = i2.id
    left join "prod2-generico".distributors ds ON 
        i2."distributor-id" =ds.id 
    left join "prod2-generico"."drugs" c on
        c."id" = b."drug-id"
    left join "prod2-generico"."bill-items-substitutes" s on
        a."id" = s."bill-item-id"
    left join "prod2-generico"."patients-metadata" pm on
        f."patient-id" = pm."patient-id"
    left join "prod2-generico"."patients" p on
        f."patient-id" = p."id"
    left join "prod2-generico"."drug-order-info" doi on
        (doi."store-id" = f."store-id"
            and doi."drug-id" = b."drug-id")
    left join "prod2-generico"."promo-codes" pc on
        NVL(f."promo-code-id", 0) = pc."id"
    left join "prod2-generico"."campaigns" ca on
        NVL(pc."campaign-id", 0) = ca."id"
    left join "prod2-generico"."{}" as pso2 on
        a."bill-id" = pso2."id" 
    left join "prod2-generico"."composition-activation" mca on
        f."store-id" = mca."store-id"
        and c."composition-master-id" = mca."composition-master-id"
    inner join "prod2-generico"."{}" as msm on
        f."store-id" = msm."id"
    where 
        a."bill-id" > {}
    union all
    select
        'etl-automation' as "updated-by",
        convert_timezone('Asia/Calcutta',
            GETDATE()) as "updated-at",
        a."bill-id" as "bill-id",
        f."patient-id" as "patient-id",
        f."store-id" as "store-id",
        b."id" as "inventory-id" ,
        b."drug-id" as "drug-id",
        c."drug-name" as "drug-name",
        c."type",
        c."category",
        c."composition",
        c."company",
        c."company-id" as "company-id",
        c."composition-master-id" as "composition-master-id",
        (a."returned-quantity") as "quantity",
        f."returned-at" as "created-at",
        extract(year
    from
        f."returned-at") as "year-created-at",
        extract(month
    from
        f."returned-at") as "month-created-at",
        (a."rate") as "rate",
        (a."rate" *-1) as "net-rate",
        (a."returned-quantity" *-1) as "net-quantity",
        (a."rate" * a."returned-quantity" *-1) as "revenue-value",
        b."purchase-rate" as "purchase-rate",
        b."ptr",
        b."mrp",
        'return' as "substitution-status",
        f."processed-by" as "created-by",
        'return' as "bill-flag",
        case
            when (12 * (extract (year
        from
            f."returned-at") - extract (year
        from
            pm."first-bill-date")) + (extract (month
        from
            f."returned-at") - extract (month
        from
            pm."first-bill-date")))>= 1 then 'old'
            else 'new'
        end as "old-new",
        pm."first-bill-date" as "first-bill-date",
        p."reference" as "p-reference",
        p."patient-category" as "patient-category",
        b."franchisee-inventory" as "lp-flag",
        doi."min",
        doi."max" ,
        doi."safe-stock" as "safe-stock",
        b2."promo-code-id" as "promo-code-id",
        b2."payment-method" as "payment-method",
        b2."doctor-id" as "doctor-id",
        pc."code-type" as "code-type" ,
        pc."type" as "pc-type",
        pc."promo-code" as "promo-code",
        ca."campaign",
        NVL(pso2."pr-flag", false),
        NVL(pso2."hd-flag", false),
        NVL(pso2."ecom-flag", false),
        'return' as "substitution-status-g",
        'return' as "substitution-status-trend",
        case
            when (f."returned-at" >= mca."system-first-inv-date") then 'available'
            else 'not-available'
        end as "goodaid-availablity-flag",
        a."cgst-rate" as "cgst-rate" ,
        0 as "cgst-amt" ,
        0 as "cgst" ,
        a."sgst-rate" as "sgst-rate" ,
        0 as "sgst-amt" ,
        0 as "sgst" ,
        (a."cgst-rate" + a."sgst-rate") as "tax-rate",
        a."igst-rate" as "igst-rate" ,
        0 as "igst-amt" ,
        a."utgst-rate" as "utgst-rate" ,
        0 as "utgst-amt" ,
        f1."serial" ,
        c."hsncode",
        c."is-repeatable" as "is-repeatable",
        msm.store as "store-name",
        msm."store-manager" ,
        msm."line-manager",
        msm.abo,
        msm.city,
        msm."store-b2b",
        msm."month-diff" as "store-month-diff",
        msm."opened-at" as "store-opened-at",
        msm."franchisee-id",
        msm."franchisee-name",
        msm."cluster-id",
        msm."cluster-name",
        a."id" as "return-item-id",
        NULL as "bill-item-id",
        cast(NULL as numeric) as "promo-discount",
        c."type" as "type-at-selling",
        c."category" as "category-at-selling",
        date(f."returned-at") as "created-date",
        ii1."invoice-item-reference",
        i2."distributor-id",
        ds."name" as "distributor-name",
        b2."created-at" as "billed-at-return-ref",
        a."return-reason" as "return-reason",
        doi."drug-grade",
        msm."acquired" ,
        msm."old-new-static"
    from
        "prod2-generico"."customer-returns-1" f
    left join
            "prod2-generico"."customer-return-items-1" a on
        f."id" = a."return-id"
    left join
            "prod2-generico"."bills-1" f1 on
        a."bill-id" = f1."id"
    left join
            "prod2-generico"."inventory-1" b on
        a."inventory-id" = b."id"
    left join "prod2-generico"."invoice-items-1" ii1 ON
        b."invoice-item-id" = ii1.id
    left join "prod2-generico".invoices i2 on
        ii1."invoice-id" = i2.id
    left join "prod2-generico".distributors ds ON 
        i2."distributor-id" =ds.id 
    inner join "prod2-generico"."drugs" c on
        c."id" = b."drug-id"
    left join "prod2-generico"."patients-metadata" pm on
        f."patient-id" = pm."patient-id"
    left join
        "prod2-generico"."patients" p on
        f."patient-id" = p."id"
    left join
        "prod2-generico"."drug-order-info" doi on
        (doi."store-id" = f."store-id"
            and doi."drug-id" = b."drug-id")
    inner join
    "prod2-generico"."bills-1" b2 on
        a."bill-id" = b2."id"
    left join
    "prod2-generico"."promo-codes" pc on
        NVL(b2."promo-code-id", 0) = pc."id"
    left join
    "prod2-generico"."campaigns" ca on
        NVL(pc."campaign-id", 0) = ca."id"
    left join "prod2-generico"."composition-activation" mca on
        f."store-id" = mca."store-id"
        and c."composition-master-id" = mca."composition-master-id"
    left join "prod2-generico"."{}" as pso2 on
        a."bill-id" = pso2."id"
    inner join "prod2-generico"."{}" as msm on
        f."store-id" = msm."id"
    where 
        a."id" > {}
    """
