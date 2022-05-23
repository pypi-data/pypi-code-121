sales = """
        select
            z."store-id",
            z."drug-id",
            avg(z."mean-fptr") as "mean-fptr",
            sum(z.quantity) as quantity
        from
            (
            select
                f."patient-id",
                f."store-id",
                f."id" as "bill-id",
                c."id" as "drug-id",
                a."quantity" as "sold-quantity",
                coalesce(g."returned-quantity", 0) as "returned-quantity",
                (a."quantity" - coalesce(g."returned-quantity", 0)) as "quantity",
                a."rate",
                case
                    when coalesce( ii."actual-quantity", 1) = 0 
                then coalesce(ii."net-value" , b."final-ptr")
                    else
                coalesce(ii."net-value" / coalesce( ii."actual-quantity", 1), b."final-ptr")
                end as "mean-fptr",
                ((a."quantity" - coalesce(g."returned-quantity", 0)) * a."rate") as "value"
            from
                "prod2-generico"."bills-1" f
            join "prod2-generico"."bill-items-1" a on
                f."id" = a."bill-id"
            left join "prod2-generico"."inventory-1" b on
                a."inventory-id" = b."id"
            left join "prod2-generico"."invoice-items-1" ii on
                b."invoice-item-id" = ii."id"
            left join "prod2-generico"."drugs" c on
                c."id" = b."drug-id"
            left join "prod2-generico"."customer-return-items-1" g on
                g."inventory-id" = a."inventory-id"
                and g."bill-id" = a."bill-id"
            where
                DATEDIFF(d,date(a."created-at"),current_date) <= {days}
                and (a."quantity" - coalesce(g."returned-quantity", 0)) > 0
                and f."store-id" = {store_id}
                )z
        group by
            z."store-id",
            z."drug-id"
        """

expiry = """
        
        -- short book
         select
            case
                when date(inv.expiry) > current_date then 'Near Expiry'
                else 'Expired'
            end as "inventory-type",
            date(i."invoice-date") as "invoice-date",
            case
                when "auto-short" = 1
                and "home-delivery" = 0
                and "patient-id" = 4480 then 'Auto Short'
                when "auto-short" = 1
                and "home-delivery" = 0
                and "patient-id" != 4480 then 'Manual Short'
                when "auto-short" = 0
                and "auto-generated" = 0
                and "home-delivery" = 0 then 'Patient Request'
                when "auto-short" = 0
                and "auto-generated" = 0
                and "home-delivery" = 1 then 'Patient Request with HD'
                when sb.id is null then 'Source not found'
                else 'Unclassified'
            end as "request-type",
            inv.id as "inventory-id",
            inv."store-id",
            inv."drug-id",
            d."drug-name",
            date(inv."created-at") as created_date,
            date(inv.expiry) as expiry,
            inv.barcode,
            inv."invoice-item-id",
            inv.quantity,
            i."id" as "invoice-id",
            i."invoice-number",
            e."name" as "store-name",
            i."distributor-id",
            f.name as "distributor-name",
            d."type" as "drug-type",
            d."category",
            df."drug-grade",
            d."cold-chain",
            df.min,
            df."safe-stock",
            df.max,
            inv."ptr" as fptr,
            inv."ptr" * inv.quantity as value,
            sb.id as "short-book-id",
            inv."locked-quantity" + inv."locked-for-audit" + inv."locked-for-check" + inv."locked-for-transfer" as "locked-quantity",
            (inv."locked-quantity" + inv."locked-for-audit" + inv."locked-for-check" + inv."locked-for-transfer") * inv."ptr" as "locked-value"
        from
            "prod2-generico"."inventory-1" inv
        left join "prod2-generico".invoices i on
            inv."invoice-id" = i.id
        left join "prod2-generico"."invoice-items-1" ii on
            inv."invoice-item-id" = ii."id"
        left join "prod2-generico"."short-book-invoice-items" sbii on
            ii."invoice-item-reference" = sbii."invoice-item-id"
        left join "prod2-generico"."short-book-1" sb on
            sbii."short-book-id" = sb.id
        join "prod2-generico"."drugs" d on
            d."id" = inv."drug-id"
        join "prod2-generico"."stores" e on
            e."id" = inv."store-id"
        left join "prod2-generico"."distributors" f on
            f."id" = i."distributor-id"
        left join "prod2-generico"."drug-order-info" df on
            df."drug-id" = inv."drug-id"
            and df."store-id" = inv."store-id"
        where
            DATEDIFF(d,current_date,date(inv.expiry))< {expiry_days}
            and extract(yrs from (inv.expiry)) <= extract(yrs from (current_date)) + 1
            and extract(yrs from (inv.expiry)) >= 2017
            and ( (inv.quantity != 0)
                or (inv."locked-quantity" + inv."locked-for-audit" + inv."locked-for-check" + inv."locked-for-transfer" > 0) )
         """

return_and_rotation = """
                    select
                        date(i."invoice-date") as "invoice-date",
                         '{inventory_type}' as "inventory-type",
                        case
                            when "auto-short" = 1
                            and "home-delivery" = 0
                            and "patient-id" = 4480 then 'Auto Short'
                            when "auto-short" = 1
                            and "home-delivery" = 0
                            and "patient-id" != 4480 then 'Manual Short'
                            when "auto-short" = 0
                            and "auto-generated" = 0
                            and "home-delivery" = 0 then 'Patient Request'
                            when "auto-short" = 0
                            and "auto-generated" = 0
                            and "home-delivery" = 1 then 'Patient Request with HD'
                            when sb.id is null then 'Source not found'
                            else 'Unclassified'
                        end as "request-type",
                        inv.id as "inventory-id",
                        inv."store-id",
                        inv."drug-id",
                        d."drug-name",
                        date(inv."created-at") as created_date,
                        date(inv.expiry) as expiry,
                        inv.barcode,
                        inv."invoice-item-id",
                        inv.quantity,
                        i."id" as "invoice-id",
                        i."invoice-number",
                        e."name" as "store-name",
                        i."distributor-id",
                        f.name as "distributor-name",
                        d."type" as "drug-type",
                        d."category",
                        df."drug-grade",
                        d."cold-chain",
                        df.min,
                        df."safe-stock",
                        df.max,
                        inv."ptr" as fptr,
                        inv."ptr" * inv.quantity as value,
                        sb.id as "short-book-id",
                        inv."locked-quantity" + inv."locked-for-audit" + inv."locked-for-check" + inv."locked-for-transfer" as "locked-quantity",
                        (inv."locked-quantity" + inv."locked-for-audit" + inv."locked-for-check" + inv."locked-for-transfer") * inv."ptr" as "locked-value"
                    from
                        "prod2-generico"."inventory-1" inv
                    left join "prod2-generico".invoices i on
                        inv."invoice-id" = i.id
                    left join "prod2-generico"."invoice-items-1" ii on
                        inv."invoice-item-id" = ii."id"
                    left join "prod2-generico"."short-book-invoice-items" sbii on
                        ii."invoice-item-reference" = sbii."invoice-item-id"
                    left join "prod2-generico"."short-book-1" sb on
                        sbii."short-book-id" = sb.id
                    join "prod2-generico"."drugs" d on
                        d."id" = inv."drug-id"
                    join "prod2-generico"."stores" e on
                        e."id" = inv."store-id"
                    left join "prod2-generico"."distributors" f on
                        f."id" = i."distributor-id"
                    left join "prod2-generico"."drug-order-info" df on
                        df."drug-id" = inv."drug-id"
                        and df."store-id" = inv."store-id"
                    where
                        concat(inv."store-id", CONCAT('-', inv."drug-id")) in {store_drug_list}
                        and DATEDIFF(d,date(inv."created-at"),current_date)>= {days}
                        and DATEDIFF(d,current_date,date(inv.expiry))>= {expiry_days}
                        and ( (inv.quantity != 0)
                            or (inv."locked-quantity" + inv."locked-for-audit" + inv."locked-for-check" + inv."locked-for-transfer" > 0) )
                        and DATEDIFF(d,date(d."created-at"),current_date)>= 270
                    """

dead_liquidation = """
                    select
                        transfer."origin-store",
                        transfer."origin-store-name",
                        transfer."destination-store",
                        transfer."destination-store-name",
                        transfer."transferred-quantity",
                        transfer."inventory-id",
                        transfer."drug-id",
                        d."drug-name",
                        d.type as "drug-type",
                        d.category,
                        doi."drug-grade",
                        transfer."received-at",
                        n."created-at" as "bill-timestamp",
                        m."rate",
                        transfer."final-ptr",
                        case
                            when n."created-at" is null then 0
                            else coalesce(m."quantity", 0)
                        end as "sold-quantity",
                        case
                            when n."created-at" is null then 0
                            else coalesce(m."returned-quantity", 0)
                        end as "returned-quantity",
                        case
                            when n."created-at" is null then 0
                            else coalesce((m."quantity" - m."returned-quantity") * m."rate", 0)
                        end as "net-value"
                    from
                        (
                        select
                            c."origin-store",
                            a."destination-store",
                            sum(b.quantity) as "transferred-quantity",
                            e."name" as "origin-store-name",
                            f."name" as "destination-store-name",
                            b."inventory-id",
                            c."drug-id",
                            avg(c."final-ptr") as "final-ptr",
                            min(b."received-at") as "received-at"
                        from
                            "prod2-generico"."stock-transfers-1" a
                        join "prod2-generico"."stock-transfer-items-1" b on
                            a."id" = b."transfer-id"
                        join "prod2-generico"."inventory-1" c on
                            b."inventory-id" = c."id"
                        left join "prod2-generico"."drugs" d on
                            c."drug-id" = d."id"
                        left join "prod2-generico"."stores" e on
                            c."origin-store" = e."id"
                        left join "prod2-generico"."stores" f on
                            a."destination-store" = f."id"
                        where
                            "source-store" = 111
                            and d."type" != 'category-4'
                            and date(b."transferred-at") <= current_date
                            and d."id" != 406872
                            and d."id" != 424692
                            and d."id" != 401179
                            and d."id" != 444213
                            and cast(b."received-at" as varchar) <> '0000-00-00 00:00:00'
                        group by
                            c."origin-store",
                            a."destination-store",
                            e."name",
                            f."name",
                            b."inventory-id",
                            c."drug-id"
                    )transfer
                    left join "prod2-generico"."bill-items-1" m
                    on
                        transfer."inventory-id" = m."inventory-id"
                    left join "prod2-generico"."bills-1" n
                    on
                        n."id" = m."bill-id"
                        and transfer."destination-store" = n."store-id"
                    left join "prod2-generico".drugs d
                    on
                        transfer."drug-id" = d.id
                    left join "prod2-generico"."drug-order-info" doi
                    on
                        doi."drug-id" = transfer."drug-id"
                        and doi."store-id" = transfer."destination-store"
                """