#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime

import click
from cgbeacon2.cli.update import genes as update_genes
from cgbeacon2.models.user import User
from cgbeacon2.utils.add import add_dataset, add_user, add_variants
from cgbeacon2.utils.parse import count_variants, extract_variants, get_vcf_samples, merge_intervals
from cgbeacon2.utils.update import update_dataset, update_event
from flask.cli import current_app, with_appcontext
from pymongo.results import InsertOneResult


@click.group()
def add():
    """Add items to database using the CLI"""


@add.command()
@with_appcontext
@click.pass_context
def demo(ctx) -> None:
    """Loads demo data into the database:
    A test dataset with public access (genome assembly GRCh37)
    Demo SNV variants filtered using a demo gene panel
    Demo SV variants
    """

    # Dropping any existing database collection from demo database
    collections = current_app.db.list_collection_names()
    click.echo(f"\n\nDropping the following collections--->{ ','.join(collections) }\n")
    for collection in collections:
        current_app.db.drop_collection(collection)

    # Creating public dataset
    ds_id = "test_public"
    ds_name = "Test public dataset"
    desc = "Test dataset with variants in genome build GRCh37"
    authlevel = "public"
    sample = "ADM1059A1"

    # Invoke update genes command
    ctx.invoke(update_genes)

    # Invoke add dataset command
    ctx.invoke(dataset, did=ds_id, name=ds_name, desc=desc, authlevel=authlevel)

    # Invoke add variants command to import all SNV variants from demo sample
    ctx.invoke(
        variants,
        ds=ds_id,
        vcf="cgbeacon2/resources/demo/test_trio.vcf.gz",
        sample=[sample],
    )

    # Invoke add variants command to import all SV variants from demo sample
    ctx.invoke(
        variants,
        ds=ds_id,
        vcf="cgbeacon2/resources/demo/test_trio.SV.vcf.gz",
        sample=[sample],
    )

    # Invoke add variants command to import also BND variants from separate VCF file
    ctx.invoke(
        variants,
        ds=ds_id,
        vcf="cgbeacon2/resources/demo/BND.SV.vcf",
        sample=[sample],
    )

    # Invoke add user command to creating an authorized user (via X-Auth-Token) for using the APIs
    demo_user = ctx.invoke(user, uid="DExterMOrgan", name="Dexter Morgan", token="DEMO")
    click.echo(f"\n\nAuth token for using the API:{demo_user.token}\n")


@add.command()
@click.option("--uid", type=click.STRING, nargs=1, required=True, help="User ID")
@click.option("--name", type=click.STRING, nargs=1, required=True, help="User name")
@click.option(
    "--token",
    type=click.STRING,
    nargs=1,
    required=False,
    help="If not specified, the token will be created automatically",
)
@click.option("--desc", type=click.STRING, nargs=1, required=False, help="User description")
@click.option("--url", type=click.STRING, nargs=1, required=False, help="User url")
@with_appcontext
def user(uid, name, token, desc, url) -> User:
    """Creates a new user for adding/removing variants using the REST API"""

    if " " in uid:
        click.echo("User ID should not contain any space")
        return
    user_info = dict(
        _id=uid,
        name=name,
        token=token,
        description=desc,
        url=url,
        created=datetime.datetime.now(),
    )
    user = User(user_info)
    add_user(current_app.db, user)
    return user


@add.command()
@click.option("--did", type=click.STRING, nargs=1, required=True, help="dataset ID")
@click.option("--name", type=click.STRING, nargs=1, required=True, help="dataset name")
@click.option(
    "--build",
    type=click.Choice(["GRCh37", "GRCh38"]),
    nargs=1,
    help="Genome assembly (default:GRCh37)",
    default="GRCh37",
)
@click.option(
    "--authlevel",
    type=click.Choice(["public", "registered", "controlled"], case_sensitive=False),
    help="the access level of this dataset",
    required=True,
)
@click.option("--desc", type=click.STRING, nargs=1, required=False, help="dataset description")
@click.option(
    "--version",
    type=click.STRING,
    nargs=1,
    required=False,
    help="dataset version, i.e. v1.0",
)
@click.option("--url", type=click.STRING, nargs=1, required=False, help="external url")
@click.option("--update", is_flag=True)
@with_appcontext
def dataset(did, name, build, authlevel, desc, version, url, update) -> None:
    """Creates a dataset object in the database or updates a pre-existing one"""

    dataset_obj = {
        "_id": did,
        "name": name,
        "description": desc,
        "assembly_id": build,
        "authlevel": authlevel,
        "version": version,
        "external_url": url,
    }
    try:
        inserted_id = add_dataset(database=current_app.db, dataset_dict=dataset_obj, update=update)
        if inserted_id:
            click.echo("Dataset collection was successfully updated")
            # register the event in the event collection
            update_event(current_app.db, did, "dataset", True)
        else:
            click.echo("An error occurred while updating dataset collection")

    except ValueError as vex:
        click.echo(vex)


@add.command()
@click.option("--ds", type=click.STRING, nargs=1, required=True, help="dataset ID")
@click.option("--vcf", type=click.Path(exists=True), required=True)
@click.option(
    "--sample",
    type=click.STRING,
    multiple=True,
    required=True,
    help="one or more samples to save variants for",
)
@click.option(
    "--panel",
    type=click.Path(exists=True),
    multiple=True,
    required=False,
    help="one or more bed files containing genomic intervals",
)
@with_appcontext
def variants(ds, vcf, sample, panel) -> None:
    """Add variants from a VCF file to a dataset"""
    # make sure dataset id corresponds to a dataset in the database

    dataset = current_app.db["dataset"].find_one({"_id": ds})
    if dataset is None:
        click.echo(f"Couldn't find any dataset with id '{ds}' in the database")
        raise click.Abort()

    # Check if required sample(s) are contained in the VCF
    vcf_samples = get_vcf_samples(vcf)

    if not all(samplen in vcf_samples for samplen in sample):
        click.echo(
            f"One or more provided sample was not found in the VCF file. Valida samples are: { ','.join(vcf_samples)}"
        )
        raise click.Abort()
    custom_samples = set(sample)  # set of samples provided by users

    filter_intervals = None
    if len(panel) > 0:
        # create BedTool panel with genomic intervals to filter VCF with
        filter_intervals = merge_intervals(list(panel))

    vcf_obj = extract_variants(vcf_file=vcf, samples=custom_samples, filter=filter_intervals)

    if vcf_obj is None:
        raise click.Abort()

    nr_variants = count_variants(vcf_obj)
    if nr_variants == 0:
        click.echo("Provided VCF file doesn't contain any variant")
        raise click.Abort()

    vcf_obj = extract_variants(vcf_file=vcf, samples=custom_samples, filter=filter_intervals)

    # ADD variants
    added = add_variants(
        database=current_app.db,
        vcf_obj=vcf_obj,
        samples=custom_samples,
        assembly=dataset["assembly_id"],
        dataset_id=ds,
        nr_variants=nr_variants,
    )
    click.echo(f"{added} variants loaded into the database")

    if added > 0:
        # Update dataset object accordingly
        update_dataset(database=current_app.db, dataset_id=ds, samples=custom_samples, add=True)
