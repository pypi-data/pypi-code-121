max_pso_id = """
            select
                max("id") as "pso-id-max"
            from
                "prod2-generico"."{}"
            """

insert_query = """
    insert
        into
        "prod2-generico"."{}" (
                "id" ,
                "created-at", 
                "created-by", 
                "updated-by", 
                "updated-at", 
                "year-created-at", 
                "month-created-at", 
                "patient-id", 
                "doctor-id", 
                "store-id", 
                "bill-id", 
                "drug-id", 
                "zeno-order-id", 
                "drug-name", 
                "pso-requested-quantity", 
                "pso-inventory-quantity", 
                "order-number", 
                "order-source", 
                "order-type", 
                "patient-request-id", 
                "payment-type", 
                "promo-id", 
                "pso-status", 
                "fulfilled-to-consumer", 
                "type", 
                "category", 
                "company", 
                "company-id", 
                "composition", 
                "composition-master-id", 
                "lp-fulfilled-qty", 
                "sb-id" , 
                "ff-distributor", 
                "ordered-distributor-id", 
                "quantity", 
                "required-quantity", 
                "ordered-at", 
                "completed-at", 
                "invoiced-at", 
                "dispatched-at", 
                "received-at", 
                "sb-status", 
                "decline-reason", 
                "inventory-at-ordering", 
                "re-ordered-at", 
                "dc-ff-time", 
                "store-received-ff-time", 
                "consumer-ff-time", 
                "order-raised-at-dc", 
                "order-raised-at-distributor", 
                "billed-at", 
                "store-name", 
                "store-manager", 
                "line-manager", 
                "abo", 
                "city", 
                "store-b2b", 
                "substituted", 
                "gross-quantity", 
                "gross-revenue-value",
                "net-quantity", 
                "net-revenue-value", 
                "selling-rate", 
                "store-delivered-at",
                "franchisee-short-book"
                )
    select
        pso."id" as "id",
        pso."created-at" as "created-at",
        pso."created-by" as "created-by",
        'etl-automation' as "updated-by",
        convert_timezone('Asia/Calcutta',GETDATE()) as "updated-at",
        extract(year from pso."created-at") as "year-created-at",
        extract(month from pso."created-at") as "month-created-at",
        pso."patient-id" as "patient-id" ,
        pso."doctor-id" as "doctor-id" ,
        pso."store-id" as "store-id" ,
        pso."bill-id" as "bill-id" ,
        pso."drug-id" as "drug-id",
        pso."zeno-order-id" as "zeno-order-id",
        pso."drug-name" as "drug-name" ,
        pso."requested-quantity" as "pso-requested-quantity",
        pso."inventory-quantity" as "pso-inventory-quantity",
        pso."order-number" as "order-number" ,
        pso."order-source" as "order-source" ,
        pso."order-type" as "order-type" ,
        pso."patient-request-id" as "patient-request-id" ,
        pso."payment-type" as "payment-type" ,
        pso."promo-id" as "promo-id",
        pso.status as "pso-status",
        (case
            when ms."gross-quantity" > 0 then 1
            else 0
        end) as "fulfilled-to-consumer",
        d2."type" ,
        d2."category" ,
        d2."company" ,
        d2."company-id" as "company-id" ,
        d2."composition" ,
        d2."composition-master-id" as "composition-master-id",
        NVL(prlp."lp-fulfilled-qty", 0) as "lp-fulfilled-qty",
        sb."id" as "sb-id",
        sb."distributor-id" as "ff-distributor",
        sb."ordered-distributor-id" as "ordered-distributor-id",
        sb."quantity" as "quantity" ,
        sb."required-quantity" as "required-quantity" ,
        case
            when sb."ordered-at" = '0101-01-01' then null
            else sb."ordered-at"
        end as "ordered-at",
        case
            when sb."completed-at" = '0101-01-01' then null
            else sb."completed-at"
        end as "completed-at",
        case
            when sb."invoiced-at" = '0101-01-01' then null
            else sb."invoiced-at"
        end as "invoiced-at",
        case
            when sb."dispatched-at" = '0101-01-01' then null
            else sb."dispatched-at"
        end as "dispatched-at",
        case
            when sb."received-at" = '0101-01-01' then null
            else sb."received-at"
        end as "received-at",
        sb."status" as "sb-status",
        sb."decline-reason" as "decline-reason",
        sb."inventory-at-ordering" as "inventory-at-ordering" ,
        case
            when sb."re-ordered-at" = '0101-01-01' then null
            else sb."re-ordered-at"
        end as "re-ordered-at",
        (case
            when (pso."created-at" = '0101-01-01'
            or msda."store-delivered-at" = '0101-01-01') then null
            else datediff(hour,
            pso."created-at",
            msda."store-delivered-at")
        end) as "dc-ff-time",
        (case
            when (pso."created-at" = '0101-01-01'
            or sb."received-at" = '0101-01-01') then null
            else datediff(hour,
            pso."created-at",
            sb."received-at")
        end) as "store-received-ff-time",
        (case
            when (pso."created-at" = '0101-01-01'
            or b2."created-at" = '0101-01-01') then null
            else datediff(hour,
            pso."created-at",
            b2."created-at")
        end) as "consumer-ff-time",
        (case
            when sb."quantity">0 then 1
            else 0
        end) as "order-raised-at-dc",
        (case
            when ("ordered-at" = '0101-01-01' or "ordered-at" is null) then 0
            else 1
        end) as "order-raised-at-distributor",
        b2."created-at" as "billed-at",
        msm."store" as "store-name",
        msm."store-manager",
        msm."line-manager",
        msm."abo",
        msm."city",
        msm."store-b2b",
        case
            when "generic-flag" is null then 'not-available'
            when "generic-flag" is not null
            and d2."type" = 'generic' then 'substituted'
            when "generic-flag" is not null
            and d2."type" != 'generic' then 'not-substituted'
            else 'not-available'
        end as "substituted",
        ms."gross-quantity",
        ms."gross-revenue-value",
        ms."net-quantity",
        ms."net-revenue-value",
        case
            when sgdp."selling-rate" is null
            and d2."type" = 'generic' then 35
            when sgdp."selling-rate" is null
            and d2."type" != 'generic' then 100
            else sgdp."selling-rate"
        end as "selling-rate",
        msda."store-delivered-at",
        sb."franchisee-short-book" as "franchisee-short-book"
    from
            "prod2-generico"."patients-store-orders" pso
    left join 
        (
        select
                    prlp."patient-request-id" ,
                    sum("fulfilled-quantity") as "lp-fulfilled-qty"
        from
                    "prod2-generico"."patient-request-local-purchase" prlp
        inner join 
                "prod2-generico"."patients-store-orders" pso on
                    NVL(pso."patient-request-id", 0) = prlp."patient-request-id"
        group by
                    prlp."patient-request-id" ) as prlp on
                prlp."patient-request-id" = NVL(pso."patient-request-id", 0)
    left join "prod2-generico"."patient-requests-short-books-map" mprsb on
        NVL(pso."patient-request-id", 0) = mprsb."patient-request-id"
    left join "prod2-generico"."short-book-1" sb on
        sb.id = mprsb."short-book-id"
    left join "prod2-generico"."store-delivered" msda on
        mprsb."short-book-id" = msda."id"
    left join "prod2-generico"."bills-1" b2 on
        b2.id = NVL(pso."bill-id", 0)
    left join "prod2-generico"."drugs" d2 on
        d2."id" = pso."drug-id"
    left join "prod2-generico"."substitutable-compositions" msc on
        msc."id" = d2."composition-master-id"
    left join "prod2-generico"."sales-agg" ms on
        ms."bill-id" = pso."bill-id"
        and ms."drug-id" = pso."drug-id"
    inner join "prod2-generico"."stores-master" msm on
        pso."store-id" = msm.id
    left join "prod2-generico"."store-group-drug-price" sgdp on
        msm."store-group-id" = sgdp."store-group-id"
        and pso."drug-id" = sgdp."drug-id" and sgdp."cluster-id" is null
    where
        pso."id" > {};
    """

update_query = """
        update "prod2-generico"."{}" as t
        set
            "updated-at" = convert_timezone('Asia/Calcutta', GETDATE()),
            "bill-id" = s."bill-id", 
            "drug-id" = s."drug-id", 
            "order-number" = s."order-number", 
            "order-type" = s."order-type", 
            "patient-request-id" = s."patient-request-id", 
            "payment-type" = s."payment-type", 
            "promo-id" = s."promo-id", 
            "pso-status" = s."pso-status", 
            "fulfilled-to-consumer" = s."fulfilled-to-consumer", 
            "type" = s."type", 
            "category" = s."category", 
            "company" = s."company", 
            "composition" = s."composition", 
            "lp-fulfilled-qty" = s."lp-fulfilled-qty", 
            "sb-id" = s."sb-id", 
            "ff-distributor" = s."ff-distributor", 
            "ordered-distributor-id" = s."ordered-distributor-id", 
            "quantity" = s."quantity", 
            "required-quantity" = s."required-quantity", 
            "ordered-at" = s."ordered-at", 
            "completed-at" = s."completed-at", 
            "invoiced-at" = s."invoiced-at", 
            "dispatched-at" = s."dispatched-at", 
            "received-at" = s."received-at", 
            "sb-status" = s."sb-status", 
            "decline-reason" = s."decline-reason", 
            "inventory-at-ordering" = s."inventory-at-ordering", 
            "re-ordered-at" = s."re-ordered-at", 
            "dc-ff-time" = s."dc-ff-time", 
            "store-received-ff-time" = s."store-received-ff-time", 
            "consumer-ff-time" = s."consumer-ff-time", 
            "order-raised-at-dc" = s."order-raised-at-dc", 
            "order-raised-at-distributor" = s."order-raised-at-distributor", 
            "billed-at" = s."billed-at", 
            "store-manager" = s."store-manager", 
            "line-manager" = s."line-manager", 
            "abo" = s."abo", 
            "substituted" = s."substituted", 
            "gross-quantity" = s."gross-quantity", 
            "gross-revenue-value" = s."gross-revenue-value",
            "net-quantity" = s."net-quantity", 
            "net-revenue-value" = s."net-revenue-value", 
            "selling-rate" = s."selling-rate", 
            "store-delivered-at" = s."store-delivered-at",
            "franchisee-short-book" = s."franchisee-short-book"
        from (
            select
                pso."id" as "id",
                pso."bill-id" as "bill-id" ,
                pso."drug-id" as "drug-id",
                pso."order-number" as "order-number" ,
                pso."order-type" as "order-type" ,
                pso."patient-request-id" as "patient-request-id" ,
                pso."payment-type" as "payment-type" ,
                pso."promo-id" as "promo-id",
                pso.status as "pso-status",
                (case
                    when ms."gross-quantity" > 0 then 1
                    else 0
                end) as "fulfilled-to-consumer",
                d2."type",
                d2."category" ,
                d2."company" ,
                d2."composition" ,
                NVL(prlp."lp-fulfilled-qty", 0) as "lp-fulfilled-qty",
                sb."id" as "sb-id",
                sb."distributor-id" as "ff-distributor",
                sb."ordered-distributor-id" as "ordered-distributor-id",
                sb."quantity" as "quantity" ,
                sb."required-quantity" as "required-quantity" ,
                case
                    when sb."ordered-at" = '0101-01-01' then null
                    else sb."ordered-at"
                end as "ordered-at",
                case
                    when sb."completed-at" = '0101-01-01' then null
                    else sb."completed-at"
                end as "completed-at",
                case
                    when sb."invoiced-at" = '0101-01-01' then null
                    else sb."invoiced-at"
                end as "invoiced-at",
                case
                    when sb."dispatched-at" = '0101-01-01' then null
                    else sb."dispatched-at"
                end as "dispatched-at",
                case
                    when sb."received-at" = '0101-01-01' then null
                    else sb."received-at"
                end as "received-at",
                sb."status" as "sb-status",
                sb."decline-reason" as "decline-reason",
                sb."inventory-at-ordering" as "inventory-at-ordering" ,
                case
                    when sb."re-ordered-at" = '0101-01-01' then null
                    else sb."re-ordered-at"
                end as "re-ordered-at",
                (case
                    when (pso."created-at" = '0101-01-01'
                    or msda."store-delivered-at" = '0101-01-01') then null
                    else datediff(hour,
                    pso."created-at",
                    msda."store-delivered-at")
                end) as "dc-ff-time",
                (case
                    when (pso."created-at" = '0101-01-01'
                    or sb."received-at" = '0101-01-01') then null
                    else datediff(hour,
                    pso."created-at",
                    sb."received-at")
                end) as "store-received-ff-time",
                (case
                    when (pso."created-at" = '0101-01-01'
                    or ms."created-at" = '0101-01-01') then null
                    else datediff(hour,
                    pso."created-at",
                    ms."created-at")
                end) as "consumer-ff-time",
                (case
                    when sb."quantity">0 then 1
                    else 0
                end) as "order-raised-at-dc",
                (case
                    when (sb."ordered-at" = '0101-01-01' or sb."ordered-at" is null) then 0
                    else 1
                end) as "order-raised-at-distributor",
                ms."created-at" as "billed-at",
                msm."store-manager",
                msm."line-manager",
                msm."abo",
                case
                    when msc."generic-flag" is null then 'not-available'
                    when msc."generic-flag" is not null
                    and d2."type" = 'generic' then 'substituted'
                    when msc."generic-flag" is not null
                    and d2."type" != 'generic' then 'not-substituted'
                    else 'not-available'
                end as "substituted",
                ms."gross-quantity",
                ms."gross-revenue-value",
                ms."net-quantity",
                ms."net-revenue-value",
                case
                    when sgdp."selling-rate" is null
                    and d2."type" = 'generic' then 35
                    when sgdp."selling-rate" is null
                    and d2."type" != 'generic' then 100
                    else sgdp."selling-rate"
                end as "selling-rate",
                msda."store-delivered-at",
                sb."franchisee-short-book" as "franchisee-short-book"
            from
                    "prod2-generico"."{}" prm 
            inner join 
                    "prod2-generico"."patients-store-orders" pso on prm.id = pso.id
            left join 
                (
                select      
                            prlp."patient-request-id" ,
                            sum("fulfilled-quantity") as "lp-fulfilled-qty"
                from
                            "prod2-generico"."patient-request-local-purchase" prlp
                inner join 
                        "prod2-generico"."patients-store-orders" pso on
                        NVL(pso."patient-request-id", 0) = prlp."patient-request-id"
                group by
                         prlp."patient-request-id" ) as prlp on
                prlp."patient-request-id" = NVL(pso."patient-request-id", 0)
            left join "prod2-generico"."patient-requests-short-books-map" mprsb on
                NVL(pso."patient-request-id", 0) = mprsb."patient-request-id"
            left join "prod2-generico"."short-book-1" sb on
                sb.id = mprsb."short-book-id"
            left join "prod2-generico"."store-delivered" msda on
                mprsb."short-book-id" = msda."id"
            inner join "prod2-generico"."drugs" d2 on
                d2."id" = pso."drug-id"
            left join "prod2-generico"."substitutable-compositions" msc on
                msc."id" = d2."composition-master-id"
            left join "prod2-generico"."sales_agg" ms on
                ms."bill-id" = pso."bill-id"
                and ms."drug-id" = pso."drug-id"
           inner join "prod2-generico"."stores-master" msm on
                pso."store-id" = msm.id
            left join "prod2-generico"."store-group-drug-price" sgdp on
                msm."store-group-id" = sgdp."store-group-id"
                and pso."drug-id" = sgdp."drug-id" and sgdp."cluster-id" is null
            where
                prm."updated-at" < pso."updated-at"
                or prm."updated-at" < sb."updated-at"
                or prm."updated-at" < msc."updated-at"
                or prm."updated-at" < msda."updated-at"
                or prm."updated-at" < d2."updated-at"
             ) as s
        where 
            t.id = s.id;             
        """
