update_query = """update "prod2-generico"."{}"
                SET
                    "cohort-quarter" = stg."cohort-quarter", 
                    "cohort-quarter-number" = stg."cohort-quarter-number", 
                    "year-cohort" = stg."year-cohort",
                    "store-id" = stg."store-id",
                    "bill-quarter" = stg."bill-quarter", 
                    "bill-quarter-number" = stg."bill-quarter-number", 
                    "year-bill" = stg."year-bill",
                    "bill-date" = stg."bill-date", 
                    "day-zero-in-cohort-quarter" = stg."day-zero-in-cohort-quarter",
                    "day-zero-in-bill-quarter" = stg."day-zero-in-bill-quarter", 
                    "day-index" = stg."day-index", 
                    "quarter-diff" = stg."quarter-diff",
                    "resurrection-candidate" = stg."resurrection-candidate", 
                    "cohort-quarter-patients" = stg."cohort-quarter-patients",
                    "cohort-resurrection-candidates" = stg."cohort-resurrection-candidates"
                from "prod2-generico"."{}" retention
                inner join "{}-stg" stg on
                    stg."patient-id" = retention."patient-id"
                """

insert_query = """insert into "prod2-generico"."{}"
                    select 
                        stg.* 
                    from
                        "{}-stg" stg
                    left join
                        "prod2-generico"."{}" retention
                    on
                       stg."patient-id" = retention."patient-id"
                    where
                        retention."patient-id" IS NULL
                """

temp_create = """create temp table "{}-stg"
                (
                    "created-at" TIMESTAMP WITHOUT TIME ZONE   ENCODE az64
                    ,"created-by" VARCHAR(765)   ENCODE lzo
                    ,"updated-by" VARCHAR(765)   ENCODE lzo
                    ,"updated-at" TIMESTAMP WITHOUT TIME ZONE   ENCODE az64
                    ,"patient-id" BIGINT NOT NULL  ENCODE az64
                    ,"store-id" INTEGER NOT NULL  ENCODE az64
                    ,"bill-date" DATE NOT NULL  ENCODE az64
                    ,"last-bill-created-at" TIMESTAMP WITHOUT TIME ZONE ENCODE az64
                    ,"year-bill" INTEGER NOT NULL  ENCODE az64
                    ,"bill-quarter" VARCHAR(255)   ENCODE lzo
                    ,"bill-quarter-number" INTEGER NOT NULL  ENCODE az64
                    ,"year-cohort" INTEGER NOT NULL  ENCODE az64
                    ,"cohort-quarter" VARCHAR(255)   ENCODE lzo
                    ,"cohort-quarter-number" INTEGER NOT NULL  ENCODE az64
                    ,"day-zero-in-cohort-quarter" TIMESTAMP WITHOUT TIME ZONE   ENCODE az64
                    ,"day-zero-in-bill-quarter" TIMESTAMP WITHOUT TIME ZONE   ENCODE az64
                    ,"day-index" INTEGER   ENCODE az64
                    ,"quarter-diff" INTEGER   ENCODE az64
                    ,"resurrection-candidate" INTEGER   ENCODE az64
                    ,"cohort-quarter-patients" BIGINT   ENCODE az64
                    ,"cohort-resurrection-candidates" BIGINT   ENCODE az64
                );"""
