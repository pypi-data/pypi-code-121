import logging, random, string, os
from psycopg2.sql import SQL, Literal
from django.db import connection
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import base, call_command, get_commands
from zut.pgsql import deploy_paths, revert_paths
from zut.django.migrations import remake_migrations

logger = logging.getLogger(__name__)


class EnsureSuperUserCommand(base.BaseCommand):
    help = "Create a super user if none exist"
    default_username = "admin"

    def default_email(self, username):
        return f"{username}@example.com"
    
    def default_password(self, username):
        if username == self.default_username:
            if "ADMIN_PASSWORD" in os.environ and os.environ["ADMIN_PASSWORD"]:
                return os.environ["ADMIN_PASSWORD"]
            elif settings.DEBUG:
                return "admin"
        return None
    
    def add_arguments(self, parser):
        parser.add_argument("--username")
        parser.add_argument("--email")
        parser.add_argument("--password")

    def handle(self, username=None, email=None, password=None, **kwargs):
        User = get_user_model()

        # Search user
        users = User.objects.filter(is_superuser=True)
        if users:
            logger.info("superuser already exist: %s", ", ".join([user.username for user in users]))

            if username and password:
                # Change password if provided
                user = users.filter(username=username).first()
                if not user:
                    logger.error("superuser %s not found", username)
                    return
                else:
                    logger.info("changing password for superuser %s", username)
                    user.set_password(password)
                    user.save()

            return

        # Create user
        if not username:
            username = self.default_username
        
        if not email:
            email = self.default_email(username)

        created_password = False
        if password is None:
            password = self.default_password(username)
            if not password:
                password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
                created_password = True

        if created_password:
            logger.info("create superuser \"%s\" with password: %s", username, password)
        else:
            logger.info("create superuser \"%s\"", username)

        User.objects.create_superuser(username=username, email=email, password=password)


class DbCommand(base.BaseCommand):
    remake_migrations_after = {}

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers()
            
        cmd_parser = subparsers.add_parser("deploy")
        self.deployrevert_configure(cmd_parser)
        cmd_parser.set_defaults(func=self.deploy)
            
        cmd_parser = subparsers.add_parser("revert")
        self.deployrevert_configure(cmd_parser)
        cmd_parser.set_defaults(func=self.revert)
        
        cmd_parser = subparsers.add_parser("reinit")
        self.reinit_configure(cmd_parser)
        cmd_parser.set_defaults(func=self.reinit)
    

    def handle(self, func=None, **kwargs):
        if not func:
            raise base.CommandError("missing db subcommand")
        func(**kwargs)


    def deployrevert_configure(self, parser):
        parser.add_argument("paths", nargs="+")

    def deploy(self, paths, **kwargs):
        deploy_paths(connection, *paths)

    def revert(self, paths, **kwargs):
        revert_paths(connection, *paths)

    def reinit_configure(self, parser):
        parser.add_argument("--drop", dest="action", action="store_const", const="drop")
        parser.add_argument("--bak", dest="action", action="store_const", const="bak")
        parser.add_argument("--bak-to", dest="action", type=str)
        
    def reinit(self, action=None, **kwargs):
        if not settings.DEBUG:
            raise base.CommandError("reinit may be used only in DEBUG mode")
        if not action:
            raise base.CommandError("please confirm what to do with current data: --drop, --bak or --bak-to")

        if action == "drop":
            self.drop()
        else:
            self.move_to_schema(action)

        remake_migrations(after=self.remake_migrations_after)
        
        logger.info("migrate")
        call_command("migrate")

        logger.info("ensuresuperuser")
        call_command("ensuresuperuser")

        defined_commands = get_commands()

        if "seed" in defined_commands:
            logger.info("seed")
            call_command("seed")

    def move_to_schema(self, new_schema, old_schema="public"):
        sql = """do language plpgsql
$$declare
    old_schema name = {};
    new_schema name = {};
    sql_query text;
begin
	sql_query = format('create schema %I', new_schema);

    raise notice 'applying %', sql_query;
    execute sql_query;
   
    for sql_query in
        select
            format('alter %s %I.%I set schema %I', case when table_type = 'VIEW' then 'view' else 'table' end, table_schema, table_name, new_schema)
        from information_schema.tables
        where table_schema = old_schema
        and table_name not in ('geography_columns', 'geometry_columns', 'spatial_ref_sys') -- postgis
    loop
        raise notice 'applying %', sql_query;
        execute sql_query;
    end loop;
end;$$;
"""

        with connection.cursor() as cursor:
            cursor.execute(SQL(sql).format(Literal(old_schema), Literal(new_schema if new_schema else "public")))


    def drop(self, schema="public"):
        sql = """do language plpgsql
$$declare
    old_schema name = {};
    sql_query text;
begin
	-- First, remove foreign-key constraints
    for sql_query in
        select
            format('alter table %I.%I drop constraint %I', table_schema, table_name, constraint_name)
        from information_schema.table_constraints
        where table_schema = old_schema and constraint_type = 'FOREIGN KEY'
        and table_name not in ('geography_columns', 'geometry_columns', 'spatial_ref_sys') -- postgis
    loop
        raise notice 'applying %', sql_query;
        execute sql_query;
    end loop;

	-- Then, drop tables
    for sql_query in
        select
            format('drop %s if exists %I.%I cascade'
                ,case when table_type = 'VIEW' then 'view' else 'table' end
                ,table_schema
                ,table_name
            )
        from information_schema.tables
        where table_schema = old_schema
        and table_name not in ('geography_columns', 'geometry_columns', 'spatial_ref_sys') -- postgis
    loop
        raise notice 'applying %', sql_query;
        execute sql_query;
    end loop;
end;$$;
"""

        with connection.cursor() as cursor:
            cursor.execute(SQL(sql).format(Literal(schema)))
