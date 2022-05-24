import typer
import logging

from . import nlp

install_app = typer.Typer()

@install_app.command()
def install_model():
    logging.info('installing spacy model')
    import spacy
    spacy.cli.download('en_core_web_lg')

app = typer.Typer()


@app.command()
def check(text: str = typer.Argument(..., help="Text to check"),
        max_sentence_length: int = typer.Option(30, "--max-sentence-length", "-m", help="Maximum sentence length"),
        use_statistical_sentencizer: bool = typer.Option(False, "--use-statistical-sentencizer", "-s", help="Use statistical sentencizer instead of rule-based sentencizer"),
        ignore_sentence_length: bool = typer.Option(False, "--ignore-sentence-length", "-l", help="Disable passive voice check"),
        ignore_passive_voice: bool = typer.Option(False, "--ignore-passive-voice", "-p", help="Disable passive voice check")):
    """
    Check if the text satisfies some simple rules for having straightforward formal writing. This includes:
    - raising warnings for sentences that are too long
    - raising warnings for sentences that use passive voice
    """
    logging.debug(f"max_sentence_length: {max_sentence_length}, text length: {len(text)}")
    nlp.check_text(text,
            max_sentence_length=max_sentence_length,
            use_statistical_sentencizer=use_statistical_sentencizer,
            ignore_sentence_length=ignore_sentence_length,
            ignore_passive_voice=ignore_passive_voice)
