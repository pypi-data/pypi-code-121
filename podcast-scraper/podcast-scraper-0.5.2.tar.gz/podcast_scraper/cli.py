import click

from podcast_scraper.csv_manager import CsvManager
from podcast_scraper.france_culture import FranceCulture
from podcast_scraper.monde_diplo import MondeDiplo


@click.group()
def click_france_culture():
    pass


@click_france_culture.command()
@click.option(
    "--url",
    default="https://www.franceculture.fr/emissions/carbone-14-le-magazine-de-larcheologie",
)
@click.option("--pages", default=-1)
@click.option("--output-path")
def france_culture(url, pages, output_path):
    """Get podcast url for France Culture"""
    FranceCulture(url).print_content(pages).write_csv(output_path)


@click.group()
def click_monde_diplo():
    pass


@click_monde_diplo.command()
@click.option(
    "--url",
    default="https://www.monde-diplomatique.fr/audio?debut_sons=0#pagination_sons",
)
@click.option("--pages", default=-1)
def monde_diplo(url, pages):
    """Get podcast url for Monde Diplo"""
    MondeDiplo().print_urls(url, pages)


@click.group()
def click_csv():
    pass


@click_csv.command()
@click.option("--csv-path")
@click.option("--podcast-path")
@click.option("--download", is_flag=True)
@click.option("--tag", is_flag=True)
def csv(csv_path, podcast_path, download, tag):
    """Download or tag the podcast defined in a csv"""
    cm = CsvManager().with_csv(csv_path).with_output(podcast_path)
    if download:
        cm.download()
    if tag:
        cm.replace_tags()


cli = click.CommandCollection(
    sources=[click_france_culture, click_monde_diplo, click_csv]
)

if __name__ == "__main__":
    cli()
