#!/usr/bin/env python
# coding: utf-8

import argparse
import json
import signal
import sys
from typing import Optional

import langdetect
import requests
from bs4 import BeautifulSoup, NavigableString  # noqa
from langdetect.lang_detect_exception import LangDetectException
from tqdm import tqdm

try:
    import ray
except ModuleNotFoundError:
    pass


class UnknownPagesNum(Exception):
    pass


def keyboard_interrupt_handler(sig: int, _) -> None:
    print(f'KeyboardInterrupt (id: {sig}) has been caught...')
    print('Terminating the session gracefully...')
    sys.exit(0)


def get_quotes(pg_num: int, author: str) -> list:
    page = requests.get(
        'https://www.goodreads.com/quotes/search?commit=Search&page='
        f'{pg_num}&q={author}&utf8=%E2%9C%93')
    soup = BeautifulSoup(page.text, 'html.parser')

    quote = soup.find(class_='leftContainer')
    if not quote:
        return []
    quote_list = quote.find_all(class_='quoteDetails')

    quotes_in_page = []
    for quote in quote_list:
        outer = quote.find(class_='quoteText')
        inner_text = [el for el in outer if isinstance(el, NavigableString)]
        inner_text = [x.replace('\n', '') for x in inner_text]
        quote_text = '\n'.join(inner_text[:-4])
        quotes_in_page.append(quote_text.strip())
    return quotes_in_page


try:

    @ray.remote
    def _get_quotes(pg_num: int, author: str) -> list:
        return get_quotes(pg_num, author)
except NameError:
    if '--enable-multiprocessing' in sys.argv:
        raise ModuleNotFoundError('Multiprocessing requires `ray`! '
                                  'Install with: `pip install ray`')


def quotes_by_author(author,
                     num_pages: Optional[int] = None,
                     enable_multiprocessing: Optional[bool] = False) -> list:
    author = author.replace(' ', '+')

    if not num_pages:
        try:
            pg = requests.get(
                'https://www.goodreads.com/quotes/search?commit=Search&page=1'
                f'&q={author}&utf8=%E2%9C%93')
            pages = BeautifulSoup(pg.text,
                                  'html.parser').find(class_='smallText').text
            nums = [
                int(x.replace(',', ''))
                for x in pages.strip().split('1-')[1].split(' of ')
            ]
            num_pages = int(nums[1] / nums[0]) + 1

            if num_pages > 100:
                print(
                    'Found more than 100 page! Maximum allowed pages is 100. '
                    'Skipping pages after 100...')
                num_pages = 100
        except ValueError:
            raise UnknownPagesNum('Could not determine the total number of '
                                  'pages! Pass it as an option: `--pages-num`')

    if enable_multiprocessing:
        try:
            futures = [
                _get_quotes.remote(q, author) for q in range(1, num_pages + 1)
            ]
        except NameError:
            raise ModuleNotFoundError('Multiprocessing requires `ray`! '
                                      'Install with: `pip install ray`')

        results = [ray.get(q) for q in tqdm(futures)]
    else:
        results = [
            get_quotes(q, author) for q in tqdm(range(1, num_pages + 1))
        ]

    return sum(results, [])


def clean_text(results: list, language: str = 'en') -> list:
    print(f'Cleaning the quotes text...')
    clean = [
        q.replace('”', '').replace('“', '').encode('ascii', 'ignore').decode()
        for q in results if q
    ]

    clean_quotes = []

    for q in clean:
        try:
            lang = langdetect.detector_factory.detect_langs(q)[0]
            if lang.lang == language:
                clean_quotes.append(q.replace('\n', '').strip())
        except LangDetectException:
            continue

    return clean_quotes


def export_quotes(fname: str, results: list) -> None:
    with open(fname, 'w') as j:
        json.dump(results, j, indent=4)
    print(f'Saved results to {fname}...')


def scrape(author,
           num_pages=None,
           enable_multiprocessing=False,
           language='en',
           output_file='quotes.json'):
    results = quotes_by_author(author=author,
                               num_pages=num_pages,
                               enable_multiprocessing=enable_multiprocessing)
    clean_results = clean_text(results=results, language=language)
    export_quotes(fname=output_file, results=clean_results)
    return clean_results


def opts() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('-a',
                        '--author',
                        help='Full name of the author you want to search',
                        type=str,
                        required=True)
    parser.add_argument(
        '-l',
        '--language',
        help='Two letters string representing the language you want to parse '
        'the results in (default: en)',
        type=str,
        default='en')
    parser.add_argument('-n',
                        '--num-pages',
                        help='Number of pages to iterate through '
                        '(if empty, will iterate through all pages)',
                        type=int)
    parser.add_argument('-o',
                        '--output-file',
                        type=str,
                        help='Name of the output file (default: quotes.json)',
                        default='quotes.json')
    parser.add_argument('--enable-multiprocessing',
                        help='Enable multiprocessing',
                        action='store_true')
    return parser.parse_args()


def main() -> list:
    signal.signal(signal.SIGINT, keyboard_interrupt_handler)
    args = opts()
    clean_results = scrape(author=args.author,
                           num_pages=args.num_pages,
                           enable_multiprocessing=args.enable_multiprocessing,
                           language=args.language,
                           output_file=args.output_file)
    return clean_results


if __name__ == '__main__':
    main()
