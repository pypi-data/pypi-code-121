#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import click
from cgbeacon2.utils.delete import delete_dataset, delete_variants
from cgbeacon2.utils.update import update_dataset, update_event
from flask.cli import current_app, with_appcontext


@click.group()
def delete():
    """Delete items from database using the CLI"""
    pass


@delete.command()
@with_appcontext
@click.option("--id", type=click.STRING, nargs=1, required=True, help="dataset ID")
def dataset(id) -> None:
    """Delete a dataset using its _id key"""

    click.echo(f"deleting dataset with id '{id}' from database")

    deleted = delete_dataset(database=current_app.db, id=id)

    if deleted is None:
        click.echo("Aborting")
    elif deleted == 0:
        click.echo(f"Coundn't find a dataset with id '{id}' in database.")
    elif deleted == 1:
        # register the event in the event collection
        update_event(current_app.db, id, "dataset", False)
        click.echo("Dataset was successfully deleted")


@delete.command()
@with_appcontext
@click.option("--ds", type=click.STRING, nargs=1, required=True, help="dataset ID")
@click.option(
    "--sample",
    type=click.STRING,
    multiple=True,
    required=True,
    help="one or more samples to remove variants for",
)
def variants(ds, sample) -> None:
    """Remove variants for one or more samples of a dataset"""

    click.confirm(
        f"Deleting variants for sample {sample}, dataset '{ds}'. Do you want to continue?",
        abort=True,
    )

    # Make sure dataset exists and contains the provided sample(s)
    dataset = current_app.db["dataset"].find_one({"_id": ds})
    if dataset is None:
        click.echo(f"Couldn't find any dataset with id '{ds}' in the database")
        raise click.Abort()

    for s in sample:
        if s not in dataset.get("samples", []):
            click.echo(f"Couldn't find any sample '{s}' in the sample list of dataset 'dataset'")
            raise click.Abort()

    updated, removed = delete_variants(current_app.db, ds, sample)
    click.echo(f"Number of variants updated:{updated}, removed:{removed}")

    if updated + removed > 0:
        # remove sample(s) from dataset
        update_dataset(database=current_app.db, dataset_id=ds, samples=list(sample), add=False)
