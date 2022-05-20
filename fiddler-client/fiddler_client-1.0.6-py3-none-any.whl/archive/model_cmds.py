import logging
import pandas as pd
import yaml

from fiddler.fiddler_api import FiddlerApi

LOG = logging.getLogger(__name__)

def execute_cmd(args):
    client = FiddlerApi(url=f'http://localhost:{args.port}', org_id=args.org)
    df = pd.read_csv('dataset.csv')
    if args.index:
        df = df.loc[[int(args.index)]]
    else:
        df = df.head()
    LOG.info('Input: ')
    LOG.info(df.head(5))
    result = client.run_model(args.project, args.model, df)
    LOG.info('Result: ')
    LOG.info(result)


def explain_cmd(args):
    client = FiddlerApi(url=f'http://localhost:{args.port}', org_id=args.org)
    df = pd.read_csv('dataset.csv')
    if args.index:
        df = df.loc[[int(args.index)]]
    else:
        df = df.head(1)
    LOG.info('Input: ')
    LOG.info(df.head(5))
    if args.explanations:
        explanations = args.explanations
    else:
        explanations = 'shap'
    result = client.run_explanation(
        args.project,
        args.model,
        df,
        dataset_id='titanic',
        explanations=explanations,
    )
    LOG.info('Output: ')
    LOG.info(yaml.dump(result))
