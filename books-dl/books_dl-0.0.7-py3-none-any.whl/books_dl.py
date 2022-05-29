#!/usr/bin/env python3

__prog__ = "books-dl"
__version__ = "0.0.7"
__desc__ = "Консольная утилита для загрузки книжек с одного замечательного сайта."

import argparse
import os
import sys
from enum import IntEnum
from typing import Optional

import requests
from bs4 import BeautifulSoup

URL = "http://213.5.52.16/"
SEARCH_ENDPOINT = "search_2.php?user_name="
READ_ENDPOINT = "book/read.php?id="
HEADERS = {
    "connection": "keep-alive",
    "cache-control": "max-age=0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en;q=0.9",
}


class ExitCodes(IntEnum):
    SUCCESS = 0
    NOTHING_FOUND_BY_QUERY = 1
    NOTHING_TO_DO = 255


def eprint(*args, **kwargs) -> None:
    print(*args, file=sys.stderr, **kwargs)


def urljoin(*args) -> str:
    return "".join((URL, *args))


def get_book_name(
    book: dict,
    max_length: Optional[int] = None,
    book_information_incomplete: bool = False,
) -> str:
    if book_information_incomplete:  # То есть, есть только название и id
        name = f'{book["name"]} ({book["id"]})'
    else:
        NAME_AND_AUTHORS_SEPARATOR = " - "
        AUTHORS_SEPARATOR = ", "
        ELLIPSIS = ", ..."
        COLLECTION_SEPARATOR_LENGTH = 3

        need_ellipsis = False
        need_collection = False
        if max_length is not None:
            length = 0
            length += len(book["name"])
            length += len(NAME_AND_AUTHORS_SEPARATOR)
            if book["collection"]:
                need_collection = True
                collection_length = (
                    len(book["collection"]) + COLLECTION_SEPARATOR_LENGTH
                )
                length += collection_length
            for i, author in enumerate(book["authors"]):
                length += len(author) + len(AUTHORS_SEPARATOR)
                if length > max_length:
                    if need_collection:
                        need_collection = False
                        length -= collection_length
                        if length <= max_length:
                            continue
                    length -= len(AUTHORS_SEPARATOR)
                    if i == 0:  # Хотя бы один автор в названии должен быть
                        i = 1
                    need_ellipsis = True
                    if length > max_length:

                        def make_space_for_ellipsis():
                            nonlocal i, length
                            if not (max_length - length < len(ELLIPSIS) or i == 1):
                                i -= 1
                                length -= len(book["authors"][i - 1])
                                make_space_for_ellipsis()

                        make_space_for_ellipsis()
                    n = i
                    break
            else:
                n = len(book["authors"])
        else:
            n = len(book["authors"])
        authors = ", ".join(book["authors"][:n])
        if need_ellipsis:
            authors += ELLIPSIS
        name = " - ".join((authors, book["name"]))
        if need_collection:
            name += f' ({book["collection"]})'
    if max_length is not None:
        # Если название всё ещё слишком длинное, то просто обрезаем его конец
        if len(name) > max_length:
            name = name[:max_length]
    return name


def get_book_text(book: dict) -> str:
    return requests.get(book["link"], headers=HEADERS).text


def download_book(
    book: dict,
    directory: str,
    download_cover: bool,
    max_file_name_length: Optional[int] = None,
    book_name: Optional[str] = None,
    book_text: Optional[str] = None,
    book_information_incomplete: bool = False,
) -> None:
    if max_file_name_length is not None:
        FILE_EXTENSION_LENGTH = 5
        max_file_name_length -= FILE_EXTENSION_LENGTH

    book_name = get_book_name(book, max_file_name_length, book_information_incomplete)
    book_file_path = os.path.join(directory, book_name + ".html")
    if book_text is None:
        eprint(f"Загружаем книгу в {book_file_path}...")
        book_text = get_book_text(book)
    else:
        eprint(f"Книга загружена в {book_file_path}.")
    with open(book_file_path, "w") as f:
        f.write(book_text)

    if download_cover:
        cover_file_path = os.path.join(directory, book_name + ".jpeg")
        eprint(f"Загружаем обложку в {cover_file_path}...")
        with open(cover_file_path, "wb") as f:
            f.write(requests.get(book["cover"], headers=HEADERS).content)


def get_search_results(query) -> list[dict]:
    bs = BeautifulSoup(
        requests.get("".join((URL, SEARCH_ENDPOINT, query)), headers=HEADERS).text,
        "html.parser",
    )

    books = []
    trs = bs.find("table", cellspacing="1", border="1").find_all("tr")

    def clean(s: str):
        s = s.strip()
        if len(s) >= 2:
            if s[0] == "[" and s[-1] == "]":
                s = s[1:-1]
            s = s.strip()
        return s

    for tr in trs:
        tds = tuple(tr.find_all("td"))
        book = {}
        book["cover"] = urljoin(tds[0].img["src"])
        book["id"] = tds[1].text
        book["name"] = clean(tds[2].text)
        book["collection"] = clean(tds[3].text)
        book["authors"] = list((clean(a.text) for a in tds[5].find_all("a")))
        book["link"] = urljoin(tds[6].a["href"])
        books.append(book)

    return books


def download_by_query(query: str, link: bool, download_book_f) -> None:
    books = get_search_results(query)

    if not books:
        eprint(f"Не найдено книг по запросу {query}.")
        exit(ExitCodes.NOTHING_FOUND_BY_QUERY)
    book_names = tuple(map(get_book_name, books))
    for i in range(len(books)):
        eprint(f"{len(books) - i}. {book_names[len(books) - i - 1]}")

    while True:
        try:
            indexes = tuple(map(lambda x: x - 1, map(int, input().split())))
            break
        except ValueError:
            continue

    if link:
        for index in indexes:
            print(books[index]["link"])
    else:
        for index in indexes:
            download_book_f(books[index], book_name=book_names[index])


def download_by_id(id: int, link: bool, download_book_f) -> None:
    id = str(id)
    book = {}
    book["link"] = urljoin(READ_ENDPOINT, id)
    if link:
        print(book["link"])
        exit(ExitCodes.SUCCESS)
    eprint(f"Загружаем книгу c ID {id}...")
    book_text = get_book_text(book)
    bs = BeautifulSoup(book_text, "html.parser")
    book["name"] = bs.find("head").find("title").text
    search_results = get_search_results(book["name"])
    for result in search_results:
        if result["id"] == id:
            book = result
            break
    else:
        book["id"] = id
        eprint("Не удалось получить полную информацию о книге.")
        download_book_f(book, book_text=book_text, book_information_incomplete=True)
    download_book_f(book, book_text=book_text)


def main():
    parser = argparse.ArgumentParser(
        prog=__prog__,
        description=__desc__,
        epilog="Примечание: имя автора всегда следует вводить на русском языке, даже если искомая книжка не на нём.",
    )
    parser.add_argument(
        "query",
        metavar="Запрос",
        type=str,
        nargs="*",
        help="Запрос для поиска",
    )
    parser.add_argument(
        "-i",
        "--id",
        metavar="ID книги",
        type=int,
    )
    parser.add_argument(
        "-d",
        "--directory",
        metavar="Директория",
        type=str,
        help="Директория для загрузки книг. Если не указана, то используется текущая",
    )
    parser.add_argument(
        "-nc", "--no-cover", action="store_true", help="Не загружать обложку"
    )
    parser.add_argument(
        "-l",
        "--link",
        action="store_true",
        help="Вывести ссылку на книгу вместо загрузки",
    )
    parser.add_argument(
        "--max-file-name-length",
        metavar="Длина",
        type=int,
        default=128,
        help="Максимальная длина имени файла, по умолчанию 128 символов",
    )
    args = parser.parse_args()
    args.query = " ".join(args.query)

    download_book_f = lambda book, **kwargs: download_book(
        book,
        args.directory or os.curdir,
        not args.no_cover,
        args.max_file_name_length,
        **kwargs,
    )

    if args.id is not None:
        download_by_id(args.id, args.link, download_book_f)
    elif args.query is not None:
        download_by_query(args.query, args.link, download_book_f)
    else:
        exit(ExitCodes.NOTHING_TO_DO)
    exit(ExitCodes.SUCCESS)


if __name__ == "__main__":
    main()
