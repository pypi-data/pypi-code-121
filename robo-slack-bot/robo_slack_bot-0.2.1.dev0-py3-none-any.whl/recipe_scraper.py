#!/bin/env python3

import sys
import logging
import argparse
import datetime
import validators
from recipe_scrapers import scrape_me
from flask import Flask, jsonify, request
from flask_cors import CORS

__version__ = '0.1.0'


def scraper(url):
    """Scrape a recipe from a website into a dictionary

    Args:
        url (string): the url to scrape

    Returns:
        dict: dictionary with the recipe details
    """
    logging.info('scraper called')
    try:
        if validators.url(url) is True:
            recipe_scraper = scrape_me(url)
            recipe_scraper_url = url
            recipe_scraper_totaltime = recipe_scraper.total_time()
            recipe_scraper_nutrients = recipe_scraper.nutrients()
            recipe_scraper_ingredients_raw = recipe_scraper.ingredients()
            recipe_scraper_ingredients = '\n'.join(recipe_scraper.ingredients())
            recipe_scraper_title = recipe_scraper.title()
            recipe_details = {
                "timestamp": datetime.datetime.now().isoformat(),
                "week": datetime.datetime.now().isocalendar()[1],
                "recipe_title": str(recipe_scraper_title),
                "recipe_scraper_totaltime": str(recipe_scraper_totaltime),
                "recipe_url": str(recipe_scraper_url),
                "recipe_ingredients": str(recipe_scraper_ingredients),
            }
            for nutrients in recipe_scraper_nutrients:
                recipe_details[nutrients] = str(
                    recipe_scraper_nutrients[nutrients].split()[0])
            logging.debug('Recipe Details=\'%s\'', recipe_details)
            logging.info('scraper finished')
            return recipe_details
        else:
            logging.error('Invalid URL')
            return 'Invalid URL'

    except Exception as e:
        logging.error("Exception: " + str(e))


def check_debug(args):
    """Check if debuging is set from the command line

    Args:
        args (dict): arguments from the command line

    Returns:
        object: Looging type object
    """

    if args.debug:
        return logging.DEBUG
    else:
        return logging.INFO


def arg_parser():
    """ Parse command line arguments

    Returns:
        argparse.Namespace: Parsed arguments
    """
    try:
        parser = argparse.ArgumentParser(description='Slack Bot', add_help=True, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('--debug', help='Debug mode', action='store_true', required=False)
        parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)
        parser.add_argument('--url', help='URL to scrape', required=False)
        parser.add_argument('--api-service', help='Run the API service', action='store_true', default=False)
        parser.add_argument('--port', help='Port to run the API service on', action='store', default='8000')
        parser.add_argument('--ip', help='IP to run the API service on', action='store', default='0.0.0.0')
        parser.add_argument('--pass-to-queue-manager', help='Pass the recipe to elasticsearch', action='store_true', default=False)
        parser.add_argument('--queue-manager-url', help='URL to the queue manager', action='store', default='http://localhost:5000')

  #  if  url or queue_manager_url is not set, then exit
        if not parser.parse_args().url and not parser.parse_args().api_service:
            logging.error('URL or queue_manager_url is not set. See helps')
            parser.print_help()
            sys.exit(1)

        return parser.parse_args()
    except Exception as e:
        print(e)
        raise
    except KeyboardInterrupt:
        print("Keyboard interrupt")
        raise


def create_app(config=None):
    """Create the flask app

    Args:
        config (str, optional): Flask config . Defaults to None.

    Returns:
        obj: Flask OBJ
    """
    app = Flask(__name__)

    # See http://flask.pocoo.org/docs/latest/config/
    app.config.update(dict(DEBUG=arg_parser().debug,))
    app.config.update(config or {})

    # Setup cors headers to allow all domains
    # https://flask-cors.readthedocs.io/en/latest/
    CORS(app)

    # Definition of the routes. Put them into their own file. See also
    # Flask Blueprints: http://flask.pocoo.org/docs/latest/blueprints
    @app.route("/api/v1/recipe_details", methods=['POST'])
    def recipe_details():
        try:
            # read the data from the POST body
            data = request.get_json()
            logging.info("data: " + str(data))
            # get the url from the data
            url = data.get('url')
            logging.info("url: " + str(url))
            recipe_details = scraper(url)
            logging.info("recipe_details: " + str(recipe_details))
            # return status code 200 OK
            if recipe_details =="Invalid URL":
                return jsonify({"status": "ok", "code": "400", "recipe": recipe_details}), 400
            else:
                return jsonify({"status": "ok", "code": "200", "recipe": recipe_details}), 200

        except Exception as e:
            logging.error("Exception: " + str(e))
    return app


def args_mgmt(args):
    """manage the args input from the command line

    Args:
        args (obj): arguments given from the command line
    """

    try:
        if args.url and args.api_service:
            logging.error("You can't pass a url and run the API service at the same time")
            sys.exit(1)
        if args.pass_to_queue_manager:
            if not args.queue_manager_url:
                logging.error("Queue Manager URL is needed if pass-to-queue-manager is enabled")
        if args.api_service:
            app = create_app()
            app.run(host=args.ip, port=int(args.port))
        else:
            if args.url:
                recipe_details = scraper(args.url)
                print(recipe_details)
            # else:
            #     logging.error("No url provided, use help for more info")

    except Exception as e:
        logging.error("Exception: " + str(e))


def main():
    """ Main functionp

    Returns:
        None
    """
    try:
        args = arg_parser()
        log_format = '%(asctime)s - %(levelname)5s - %(filename)20s:%(lineno)5s - %(funcName)20s()  - %(message)s'
        logging.basicConfig(level=check_debug(args), format=log_format)
        logging.debug('Arguments: ' + str(args))
        args_mgmt(args)
    except Exception as e:
        print(e)
        raise


if __name__ == '__main__':
    main()
