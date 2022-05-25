max_bill_id = """
            select
                max("id") as "bill-id-max"
            from
                "prod2-generico"."{}"
            """

insert_bill_flags_query = """
        insert
            into
            "prod2-generico"."{}" (
                "id",
                "created-by", 
                "created-at", 
                "updated-by", 
                "updated-at",  
                "pr-flag", 
                "hd-flag", 
                "ecom-flag"
                )
        select
            pso."bill-id" as "id",        
            'etl-automation' as "created-by",
            convert_timezone('Asia/Calcutta',GETDATE()) as "created-at",
            'etl-automation' as "updated-by",
            convert_timezone('Asia/Calcutta',GETDATE()) as "updated-at",
            bool_or(case when pso."patient-request-id" is null then false else true end) as "pr-flag",
            bool_or(case when pso."order-type" = 'delivery' then true else false end) as "hd-flag",
            bool_or(case when pso."order-source" = 'zeno' then true else false end) as "ecom-flag"
        from 
            "prod2-generico"."patients-store-orders" pso
            left join "prod2-generico"."bill-flags" bf
            on NVL(pso."bill-id",0)= bf."id"
        where
            bf."id" is null
        group by
            pso."bill-id";
        """

update_bill_flags_query = """
        update "prod2-generico"."{}" as bf
        set
            "updated-at" = convert_timezone('Asia/Calcutta', GETDATE()),
            "pr-flag" = b."pr-flag",
            "hd-flag" = b."hd-flag",
            "ecom-flag" = b."ecom-flag"
        from (
            select
                "bill-id" as "id",        
                bool_or(case when pso."patient-request-id" is null then false else true end) as "pr-flag",
                bool_or(case when pso."order-type" = 'delivery' then true else false end) as "hd-flag",
                bool_or(case when pso."order-source" = 'zeno' then true else false end) as "ecom-flag"
            from 
                "prod2-generico"."{}" bf inner join 
                "prod2-generico"."patients-store-orders" pso on
                bf.id = pso."bill-id"
            where
                pso."updated-at" > bf."updated-at"
            group by
                pso."bill-id"
             ) as b
        where 
            bf.id = b.id;             
        """
