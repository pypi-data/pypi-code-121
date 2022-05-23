import asyncio
import datetime
import functools
import os
import re
import urllib.parse
from pathlib import Path
from typing import List, Optional
from datetime import datetime, date, timedelta

import aiohttp
import gidgethub
import typer
import pandas
from gidgethub.aiohttp import GitHubAPI
import cachetools
import peewee
import more_itertools as mi
import matplotlib.pyplot
import dateutil.parser
import sqlite3

from gha_stats import __version__, config
from gha_stats.database import database, Job, Run

cli = typer.Typer()


def make_sync(fn):
    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(fn(*args, **kwargs))

    return wrapped


def prepare_database(dbfile: Path):
    database.init(dbfile)
    database.connect()
    database.create_tables([Job, Run])


@cli.command(help="")
@make_sync
async def collect(
    database: Path = typer.Argument(..., dir_okay=False, exists=True),
    repo: str = typer.Argument(...),
    token: str = typer.Option(
        config.GH_TOKEN,
        help="Github API token to use. Can be supplied with environment variable GH_TOKEN",
    ),
    since: Optional[datetime] = None,
    skip: bool = True,
):
    prepare_database(database)

    cache = cachetools.LRUCache(maxsize=500)
    if since is not None:
        since: date = since.date()

    most_recent = Run.select().order_by(Run.created_at.desc()).limit(1).first()

    async with aiohttp.ClientSession(loop=asyncio.get_event_loop()) as session:
        gh = GitHubAPI(session, __name__, oauth_token=token, cache=cache)
        url = f"/repos/{repo}/actions/runs"
        if since is not None:
            url += f"?created=%3A>{since:%Y-%m-%d}"
        elif skip and most_recent is not None:
            #  print(most_recent.created_at, repr(most_recent.created_at))
            created_at = dateutil.parser.parse(most_recent.created_at) - timedelta(
                days=1
            )
            url += f"?created=%3A>={created_at:%Y-%m-%d}"

        async for run in gh.getiter(url, iterable_key="workflow_runs"):
            rows = []

            print(f"- run id: {run['id']} created_at: {run['created_at']}")

            kw = dict(
                created_at=dateutil.parser.parse(run["created_at"]),
                updated_at=dateutil.parser.parse(run["updated_at"]),
                run_started_at=dateutil.parser.parse(run["run_started_at"]),
                **{
                    k: run[k]
                    for k in [
                        "id",
                        "name",
                        "head_branch",
                        "head_sha",
                        "path",
                        "run_number",
                        "event",
                        "status",
                        "conclusion",
                        "workflow_id",
                        "check_suite_id",
                        "url",
                        "html_url",
                        "run_attempt",
                        "jobs_url",
                    ]
                },
            )

            try:
                run_model = Run.create(**kw)
            except peewee.IntegrityError:
                try:
                    Run.replace(**kw).execute()
                except:
                    print(kw)
                    raise
                continue

            jobs = []

            print("Getting jobs")

            async for job in gh.getiter(run["jobs_url"], iterable_key="jobs"):
                row = {
                    "started_at": dateutil.parser.parse(job["started_at"]),
                    "completed_at": None
                    if job["completed_at"] is None
                    else dateutil.parser.parse(job["completed_at"]),
                    "run": run_model,
                }
                row.update(
                    {
                        k: job[k]
                        for k in [
                            "id",
                            "head_sha",
                            "url",
                            "html_url",
                            "status",
                            "conclusion",
                            "name",
                            "check_run_url",
                        ]
                    }
                )
                jobs.append(row)

                print(f"Inserting {len(jobs)} jobs")

            Job.insert_many(jobs).on_conflict_replace().execute()


@cli.command()
def plot(
    database: Path = typer.Argument(..., dir_okay=False, exists=True),
    output: Path = typer.Option(Path.cwd(), "--output", "-o", file_okay=False),
    format: str = typer.Option("pdf", "--format", "-f"),
):
    prepare_database(database)
    if not output.exists():
        output.mkdir(parents=True)

    con = sqlite3.connect(database)

    df = pandas.read_sql(
        "SELECT a.*, r.head_branch, r.name as run_name FROM job as a JOIN run as r ON a.run_id = r.id WHERE r.created_at > '2022-01-01 00:00:00+00:00' AND r.conclusion != 'skipped' ORDER BY r.created_at ASC",
        con,
    )

    df.started_at = pandas.to_datetime(df.started_at)
    df.completed_at = pandas.to_datetime(df.completed_at)
    df["duration"] = (df.completed_at - df.started_at).dt.total_seconds()
    df["day"] = df.started_at.dt.date
    df["fqn"] = df[["run_name", "name"]].agg(" / ".join, axis=1)

    for w, wdf in df[(df.conclusion == "success")].groupby("run_name"):
        for i, chunk in enumerate(mi.chunked(wdf.groupby("name"), 6)):
            fig, ax = matplotlib.pyplot.subplots(figsize=(15, 5))
            for g, gdf in chunk:
                # display(gdf)
                gdf.duration /= 60
                ddf = (
                    gdf.resample("d", on="started_at")
                    .agg({"duration": ["mean", "std", "size"]})
                    .dropna()
                )
                if ddf.empty:
                    continue
                # if np.all(ddf.duration < 5*60):
                #     continue
                # display(ddf)
                # display(ddf.columns)
                # ddf.index = ddf[day
                # ddf.duration /= 60
                # ddf.plot(y="mean", ax=ax, label=g)
                up = ddf["duration", "mean"] + ddf["duration", "std"]
                down = ddf["duration", "mean"] - ddf["duration", "std"]
                pc = ax.fill_between(ddf.index, down, up, alpha=0.2)
                ax.plot(
                    ddf.index,
                    ddf["duration", "mean"],
                    label=f"{w} / {g}",
                    c=pc.get_fc(),
                    alpha=1,
                )
                # print(ax.lines[-1].get_color())
                # ax.plot(ddf.index, ddf["duration", "std"], label=g)

            ax.legend(ncol=3)
            ymin, ymax = ax.get_ylim()
            ax.set_ylim(ymin, 1.2 * ymax)
            ax.set_xlabel("date")
            ax.set_ylabel("duration [min]")
            fig.tight_layout()
            fig.savefig(str(output / f"citime_{w}_{i}.{format}"))


@cli.command()
def init(
    database: Path = typer.Argument(..., dir_okay=False),
):
    prepare_database(database)


@cli.callback()
def main():
    pass


main.__doc__ = """
GitHub Actions statistics, version {version}
""".format(
    version=__version__
)
