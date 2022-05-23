max_store_id = """
            select
                max("id") as "store-id-max"
            from
                "prod2-generico"."{}"
            """

insert_stores_query = """
                        insert
                            into
                            "prod2-generico"."{}" (
                                "id",
                                "etl-created-by",
                                "created-at",
                                "updated-by",
                                "updated-at",
                                "store",
                                "line-manager",
                                "abo",
                                "store-manager",
                                "store-type",
                                "opened-at",
                                "date-diff",
                                "month-diff",
                                "latitude",
                                "longitude",
                                "store-contact-1",
                                "store-contact-2",
                                "store-address",
                                "city",
                                "store-b2b",
                                "line",
                                "landmark",
                                "store-group-id",
                                "franchisee-id",
                                "franchisee-name",
                                "cluster-id",
                                "cluster-name",
                                "acquired",
                                "old-new-static"
                                )
                        select
                            st.id as id,
                            'etl-automation' as "etl-created-by",
                            max(st."created-at") as "created-at",
                            'etl-automation' as "updated-by",
                            convert_timezone('Asia/Calcutta', GETDATE()) as "updated-at",
                            max(st.name) as "store",
                            max(case when b.type = 'line-manager' then b.name end) as "line-manager",
                            max(case when b.type = 'area-business-owner' then b.name end) as "abo",
                            max(case when b.type = 'store-manager' then b.name end) as "store-manager",
                            max(st.category) as "store-type",
                            DATE("opened-at") as "opened-at",
                            datediff(day, DATE("opened-at"), current_date) as "date-diff",
                            datediff(month, DATE("opened-at"), current_date) as "month-diff",
                            max(st."lat") as "latitude",
                            max(st."lon") as "longitude",
                            max(st."contact-number-1") as "store-contact-1",
                            max(st."contact-number-2") as "store-contact-2",
                            max(st."address") as "store-address",
                            max(sg.name) as "city",
                            case when lower(SUBSTRING(st.name, 1, 3))= 'b2b' then 'B2B' else 'Store' end as "store-b2b",
                            '' as line,
                            '' as landmark,
                            max(st."store-group-id") as "store-group-id",
                            st."franchisee-id",
                            f."name",
                            s."cluster-id",
                            s."cluster-name",
                            st."acquired",
                            (case when date(st."opened-at")>='2022-04-01' then 'new'
                            when date(st."opened-at")='0101-01-01' then 'not-opened'
                            else 'old' end) as "old-new-static"
                        from 
                            "prod2-generico".stores st
                        inner join "prod2-generico".franchisees f
                            on
                            st."franchisee-id" = f.id
                        left join 
                        (
                            select
                                us."store-id",
                                u."name" as name,
                                u."created-at" as "date",
                                u.type,
                                row_number() over(
                                partition by us."store-id",
                                u.type
                            order by
                                u."created-at" desc) as t_rank
                            from
                                "prod2-generico"."users-stores" as us
                            inner join "prod2-generico"."users" as u on
                                u."id" = us."user-id"
                            where
                                u.type in ('line-manager', 'store-manager', 'area-business-owner')) as b 
                            on
                            st.id = b."store-id"
                            and b.t_rank = 1
                        inner join "prod2-generico"."store-groups" sg on
                            st."store-group-id" = sg.id   
                        left join (
                            select
                                sf."store-id" as "store-id",
                                sf."is-active" as "sf-is-active",
                                sc."cluster-id" as "cluster-id",
                                c.name as "cluster-name",
                                sc."is-active" as "sc-is-active"
                            from
                                    "prod2-generico".features f
                                join 
                                    "prod2-generico"."store-features" sf
                                    on
                                    f.id = sf."feature-id"
                                join 
                                    "prod2-generico"."store-clusters" sc
                                    on
                                    sc."store-id" = sf."store-id"
                                join 
                                    "prod2-generico".clusters c 
                                    on
                                    c.id = sc."cluster-id"
                            where
                                sf."feature-id" = 69
                                and sf."is-active" = 1
                                and sc."is-active" = 1
                        ) as s
                        on 
                            st.id = s."store-id"
                        where
                            st.id > {}
                        group by
                            st.id,
                            st.name,
                            st."opened-at",
                            st."franchisee-id",
                            f."name",
                            s."cluster-id",
                            s."cluster-name",
                            st."acquired",
                            "old-new-static";
                        """

update_stores_query = """update "prod2-generico"."{}" as sm
                                set
                                    "updated-at" = convert_timezone('Asia/Calcutta', GETDATE()),
                                    "line-manager" = b."line-manager",
                                    "abo" = b."abo",
                                    "store" = b."store",
                                    "franchisee-name" = b."franchisee-name",
                                    "cluster-id" = b."cluster-id",
                                    "cluster-name" = b."cluster-name",
                                    "acquired"=b."acquired",
                                    "opened-at"=b."opened-at",
                                    "old-new-static"=b."old-new-static"
                                from (
                                    select 
                                        st.id as id,
                                        st."acquired",
                                        st.name as "store",
                                        st."opened-at",
                                        (case when date(st."opened-at")>='2022-04-01' then 'new'
										when date(st."opened-at")='0101-01-01' then 'not-opened'
										else 'old' end) as "old-new-static",
                                        f."name" as "franchisee-name",
                                        s."cluster-id" as "cluster-id",
                                        s."cluster-name" as "cluster-name",
                                        max(case when b.type = 'line-manager' then b.name end) as "line-manager",
                                        max(case when b.type = 'area-business-owner' then b.name end) as "abo"
                                    from "prod2-generico"."{}" sm
                                    inner join "prod2-generico".stores st on
                                        st.id = sm.id
                                    inner join "prod2-generico".franchisees f
                                        on
                                        st."franchisee-id" = f.id
                                    left join 
                                    (
                                        select
                                            us."store-id",
                                            u."name" as name,
                                            u."created-at" as "date",
                                            u.type,
                                            row_number() over(
                                            partition by us."store-id",
                                            u.type
                                        order by
                                            u."created-at" desc) as t_rank
                                        from
                                            "prod2-generico"."users-stores" as us
                                        inner join "prod2-generico"."users" as u on
                                            u."id" = us."user-id"
                                        where
                                            u.type in ('line-manager', 'store-manager', 'area-business-owner')) as b 
                                        on
                                        st.id = b."store-id"
                                        and b.t_rank = 1
                                    inner join "prod2-generico"."store-groups" sg on
                                        st."store-group-id" = sg.id   
                                    left join (
                                        select
                                            sf."store-id" as "store-id",
                                            sf."is-active" as "sf-is-active",
                                            sc."cluster-id" as "cluster-id",
                                            c.name as "cluster-name",
                                            sc."is-active" as "sc-is-active"
                                        from
                                                "prod2-generico".features f
                                            join 
                                                "prod2-generico"."store-features" sf
                                                on
                                                f.id = sf."feature-id"
                                            join 
                                                "prod2-generico"."store-clusters" sc
                                                on
                                                sc."store-id" = sf."store-id"
                                            join 
                                                "prod2-generico".clusters c 
                                                on
                                                c.id = sc."cluster-id"
                                        where
                                            sf."feature-id" = 69
                                            and sf."is-active" = 1
                                            and sc."is-active" = 1
                                    ) as s
                                    on 
                                        st.id = s."store-id"
                                    group by
                                        st.id,
                                        st."acquired",
                                        st.name,
                                        st."opened-at",
                                        "old-new-static",
                                        f."name",
                                        s."cluster-id",
                                        s."cluster-name") as b
                                where 
                                    sm.id = b.id
                                    and
                                    (sm.abo != b.abo
                                    or
                                    sm."line-manager" != b."line-manager"
                                    or
                                    sm."acquired" != b."acquired"
                                    or
									b."cluster-id" != sm."cluster-id"
									or
									b."cluster-name" != sm."cluster-name"
                                    or
                                    b."franchisee-name" != sm."franchisee-name"
                                    or
                                    b."opened-at" != sm."opened-at");             
                                    """