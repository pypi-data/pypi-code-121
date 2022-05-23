import click
import uvicorn
import logging

from app.config import settings
from app.main import app

logger = logging.getLogger(__name__)


@click.group()
def cli():
    pass


@cli.command()
def run():
    logger.info(f"run in {settings.host}:{settings.port}")
    uvicorn.run(app, host=settings.host, port=settings.port)
