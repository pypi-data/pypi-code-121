import peewee

database = peewee.SqliteDatabase(None)


class Model(peewee.Model):
    class Meta:
        database = database


class Run(Model):
    id = peewee.IntegerField(primary_key=True, unique=True)
    name = peewee.CharField()
    head_branch = peewee.CharField()
    head_sha = peewee.CharField(max_length=40)
    path = peewee.CharField()
    run_number = peewee.IntegerField()
    event = peewee.CharField()
    status = peewee.CharField()
    conclusion = peewee.CharField(null=True)
    workflow_id = peewee.IntegerField()
    check_suite_id = peewee.IntegerField()
    url = peewee.TextField()
    html_url = peewee.TextField()
    created_at = peewee.DateTimeField(index=True)
    updated_at = peewee.DateTimeField()
    run_attempt = peewee.IntegerField()
    run_started_at = peewee.DateTimeField()
    jobs_url = peewee.TextField()


class Job(Model):
    id = peewee.IntegerField(primary_key=True, unique=True)
    run = peewee.ForeignKeyField(Run, backref="jobs")
    head_sha = peewee.CharField(max_length=40)
    url = peewee.TextField()
    html_url = peewee.TextField()
    status = peewee.CharField()
    conclusion = peewee.CharField(null=True)
    started_at = peewee.DateTimeField()
    completed_at = peewee.DateTimeField(null=True)
    name = peewee.CharField()
    check_run_url = peewee.TextField()
