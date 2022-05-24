#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_READ_COMMITTED
from psycopg2.extras import RealDictCursor

from pg_metadata.Namespace      import Namespace
from pg_metadata.Table          import Table
from pg_metadata.View           import View
from pg_metadata.Sequence       import Sequence
from pg_metadata.Function       import Function
from pg_metadata.ForeignServer  import ForeignServer
from pg_metadata.ForeignTable   import ForeignTable
from pg_metadata.Extension      import Extension
from pg_metadata.Publication    import Publication
from pg_metadata.Subscription   import Subscription
from pg_metadata.EventTrigger   import EventTrigger
from pg_metadata.Cast           import Cast
from pg_metadata.System         import CalcDuration

class Database():
    def __init__(self, connect, exclude_schemas=[]):
        """
            Database object
            @param connect: Connection params
            @param exclude_schemas: Excluded schemas (namespaces)
        """
        self.Connect        = self.GetConnectionString(connect)
        self.IsSuperUser    = False
        self.Version        = None
        self.Objects        = {}
        self.ExcludeSchemas = exclude_schemas

    def __str__(self):
        """
            String representation
        """
        return str(self.PG)

    def Parse(self):
        """
            Database metadata (DDL) parsing
        """
        logging.debug("Parsing started = %s", self.Connect)

        with psycopg2.connect(self.Connect) as conn:
            conn.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)
            with conn.cursor(cursor_factory = RealDictCursor) as cursor:
                self.GetSuperUser(cursor)
                self.GetVersion(cursor)
                self.GetNamespace(cursor)
                self.GetTable(cursor)
                self.GetFunction(cursor)
                self.GetView(cursor)
                self.GetSequence(cursor)
                self.GetForeignServer(cursor)
                self.GetForeignTable(cursor)
                self.GetExtension(cursor)
                self.GetPublication(cursor)
                self.GetSubscription(cursor)
                self.GetEventTrigger(cursor)
                self.GetCast(cursor)

    def GetConnectionString(self, connect):
        assert connect is not None, \
            "connection params is null"

        assert isinstance(connect, dict), \
            "connection params is not dict"

        assert len(connect.keys()) > 0, \
            "connection dict is empty"

        host = (connect.get("host") or "").strip()
        assert len(host) > 0, \
            "host name is empty"

        port = connect.get("port") or 5432

        database = (connect.get("database") or "").strip()
        assert len(database) > 0, \
            "database name is empty"

        username = (connect.get("username") or "").strip()
        assert len(username) > 0, \
            "username is empty"

        password = (connect.get("password") or "").strip()
        assert len(password) > 0, \
            "password is empty"

        return "host={0} port={1} dbname={2} user={3} password={4}".format(
            host, port, database, username, password)

    @CalcDuration
    def GetSuperUser(self, cursor):
        cursor.execute("""select exists(select 1 from pg_roles where rolname = user and rolsuper) as is_super""")

        for row in cursor.fetchall():
            self.IsSuperUser = row.get("is_super") or False

        logging.info("IsSuperUser = {0}".format(self.IsSuperUser))

    @CalcDuration
    def GetVersion(self, cursor):
        cursor.execute("""
            select trim(replace(v.v, 'PostgreSQL ', ''))::integer as version
            from unnest((select regexp_matches(version(), 'PostgreSQL \\d{1,}'))) v
        """)

        for row in cursor.fetchall():
            self.Version = row.get("version")

        assert (self.Version or 0) > 0, \
            "failed to get PostgreSQL version "

        logging.info("PostgreSQL version = {0}".format(self.Version))

    @CalcDuration
    def GetNamespace(self, cursor):
        cursor.execute("""
            SELECT
                n.oid,
                trim(lower(n.nspname)) AS name,
                trim(lower(r.rolname)) AS owner,
                trim(coalesce(obj_description(n.oid, 'pg_namespace'), '')) AS comment,
                n.nspacl::varchar[] as acl
            FROM pg_namespace n
            JOIN pg_roles r ON
                r.oid = n.nspowner
            WHERE
                n.nspname != ALL(%s) AND
                n.nspname !~* '^pg_temp' AND
                n.nspname !~* '^pg_toast'
            ORDER BY 2,3
        """, [self.ExcludeSchemas])

        for row in cursor.fetchall():
            self.Objects.update(Namespace(None, row).Export())

        logging.info("Namespaces loaded = {0}".format(cursor.rowcount))

    @CalcDuration
    def GetTable(self, cursor):
        if self.Version in (9, 9):
            query = """
                SELECT
                    c.oid,
                    trim(lower(n.nspname)) AS schema,
                    trim(lower(c.relname)) AS name,
                    trim(lower(r.rolname)) AS owner,
                    trim(upper(c.relhasoids::varchar)) as has_oids,
                    obj_description(c.oid, 'pg_class') AS comment,
                    case
                        when coalesce(trim(pc.relname), '') = '' then null
                        else pn.nspname || '.' || pc.relname
                    end AS parent_table,
                    null::varchar as part_border,
                    null::varchar as part_key,
                    c.relacl AS acl,
                    c.reloptions,
                    &columns&,
                    &constraints&,
                    &indexes&,
                    &triggers&
                FROM pg_class c
                JOIN pg_namespace n ON
                    n.oid = c.relnamespace AND
                    n.nspname !~* '^pg_temp' AND
                    n.nspname !~* '^pg_toast'
                JOIN pg_roles r ON
                    r.oid = c.relowner
                LEFT JOIN pg_inherits inh ON
                    c.oid = inh.inhrelid
                LEFT JOIN pg_class pc ON
                    pc.oid = inh.inhparent
                LEFT JOIN pg_namespace pn ON
                    pn.oid = pc.relnamespace
                WHERE
                    c.relkind in ('r','p') AND
                    n.nspname != ALL(%s)
                ORDER BY 2,3
            """
        elif self.Version in (10,11):
            query = """
                SELECT
                    c.oid,
                    trim(lower(n.nspname)) AS schema,
                    trim(lower(c.relname)) AS name,
                    trim(lower(r.rolname)) AS owner,
                    trim(upper(c.relhasoids::varchar)) as has_oids,
                    obj_description(c.oid, 'pg_class') AS comment,
                    case
                        when coalesce(trim(pc.relname), '') = '' then null
                        else pn.nspname || '.' || pc.relname
                    end AS parent_table,
                    pg_get_expr(c.relpartbound, c.oid, true) as part_border,
                    pg_get_partkeydef(c.oid) as part_key,
                    c.relacl::varchar[] AS acl,
                    c.reloptions,
                    &columns&,
                    &constraints&,
                    &indexes&,
                    &triggers&
                FROM pg_class c
                JOIN pg_namespace n ON
                    n.oid = c.relnamespace AND
                    n.nspname !~* '^pg_temp' AND
                    n.nspname !~* '^pg_toast'
                JOIN pg_roles r ON
                    r.oid = c.relowner
                LEFT JOIN pg_inherits inh ON
                    c.oid = inh.inhrelid
                LEFT JOIN pg_class pc ON
                    pc.oid = inh.inhparent
                LEFT JOIN pg_namespace pn ON
                    pn.oid = pc.relnamespace
                WHERE
                    c.relkind in ('r','p') AND
                    n.nspname != ALL(%s)
                ORDER BY 2,3
            """
        elif self.Version in (12,13,14):
            query = """
                SELECT
                    c.oid,
                    trim(lower(n.nspname)) AS schema,
                    trim(lower(c.relname)) AS name,
                    trim(lower(r.rolname)) AS owner,
                    false::varchar as has_oids,
                    obj_description(c.oid, 'pg_class') AS comment,
                    case
                        when coalesce(trim(pc.relname), '') = '' then null
                        else pn.nspname || '.' || pc.relname
                    end AS parent_table,
                    pg_get_expr(c.relpartbound, c.oid, true) as part_border,
                    pg_get_partkeydef(c.oid) as part_key,
                    c.relacl::varchar[] AS acl,
                    c.reloptions,
                    &columns&,
                    &constraints&,
                    &indexes&,
                    &triggers&
                FROM pg_class c
                JOIN pg_namespace n ON
                    n.oid = c.relnamespace AND
                    n.nspname !~* '^pg_temp' AND
                    n.nspname !~* '^pg_toast'
                JOIN pg_roles r ON
                    r.oid = c.relowner
                LEFT JOIN pg_inherits inh ON
                    c.oid = inh.inhrelid
                LEFT JOIN pg_class pc ON
                    pc.oid = inh.inhparent
                LEFT JOIN pg_namespace pn ON
                    pn.oid = pc.relnamespace
                WHERE
                    c.relkind in ('r','p') AND
                    n.nspname != ALL(%s)
                ORDER BY 2,3
            """
        else:
            raise Exception("Unknown PostgreSQL version - {0}".format(self.Version))

        query = query.replace("&columns&", """
                    (
                        select jsonb_agg(q order by q.order_num)
                        from (
                            select
                                trim(lower(a.attname)) as name,
                                trim(lower(format_type(a.atttypid, a.atttypmod))) as type,
                                a.attnotnull as not_null,
                                pg_get_expr(ad.adbin, ad.adrelid) as default_value,
                                trim(d.description) as comment,
                                a.attnum as order_num,
                                max(a.attnum) over (partition by a.attrelid) as max_order_num
                            from pg_attribute a
                            left join pg_attrdef ad on
                                a.atthasdef and
                                ad.adrelid = a.attrelid and
                                ad.adnum = a.attnum
                            left join pg_description d on
                                d.objoid = a.attrelid and
                                d.objsubid = a.attnum
                            where
                                a.attrelid = c.oid and
                                a.attnum > 0 and
                                not a.attisdropped
                        ) q
                    ) as columns
        """)

        query = query.replace("&constraints&", """
                    (
                        select jsonb_agg(q order by q.order_num, q.name)
                        from (
                            select
                                trim(lower(co.conname)) as name,
                                trim(lower(co.contype)) as type,
                                case trim(lower(co.contype))
                                    when 'p' then 1
                                    when 'u' then 2
                                    when 'c' then 3
                                    when 'f' then 4
                                    else          5
                                end::integer as order_num,
                                pg_get_constraintdef(co.oid) as definition,
                                case trim(lower(co.confupdtype))
                                    when 'a' then 'ON UPDATE NO ACTION'
                                    when 'r' then 'ON UPDATE RESTRICT'
                                    when 'c' then 'ON UPDATE CASCADE'
                                    when 'n' then 'ON UPDATE SET NULL'
                                    when 'd' then 'ON UPDATE SET DEFAULT'
                                end as update_action,
                                case trim(lower(co.confdeltype))
                                    when 'a' then 'ON DELETE NO ACTION'
                                    when 'r' then 'ON DELETE RESTRICT'
                                    when 'c' then 'ON DELETE CASCADE'
                                    when 'n' then 'ON DELETE SET NULL'
                                    when 'd' then 'ON DELETE SET DEFAULT'
                                end as delete_action,
                                case trim(lower(co.confmatchtype))
                                    when 'f' then 'MATCH FULL'
                                    when 'p' then 'MATCH PARTIAL'
                                    when 'u' then 'MATCH SIMPLE'
                                    when 's' then 'MATCH SIMPLE'
                                end as match_action,
                                case
                                    when trim(lower(co.contype)) != 'f' then ''
                                    when co.condeferrable and co.condeferred then
                                        'DEFERRABLE INITIALLY DEFERRED'
                                    when co.condeferrable and not co.condeferred then
                                        'DEFERRABLE INITIALLY IMMEDIATE'
                                    else
                                        'NOT DEFERRABLE'
                                end as deferrable_type
                            from pg_constraint co
                            where
                                co.conrelid = c.oid and
                                co.conislocal
                        ) q
                    ) as constraints
        """)

        query = query.replace("&indexes&", """
                    (
                        select jsonb_agg(q order by q.name)
                        from (
                            select
                                trim(lower(ic.relname)) as name,
                                pg_get_indexdef(i.indexrelid, 0, true) as definition
                            from pg_index i
                            join pg_class ic on
                                ic.oid = i.indexrelid
                            where
                                i.indrelid = c.oid and
                                not i.indisprimary and
                                not exists(
                                    select 1
                                    from pg_constraint co
                                    where co.conindid = ic.oid
                                )
                        ) q
                    ) as indexes
        """)

        query = query.replace("&triggers&", """
                    (
                        select jsonb_agg(q order by q.name)
                        from (
                            select
                                trim(lower(tr.tgname)) as name,
                                tr.tgenabled = 'D' as is_disabled,
                                pg_get_triggerdef(tr.oid) as definition
                            FROM pg_trigger tr
                            where
                                tr.tgrelid = c.oid and
                                not tr.tgisinternal
                        ) q
                    ) as triggers
        """)

        cursor.execute(query, [self.ExcludeSchemas])

        for row in cursor.fetchall():
            self.Objects.update(Table(None, row).Export())

        logging.info("Tables loaded = {0}".format(cursor.rowcount))

    @CalcDuration
    def GetFunction(self, cursor):
        cursor.execute("""
            select
                p.oid,
                trim(lower(n.nspname)) as schema,
                trim(lower(p.proname)) as proc,
                oidvectortypes(proargtypes) as args_in_types,
                pg_get_function_arguments(p.oid) as args_in,
                regexp_replace(regexp_replace(regexp_replace(pg_get_function_result(p.oid), '(?<=[A-Za-z\]])\, ', e'\,\n    ', 'igm'), 'table\(', e'TABLE\(\n    ', 'igm'), '\)$', e'\n\)', 'igm') as args_out,
                coalesce(p.procost, 0) as cost,
                coalesce(p.prorows, 0) as rows,
                trim(lower(o.rolname)) as owner,
                trim(lower(l.lanname)) as lang,
                obj_description(p.oid, 'pg_proc') as comment,
                case
                    when p.provolatile = 'i' then 'IMMUTABLE'
                    when p.provolatile = 's' then 'STABLE'
                    when p.provolatile = 'v' then 'VOLATILE'
                end || case
                    when p.proisstrict then ' STRICT'
                    else ''
                end || case
                    when not p.prosecdef then ''
                    else ' SECURITY DEFINER'
                end as volatility,
                1 < count(*) over (partition by n.nspname, p.proname) as has_duplicate,
                coalesce(trim(lower(t.typname)), '') = 'trigger' as is_trigger,
                replace(p.prosrc, E'\r', '') as code,
                p.proacl::varchar[] as acl
            from pg_proc p
            join pg_namespace n on
                n.oid = p.pronamespace and
                n.nspname !~* '^pg_temp' AND
                n.nspname !~* '^pg_toast' AND
                n.nspname != ALL(%s)
            join pg_language l on
                l.oid = p.prolang and
                l.lanname in ('sql','plpgsql','plpythonu','plpython3u','plproxy')
            join pg_roles o on
                o.oid = p.proowner
            join pg_type t on
                t.oid = p.prorettype
            order by 1
        """, [self.ExcludeSchemas])

        for row in cursor.fetchall():
            self.Objects.update(Function(None, row).Export())

        logging.info("Functions loaded = {0}".format(cursor.rowcount))

    @CalcDuration
    def GetView(self, cursor):
        query = """
            SELECT
                c.oid,
                trim(lower(n.nspname)) AS schema,
                trim(lower(c.relname)) AS name,
                trim(lower(r.rolname)) AS owner_name,
                trim(coalesce(obj_description(c.oid, 'pg_class'), '')) AS comment,
                pg_get_viewdef(c.oid, true) as definition,
                c.relacl::varchar[] AS acl,
                c.relkind = 'm' as is_materialized,
                &indexes&
            FROM pg_class c
            JOIN pg_namespace n ON
                n.oid = c.relnamespace AND
                n.nspname !~* '^pg_temp' AND
                n.nspname !~* '^pg_toast' AND
                n.nspname != ALL(%s)
            JOIN pg_roles r ON
                r.oid = c.relowner
            WHERE c.relkind in ('v','m')
            ORDER BY 2,3
        """

        query = query.replace("&indexes&", """
                (
                    select jsonb_agg(q order by q.name)
                    from (
                        select
                            trim(lower(ic.relname)) as name,
                            pg_get_indexdef(i.indexrelid, 0, true) as definition
                        from pg_index i
                        join pg_class ic on
                            ic.oid = i.indexrelid
                        where
                            i.indrelid = c.oid and
                            not i.indisprimary and
                            not exists(
                                select 1
                                from pg_constraint co
                                where co.conindid = ic.oid
                            )
                    ) q
                ) as indexes
        """)

        cursor.execute(query, [self.ExcludeSchemas])
        for row in cursor.fetchall():
            self.Objects.update(View(None, row).Export())

        logging.info("Views loaded = {0}".format(cursor.rowcount))

    @CalcDuration
    def GetSequence(self, cursor):
        cursor.execute("""
            SELECT
                c.oid,
                trim(lower(n.nspname)) AS schema,
                trim(lower(c.relname)) AS name,
                trim(lower(r.rolname)) AS owner,
                trim(coalesce(obj_description(c.oid, 'pg_class'), '')) AS comment,
                c.relacl::varchar[] AS acl,
                s.increment,
                s.minimum_value,
                s.maximum_value,
                s.cycle_option = 'YES' AS is_cycle,
                1 AS start,
                1 AS cache
            FROM pg_class c
            JOIN pg_namespace n ON
                n.oid = c.relnamespace AND
                n.nspname !~* '^pg_temp' AND
                n.nspname !~* '^pg_toast' AND
                n.nspname != ALL(%s)
            JOIN pg_roles r ON
                r.oid = c.relowner
            JOIN information_schema.sequences s ON
                s.sequence_schema = n.nspname and
                s.sequence_name = c.relname
            WHERE c.relkind = 'S'
            ORDER BY 2,3
        """, [self.ExcludeSchemas])

        for row in cursor.fetchall():
            self.Objects.update(Sequence(None, row).Export())

        logging.info("Sequences loaded = {0}".format(cursor.rowcount))

    @CalcDuration
    def GetForeignServer(self, cursor):
        cursor.execute("""
            select
                s.oid,
                s.srvname as server_name,
                w.fdwname as fdw_name,
                o.rolname as owner_name,
                s.srvoptions as options,
                s.srvacl::varchar[] AS acl,
                obj_description(s.oid, 'pg_foreign_server') AS comment
            from pg_foreign_server s
            join pg_roles o on
                o.oid = s.srvowner
            join pg_foreign_data_wrapper w on
                w.oid = s.srvfdw
        """, [self.ExcludeSchemas])

        for row in cursor.fetchall():
            self.Objects.update(ForeignServer(None, row).Export())

        logging.info("Foreign servers loaded = {0}".format(cursor.rowcount))

    @CalcDuration
    def GetForeignTable(self, cursor):
        cursor.execute("""
            select
                c.oid,
                n.nspname as schema_name,
                c.relname as table_name,
                o.rolname as owner_name,
                s.srvname as server_name,
                t.ftoptions as options,
                obj_description(c.oid, 'pg_class') AS comment,
                c.relacl::varchar[] AS acl,
                (
                    select array_agg(concat_ws(' ',
                        a.attname,
                        trim(lower(format_type(a.atttypid, a.atttypmod))),
                        case when a.attnotnull then 'NOT NULL' end
                    ))
                    from pg_attribute a
                    where
                        a.attrelid = c.oid and
                        a.attnum > 0
                ) as columns_list
            from pg_foreign_table t
            join pg_foreign_server s on
                s.oid = t.ftserver
            join pg_class c on
                c.oid = t.ftrelid
            join pg_roles o on
                o.oid = c.relowner
            join pg_namespace n on
                n.oid = c.relnamespace AND
                n.nspname !~* '^pg_temp' AND
                n.nspname !~* '^pg_toast' AND
                n.nspname != ALL(%s)
        """, [self.ExcludeSchemas])

        for row in cursor.fetchall():
            self.Objects.update(ForeignTable(None, row).Export())

        logging.info("Foreign tables loaded = {0}".format(cursor.rowcount))

    @CalcDuration
    def GetExtension(self, cursor):
        cursor.execute("""
            SELECT
                e.oid,
                n.nspname AS schema,
                o.rolname AS owner,
                e.extname AS name,
                e.extversion AS version
            FROM pg_extension e
            JOIN pg_namespace n ON
                n.oid = e.extnamespace
            JOIN pg_roles o ON
                o.oid = e.extowner
        """)

        for row in cursor.fetchall():
            self.Objects.update(Extension(None, row).Export())

        logging.info("Extensions loaded = {0}".format(cursor.rowcount))

    @CalcDuration
    def GetPublication(self, cursor):
        query = """
            select
                p.oid,
                p.pubname as name,
                r.rolname as owner,
                p.pubviaroot as is_via_root,
                p.puballtables as is_all_tables,
                concat_ws(', ',
                    case when p.pubinsert   then 'insert'   end,
                    case when p.pubupdate   then 'update'   end,
                    case when p.pubdelete   then 'delete'   end,
                    case when p.pubtruncate then 'truncate' end
                ) as actions,
                (
                    select array_agg(distinct concat_ws('.', n.nspname, c.relname)
                        order by concat_ws('.', n.nspname, c.relname))
                    from pg_publication_rel pt
                    join pg_class c on
                        c.oid = pt.prrelid
                    join pg_namespace n on
                        n.oid = c.relnamespace
                    where pt.prpubid = p.oid
                ) as tables
            from pg_publication p
            join pg_roles r on
                r.oid = p.pubowner
        """

        if self.Version <= 12:
            query = query.replace("p.pubviaroot", "FALSE")

        cursor.execute(query)
        for row in cursor.fetchall():
            self.Objects.update(Publication(None, row).Export())

        logging.info("Publications loaded = {0}".format(cursor.rowcount))

    @CalcDuration
    def GetSubscription(self, cursor):
        if not self.IsSuperUser:
            return

        cursor.execute("""
            select
                s.oid,
                s.subname as name,
                r.rolname as owner,
                s.subenabled as is_enabled,
                (
                    select string_agg(r, ' ')
                    from regexp_split_to_table(s.subconninfo, ' ', 'im') r
                    where r !~* '^password'
                ) as connect,
                s.subslotname as slot,
                s.subsynccommit as sync_commit,
                s.subpublications as publications,
                (
                    select array_agg(distinct concat_ws('.', n.nspname, c.relname)
                        order by concat_ws('.', n.nspname, c.relname))
                    from pg_subscription_rel st
                    join pg_class c on
                        c.oid = st.srrelid
                    join pg_namespace n on
                        n.oid = c.relnamespace
                    where st.srsubid = s.oid
                ) as tables
            from pg_subscription s
            join pg_roles r on
                r.oid = s.subowner
        """)

        for row in cursor.fetchall():
            self.Objects.update(Subscription(None, row).Export())

        logging.info("Subscriptions loaded = {0}".format(cursor.rowcount))

    @CalcDuration
    def GetEventTrigger(self, cursor):
        cursor.execute("""
            select
                t.oid,
                t.evtname as name,
                r.rolname as owner,
                upper(t.evtevent) as event,
                t.evttags as tags,
                format('%s.%s(%s)', n.nspname, p.proname, oidvectortypes(p.proargtypes)) as fnc,
                case t.evtenabled
                    when 'D' then 'DISABLE'
                    when 'R' THEN 'ENABLE REPLICA'
                    when 'A' THEN 'ENABLE ALWAYS'
                    else 'ENABLE'
                end as status
            from pg_event_trigger t
            join pg_roles r on
                r.oid = t.evtowner
            join pg_proc p on
                p.oid = t.evtfoid
            join pg_namespace n on
                n.oid = p.pronamespace
        """)

        for row in cursor.fetchall():
            self.Objects.update(EventTrigger(None, row).Export())

        logging.info("Event triggers loaded = {0}".format(cursor.rowcount))

    @CalcDuration
    def GetCast(self, cursor):
        cursor.execute("""
            select
                c.oid,
                pg_catalog.format_type(ts.oid,ts.typtypmod) as type_from,
                pg_catalog.format_type(tt.oid,tt.typtypmod) as type_to,
                case c.castcontext
                    when 'i' then 'IMPLICIT'
                    when 'a' then 'ASSIGNMENT'
                    when 'e' then 'EXPLICIT'
                end as context,
                case
                    when p.oid is null then null
                    else format('%s.%s(%s)', pn.nspname, p.proname, oidvectortypes(p.proargtypes))
                end as func
            from pg_cast c
            join pg_type ts on
                ts.oid = c.castsource
            join pg_type tt on
                tt.oid = c.casttarget
            left join pg_proc p on
                p.oid = c.castfunc
            left join pg_namespace pn on
                pn.oid = p.pronamespace
            where c.oid > 16383
        """)

        for row in cursor.fetchall():
            self.Objects.update(Cast(None, row).Export())

        logging.info("Casts loaded = {0}".format(cursor.rowcount))
