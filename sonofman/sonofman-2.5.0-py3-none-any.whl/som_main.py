#!/usr/bin/env python3

# noinspection SpellCheckingInspection
"""
==========
Install
==========

=> 1) ok when installing all UTF8, iso88591 of en_US, fr_FR, it_IT, es_ES, terminal in UTF8:
sudo dpkg-reconfigure locales
locale

My locales
-------------
LANG=en_US.utf8
LANGUAGE=en_US.utf8
LC_CTYPE="en_US.utf8"
LC_NUMERIC="en_US.utf8"
LC_TIME="en_US.utf8"
LC_COLLATE="en_US.utf8"
LC_MONETARY="en_US.utf8"
LC_MESSAGES="en_US.utf8"
LC_PAPER="en_US.utf8"
LC_NAME="en_US.utf8"
LC_ADDRESS="en_US.utf8"
LC_TELEPHONE="en_US.utf8"
LC_MEASUREMENT="en_US.utf8"
LC_IDENTIFICATION="en_US.utf8"
LC_ALL=en_US.utf8

=> 2) no need to install unicurses, the library is in the project :)


==========================
Last minute before release
==========================
- restore db: clear tab caches, fav


=============
Next releases
=============
x Check Windows
- TTS
- Invite friend
- Highlight search
- [Theme ready]


=============
Other
=============
- bug: echo in PyCharm Terminal!
- resizing => dimensions changes


=============
Coding
=============
- wclear => werase ?
- wgetch => getch  ?
- nodelay(false), linked to getch
"""

import os
import re
import sys
import traceback
import threading
import webbrowser
import xml.etree.ElementTree

import pkg_resources
import xerox

import sonofman.som_cachetab as som_cachetab
import sonofman.som_config as som_config
import sonofman.som_dal as som_dal
import sonofman.som_unicurses as u
import sonofman.som_util as som_util
import sonofman.som_version as som_version
import sonofman.som_winutil as som_winutil

_DEBUG = False

somversion = som_version.SomVersion
somconfig = som_config.SomConfig()
somdal = som_dal.SomDal(path_to_data=somconfig.path, new_version=somversion.db_version)
somutil = som_util.SomUtil
somsignal = None

# if _DEBUG:
#     import sonofman.som_signal as som_signal
#     # noinspection PyRedeclaration
#     somsignal = som_signal.SomSignal("{0}".format(pkg_resources.resource_filename('sonofman.data', 'log.txt')))

_locale = None
_alt_locale = None
_tabId = -1
_bbName = _tbbName = "k"
_bNumber = 1
_cNumber = 1
_history = []
_action_type = None
_action_type_sf = None
_action_bbname = None
_action_query = None
_action_order_by = None
_action_fav_filter = None
_delimiterVerse = "§§"
_attrFirst = u.A_REVERSE
_maxY = 0
_maxX = 0
_searchStringLimit = 3
_queryExpr = ""
_useColors = False
_colorTheme = 0
_colorThemeDialog = 0
_colorThemeErr = 0
_colorThemeFunc1 = 0
_colorThemeFunc2 = 0
_colorBible = {"k": "", "v": "", "l": "", "d": "", "a": "", "o": "", "s": "", "2": "", "HIGHLIGHT_SEARCH": ""}
_themeNr = None
_reset_status_before_key = True
_resource = {}
_title = ""
_sub_title = ""
_xml = None
_win_row = None
_panel_row = None
_win_status = None
_win_title = None
_wm_util = None
_cy = -1
_fav = {}
_historyType = "S"      # S or F only
_orderBy = 2
_favFilter = -1


def set_locale(locale):
    """
    Set locale resources
    :param locale: "en" (default), "es", "fr", "it", "pt", "de"
    :return: set locale resource
    """
    global _resource, _locale, _alt_locale, _bbName, _tbbName

    somdal.set_favorite_representation_dict(locale)

    if locale == "en":
        _resource = {
            "ABOUT": "About/Contact",
            "ALL": "All",
            "ALT_LANGUAGE": "ALT_LANGUAGE",
            "ARTICLES": "Articles",
            "BIBLE_PREFERRED": "Bible preferred",
            "BIBLE_MULTI": "Bibles to display",
            "BOOK": "Book",
            "BOOKS": "Books",
            "CLEAR": "Clear",
            "COLOR_MODE": "Color (mode)",
            "COLORS": "Colors",
            "CONFIRM": "Confirm (<ENTER>)",
            "ERR": "Error",
            "ERR_EMPTY": "No result!",
            "ERR_INVALID": "Invalid!",
            "ERR_OPERATION_CANCELLED": "Operation cancelled!",
            "ERR_KJV2000_LIMIT_500": "No more than 500 verses (c) KJV2000",
            "ERR_KJV2000_LIMIT_FULLBOOK": "No full book (c) KJV2000",
            "FILTER": "Filter",
            "FOUND": "Found",
            "HELP": "Help",
            "KEYS": "Keys",
            "HIGHLIGHT_SEARCH": "Search style",
            "MENU": "Menu",
            "PARABLES": "Parables",
            "OPEN": "Open",
            "SAVE": "Save",
            "SEARCH": "Search",
            "SEARCH_FAV": "Search☆",
            "SEARCH_LANGUAGE": "Bibles",
            "SETTINGS": "Settings",
            "SYSTEM": "System",
            "QUIT": "Quit",
            "CONTEXT_MENU": "Context menu",
            "OPEN_CHAPTER": "Open chapter",
            "CROSS_REFERENCES": "Cross references",
            "HISTORY": "History",
            "FAVORITES": "Favorites",
            "FAV_ORDER_TITLE": "Sort by",
            "FAV_ORDER_BY_BOOK": "Book",
            "FAV_ORDER_BY_DATE": "Date",
            "CLIPBOARD": "Clipboard",
            "CLIPBOARD_CLEAR": "Clear all",
            "CLIPBOARD_ADD_VERSE": "Add the verse",
            "CLIPBOARD_ADD_CHAPTER": "Add the chapter",
            "DELETE": "Delete",
            "fav0": "Internal",
            "fav1": "Favorite",
            "fav2": "Reading",
            "fav10": "Love",
            "fav20": "Top 100",
            "fav23": "To read",
            "fav30": "To study",
            "fav40": "To solve",
            "fav50": "Done",
            "fav60": "Exclamation",
            "fav70": "Question",
            "fav80": "Important",
            "fav90": "Danger",
            "fav100": "Death",
            "fav105": "Life",
            "fav110": "Prophecy"
        }
    elif locale == "es":
        _resource = {
            "ABOUT": "A propósito/Contacto",
            "ALL": "Todo",
            "ALT_LANGUAGE": "ALT_LANGUAGE",
            "ARTICLES": "Artículos",
            "BIBLE_PREFERRED": "Biblia preferida",
            "BIBLE_MULTI": "Biblias a mostrar",
            "BOOK": "Libro",
            "BOOKS": "Libros",
            "COLOR_MODE": "Color (modo)",
            "COLORS": "Colores",
            "CLEAR": "Eliminar",
            "CONFIRM": "Confirma (<ENTER>)",
            "ERR": "Errore",
            "ERR_EMPTY": "Ningún resultado!",
            "ERR_INVALID": "Inválido!",
            "ERR_OPERATION_CANCELLED": "Operación cancelada!",
            "ERR_KJV2000_LIMIT_500": "No more than 500 verses (c) KJV2000",
            "ERR_KJV2000_LIMIT_FULLBOOK": "No full book (c) KJV2000",
            "FILTER": "Filtro",
            "FOUND": "Encontrado",
            "HELP": "Ayuda",
            "KEYS": "Teclas",
            "HIGHLIGHT_SEARCH": "Estilo de búsqueda",
            "MENU": "Menú",
            "PARABLES": "Parábolas",
            "OPEN": "Abrir",
            "SAVE": "Salvar",
            "SEARCH": "Buscar",
            "SEARCH_FAV": "Buscar☆",
            "SEARCH_LANGUAGE": "Biblias",
            "SETTINGS": "Parámetros",
            "SYSTEM": "System",
            "QUIT": "Cerrar",
            "CONTEXT_MENU": "Menú contextual",
            "OPEN_CHAPTER": "Abrir capítulo",
            "CROSS_REFERENCES": "Referencias cruzadas",
            "HISTORY": "Historial",
            "FAVORITES": "Favoritos",
            "FAV_ORDER_TITLE": "Ordenar por",
            "FAV_ORDER_BY_BOOK": "Libro",
            "FAV_ORDER_BY_DATE": "Fecha",
            "CLIPBOARD": "Portapapeles",
            "CLIPBOARD_CLEAR": "Vaciar",
            "CLIPBOARD_ADD_VERSE": "Añadir el versículo",
            "CLIPBOARD_ADD_CHAPTER": "Añadir el capítulo",
            "DELETE": "Eliminar",
            "fav0": "Internal",
            "fav1": "Favorito",
            "fav2": "Lectura",
            "fav10": "Amor",
            "fav20": "Top 100",
            "fav23": "A leer",
            "fav30": "A estudiar",
            "fav40": "A resolver",
            "fav50": "Hecho",
            "fav60": "Exclamación",
            "fav70": "Pregunta",
            "fav80": "Importante",
            "fav90": "Peligro",
            "fav100": "Muerte",
            "fav105": "Vida",
            "fav110": "Profecía"
        }
    elif locale == "fr":
        _resource = {
            "ABOUT": "A propos/Contact",
            "ALL": "Tout",
            "ALT_LANGUAGE": "ALT_LANGUAGE",
            "ARTICLES": "Articles",
            "BIBLE_PREFERRED": "Bible préférée",
            "BIBLE_MULTI": "Bibles à afficher",
            "BOOK": "Livre",
            "BOOKS": "Livres",
            "CLEAR": "Effacer",
            "COLOR_MODE": "Couleur (mode)",
            "COLORS": "Couleurs",
            "CONFIRM": "Confirmez (<ENTER>)",
            "ERR": "Erreur",
            "ERR_EMPTY": "Pas de résultat!",
            "ERR_INVALID": "Invalide!",
            "ERR_OPERATION_CANCELLED": "Opération annulée!",
            "ERR_KJV2000_LIMIT_500": "No more than 500 verses (c) KJV2000",
            "ERR_KJV2000_LIMIT_FULLBOOK": "No full book (c) KJV2000",
            "FILTER": "Filtre",
            "FOUND": "Trouvé",
            "HELP": "Aide",
            "KEYS": "Touches",
            "HIGHLIGHT_SEARCH": "Style de la recherche",
            "MENU": "Menu",
            "OPEN": "Ouvrir",
            "PARABLES": "Paraboles",
            "SAVE": "Sauver",
            "SEARCH": "Chercher",
            "SEARCH_FAV": "Chercher☆",
            "SEARCH_LANGUAGE": "Bibles",
            "SETTINGS": "Params",
            "SYSTEM": "System",
            "QUIT": "Quitter",
            "CONTEXT_MENU": "Menu contextuel",
            "OPEN_CHAPTER": "Ouvrir chapitre",
            "CROSS_REFERENCES": "Références croisées",
            "HISTORY": "Historique",
            "FAVORITES": "Favoris",
            "FAV_ORDER_TITLE": "Trier par",
            "FAV_ORDER_BY_BOOK": "Livre",
            "FAV_ORDER_BY_DATE": "Date",
            "CLIPBOARD": "Presse-papier",
            "CLIPBOARD_CLEAR": "Vider",
            "CLIPBOARD_ADD_VERSE": "Ajouter le verset",
            "CLIPBOARD_ADD_CHAPTER": "Ajouter le chapitre",
            "DELETE": "Supprimer",
            "fav0": "Internal",
            "fav1": "Favori",
            "fav2": "Lecture",
            "fav10": "Amour",
            "fav20": "Top 100",
            "fav23": "A lire",
            "fav30": "A étudier",
            "fav40": "A résoudre",
            "fav50": "Fait",
            "fav60": "Exclamation",
            "fav70": "Question",
            "fav80": "Important",
            "fav90": "Danger",
            "fav100": "Mort",
            "fav105": "Vie",
            "fav110": "Prophétie"

        }
    elif locale == "it":
        _resource = {
            "ABOUT": "A proposito/Contatto",
            "ALL": "Tutto",
            "ALT_LANGUAGE": "ALT_LANGUAGE",
            "ARTICLES": "Articoli",
            "BIBLE_PREFERRED": "Bibbia preferita",
            "BIBLE_MULTI": "Bibbie ad affiggere",
            "BOOK": "Libro",
            "BOOKS": "Libri",
            "CLEAR": "Eliminare",
            "COLOR_MODE": "Colore (modalità)",
            "COLORS": "Colori",
            "CONFIRM": "Conferma (<ENTER>)",
            "ERR": "Errore",
            "ERR_EMPTY": "Alcun risultato!",
            "ERR_INVALID": "Invalido!",
            "ERR_OPERATION_CANCELLED": "Operazione cancellata!",
            "ERR_KJV2000_LIMIT_500": "No more than 500 verses (c) KJV2000",
            "ERR_KJV2000_LIMIT_FULLBOOK": "No full book (c) KJV2000",
            "FILTER": "Filtro",
            "FOUND": "Trovato",
            "HELP": "Aiuto",
            "KEYS": "Tasti",
            "HIGHLIGHT_SEARCH": "Stile di ricerca",
            "MENU": "Menu",
            "PARABLES": "Parabole",
            "OPEN": "Aprire",
            "SAVE": "Salvare",
            "SEARCH": "Cercare",
            "SEARCH_FAV": "Cercare☆",
            "SEARCH_LANGUAGE": "Bibbie",
            "SETTINGS": "Parametri",
            "SYSTEM": "System",
            "QUIT": "Chiudere",
            "CONTEXT_MENU": "Menu contestuale",
            "OPEN_CHAPTER": "Aprire capitolo",
            "CROSS_REFERENCES": "Riferimenti incrociati",
            "HISTORY": "Cronologia",
            "FAVORITES": "Favoriti",
            "FAV_ORDER_TITLE": "Ordinare per",
            "FAV_ORDER_BY_BOOK": "Libro",
            "FAV_ORDER_BY_DATE": "Data",
            "CLIPBOARD": "Clipboard",
            "CLIPBOARD_CLEAR": "Svuotare",
            "CLIPBOARD_ADD_VERSE": "Aggiungere il versetto",
            "CLIPBOARD_ADD_CHAPTER": "Aggiungere il capitolo",
            "DELETE": "Eliminare",
            "fav0": "Internal",
            "fav1": "Favorito",
            "fav2": "Lettura",
            "fav10": "Amore",
            "fav20": "Top 100",
            "fav23": "A leggere",
            "fav30": "A studiare",
            "fav40": "A risolvere",
            "fav50": "Fatto",
            "fav60": "Esclamazione",
            "fav70": "Domanda",
            "fav80": "Importante",
            "fav90": "Pericolo",
            "fav100": "Morte",
            "fav105": "Vita",
            "fav110": "Profezia"
        }
    elif locale == "pt":
        _resource = {
            "ABOUT": "Sobre/Contato",
            "ALL": "Tudo",
            "ALT_LANGUAGE": "ALT_LANGUAGE",
            "ARTICLES": "Artigos",
            "BIBLE_PREFERRED": "Bíblia favorita",
            "BIBLE_MULTI": "Bíblias para mostrar",
            "BOOK": "Livro",
            "BOOKS": "Livros",
            "COLOR_MODE": "Cor (modo)",
            "COLORS": "Cores",
            "CLEAR": "Eliminar",
            "CONFIRM": "Confirma (<ENTER>)",
            "ERR": "Errore",
            "ERR_EMPTY": "Nenhum resultado!",
            "ERR_INVALID": "Inválido!",
            "ERR_OPERATION_CANCELLED": "Operação cancelada!",
            "ERR_KJV2000_LIMIT_500": "No more than 500 verses (c) KJV2000",
            "ERR_KJV2000_LIMIT_FULLBOOK": "No full book (c) KJV2000",
            "FILTER": "Filtro",
            "FOUND": "Encontrado",
            "HELP": "Ajuda",
            "KEYS": "Teclas",
            "HIGHLIGHT_SEARCH": "Tipo de pesquisa",
            "MENU": "Menu",
            "PARABLES": "Parábolas",
            "OPEN": "Abrir",
            "SAVE": "Salvar",
            "SEARCH": "Buscar",
            "SEARCH_FAV": "Buscar☆",
            "SEARCH_LANGUAGE": "Bíblias",
            "SETTINGS": "Parâmetros",
            "SYSTEM": "Sistema",
            "QUIT": "Fechar",
            "CONTEXT_MENU": "Menu de contexto",
            "OPEN_CHAPTER": "Abrir capítulo",
            "CROSS_REFERENCES": "Referências cruzadas",
            "HISTORY": "Histórico",
            "FAVORITES": "Favoritos",
            "FAV_ORDER_TITLE": "Ordenar por",
            "FAV_ORDER_BY_BOOK": "Livro",
            "FAV_ORDER_BY_DATE": "Data",
            "CLIPBOARD": "Clipboard",
            "CLIPBOARD_CLEAR": "Limpar tudo",
            "CLIPBOARD_ADD_VERSE": "Adicionar o versículo",
            "CLIPBOARD_ADD_CHAPTER": "Adicionar o capítulo",
            "DELETE": "Excluir",
            "fav0": "Internal",
            "fav1": "Favorito",
            "fav2": "Leitura",
            "fav10": "Amor",
            "fav20": "Top 100",
            "fav23": "Para ler",
            "fav30": "Para estudar",
            "fav40": "Para resolver",
            "fav50": "Concluído",
            "fav60": "Exclamação",
            "fav70": "Pergunta",
            "fav80": "Importante",
            "fav90": "Perigo",
            "fav100": "Morte",
            "fav105": "Vida",
            "fav110": "Profecia"
        }
    elif locale == "de":
        _resource = {
            "ABOUT": "Über/Kontakt",
            "ALL": "Alle",
            "ALT_LANGUAGE": "Alternative Sprache (Artikeln)",
            "ARTICLES": "Artikeln",
            "BIBLE_PREFERRED": "Lieblingsbibel",
            "BIBLE_MULTI": "Zu zeigende Bibeln",
            "BOOK": "Buch",
            "BOOKS": "Bücher",
            "CLEAR": "Zu löschen",
            "COLOR_MODE": "Farbe (Modus)",
            "COLORS": "Farben",
            "CONFIRM": "Bestätigen (<ENTER>)",
            "ERR": "Fehler",
            "ERR_EMPTY": "Kein Ergebnis!",
            "ERR_INVALID": "Ungültig!",
            "ERR_OPERATION_CANCELLED": "Vorgang abgebrochen!",
            "ERR_KJV2000_LIMIT_500": "No more than 500 verses (c) KJV2000",
            "ERR_KJV2000_LIMIT_FULLBOOK": "No full book (c) KJV2000",
            "FILTER": "Filter",
            "FOUND": "Gefunden",
            "HELP": "Hilfe",
            "KEYS": "Tasten",
            "HIGHLIGHT_SEARCH": "Stil der Suche",
            "MENU": "Menü",
            "PARABLES": "Parabeln",
            "OPEN": "Öffnen",
            "SAVE": "Speichern",
            "SEARCH": "Suchen",
            "SEARCH_FAV": "Suchen☆",
            "SEARCH_LANGUAGE": "Bibeln",
            "SETTINGS": "Einstellungen",
            "SYSTEM": "System",
            "QUIT": "Beenden",
            "CONTEXT_MENU": "Kontextmenü",
            "OPEN_CHAPTER": "Kapitel öffnen",
            "CROSS_REFERENCES": "Querverweisen",
            "HISTORY": "Geschichte",
            "FAVORITES": "Favoriten",
            "FAV_ORDER_TITLE": "Sortieren nach",
            "FAV_ORDER_BY_BOOK": "Buch",
            "FAV_ORDER_BY_DATE": "Datum",
            "CLIPBOARD": "Zwischenablage",
            "CLIPBOARD_CLEAR": "Leer",
            "CLIPBOARD_ADD_VERSE": "Vers hinzufügen",
            "CLIPBOARD_ADD_CHAPTER": "Kapitel hinzufügen",
            "DELETE": "Löschen",
            "fav0": "Internal",
            "fav1": "Favorit",
            "fav2": "Lesen",
            "fav10": "Liebe",
            "fav20": "Top 100",
            "fav23": "Zu lesen",
            "fav30": "Zu studieren",
            "fav40": "Zu lösen",
            "fav50": "Erledigt",
            "fav60": "Ausruf",
            "fav70": "Frage",
            "fav80": "Wichtig",
            "fav90": "Gefahr",
            "fav100": "Tod",
            "fav105": "Leben",
            "fav110": "Prophezeiung"
        }
    else:
        _locale = "en"
        _alt_locale = _locale
        _bbName = _tbbName = "k"
        somutil.print("! Unsupported locale ('{0}'), locale set to 'en'.".format(locale))
        set_locale(_locale)


# noinspection PyBroadException
def res(k):
    try:
        return _resource[k]
    except Exception:
        if _DEBUG:
            somutil.print("! Unknown key: '{0}'".format(k))
        return "KEY"


def res_ponct(k):
    """Add ponctuation for presentation"""
    return "{0}: ".format(res(k))


def print_ex(ex):
    msg = "{0} > {1}\n\n".format(res("ERR"), ex)
    stack = stack_trace()
    sys.stderr.write(msg)
    sys.stderr.write(stack)

    height = _maxY
    width = _maxX

    win_ex = u.newwin(height, width, 2, 0)
    u.mvwaddstr(win_ex, 1, 1, msg, _colorTheme)
    u.waddstr(win_ex, stack, _colorTheme)
    u.wgetch(win_ex)
    finish(1)


def stack_trace():
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lst = ["*** "]
    lst_trace = traceback.format_exception(exc_type, exc_value, exc_traceback)
    lst.append("".join(str(i) for i in lst_trace))
    return "".join(str(i) for i in lst)


def show_search(search_type):
    """
    Search in the bible or open a book or search in favorites
    :param search_type: S=Search Bible, F=Search Fav, B:Open Book
    :return: bbname, query, search_type_sf, order_by, fav_filter
    """
    dict_menu = get_bible_dict_verbose()
    width = _maxX

    msg = res_ponct("SEARCH") if search_type in ("S", "F") else res_ponct("OPEN")
    menu_title = res("SEARCH_LANGUAGE")

    # Bibles
    # noinspection PyTypeChecker
    selected_bible_menu_index = get_bible_menu_index(_bbName)
    menu_selected, movement, char_key = show_menu(0, menu_title, dict_menu, False, False, selected_bible_menu_index)

    if menu_selected < 0:
        return None, None, None, None, None

    bbnames = get_bible_dict_short()
    bbname_selected = bbnames[menu_selected]

    # To return
    book_nr = ""
    search_type_sf = "F" if search_type == "F" else "S"
    order_by = 2
    fav_filter = -1

    # Books
    language_selected = "({0}) ".format(dict_menu[menu_selected])
    book_name_selected = show_books(0, res("BOOKS"), bbname_selected, None if search_type == "B" else res("ALL"))

    if book_name_selected is None:
        return None, None, None, None, None
    elif book_name_selected == res("ALL"):
        upd_book_name = ""
    else:
        book_nr = book_name_selected.split(")")[0].replace("(", "").lstrip()
        book_nr = "{0:} ".format(book_nr)
        book_name_start = book_name_selected.find(")") + 1
        upd_book_name = "{0} ".format(book_name_selected[book_name_start:].rstrip())

    # Fav selection
    if search_type == "F":
        menu_search_type_selected = 0 if search_type == "S" else 1

        if menu_search_type_selected == 0:
            pass    # Bible search
        elif menu_search_type_selected == 1:
            # Fav search
            # Fav filter
            menu_fav_selected, dummy_movement, dummy_char_key, fav_filter = show_favorites(False)
            if menu_fav_selected < 0:
                return None, None, None, None, None

            # Fav order
            dict_fav_order_menu = {0: res("FAV_ORDER_BY_DATE"), 1: res("FAV_ORDER_BY_BOOK")}
            menu_fav_order_title = res("FAV_ORDER_TITLE")
            menu_fav_order_selected, movement, char_key = show_menu(0, menu_fav_order_title, dict_fav_order_menu, False, False, 0)
            if menu_fav_order_selected < 0:
                return None, None, None, None, None
            order_by = menu_fav_order_selected + 1

    # Presentation of selections
    win_q = u.newwin(3, width, 2, 0)     # len(language_selected) + len(upd_book_name)
    u.wbkgd(win_q, " ", _colorTheme)
    u.mvwhline(win_q, 2, 0, u.ACS_HLINE + _colorTheme, width)
    u.mvwaddstr(win_q, 0, 0, language_selected)
    u.waddstr(win_q, upd_book_name)
    u.update_panels()
    u.doupdate()

    # Search string
    if search_type in ("S", "F"):
        u.echo()
        search_string = u.wgetstr(win_q)
        u.noecho()

        try:
            search_string = search_string.decode("utf-8") if len(search_string) > 0 else ""
        except Exception:
            search_string = ""      # TODO: loop or give error (same for other 2 decode("utf

        u.wclear(win_q)
        u.wrefresh(win_q)
    else:
        chapter_count = somdal.get_bible_chapter_count_by_book(book_nr)[0]

        while True:
            u.echo()
            search_string = u.wgetstr(win_q)    # TODO: get escape and quit
            u.noecho()

            try:
                search_string = search_string.strip().decode("utf-8") if len(search_string) > 0 else "1"
            except Exception:
                search_string = "1"

            is_number = re.match(r"^[\d]*$", search_string)
            cnumber = -1

            if is_number:
                cnumber = int(search_string)
            if not is_number or cnumber <= 0 or cnumber > chapter_count:
                msg = "{0} [1..{1}]".format(res("ERR_INVALID"), chapter_count)
                show_status(msg, _colorTheme, False)
                u.wclear(win_q)
                u.mvwhline(win_q, 2, 0, u.ACS_HLINE + _colorTheme, width)
                u.mvwaddstr(win_q, 0, 0, language_selected)
                u.waddstr(win_q, upd_book_name)
                u.wrefresh(win_q)
                continue
            else:
                break

    u.delwin(win_q)

    # Finally
    u.noecho()
    # if win_b is not None:
    #    u.delwin(win_b)

    return bbname_selected, "{0}{1}".format(book_nr, search_string), search_type_sf, order_by, fav_filter


def show_menu(menu_x, menu_title, dict_menu, allow_scrolling_menu=False, allow_filter_menu=False, selected_menu_index=0):
    """
    Create, show menu and returns the selected item index
    :param menu_x: position x; 0 as default
    :param menu_title: title msg
    :param dict_menu: menu. Dictionary of text => no colors: { 0: "text"... }, \
    Dictionary of list items => colors: { 0: ["text", "attributes"]... }
    :param allow_scrolling_menu: scrolling menu
    :param allow_filter_menu: use filter (press TAB key to change filter)
    :param selected_menu_index: start value selected
    :return: 1) index of item selected or position (-1 if not selected)
             2) -1|0|1 has movement (-1 = up, 0 = selected or ESC, 1 = down, 3 = filter)
             3) char of key pressed when allow_filter_menu is True else None
    """
    win_b = win_lb = panel = None
    try:
        if len(dict_menu) == 0:
            return 0, -1, None    # Reload up

        allow_color_menu = True if type(dict_menu[0]) is list else False
        max_height = len(dict_menu) + 2
        max_width = len(menu_title)

        for k in dict_menu.keys():
            menu_item_width = len(dict_menu.get(k))
            if menu_item_width > max_width:
                max_width = menu_item_width

        max_width += 4
        if max_height > _maxY:
            raise Exception("Terminal height should be bigger!")

        size = len(dict_menu)

        win_lb = u.newwin(max_height + 1, _maxX, 2, menu_x)     # TODO: here to remove hline, use max_width instead
        u.wbkgd(win_lb, " ", _colorTheme)
        u.mvwhline(win_lb, max_height, 0, u.ACS_HLINE + _colorTheme, _maxX)
        u.wrefresh(win_lb)

        win_b = u.newwin(max_height, max_width, 2, menu_x)
        u.wbkgd(win_b, " ", _colorTheme)
        panel = u.new_panel(win_lb)
        u.panel_above(panel)
        u.update_panels()
        u.doupdate()

        u.noecho()
        u.keypad(win_b, True)

        highlight = selected_menu_index
        # TODO: reverse the selected
        while True:
            u.wattron(win_b, _colorThemeDialog)
            u.box(win_b)
            u.mvwaddstr(win_b, 0, 2, menu_title)
            u.wattroff(win_b, _colorTheme)

            for i in range(0, size):
                attr = _colorTheme if i != highlight else u.A_REVERSE
                if not allow_color_menu:
                    u.mvwaddstr(win_b, 1 + i, 2, dict_menu[i], attr)
                else:
                    u.mvwaddstr(win_b, 1 + i, 2, dict_menu[i][0], eval(dict_menu[i][1]) if i != highlight else eval(dict_menu[i][1]) + u.A_REVERSE)

            key = u.wgetch(win_b)
            if key == 27:
                return -1, 0, None
            elif key in (32, 10):   # space, enter
                return highlight, 0, None
            elif key == u.KEY_DOWN:
                if highlight + 1 >= size:
                    if not allow_scrolling_menu:
                        highlight = 0
                    else:
                        return 0, 1, None
                else:
                    highlight += 1
            elif key == u.KEY_UP:
                if highlight - 1 < 0:
                    if not allow_scrolling_menu:
                        highlight = size - 1
                    else:
                        return size - 1, -1, None
                else:
                    highlight -= 1
            elif key == u.KEY_END:
                highlight = size - 1
            elif key == u.KEY_HOME:
                highlight = 0
            elif key == u.KEY_RIGHT:
                if not allow_scrolling_menu:
                    pass
                else:
                    return highlight + size, 1, None
            elif key == u.KEY_LEFT:
                if not allow_scrolling_menu:
                    pass
                else:
                    return highlight - size, -1, None
            else:
                if re.match("^[a-zA-Z]*$", chr(key)):
                    if allow_filter_menu:
                        return highlight, 3, chr(key)
    except Exception as ex:
        print_ex(ex)
    finally:
        if win_b is not None:
            u.delwin(win_b)
        if win_lb is not None:
            u.delwin(win_lb)
        if panel is not None:
            u.del_panel(panel)
        u.update_panels()
        u.doupdate()


def clear_status():
    """
    Clear status bar
    """
    u.wclear(_win_status)
    u.wrefresh(_win_status)


# noinspection PyBroadException
def show_status(msg, attr, reset_status_before_key=False):
    """
    Show message in status bar some seconds
    :param msg: message
    :param attr: attribute
    :param reset_status_before_key: if True, wclear will clear the status before user input in main loop
    """
    global _reset_status_before_key

    try:
        _reset_status_before_key = reset_status_before_key

        msg = msg.replace("\n", " ")

        x = y = 0
        u.wclear(_win_status)
        u.mvwaddstr(_win_status, y, x, msg, attr)
        u.wrefresh(_win_status)

        # TODO: show the msg for specific time
    except Exception:
        pass
        # TODO: print_ex(ex) ?


def save_action(action_type, action_bbname, action_query, action_order_by, action_fav_filter, should_add=True):
    """
    Save action type
    :param action_type: "A":article, "P":parable, "S":search, "B":book, "F":fav, other:none
    :param action_bbname: bible name
    :param action_query: query
    :param action_order_by: order by
    :param action_fav_filter: fav filter
    :param should_add: True:add, False:update
    """
    global _action_type, _action_type_sf, _action_bbname, _action_query, _action_order_by, _action_fav_filter, _history, _tabId

    _action_type = action_type
    _action_type_sf = "F" if action_type == "F" else "S"
    _action_bbname = action_bbname
    _action_query = action_query
    _action_order_by = action_order_by
    _action_fav_filter = action_fav_filter

    _history = [_action_bbname, _action_query, _action_type_sf, _action_order_by, _action_fav_filter]

    tab_type = _action_type if _action_type in ("A", "P", "F") else "S"

    if should_add:
        # Add
        tab_id = somdal.get_first_cache_tab_id_by_query(tab_type, _action_query, _action_fav_filter)
        if tab_id >= 0:
            if _action_type_sf == "F":
                somdal.delete_cache_tab_by_id(tab_id)
            else:
                if tab_id != _tabId or _tabId < 0:
                    _tabId = tab_id
                    show_title_and_subtitle()
                return

        if tab_id < 0:
            tab_id = somdal.get_cache_tab_id_max() + 1

        ct = som_cachetab.SomCacheTab(
            rq=True,
            tabid=tab_id,
            tabtype=tab_type,
            tabtitle=_action_query,
            fullquery=_action_query,
            scrollposy=0,
            bbname=_action_bbname,
            isbook=0,
            ischapter=0,
            isverse=0,
            bnumber=0,
            cnumber=0,
            vnumber=0,
            trad=_tbbName,
            orderby=_action_order_by,
            favfilter=_action_fav_filter
        )
        somdal.add_cache_tab(ct)
        _tabId = tab_id
        show_title_and_subtitle()
    else:
        # Update
        tab_id = _tabId
        ct = som_cachetab.SomCacheTab(
            rq=True,
            tabid=tab_id,
            tabtype=tab_type,
            tabtitle=_action_query,
            fullquery=_action_query,
            scrollposy=0,
            bbname=_action_bbname,
            isbook=0,
            ischapter=0,
            isverse=0,
            bnumber=0,
            cnumber=0,
            vnumber=0,
            trad=_tbbName,
            orderby=_action_order_by,
            favfilter=_action_fav_filter
        )
        somdal.update_cache_tab(ct)
        # _tabId OK

    # Manage limit
    if tab_type in ("A", "P"):
        count = somdal.get_cache_tab_count_by_type(tab_type)
        if count > som_util.SomUtil.history_limit:
            tab_id_del = somdal.get_first_cache_tab_id_by_type(tab_type)
            if tab_id_del >= 0:
                somdal.delete_cache_tab_by_id(tab_id_del)


def save_title(title):
    global _title
    _title = title.replace("\n", "")


def save_sub_title(sub_title):
    global _sub_title
    _sub_title = sub_title.replace("\n", "")


# noinspection PyBroadException
def show_title_and_subtitle():
    """Show full title bar"""
    global _tabId

    try:
        title = _title
        sub_title = _sub_title

        if len(_title) == 0:
            title = somversion.app_name
            sub_title = ""
            full_title = title
        elif len(sub_title) == 0:
            full_title = title
        else:
            words = sub_title.split(" ")
            if len(words) == 4:
                if words[1].isdigit() and words[2].isdigit() and words[3].upper() == "CR:":
                    sub_title = "{0} {1}.{2}".format(words[0], words[1], words[2])
            full_title = "[{2}] {0} > {1}".format(title, sub_title, _tabId)

        size = _maxX
        if len(full_title) >= size:
            full_title = "{0}.".format(full_title[0: size - 1])

        y = 0
        x = _maxX - len(full_title) - 1
        if x < 0:
            x = 0

        u.wclear(_win_title)
        u.mvwaddstr(_win_title, y, x, full_title, u.A_NORMAL)
        u.wrefresh(_win_title)
    except Exception:
        pass
        # TODO: print_ex(ex) ?


def merge_words(from_word_pos, words):
    to_word_pos = len(words)
    merged_string = ""
    for i in range(from_word_pos, to_word_pos):
        fmt = "{0} {1}" if i != from_word_pos else "{0}{1}"
        merged_string = fmt.format(merged_string, words[i])
    return merged_string


# noinspection PyUnusedLocal
def prepare_bible_search_string(bbname, query, search_type_sf):
    """
    Prepare search bible parameters (called only by get_bible_search)
    :param bbname: bible name
    :param query: complete query
    :param search_type_sf: S or F
    :return: search_type_nr, book_number, chapter_number, verse_number, verse_number_to, search_string, book name verbose
             search_type_nr: 0:no search, 1:search string in Bible/Favorites, 2:verses from to, 3:book, 4:cr
    """
    book_number = chapter_number = verse_number = verse_number_to = -1
    book_name_verbose = book_short_name = ""
    search_string = ""
    search_type_nr = 0   # 0:no search, 1:search string, 2:verses from to, 3:book, 4:cr

    words = query.split(" ")
    word_count = len(words)
    if word_count == 0:
        pass
    else:
        if search_type_nr == 0:
            if words[0].isdigit():
                book_number = int(words[0])

        if search_type_nr == 0:
            if word_count == 4:
                if words[0].isdigit() and words[1].isdigit() and words[2].isdigit() and words[3].isdigit():
                    search_type_nr = 2
                    if book_number <= 0:
                        book_number = int(words[0])
                    chapter_number = int(words[1])
                    verse_number = int(words[2])
                    verse_number_to = int(words[3])
                    # call
                elif words[1].isdigit() and words[2].isdigit() and words[3].upper() == "CR:":
                    search_type_nr = 4
                    if book_number <= 0:
                        book_number = int(words[0])
                    chapter_number = int(words[1])
                    verse_number = int(words[2])
                    verse_number_to = -1
                    # call

        if search_type_nr == 0:
            if word_count == 3:
                # <bNumber> <cNumber> <vNumber>
                if (words[0].isdigit() and words[1].isdigit() and words[2].isdigit()) or (
                        book_number > 0 and words[1].isdigit() and words[2].isdigit()):
                    search_type_nr = 2
                    if book_number <= 0:
                        book_number = int(words[0])
                    chapter_number = int(words[1])
                    verse_number = int(words[2])
                    verse_number_to = verse_number
                    # call

        if search_type_nr == 0:
            if word_count >= 3:
                # <bNumber> <cNumber> <expr> ...
                if (words[0].isdigit() and words[1].isdigit()) or (book_number > 0 and words[1].isdigit()):
                    search_type_nr = 1
                    if book_number <= 0:
                        book_number = int(words[0])
                    chapter_number = int(words[1])
                    verse_number = 0
                    search_string = merge_words(2, words)
                    # call

        if search_type_nr == 0:
            if word_count == 2:
                # <bNumber> <cNumber>
                if (words[0].isdigit() and words[1].isdigit()) or (book_number > 0 and words[1].isdigit()):
                    search_type_nr = 3
                    if book_number <= 0:
                        book_number = int(words[0])
                    chapter_number = int(words[1])
                    verse_number = 0
                    # call

        if search_type_nr == 0:
            if word_count >= 2:
                # <bNumber> <expr> ...
                if words[0].isdigit() or book_number > 0:
                    search_type_nr = 1
                    if book_number <= 0:
                        book_number = int(words[0])
                    chapter_number = 0
                    verse_number = 0
                    search_string = merge_words(1, words)
                    # call

        if search_type_nr == 0:
            if word_count == 1:
                # <bNumber>
                if words[0].isdigit():
                    search_type_nr = 3
                    if book_number <= 0:
                        book_number = int(words[0])
                    chapter_number = 1
                    verse_number = 0
                    # call

        if search_type_nr == 0:
            if (search_type_sf == "S" and len(query) >= _searchStringLimit) or (search_type_sf == "F"):
                # Finally <expr> ...
                search_type_nr = 1
                book_number = 0
                chapter_number = 0
                verse_number = 0
                search_string = merge_words(0, words)
                # call

        if book_number > 0:
            book_name_verbose, book_short_name = somdal.get_book_ref(bbname, book_number)

    # Finally
    return search_type_nr, book_number, chapter_number, verse_number, verse_number_to, search_string, book_name_verbose


def get_bible_search(bbname, query, search_type_sf, order_by, fav_filter, should_add=True):
    """
    Get bible search result (called after show_search)
    :param bbname: bible name
    :param query: query
    :param search_type_sf: S or F
    :param order_by:
    :param fav_filter:
    :param should_add: True:add, False:update
    :return: strings and set _queryExpr
    """
    global _bNumber, _cNumber, _queryExpr

    # TODO: change here the regex. Actually it's impossible to quit a search, a book search
    # TODO: don't change history if we quit or there is no result
    # TODO: if there is no result, tell it and ask to retry or quit

    s = ""
    search_type_nr = 0
    _queryExpr = ""

    if (search_type_sf == "S" and len(query) > 0) or (search_type_sf == "F"):
        search_type_nr, book_number, chapter_number, verse_number, verse_number_to, search_string, book_name_verbose = prepare_bible_search_string(bbname, query, search_type_sf)
        _queryExpr = search_string

        if search_type_nr > 0:
            vcount = 0
            _bNumber = book_number
            _cNumber = chapter_number

            if search_type_nr == 1:
                save_title(res("FAVORITES") if search_type_sf == "F" else res("SEARCH"))
                s, vcount = somdal.search_bible_string(_delimiterVerse, _tbbName, bbname, book_number,
                                                       chapter_number, search_string, search_type_sf, order_by, fav_filter)
            elif search_type_nr == 2:
                save_title(res("SEARCH"))
                s = somdal.get_verses(_delimiterVerse, _tbbName, book_number, chapter_number,
                                      verse_number, verse_number_to)
            elif search_type_nr == 3:
                save_title(res("BOOKS"))
                s = somdal.search_bible(_delimiterVerse, _tbbName, book_number, chapter_number)

            elif search_type_nr == 4:
                save_title(res("CROSS_REFERENCES"))
                s = somdal.get_cross_references(_delimiterVerse, _tbbName, book_number, chapter_number, verse_number)

            if len(s) > 0:
                _wm_util.move(0)
                if len(book_name_verbose) > 0:
                    words = query.split(" ")
                    words[0] = book_name_verbose
                    sub_title = " ".join(words)
                else:
                    sub_title = query

                if search_type_sf == "F":
                    sub_title = sub_title.strip()
                    if len(sub_title) > 0:
                        sub_title = "{0} {1}".format(_fav["fav{0}".format(fav_filter)]["emo"], sub_title)
                    else:
                        sub_title = "{0}".format(_fav["fav{0}".format(fav_filter)]["emo"])

                save_sub_title(sub_title)
                show_title_and_subtitle()

                if search_type_nr == 1:
                    msg = "{0}: {1}".format(res("FOUND"), vcount)
                    show_status(msg, _colorTheme, False)       # was: + u.A_BOLD
            else:
                save_sub_title(query)
                show_title_and_subtitle()
                show_status(res("ERR_EMPTY"), _colorTheme, False)
                return ""
    else:
        save_title(res("SEARCH"))
        save_sub_title(query)
        show_title_and_subtitle()
        return ""

    # Save history
    if search_type_nr == 0:
        action_type = ""
    elif search_type_nr == 3:
        action_type = "B"
    elif search_type_nr == 1 and search_type_sf == "F":
        action_type = "F"
    else:
        action_type = "S"

    save_action(action_type, bbname, query, order_by, fav_filter, should_add=should_add)
    return s


def menu():
    """
    Menu of preferences
    :return: False: ESC, True: used
    """
    global _useColors

    menu_k = "MENU"
    menu_title = res(menu_k)

    show_menu_title = res(menu_k)
    save_title(show_menu_title)

    if _locale == "de":
        dict_menu = {
            0: res("BIBLE_PREFERRED"),
            1: res("ALT_LANGUAGE"),
            2: res("BIBLE_MULTI"),
            3: res("COLOR_MODE"),
            4: res("COLORS"),
            5: res("ABOUT")
        }
    else:
        dict_menu = {
            0: res("BIBLE_PREFERRED"),
            1: res("BIBLE_MULTI"),
            2: res("COLOR_MODE"),
            3: res("COLORS"),
            4: res("ABOUT")
        }

    menu_selected, movement, char_key = show_menu(0, menu_title, dict_menu, False, False)
    menu_is_used = False

    if _locale == "de":
        if menu_selected < 0:
            menu_is_used = False
        elif menu_selected == 0:
            menu_is_used = False if show_bible_preferred() is None else True
        elif menu_selected == 1:
            show_alt_language()
            menu_is_used = True
        elif menu_selected == 2:
            show_bible_multi()
            menu_is_used = True
        elif menu_selected == 3:
            menu_is_used = show_themes()
        elif menu_selected == 4:
            show_bible_colors()
            menu_is_used = True
        elif menu_selected == 5:
            show_about()
            menu_is_used = True
        return menu_is_used
    else:
        if menu_selected < 0:
            menu_is_used = False
        elif menu_selected == 0:
            menu_is_used = False if show_bible_preferred() is None else True
        elif menu_selected == 1:
            show_bible_multi()
            menu_is_used = True
        elif menu_selected == 2:
            menu_is_used = show_themes()
        elif menu_selected == 3:
            show_bible_colors()
            menu_is_used = True
        elif menu_selected == 4:
            show_about()
            menu_is_used = True
        return menu_is_used


def show_bible_preferred():
    """
    Menu of bible preferred
    :return: item selected or None
    """
    global _bbName, _tbbName, _locale, _alt_locale

    # panel_below(panel_search)
    dict_menu = get_bible_dict_verbose()
    menu_title_upd = "{0}: {1} ".format(res("BIBLE_PREFERRED"), _bbName)
    menu_item_selected, movement, char_key = show_menu(0, menu_title_upd, dict_menu, False)

    if menu_item_selected < 0:
        return None
    elif menu_item_selected == 0:
        _bbName = "k"
        _locale = "en"
        _alt_locale = _locale
    elif menu_item_selected == 1:
        _bbName = "2"
        _locale = "en"
        _alt_locale = _locale
    elif menu_item_selected == 2:
        _bbName = "v"
        _locale = "es"
        _alt_locale = _locale
    elif menu_item_selected == 3:
        _bbName = "l"
        _locale = "fr"
        _alt_locale = _locale
    elif menu_item_selected == 4:
        _bbName = "o"
        _locale = "fr"
        _alt_locale = _locale
    elif menu_item_selected == 5:
        _bbName = "d"
        _locale = "it"
        _alt_locale = _locale
    elif menu_item_selected == 6:
        _bbName = "a"
        _locale = "pt"
        _alt_locale = _locale
    elif menu_item_selected == 7:
        _bbName = "s"
        _locale = "de"
        _alt_locale = "en"

    if _tbbName.find(_bbName) < 0:
        _tbbName = "{0}{1}".format(_bbName, _tbbName)

    restart(True)
    return menu_item_selected


def show_alt_language():
    """
    Menu of alt language
    :return: item selected or None
    """
    global _alt_locale

    dict_menu = {
        0: "English",
        1: "Español",
        2: "Français",
        3: "Italiano",
        4: "Português"
    }

    if _alt_locale == "es":
        alt_language_verbose = dict_menu[1]
    elif _alt_locale == "fr":
        alt_language_verbose = dict_menu[2]
    elif _alt_locale == "it":
        alt_language_verbose = dict_menu[3]
    elif _alt_locale == "pt":
        alt_language_verbose = dict_menu[4]
    else:
        alt_language_verbose = dict_menu[0]

    menu_title_upd = "{0}: {1} ".format(res("ALT_LANGUAGE"), alt_language_verbose)
    menu_item_selected, movement, char_key = show_menu(0, menu_title_upd, dict_menu, False)

    if menu_item_selected < 0:
        return None
    elif menu_item_selected == 0:
        _alt_locale = "en"
    elif menu_item_selected == 1:
        _alt_locale = "es"
    elif menu_item_selected == 2:
        _alt_locale = "fr"
    elif menu_item_selected == 3:
        _alt_locale = "it"
    elif menu_item_selected == 4:
        _alt_locale = "pt"

    restart(True)
    return menu_item_selected


def show_bible_multi():
    """
    Menu to select bibles to display
    """
    global _tbbName, _bbName

    dict_menu = {
        0: res("CLEAR"),
        1: "(EN) King James 1611 (K)",
        2: "(EN) King James 2000 (2)",
        3: "(ES) Reina Valera (V)",
        4: "(FR) Louis Segond (L)",
        5: "(FR) Ostervald (O)",
        6: "(IT) G. Diodati (D)",
        7: "(PT) Almeida (A)",
        8: "(DE) Schlachter (S)"
    }

    # TODO: use get_bible_dict and change CLEAR option
    menu_title = res("BIBLE_MULTI")
    tbbname = _tbbName

    # TODO: if to simplify
    while True:
        menu_title_upd = "{0}: {1} ".format(menu_title, tbbname)
        menu_item_selected, movement, char_key = show_menu(0, menu_title_upd, dict_menu, False, False)

        if menu_item_selected < 0:
            if len(tbbname) == 0:
                _tbbName = tbbname = _bbName
            else:
                if tbbname.find(_bbName) < 0:
                    tbbname = "{0}{1}".format(_bbName, tbbname)
                _tbbName = tbbname
            break

        elif menu_item_selected == 0:
            tbbname = ""

        elif menu_item_selected == 1:
            bbname = "k"
            if tbbname.find(bbname) < 0:
                tbbname = "{0}{1}".format(tbbname, bbname)
            else:
                tbbname = tbbname.replace(bbname, "")

        elif menu_item_selected == 2:
            bbname = "2"
            if tbbname.find(bbname) < 0:
                tbbname = "{0}{1}".format(tbbname, bbname)
            else:
                tbbname = tbbname.replace(bbname, "")

        elif menu_item_selected == 3:
            bbname = "v"
            if tbbname.find(bbname) < 0:
                tbbname = "{0}{1}".format(tbbname, bbname)
            else:
                tbbname = tbbname.replace(bbname, "")

        elif menu_item_selected == 4:
            bbname = "l"
            if tbbname.find(bbname) < 0:
                tbbname = "{0}{1}".format(tbbname, bbname)
            else:
                tbbname = tbbname.replace(bbname, "")

        elif menu_item_selected == 5:
            bbname = "o"
            if tbbname.find(bbname) < 0:
                tbbname = "{0}{1}".format(tbbname, bbname)
            else:
                tbbname = tbbname.replace(bbname, "")

        elif menu_item_selected == 6:
            bbname = "d"
            if tbbname.find(bbname) < 0:
                tbbname = "{0}{1}".format(tbbname, bbname)
            else:
                tbbname = tbbname.replace(bbname, "")

        elif menu_item_selected == 7:
            bbname = "a"
            if tbbname.find(bbname) < 0:
                tbbname = "{0}{1}".format(tbbname, bbname)
            else:
                tbbname = tbbname.replace(bbname, "")

        elif menu_item_selected == 8:
            bbname = "s"
            if tbbname.find(bbname) < 0:
                tbbname = "{0}{1}".format(tbbname, bbname)
            else:
                tbbname = tbbname.replace(bbname, "")

    restart(False)


def show_bible_colors():
    """
    Menu to select bible colors
    """
    global _colorBible

    menu_title = res("COLORS")
    dict_menu = get_bible_dict_verbose()
    dict_menu[8] = "(**) {0}".format(res("HIGHLIGHT_SEARCH"))

    if not _useColors:
        dict_menu_colors = {
            0: ["Normal", "u.A_NORMAL"],
            1: ["Dim", "u.A_DIM"],
            2: ["Bold", "u.A_BOLD"],
            3: ["Underline", "u.A_UNDERLINE"],
            4: ["Reverse", "u.A_REVERSE"]
        }
        replace_colors()
    else:
        # TODO: add more colors and make pagination
        dict_menu_colors = {
            0: ["Normal", "u.A_NORMAL"],
            1: ["Dim", "u.A_DIM"],
            2: ["Bold", "u.A_BOLD"],
            3: ["Underline", "u.A_UNDERLINE"],
            4: ["Reverse", "u.A_REVERSE"],
            5: ["COLOR1", "u.color_pair(1)"],
            6: ["COLOR2", "u.color_pair(2)"],
            7: ["COLOR3", "u.color_pair(3)"],
            8: ["COLOR4", "u.color_pair(4)"],
            9: ["COLOR5", "u.color_pair(5)"],
            10: ["COLOR6", "u.color_pair(6)"],
            11: ["COLOR11", "u.color_pair(11)"],
            12: ["COLOR12", "u.color_pair(12)"],
            13: ["COLOR13", "u.color_pair(13)"],
            14: ["COLOR21", "u.color_pair(21)"],
            15: ["COLOR22", "u.color_pair(22)"]
        }

    while True:
        menu_item_selected, movement, char_key = show_menu(0, menu_title, dict_menu, False, False)

        color_key = ""
        color = []
        if menu_item_selected == -1:
            break
        elif menu_item_selected == 0:
            color_key = "k"
        elif menu_item_selected == 1:
            color_key = "2"
        elif menu_item_selected == 2:
            color_key = "v"
        elif menu_item_selected == 3:
            color_key = "l"
        elif menu_item_selected == 4:
            color_key = "o"
        elif menu_item_selected == 5:
            color_key = "d"
        elif menu_item_selected == 6:
            color_key = "a"
        elif menu_item_selected == 7:
            color_key = "s"
        elif menu_item_selected == 8:
            color_key = "HIGHLIGHT_SEARCH"

        color_item = _colorBible[color_key].split("#")
        if len(color_item) >= 2:
            str_color = color_item[0]
            code_color = color_item[1]
        else:
            str_color = color_item[0]
            code_color = ""

        arr_attr = str_color.split("+")
        for item_color in arr_attr:
            color.append(item_color)

        str_color = ""
        for c in color:
            str_color = "{0}+{1}".format(str_color, c)

        if len(color) > 0 and str_color[0] == "+":
            str_color = str_color[1:]

        while True:
            menu_title_color = "{0}: {1} -> ({2}) {3}".format(menu_title, dict_menu[menu_item_selected], str_color, code_color)
            menu_item_selected_color, movement_color, char_key_color = show_menu(0, menu_title_color, dict_menu_colors, False, False)

            if menu_item_selected_color == -1:
                _colorBible[color_key] = "{0}#{1}".format(str_color, code_color)
                color.clear()
                break
            elif menu_item_selected_color < 5:
                item_color = "A_{0}".format(dict_menu_colors[menu_item_selected_color][0].upper())
                # noinspection PyBroadException
                if item_color in color:
                    color.remove(item_color)
                else:
                    color.append(item_color)

                str_color = ""
                for c in color:
                    str_color = "{0}+{1}".format(str_color, c)

                if len(color) > 0 and str_color[0] == "+":
                    str_color = str_color[1:]
            else:
                item_color = dict_menu_colors[menu_item_selected_color][0].upper()
                code_color = "" if item_color == code_color else item_color

    restart(False)


def show_themes():
    """
    Menu to select themes
    :return: False: ESC, True: used
    """
    global _useColors, _themeNr

    dict_menu_themes = {
        0: "No color",
        1: "Classic Blue  (with white)",
        2: "Classic Black (with green)",
        3: "Classic White (with black)"
    }

    menu_title = res("COLOR_MODE")
    menu_item_selected, movement, char_key = show_menu(0, menu_title, dict_menu_themes, False, False)

    if menu_item_selected == -1:
        return False

    _themeNr = menu_item_selected
    _useColors = False if menu_item_selected == 0 else True
    load_colors()
    restart(False)


def test():
    win_b = u.newwin(5, 40, 0, 0)
    u.box(win_b)
    u.wbkgd(win_b, " ", _colorThemeFunc2)
    u.mvwaddstr(win_b, 1, 1, "My string", u.A_BOLD)
    u.mvwaddstr(win_b, 3, 1, "Test...", u.A_REVERSE)
    panel = u.new_panel(win_b)
    u.panel_above(panel)
    u.update_panels()
    u.doupdate()
    u.getch()
    u.del_panel(panel)
    u.delwin(win_b)


def focus_row_init():
    global _cy
    _cy = _wm_util.win_top_border_lines - 1     # Tip: -1 to find first
    focus_row(1)


def focus_row(step):
    """
    Focus current row.
    The better is to use it before quitting a menu and returning the parameters but some menus are used everywhere like
    show_menu() or menu() has a lot of sub-menus, difficult to know all options.
    In that case call focus_row(0) in the caller, not in the called.
    :param step: +1, -1, 0
    """
    global _win_row, _panel_row, _cy

    new_cy = _cy
    pos_from = _wm_util.win_top_border_lines
    pos_to = _wm_util.win_top_border_lines + _wm_util.win_lines

    # Find row
    while True:
        # Move
        if step < 0:
            new_cy = pos_from if new_cy < pos_from else new_cy + step
        elif step >= 0:
            new_cy = pos_to if new_cy > pos_to else new_cy + step

        # Possible range but not sure something is written
        if new_cy < pos_from or new_cy > pos_to or new_cy < 0:
            return  # TODO: add cond. for last in page

        # Check the line
        pos = _wm_util.position_in_list_by_cy(new_cy)
        if pos > _wm_util.s_lines_max:
            return
        if len(_wm_util.s_lst) == 0:
            return

        row = _wm_util.s_lst[pos][0]
        lst_content = row.split("|")
        size = len(lst_content)

        if size == 2:
            if lst_content[0] != _bbName:
                continue
            if lst_content[1].find(":") < 0:
                continue
            break   # if pos > _wm_util.win_lines - _wm_util.win_top_border_lines - _wm_util.win_bottom_border_lines
        elif size == 1:
            if lst_content[0].find("https://") >= 0 or lst_content[0].find("http://") >= 0:
                break

    # Display row
    _cy = new_cy

    if _win_row is not None:
        u.delwin(_win_row)

    if _panel_row is not None:
        u.del_panel(_panel_row)

    _win_row = u.newwin(1, _maxX, _cy, 0)
    _panel_row = u.new_panel(_win_row)

    u.wbkgd(_win_row, " ", _colorThemeFunc2 if _useColors else _colorThemeFunc2 + u.A_REVERSE)
    u.mvwaddstr(_win_row, 0, 0, lst_content[1] if size == 2 else lst_content[0], _colorThemeFunc2 if _useColors else _colorThemeFunc2 + u.A_REVERSE)

    # Highlight search
    if pos in _wm_util.s_dict_expr:
        text = lst_content[1]
        attr_highlight_search, code_color_highlight_search = _wm_util.get_color(color_key="HIGHLIGHT_SEARCH")
        for expr_start in _wm_util.s_dict_expr[pos]:
            text_part = text[expr_start:expr_start + len(_wm_util.s_query_expr)]
            if not (code_color_highlight_search is None):
                u.mvwaddstr(_win_row, 0, expr_start, text_part, attr_highlight_search + code_color_highlight_search)
            else:
                u.mvwaddstr(_win_row, 0, expr_start, text_part, attr_highlight_search)

    u.panel_above(_panel_row)
    u.update_panels()
    u.doupdate()


def show_context_menu(panel_ref, win_ref, action):
    """
    :param panel_ref:
    :param win_ref:
    :param action: "C" to access clipboard menu directly, "": full context menu
    """
    global _bNumber, _cNumber, _queryExpr

    if _cy < 0:
        return

    if len(_wm_util.s_lst) == 0:
        return

    # Row with ID
    pos_in_list = _wm_util.position_in_list_by_cy(_cy)
    if pos_in_list < 0 or pos_in_list >= len(_wm_util.s_lst):
        return
    row = _wm_util.s_lst[pos_in_list][0]
    if len(_wm_util.s_lst[pos_in_list][1]) == 0:
        bible_id = ''
    else:
        bible_id = _wm_util.s_lst[pos_in_list][1][0]

    if bible_id != '':
        ref_book_short, ref_book_name, bnumber, cnumber, vnumber, dummy_vtext, dummy_bbname = somdal.get_verse(bible_id)
        if ref_book_short is None:
            return
    else:
        # Row without ID
        row_content = row.split("|")
        row_content_length = len(row_content)

        if row_content_length == 1:
            http_pos = row_content[0].find("https://")
            if http_pos <= 0:
                http_pos = row_content[0].find("http://")
            if http_pos <= 0:
                return
            url = row_content[0][http_pos:]
            open_url(url)
            return

        elif row_content_length != 2:
            return

        pos_column = row_content[1].find(":")
        if pos_column < 0:
            return

        ref_full = row_content[1][0: pos_column]  # Exod 22.2
        ref_split_part0 = ref_full.split(" ")

        # Try to get bnumber
        i = 0
        ref_book_short = ref_split_part0[i].strip()
        bnumber = somdal.get_book_number_by_bsname(_bbName, ref_book_short)
        if bnumber <= 0:
            # Retry to get bnumber
            i = 1
            ref_book_short = ref_split_part0[i].strip()
            bnumber = somdal.get_book_number_by_bsname(_bbName, ref_book_short)
            if bnumber <= 0:
                return

        ref_split_part1 = ref_split_part0[i+1].split(".")
        cnumber = int(ref_split_part1[0])
        vnumber = int(ref_split_part1[1])

        ref_book_name, dummy = somdal.get_book_ref(_bbName, bnumber)
        bible_id = somdal.get_bible_id(_bbName, bnumber, cnumber, vnumber)

    # Menu
    has_cr = True if row.find("[") >= 0 else False

    if has_cr:
        dict_context_menu = {
            0: f"{res('OPEN_CHAPTER')}",
            1: f"{res('CROSS_REFERENCES')}",
            2: f"{res('FAVORITES')}",
            3: f"{res('CLIPBOARD')}"
        }
    else:
        dict_context_menu = {
            0: f"{res('OPEN_CHAPTER')}",
            1: f"{res('FAVORITES')}",
            2: f"{res('CLIPBOARD')}"
        }

    u.panel_below(panel_ref)

    if action == "C":
        if has_cr:
            menu_item_selected = 3
        else:
            menu_item_selected = 2
    else:
        menu_title = res("CONTEXT_MENU")
        menu_item_selected, dummy_movement, dummy_char_key = show_menu(0, menu_title, dict_context_menu, False, False)

    if menu_item_selected == -1:
        focus_row(0)
        return

    elif menu_item_selected == 0:
        _bNumber = bnumber
        _cNumber = cnumber
        action_type = "B"
        action_query = f"{bnumber} {cnumber}"
        action_order_by = 2
        action_fav_filter = -1
        title = res("BOOK")
        sub_title = f"{ref_book_name} {cnumber}"
        s = somdal.get_verses(_delimiterVerse, _tbbName, bnumber, cnumber, 1, None)
        _queryExpr = ""

    elif has_cr and menu_item_selected == 1:
        action_type = "S"
        action_query = f"{bnumber} {cnumber} {vnumber} CR:"
        action_order_by = 2
        action_fav_filter = -1
        title = res("CROSS_REFERENCES")
        sub_title = f"{ref_book_name} {cnumber}.{vnumber}"
        s = somdal.get_cross_references(_delimiterVerse, _tbbName, bnumber, cnumber, vnumber)
        _queryExpr = ""

    elif (has_cr and menu_item_selected == 2) or (not has_cr and menu_item_selected == 1):
        menu_item_selected, dummy_movement, dummy_char_key, fav_filter = show_favorites(True)

        if menu_item_selected == -1:
            focus_row(0)
            return
        else:
            action = -1 if menu_item_selected == 0 else 1

            somdal.manage_favorite(bible_id, action, fav_filter)
            reset_window(panel_ref, win_ref)
            show_history(_history, _wm_util.s_line_pos)
            return

    elif (has_cr and menu_item_selected == 3) or (not has_cr and menu_item_selected == 2):
        dict_clipboard_menu = {
            0: f"{res('CLIPBOARD_ADD_VERSE')}",
            1: f"{res('CLIPBOARD_ADD_CHAPTER')}",
            2: f"{res('CLIPBOARD_CLEAR')}",
        }
        menu_title = res("CLIPBOARD")
        menu_item_selected, dummy_movement, dummy_char_key = show_menu(0, menu_title, dict_clipboard_menu, False, False)

        if menu_item_selected == -1:
            focus_row(0)
            return
        elif menu_item_selected == 0:
            somdal.add_verses_to_clipboard(_tbbName, bnumber, cnumber, vnumber)
        elif menu_item_selected == 1:
            somdal.add_chapter_to_clipboard(_tbbName, bnumber, cnumber)
        elif menu_item_selected == 2:
            somdal.delete_all_clipboard()

        generate_text_for_clipboard()
        focus_row(0)
        return
    else:
        return

    save_action(action_type, _bbName, action_query, action_order_by, action_fav_filter)
    save_title(title)
    save_sub_title(sub_title)
    show_title_and_subtitle()

    reset_window(panel_ref, win_ref)
    _wm_util.fill_window(s, 0, _queryExpr)
    focus_row_init()


def show_favorites(should_show_delete_item):
    """
    Show all favorites for selection
    :param should_show_delete_item: True:Delete, False:ALL item
    :return: menu_item_selected, movement, char_key, fav_filter: -1:not used, 0:ALL, 1..
    """
    dict_favorites = {}
    dict_values = {0: 0}

    i = 0
    for k in _fav.keys():
        if k == "fav0":
            dict_favorites[i] = "{0:2s} {1}".format(_fav[k]["emo"], res("ALL"))
            i += 1
            continue
        dict_favorites[i] = "{0:2s} {1}".format(_fav[k]["emo"], _fav[k]["desc"])
        dict_values[i] = int(k.replace("fav", ""))
        i += 1

    if should_show_delete_item:
        dict_favorites[0] = res("DELETE")

    menu_title = res("FAVORITES")
    menu_item_selected, movement, char_key = show_menu(0, menu_title, dict_favorites, False, False)

    if menu_item_selected < 0:
        fav_filter = -1
    else:
        fav_filter = 0 if menu_item_selected == 0 else dict_values[menu_item_selected]

    return menu_item_selected, movement, char_key, fav_filter


def open_url(url):
    try:
        url = "".join(url.rsplit(sep=" ", maxsplit=1))
        clipboard_copy(url)
        webbrowser.open(url, new=2)
    except Exception as ex:
        if _DEBUG: 
            raise ex


def clipboard_copy(msg=""):
    try:
        xerox.copy(msg)
    except Exception as ex:
        if _DEBUG: 
            raise ex


def generate_text_for_clipboard():
    try:
        bbnames = somdal.get_clipboard_bbnames()

        # Checks
        if bbnames.find("2") >= 0:
            warn_type = 0
            lst_full_books = somdal.get_clipboard_list_fullbooks("2")
            if len(lst_full_books) > 0:
                warn_type = 1
            else:
                vcount = somdal.get_clipboard_count_for_bbname("2")
                if vcount > 500:
                    warn_type = 2

            if warn_type > 0:
                bbnames = bbnames.replace("2", "")
                somdal.delete_clipboard_for_bbname("2")
                show_status(res("ERR_KJV2000_LIMIT_FULLBOOK") if warn_type == 1 else res("ERR_KJV2000_LIMIT_500"), _colorTheme, False)     # TODO: show status delay

        # Gen
        prev_id = -1
        sb = []
        lst_id_gen = somdal.get_clipboard_list_ids()
        size = len(lst_id_gen)
        for index in range(0, size):
            # Current
            id_current = lst_id_gen[index]

            bsname, bname, bnumber, cnumber, vnumber, vtext, bbname = somdal.get_verse(id_current)
            if bsname is None:
                continue

            bnumber_current = bnumber
            cnumber_current = cnumber
            vnumber_current = vnumber
            vtext_current = vtext
            bname_current = bname
            bbname_current = bbname

            if prev_id == -1:
                sb.append(f"\n\n{bname_current} {cnumber_current}\n")
            elif prev_id + 1 != id_current:
                sb.append("\n")

            sb.append(f"{vnumber_current}: {vtext_current}\n")
            prev_id = id_current

            # Next
            if (index + 1) < size:
                id_next = lst_id_gen[index + 1]

                bsname, bname, bnumber, cnumber, vnumber, vtext, bbname = somdal.get_verse(id_next)
                if bsname is None:
                    continue

                bnumber_next = bnumber
                cnumber_next = cnumber
                bbname_next = bbname

                if (bnumber_current != bnumber_next) or (cnumber_current != cnumber_next) or (bbname_current != bbname_next):
                    prev_id = -1

        # Sources
        bbnames_verbose = ""
        for i in range(0, len(bbnames)):
            bbname = bbnames[i]
            if bbname == "k":
                bbnames_verbose = f"{bbnames_verbose}, KJV 1611"
            if bbname == "l":
                bbnames_verbose = f"{bbnames_verbose}, Louis Segond"
            if bbname == "o":
                bbnames_verbose = f"{bbnames_verbose}, Ostervald"
            if bbname == "v":
                bbnames_verbose = f"{bbnames_verbose}, Reina Valera"
            if bbname == "a":
                bbnames_verbose = f"{bbnames_verbose}, Almeida"
            if bbname == "d":
                bbnames_verbose = f"{bbnames_verbose}, Diodati"
            if bbname == "s":
                bbnames_verbose = f"{bbnames_verbose}, Schlachter"
            if bbname == "2":
                bbnames_verbose = f"{bbnames_verbose}, KJV 2000"

        if len(bbnames_verbose) > 0:
            bbnames_verbose = bbnames_verbose[2:]
            sb.append(f"\n({bbnames_verbose})")

        # Finally
        text_to_clipboard = ("".join(item for item in sb)).strip()
        clipboard_copy("Clipboard is empty :)" if len(text_to_clipboard) == 0 else text_to_clipboard)

    except Exception as ex:
        raise ex


# noinspection PyUnusedLocal
def show_about():
    dict_menu = {
        0: "- {0}{1} -".format(somversion.app_name[0].upper(), somversion.app_name[1:]),
        1: "{0} ({1}) - {2}".format(somversion.app_version,
                                 somdal.get_db_version_of_db(),
                                 somversion.app_version_date),
        2: "Email    : {0}".format(somversion.author_email),
        3: "Gitlab   : {0}".format(somversion.url),
        4: "Telegram : {0}".format(somversion.telegram),
        # 5: "TEST"
    }

    menu_title = res("ABOUT")
    menu_item_selected, movement, char_key = show_menu(0, menu_title, dict_menu, False, False)

    if menu_item_selected == 2:
        open_url(somversion.author_email)
    elif menu_item_selected == 3:
        open_url(somversion.url)
    elif menu_item_selected == 4:
        open_url(somversion.telegram)
    elif menu_item_selected == 5:
        tts()


def tts_init():
    # Need a thread, non blocking the interface, able to stop when quiting...
    voice = 0
    msg = ""

    if _bbName in ("k", "2"):
        voice = 0
        msg = """Are you serious? Yes, I'm serious, signs are everywhere. This application, giving the real Word of God, can help you be strong during this period when the devil will try to deceive you more than never and to be ready when Christ will come back. Remember yourselves that the devil knows the Scriptures. I added only good original Bibles (no re-edition) in several languages, I can understand, to help you find Jesus because he's the only way towards our Father. Don't remain in the darkness little children of God. Be good to your brothers and sisters, spread the light, love, pray, repent, have faith, joy, follow the commandments, stop your sins and sow abundantly. Let's follow Jesus, the good Shepherd, our only saviour... God bless you. Amen."""
    elif _bbName in ("l", "o"):
        voice = 38  # !
        msg = """Oui, je suis sérieux, les signes sont partout. Cetrte application donnant la vraie parole de Dieu peut vous aider à être
    fort durant cette période quand le diable essayera de vous tromper plus que jamais et d'être prêt quand le Christ reviendra. Rappelez-vous que le
    diable connaît les Écritures. Je n'ai ajouté que de bonnes bibles originales (pas de re-édition) en plusieurs langues, que je peux comprendre, pour
    vous aider à trouver Jésus parce qu'il est le seul chemin vers notre Père. Ne restez pas dans les ténèbres petits enfants de Dieu. Soyez bon avec
    vos frères et soeurs, répandez la lumière, l'amour, priez, repentez-vous, ayez la foi, la joie, suivez les commandements, arrêtez vos péchés et
    semez abondamment. Suivons Jésus, le bon Berger, notre unique sauveur... Que Dieu vous bénisse. Amen."""
    elif _bbName == "d":
        voice = 21
        msg = """Sì, sono serio, i segni sono dovunque. Questa applicazione che dà la vera parola di Dio può aiutarvi ad essere forti
    durante questo periodo quando il diavolo provera di ingannarvi più che mai e di essere pronto quando il Cristo ritornerà. Ricordatevi che il
    diavolo conosce le Scritture. Ho aggiunto che le buone Bibbie originali (non re-edizione) in diverse lingue, che posso capire, per aiutarvi a
    trovare Gesù, perché è la sola strada verso nostro Padre. Non restate nelle tenebre piccoli bambini di Dio. Siate buono coi vostri fratelli e
    sorelle, spargete la luce, l'amore, pregate, pentitesivi, abbiate la fede, la gioia, segua i comandi, fermate i vostri peccati e seminate
    abbondantemente. Seguiamo Gesù, il buono Pastore, il nostro unico salvatore... Che Dio vi benedicesse. Amen."""
    elif _bbName == "v":
        msg = """no"""
    elif _bbName == "a":
        msg = """no"""
    elif _bbName == "s":
        msg = """no"""

    return voice, msg


def tts():
    try:
        import pyttsx3

        voice, msg = tts_init()
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[voice].id)
        engine.say(msg)
        engine.runAndWait()
    except Exception as ex:
        raise ex


def show_art_prbl(is_article, art_name_filter):
    """
    Show menu with articles or parables
    :param is_article: is article
    :param art_name_filter: article name
    :return: 1) item name selected
             2) prbl digits
             3) item verbose name
    """
    if is_article:
        menu_k = "ARTICLES"
        menu_title = res(menu_k)
        array_name = "ART_ARRAY"
    else:
        menu_k = "PARABLES"
        menu_title = res(menu_k)
        array_name = "PRBL_ARRAY"

    show_menu_title = res(menu_k)
    save_title(show_menu_title)

    dict_menu = {}
    xml_lst = _xml.find(array_name).findall("item")

    # Simple filter
    if art_name_filter is not None:
        f = 0
        xml_lst_filtered = []
        for item in xml_lst:
            if item.text.find(art_name_filter) >= 0:
                xml_lst_filtered.append(xml_lst[f])
            f += 1
        xml_lst = xml_lst_filtered

    # Create menu
    i = 0
    for item in xml_lst:
        if is_article:
            xml_item = _xml.find(item.text)
            dict_menu[i] = xml_item.text
        else:
            prbl_fields = item.text.split("|")
            prbl_name = prbl_fields[0]
            xml_prbl_name = _xml.find(prbl_name)
            dict_menu[i] = xml_prbl_name.text
        i += 1

    pos_start = 0
    pos_block = 0
    size_menu_mini = 10
    size_menu = len(dict_menu)

    while True:
        j = 0
        dict_menu_mini = {}
        for i in range(pos_start, pos_start + size_menu_mini):
            if i >= size_menu:
                break
            dict_menu_mini[j] = dict_menu[i]
            j += 1

        highlight_menu_index = 0
        menu_item_selected, movement, char_key = show_menu(0, menu_title, dict_menu_mini, True, False, highlight_menu_index)

        if movement == 0:
            break
        elif movement in (-1, 1):
            pos_block += movement
            if pos_block < 0:
                pos_block = 0
            pos_start = pos_block * size_menu_mini

    # Finally
    if menu_item_selected < 0:
        focus_row(0)
        return None, None, None

    xml_item_selected = xml_lst[pos_block * size_menu_mini + menu_item_selected]
    item_verbose_name = dict_menu[pos_block * size_menu_mini + menu_item_selected]

    if is_article:
        item_name = _xml.find(xml_item_selected.text).tag
    else:
        item_name = xml_item_selected.text

    if is_article:
        return item_name, None, item_verbose_name
    else:
        prbl_arr = item_name.split("|")
        item_name = prbl_arr[0]
        prbl_digits = prbl_arr[1]
        return item_name, prbl_digits, item_verbose_name


def show_books(menu_x, menu_title_book, bbname, res_all_item):
    """
    Show books
    :param menu_x: x pos
    :param menu_title_book: title
    :param bbname: language
    :param res_all_item: resource
    :return: book name selected
    """
    is_order_by_name = True
    lst = somdal.get_list_book_by_name(25, bbname, is_order_by_name, res_all_item, "")
    i = 0
    dict_menu = {}
    for item in lst:
        dict_menu[i] = item
        i += 1

    menu_title_filter = " {0} ({1}): ".format(res("FILTER"), res("BOOKS"))
    size_menu = len(dict_menu)
    size_menu_mini = 10
    pos_start = 0
    pos_block = 0

    while True:
        j = 0
        dict_menu_mini = {}
        for i in range(pos_start, pos_start + size_menu_mini):
            if i >= size_menu:
                break
            dict_menu_mini[j] = dict_menu[i]
            j += 1

        highlight_menu_index = 1 if len(dict_menu_mini) == 2 and dict_menu_mini[0] == res("ALL") else 0
        menu_item_selected, movement, char_key = show_menu(menu_x, menu_title_book, dict_menu_mini, True, True,
                                                           highlight_menu_index)
        if movement == 0:
            break
        elif movement in (-1, 1):
            pos_block += movement
            if pos_block < 0:
                pos_block = 0
            pos_start = pos_block * size_menu_mini
        elif movement == 3:
            win_filter = u.newwin(3, _maxX, 2, 0)
            u.wbkgd(win_filter, " ", _colorTheme)
            u.mvwhline(win_filter, 2, 0, u.ACS_HLINE + _colorTheme, _maxX)
            u.mvwaddstr(win_filter, 0, 0, menu_title_filter)  # + char_key
            u.update_panels()
            u.doupdate()

            u.echo()
            filter_string = u.wgetstr(win_filter)
            u.noecho()

            try:
                filter_string = filter_string.strip().decode("utf-8") if len(filter_string) > 0 else ""
            except Exception:
                filter_string = ""

            u.delwin(win_filter)
            u.update_panels()
            u.doupdate()

            lst = somdal.get_list_book_by_name(25, bbname, is_order_by_name, res_all_item, filter_string)
            if len(lst) == 0:
                continue

            i = 0
            dict_menu = {}
            for item in lst:
                dict_menu[i] = item
                i += 1

            pos_block = 0
            pos_start = 0
            size_menu = len(dict_menu)

    # Finally
    if menu_item_selected < 0:
        return None

    item_selected = dict_menu_mini[menu_item_selected]
    return item_selected


def get_history_dict_menu():
    """
    Get history_dict_menu
    :return: dict_menu
    """
    lst = somdal.get_list_all_cache_tab_for_history()
    if len(lst) == 0:
        return None

    i = 0
    dict_menu = {}
    tabtitle = ""
    for item in lst:
        tabid, tabtype, bbname, fullquery, favfilter = item[0], item[1], item[2], item[3], item[4]
        tabid = "{0:4s}".format(str(tabid))     # TODO: flexible space with get max id +++ also tests
        if tabtype in ("A", "P"):
            verbose_name = _xml.find(fullquery).text
            tabtitle = "{0} {1}".format(tabid, verbose_name)
        elif tabtype in ("S", "F"):
            favsymbol = "" if tabtype == "S" else _fav["fav{0}".format(favfilter)]["emo"]  # TODO: symbol when ALL or not found
            words = fullquery.split(" ")
            words_count = len(words)

            """
            if (words_count == 4 and words[0].isdigit() and words[1].isdigit() and words[2].isdigit() and words[3].isdigit()) \
                    or (words_count == 4 and words[0].isdigit() and words[1].isdigit() and words[2].isdigit() and words[3].upper() == "CR:") \
                    or (words_count == 3 and words[0].isdigit() and words[1].isdigit() and words[2].isdigit()) \
                    or (words_count == 2 and words[0].isdigit() and words[1].isdigit()):
                bbname_ref = _bbName
            else:
                bbname_ref = bbname
            """
            bbname_ref = bbname

            if words_count >= 2 and words[0].isdigit():
                bnumber = int(words[0])
                book_name_verbose, dummy = somdal.get_book_ref(bbname_ref, bnumber)
                if book_name_verbose is None:
                    if tabtype == "S":
                        tabtitle = "{0} {1}".format(tabid, fullquery)
                    else:
                        tabtitle = "{0} {1} {2}".format(tabid, favsymbol, fullquery)
                else:
                    words_str = ""
                    words[0] = book_name_verbose
                    for part in words:
                        words_str = "{0} {1}".format(words_str, part)

                    if tabtype == "S":
                        tabtitle = "{0}{1}".format(tabid, words_str)
                    else:
                        tabtitle = "{0} {1}{2}".format(tabid, favsymbol, words_str)
            else:
                if tabtype == "S":
                    tabtitle = "{0} {1}".format(tabid, fullquery)
                else:
                    tabtitle = "{0} {1} {2}".format(tabid, favsymbol, fullquery)

        dict_menu[i] = tabtitle     # item
        i += 1

    return dict_menu


def show_history_menu(menu_x, menu_title_cache_tab):
    """
    Show cache tabs
    :param menu_x: x pos
    :param menu_title_cache_tab: title
    :return: item selected or None if esc
    """
    dict_menu = get_history_dict_menu()
    if dict_menu is None or len(dict_menu) == 0:
        return None
    size_menu = len(dict_menu)
    size_menu_mini = 10
    pos_start = 0
    pos_block = 0
    highlight_menu_index = 0

    while True:
        j = 0
        dict_menu_mini = {}
        for i in range(pos_start, pos_start + size_menu_mini):
            if i >= size_menu:
                break
            dict_menu_mini[j] = dict_menu[i]
            j += 1

        menu_item_selected, movement, char_key = show_menu(menu_x, menu_title_cache_tab, dict_menu_mini, True, True,
                                                           highlight_menu_index)
        if movement == 0:
            break
        elif movement in (-1, 1):
            pos_block += movement
            if pos_block < 0:
                pos_block = 0
            pos_start = pos_block * size_menu_mini
            highlight_menu_index = 0
        elif movement == 3:
            if char_key not in ("x", "X"):
                continue
            if dict_menu_mini is None or len(dict_menu_mini) == 0:
                continue

            try:
                item_to_delete = dict_menu_mini[menu_item_selected]
            except KeyError:
                continue

            if item_to_delete == "":
                continue

            tabid_to_delete = int(item_to_delete.split(" ")[0])
            somdal.delete_cache_tab_by_id(tabid_to_delete)

            # Rebuild menu
            dict_menu = get_history_dict_menu()
            if dict_menu is None or len(dict_menu) == 0:
                return None
            size_menu = len(dict_menu)
            highlight_menu_index = menu_item_selected

    # Finally
    if menu_item_selected < 0 or menu_item_selected >= len(dict_menu_mini):
        return None

    item_selected = dict_menu_mini[menu_item_selected]
    return item_selected


def get_bible_dict_verbose():
    return {
        0: "(EN) King James 1611 (K)",
        1: "(EN) King James 2000 (2)",
        2: "(ES) Reina Valera (V)",
        3: "(FR) Louis Segond (L)",
        4: "(FR) Ostervald (O)",
        5: "(IT) G. Diodati (D)",
        6: "(PT) Almeida (A)",
        7: "(DE) Schlachter (S)"
    }


def get_bible_dict_short():
    return {
        0: "k",
        1: "2",
        2: "v",
        3: "l",
        4: "o",
        5: "d",
        6: "a",
        7: "s"
    }


def get_bible_menu_index(bbname):
    if bbname == "k":
        return 0
    elif bbname == "2":
        return 1
    elif bbname == "v":
        return 2
    elif bbname == "l":
        return 3
    elif bbname == "o":
        return 4
    elif bbname == "d":
        return 5
    elif bbname == "a":
        return 6
    elif bbname == "s":
        return 7
    return 0


def generate_bookmark_dict():
    """
    Generate bookmark dict
    "desc": description
    "emo": emoji
    """
    try:
        gen_dict = {}
        bookmark_representation_dict = somdal.get_favorite_representation_dict()
        for k in bookmark_representation_dict.keys():
            k_name = "fav{0}".format(k)
            gen_dict[k_name] = {
                "desc": res(k_name),
                "emo": bookmark_representation_dict[k]
            }
        return gen_dict
    except Exception as ex:
        raise ex


# noinspection PyBroadException
def get_article(art_name):
    """
    Get article
    :param art_name: article name
    :return: article content as list, art_name_verbose
    """
    sep_block = "__ <br>"  # Space needed at the end
    art_name_verbose = _xml.find(art_name).text
    xml_art_content = _xml.find("{0}_CONTENT".format(art_name))
    if xml_art_content is not None:
        art_content = xml_art_content.text
    else:
        xml_en = xml.etree.ElementTree.parse(
            "{0}".format(pkg_resources.resource_filename('sonofman.data', 'strings-en.xml')),
            xml.etree.ElementTree.XMLParser()).getroot()
        xml_art_content = xml_en.find("{0}_CONTENT".format(art_name))
        art_content = xml_art_content.text

    tag = "R"
    tag_start = "<{0}>".format(tag)
    tag_end = "</{0}>".format(tag)
    while True:
        rtag_start = art_content.find(tag_start)
        if rtag_start < 0:
            break
        rtag_end = art_content.find(tag_end, rtag_start)
        if rtag_end < 0:
            continue
        rdigits = art_content[rtag_start:rtag_end].replace(tag_start, "").split(" ")
        if len(rdigits) == 4:
            bbname = _bbName
            bnumber, cnumber, verse_number, verse_number_to = int(rdigits[0]), int(rdigits[1]), int(rdigits[2]), int(rdigits[3])
        else:
            bbname, bnumber, cnumber, verse_number, verse_number_to = rdigits[0], int(rdigits[1]), int(rdigits[2]), int(rdigits[3]), int(rdigits[4])
        s = somdal.get_verses(_delimiterVerse, _tbbName, bnumber, cnumber, verse_number, verse_number_to)   # bbName??
        s_string = somdal.get_verses_string(s)
        art_content = "{0}{1}{2}<br><br>{3}".format(art_content[0:rtag_start], sep_block, s_string,
                                                    art_content[rtag_end + len(tag_end):])

    tag = "HB"
    tag_start = "<{0}>".format(tag)
    tag_end = "</{0}>".format(tag)
    while True:
        rtag_start = art_content.find(tag_start)
        if rtag_start < 0:
            break

        rtag_end = art_content.find(tag_end, rtag_start)
        if rtag_end < 0:
            continue

        bnumber = art_content[rtag_start:rtag_end].replace(tag_start, "")
        bbname = _bbName
        bname, bsname = somdal.get_book_ref(bbname, bnumber)
        s = "<br><br>_HB_{0}<br><br>".format(bname)
        art_content = "{0}{1}{2}".format(art_content[0:rtag_start], s, art_content[rtag_end + len(tag_end):])

    art_content = art_content.replace("\n", "")  # At the beginning
    art_content = art_content.replace("<b>", "")
    art_content = art_content.replace("</b>", "")
    art_content = art_content.replace("<blockquote>", "\n{0}".format(sep_block))
    art_content = art_content.replace("</blockquote>", "\n")
    art_content = art_content.replace("<i>", "")
    art_content = art_content.replace("</i>", "")
    art_content = art_content.replace("<u>", "")
    art_content = art_content.replace("</u>", "")
    art_content = art_content.replace("<center>", "")
    art_content = art_content.replace("</center>", "")
    art_content = art_content.replace("<H>", "\n\n#")
    art_content = art_content.replace("</H>", "\n\n")
    art_content = art_content.replace("<HA/>", "#{0}<br><br>".format(art_name_verbose))
    art_content = art_content.replace("<HS>", "<br>• ")
    art_content = art_content.replace("</HS>", "<br><br>")
    art_content = art_content.replace("\\'", "'")
    art_content = art_content.replace('\\"', '"')
    art_content = art_content.replace("&#8230;", "...")
    art_content = art_content.replace("&nbsp;", " ")
    art_content = art_content.replace("&lt;", "<")
    art_content = art_content.replace("&gt;", ">")
    art_content = art_content.replace("<br>", "\n")  # At the end

    lst = []
    art_content_arr = art_content.splitlines(True)
    ref = ["", ""]
    for itm in art_content_arr:
        item = [itm, ref]
        lst.append(item)

    return lst, art_name_verbose


def move_art_prbl(is_article, step):
    """
    Move LEFT/RIGHT within ART/PRBL
    param is_article: is article
    param step: +1, -1
    No return value
    """
    array_name = "ART_ARRAY" if is_article else "PRBL_ARRAY"
    xml_lst = _xml.find(array_name).findall("item")

    # Search
    pos = 0
    if is_article:
        for item in xml_lst:
            if item.text == _action_query:
                break
            pos += 1
    else:
        for item in xml_lst:
            if item.text.split("|")[0] == _action_query:
                break
            pos += 1

    # Move
    if (pos + step) >= len(xml_lst) or (pos + step < 0):
        return

    pos += step
    action_query = xml_lst[pos].text if is_article else xml_lst[pos].text.split("|")[0]
    save_action(_action_type, _action_bbname, action_query, 2, -1, should_add=False)
    show_history(_history, 0)


def show_history(history, from_line_nr):
    """
    Show history
    :param history: history parameter
    :param from_line_nr:
    """
    global _queryExpr

    if len(history) == 2:
        history_bbname = history[0]
        history_query = history[1]
        history_type_sf = "S"
        history_order_by = 2
        history_fav_filter = -1
    elif len(history) == 5:
        history_bbname = history[0]
        history_query = history[1]
        history_type_sf = history[2]
        history_order_by = int(history[3])
        history_fav_filter = int(history[4])
    else:
        return

    if history_query.find("ART") == 0:
        s, art_name_verbose = get_article(history_query)
        _queryExpr = ""
        _wm_util.fill_window(s, from_line_nr, _queryExpr)
        focus_row_init()

        save_action("A", history_bbname, history_query, history_order_by, history_fav_filter)
        save_title(res("ARTICLES"))
        save_sub_title(art_name_verbose)
        show_title_and_subtitle()

    elif history_query.find("PRBL") == 0:
        xml_lst = _xml.find("PRBL_ARRAY").findall("item")
        prbl_digits = None
        prbl_name_verbose = ""
        for item in xml_lst:
            prbl_fields = item.text.split("|")
            prbl_name = prbl_fields[0]
            if prbl_name == history_query:
                prbl_digits = prbl_fields[1]
                prbl_name_verbose = _xml.find(prbl_name).text
                break

        if prbl_digits is None:
            raise Exception("Unable to find parable '{0}'!".format(history_query))

        digits = prbl_digits.split(" ")
        bnumber, cnumber, verse_number, verse_number_to = int(digits[0]), int(digits[1]), int(digits[2]), int(digits[3])

        s = somdal.get_verses(_delimiterVerse, _tbbName, bnumber, cnumber, verse_number, verse_number_to)
        _queryExpr = ""
        _wm_util.fill_window(s, from_line_nr, _queryExpr)
        focus_row_init()

        save_action("P", history_bbname, history_query, history_order_by, history_fav_filter)
        save_title(res("PARABLES"))
        save_sub_title(prbl_name_verbose)
        show_title_and_subtitle()
    else:
        s = get_bible_search(history_bbname, history_query, history_type_sf, history_order_by, history_fav_filter)
        _wm_util.fill_window(s, from_line_nr, _queryExpr)
        focus_row_init()

    return


def replace_colors():
    for k in _colorBible.keys():
        pos_color = _colorBible[k].find("COLOR")
        if pos_color >= 0:
            _colorBible[k] = _colorBible[k][0:pos_color]


def load_colors():
    global _colorBible

    color_k = somconfig.get_option("PREFERENCES", "COLOR_K" if _useColors else "NO_COLOR_K", None, "#")
    color_2 = somconfig.get_option("PREFERENCES", "COLOR_2" if _useColors else "NO_COLOR_2", None, "#")
    color_v = somconfig.get_option("PREFERENCES", "COLOR_V" if _useColors else "NO_COLOR_V", None, "#")
    color_l = somconfig.get_option("PREFERENCES", "COLOR_L" if _useColors else "NO_COLOR_L", None, "#")
    color_o = somconfig.get_option("PREFERENCES", "COLOR_O" if _useColors else "NO_COLOR_O", None, "#")
    color_d = somconfig.get_option("PREFERENCES", "COLOR_D" if _useColors else "NO_COLOR_D", None, "#")
    color_a = somconfig.get_option("PREFERENCES", "COLOR_A" if _useColors else "NO_COLOR_A", None, "#")
    color_s = somconfig.get_option("PREFERENCES", "COLOR_S" if _useColors else "NO_COLOR_S", None, "#")
    color_highlight_search = somconfig.get_option("PREFERENCES", "COLOR_HIGHLIGHT_SEARCH" if _useColors else "NO_COLOR_HIGHLIGHT_SEARCH", None, "A_REVERSE#")
    _colorBible = {"k": color_k, "v": color_v, "l": color_l, "d": color_d, "a": color_a, "o": color_o, "s": color_s, "2": color_2, "HIGHLIGHT_SEARCH": color_highlight_search}


def load_config():
    global _locale, _alt_locale, _useColors, _bbName, _tbbName, _history, _colorBible, _themeNr

    _locale = somconfig.get_option("PREFERENCES", "LOCALE", ("en", "es", "fr", "it", "pt", "de"), "en")
    _alt_locale = somconfig.get_option("PREFERENCES", "ALT_LOCALE", ("en", "es", "fr", "it", "pt"), "en")
    _themeNr = somconfig.get_option("PREFERENCES", "USE_COLORS", ("0", "1", "2", "3"), "0")
    _useColors = False if _themeNr == "0" else True
    _bbName = somconfig.get_option("PREFERENCES", "BIBLE_PREFERED", ("k", "v", "l", "d", "a", "o", "s", "2"), "k")
    _tbbName = somconfig.get_option("PREFERENCES", "BIBLE_MULTI", None, _bbName)

    if _locale != "de":
        _alt_locale = _locale

    load_colors()

    if not _useColors:
        replace_colors()

    set_locale(_locale)

    try:
        history_current_key = somconfig.get_option("PREFERENCES", "HISTORY_CURRENT", None, "0")
        if somconfig.config.has_option("HISTORY", history_current_key):
            history_current_value = somconfig.get_option("HISTORY", history_current_key, None, "ART_APP_HELP")
            history_current_values = history_current_value.split("#")
            history_current_values_size = len(history_current_values)
            if history_current_values_size == 5:
                _history = [history_current_values[0], history_current_values[1], history_current_values[2], history_current_values[3], history_current_values[4]]
            elif history_current_values_size == 2:
                _history = [history_current_values[0], history_current_values[1]]
            elif history_current_values_size == 1:
                _history = [_bbName, history_current_values[0]]
            else:
                somutil.print("! (was) invalid history option: '{0}'".format(history_current_value))
                _history = [_bbName, "ART_APP_HELP", "S", 2, -1]
        else:
            somutil.print("! (was) invalid history_current: '{0}'".format(history_current_key))
            _history = [_bbName, "ART_APP_HELP", "S", 2, -1]
    except Exception as ex:
        somutil.print("! (was) unable to read history, please check: {0}".format(ex))
        _history = [_bbName, "ART_APP_HELP", "S", 2, -1]

    # somconfig.get_option("PREFERENCES", "BIBLE_TRAD")     # => tbbname
    # somconfig.get_option("UI", "COLOR_THEME_NR")
    # somconfig.get_option("UI", "COLOR_THEME_DIALOG_NR")
    # somconfig.get_option("UI", "COLOR_THEME_ERROR_NR")


def save_config():
    if not _useColors:
        replace_colors()

    somconfig.set_option("PREFERENCES", "LOCALE", _locale)
    somconfig.set_option("PREFERENCES", "ALT_LOCALE", _alt_locale)
    somconfig.set_option("PREFERENCES", "USE_COLORS", _themeNr)
    somconfig.set_option("PREFERENCES", "BIBLE_PREFERED", _bbName)
    somconfig.set_option("PREFERENCES", "BIBLE_MULTI", _tbbName)
    somconfig.set_option("PREFERENCES", "COLOR_K" if _useColors else "NO_COLOR_K", _colorBible["k"])
    somconfig.set_option("PREFERENCES", "COLOR_2" if _useColors else "NO_COLOR_2", _colorBible["2"])
    somconfig.set_option("PREFERENCES", "COLOR_V" if _useColors else "NO_COLOR_V", _colorBible["v"])
    somconfig.set_option("PREFERENCES", "COLOR_L" if _useColors else "NO_COLOR_L", _colorBible["l"])
    somconfig.set_option("PREFERENCES", "COLOR_O" if _useColors else "NO_COLOR_O", _colorBible["o"])
    somconfig.set_option("PREFERENCES", "COLOR_D" if _useColors else "NO_COLOR_D", _colorBible["d"])
    somconfig.set_option("PREFERENCES", "COLOR_A" if _useColors else "NO_COLOR_A", _colorBible["a"])
    somconfig.set_option("PREFERENCES", "COLOR_S" if _useColors else "NO_COLOR_S", _colorBible["s"])
    somconfig.set_option("PREFERENCES", "COLOR_HIGHLIGHT_SEARCH" if _useColors else "NO_COLOR_HIGHLIGHT_SEARCH", _colorBible["HIGHLIGHT_SEARCH"])

    history_item = "{0}#{1}#{2}#{3}#{4}".format(_action_bbname, _action_query, _action_type_sf, _action_order_by, _action_fav_filter)
    somconfig.set_option("PREFERENCES", "HISTORY_CURRENT", "0")
    somconfig.set_option("HISTORY", "0", history_item)

    somconfig.save_config()


def restart(allow_to_load_another_article):
    """
    Restart
    :param allow_to_load_another_article: True/False
    """
    if allow_to_load_another_article:
        if _action_query == "ART_APP_HELP_BEGINNING":
            save_action("A", _bbName, "ART_APP_HELP", 2, -1)

    save_config()
    python = sys.executable
    os.execl(python, python, *sys.argv)


def finish(return_code):
    global _wm_util

    del _wm_util
    u.endwin()
    u.reset_shell_mode()
    u.curs_set(1)

    somutil.print("* Tips: if you have problems in console, type reset or CTRL-D to restore it.")
    exit(return_code)


def reset_window(panel, win):
    u.panel_above(panel)
    u.update_panels()
    u.doupdate()

    u.wclear(win)


# noinspection PyTypeChecker
def main():
    global _maxY, _maxX, _bbName, _bNumber, _cNumber, _useColors, _colorTheme, _colorThemeDialog, \
            _colorThemeErr, _colorThemeFunc1, _colorThemeFunc2, _themeNr, _reset_status_before_key, _win_status, \
            _win_title, _xml, _wm_util, _cy, _tabId, _fav, _queryExpr

    try:
        # Config
        load_config()

        # Resource
        _xml = xml.etree.ElementTree.parse(
            "{0}".format(pkg_resources.resource_filename('sonofman.data', 'strings-{0}.xml'.format(_alt_locale))),
            xml.etree.ElementTree.XMLParser()).getroot()

        # Settings before initialization of ncurses
        os.environ.setdefault('ESCDELAY', '25')

        # Screen
        stdscr = u.initscr()
        u.start_color()
        u.noecho()

        # Colors
        if _useColors:
            if u.has_colors():
                u.init_pair(0, -1, -1)
                u.init_pair(1, u.COLOR_WHITE, u.COLOR_BLACK)
                u.init_pair(2, u.COLOR_GREEN, u.COLOR_BLACK)
                u.init_pair(3, u.COLOR_CYAN, u.COLOR_BLACK)
                u.init_pair(4, u.COLOR_MAGENTA, u.COLOR_BLACK)
                u.init_pair(5, u.COLOR_YELLOW, u.COLOR_BLACK)
                u.init_pair(6, u.COLOR_RED, u.COLOR_BLACK)
                u.init_pair(11, u.COLOR_WHITE, u.COLOR_BLUE)
                u.init_pair(12, u.COLOR_BLACK, u.COLOR_CYAN)
                u.init_pair(13, u.COLOR_YELLOW, u.COLOR_BLUE)
                u.init_pair(21, u.COLOR_WHITE, u.COLOR_RED)
                u.init_pair(22, u.COLOR_BLACK, u.COLOR_WHITE)
            else:
                _useColors = False
                for i in (0, 1, 2, 3, 4, 5, 6, 11, 12, 13, 21, 22):
                    u.init_pair(i, -1, -1)
        else:
            for i in (0, 1, 2, 3, 4, 5, 6, 11, 12, 13, 21, 22):
                u.init_pair(i, -1, -1)

        color_theme_no_color_nr = 0
        color_theme_err_nr = 21
        color_theme_func_nr1 = 1
        color_theme_func_nr2 = 12

        if _themeNr == "1":
            color_theme_nr = 11
            color_theme_dialog_nr = 11
        elif _themeNr == "3":
            color_theme_nr = 22
            color_theme_dialog_nr = 22
        else:
            color_theme_nr = 2
            color_theme_dialog_nr = 1

        _colorTheme = u.color_pair(color_theme_nr if _useColors else color_theme_no_color_nr)
        _colorThemeDialog = u.color_pair(color_theme_dialog_nr if _useColors else color_theme_no_color_nr)
        _colorThemeErr = u.color_pair(color_theme_err_nr if _useColors else color_theme_no_color_nr)
        _colorThemeFunc1 = u.color_pair(color_theme_func_nr1 if _useColors else color_theme_no_color_nr)
        _colorThemeFunc2 = u.color_pair(color_theme_func_nr2 if _useColors else color_theme_no_color_nr)

        # Dims
        _maxY, _maxX = u.getmaxyx(stdscr)
        somutil.print("* Lines/Cols: {0}x{1}".format(_maxY, _maxX))

        win_main_top_border_lines = 2     # 2 lines
        win_main_bottom_border_lines = 3  # 3 lines
        win_main_lines = _maxY - win_main_top_border_lines - win_main_bottom_border_lines  # Border Y
        win_main_cols = _maxX      # Border X: 0
        win_title_cols = _maxX

        if _maxY < 20:
            somutil.print("! Terminal should have min. 20 lines")

        # Bar
        u.mvwhline(stdscr, _maxY - 3, 0, _colorTheme, _maxX)
        u.mvwaddstr(stdscr, _maxY - 2, 0, " " * _maxX, _colorTheme)
        function_keys_dict = {
            "1|M": res("MENU"),
            "2|{0}".format("B" if sys.platform == 'darwin' else "F2"): res("BOOKS"),
            "3|{0}".format("S" if sys.platform == 'darwin' else "F3"): res("SEARCH"),
            "4|{0}".format("F" if sys.platform == 'darwin' else "F6"): res("SEARCH_FAV"),
            "5|{0}".format("A" if sys.platform == 'darwin' else "F4"): res("ARTICLES"),
            "6|{0}".format("P" if sys.platform == 'darwin' else "F5"): res("PARABLES"),
            "7|Q": res("QUIT")
        }
        func_pos = 0
        for k in sorted(function_keys_dict.keys()):
            v = function_keys_dict[k]
            kstr = k.split("|")[1]
            u.mvwaddstr(stdscr, _maxY - 2, func_pos, kstr, _colorThemeFunc1)
            func_pos += len(kstr)
            u.mvwaddstr(stdscr, _maxY - 2, func_pos, v, _colorThemeFunc2 if _useColors else _colorThemeFunc2 + u.A_REVERSE)
            func_pos += len(v)
            u.mvwaddstr(stdscr, _maxY - 2, func_pos, " ", _colorThemeFunc1)
            func_pos += 1
        if (func_pos - 1) > win_title_cols:
            u.mvwaddstr(stdscr, _maxY - 2, 0, " " * _maxX, _colorTheme)
            u.mvwaddstr(stdscr, _maxY - 2, 0, "H:", _colorThemeFunc1)
            u.mvwaddstr(stdscr, _maxY - 2, 2, res("HELP"), _colorThemeFunc2 if _useColors else _colorThemeFunc2 + u.A_REVERSE)
        del function_keys_dict

        # Title
        u.mvwhline(stdscr, 1, 0, _colorTheme, _maxX)

        _win_title = u.newwin(1, win_title_cols, 0, 0)
        u.wbkgd(_win_title, " ", _colorThemeFunc2)
        u.keypad(_win_title, False)
        u.new_panel(_win_title)     # Should be panel_title = u.new_panel(_win_title)

        _win_status = u.newwin(1, win_title_cols, _maxY - 1, 0)
        u.wbkgd(_win_status, " ", _colorTheme)
        u.keypad(_win_status, False)
        u.new_panel(_win_status)    # Should be panel_status = u.new_panel(_win_status)

        win_main = u.newwin(win_main_lines, win_main_cols, win_main_top_border_lines, 0)
        u.wbkgd(win_main, " ", _colorTheme)
        u.keypad(win_main, True)
        # u.notimeout(win_main, True)   # TODO: notimeout ?
        # u.nodelay(win_main, True)     # TODO: nodelay ?
        panel_main = u.new_panel(win_main)
        # wbkgd(win_main, " ", color_pair(2))

        u.panel_above(panel_main)
        u.update_panels()
        u.doupdate()

        # Settings after initialization of ncurses
        u.curs_set(1)

        # Other load
        _fav = generate_bookmark_dict()

        # Search
        _wm_util = som_winutil.WinUtil(win_main, win_main_lines, win_main_cols, win_main_top_border_lines, win_main_bottom_border_lines, _colorBible)
        show_history(_history, 0)

        while True:
            key = u.wgetch(win_main)

            if _reset_status_before_key is False:        # TODO: to optimize
                _reset_status_before_key = True
                clear_status()

            if key in (118, 86):  # v V
                focus_row(1)
                continue

            elif key in (116, 84):  # t T, u.KEY_SR:Shift-Up, u.KEY_SF:Shift-Down
                focus_row(-1)
                continue

            elif key in (10, 99, 67):   # ENTER, c, C
                show_context_menu(panel_main, win_main, "" if key == 10 else "C")
                continue

            elif key == 9:  # TAB
                cache_tab_selected = show_history_menu(0, res("HISTORY"))
                if cache_tab_selected is None:
                    focus_row(0)
                    continue
                words = cache_tab_selected.split(" ")
                tabid = int(words[0])
                ct = somdal.get_cache_tab_by_id(tabid)
                if ct is None:
                    continue
                _tabId = tabid
                history = [ct.bbname, ct.fullquery, "F" if ct.tabtype == "F" else "S", ct.orderby, ct.favfilter]
                show_history(history, 0)
                continue

            elif key in (u.KEY_UP, u.KEY_PPAGE):
                mv = _wm_util.move(-1)
                if not mv:
                    continue
                _wm_util.fill_window(None, _wm_util.s_line_pos, _queryExpr)
                focus_row_init()
                continue

            elif key in (u.KEY_DOWN, u.KEY_NPAGE):
                mv = _wm_util.move(1)
                if not mv:
                    continue
                _wm_util.fill_window(None, _wm_util.s_line_pos, _queryExpr)
                focus_row_init()
                continue

            elif key == u.KEY_LEFT:
                if _action_type == 'B':
                    if _cNumber <= 1:
                        continue
                    _cNumber -= 1

                    query = "{0} {1}".format(_bNumber, _cNumber)
                    s = get_bible_search(_action_bbname, query, _action_type_sf, _action_order_by, _action_fav_filter, should_add=False)
                    _wm_util.fill_window(s, 0, _queryExpr)
                    focus_row_init()
                    continue

                elif _action_type == 'A':
                    move_art_prbl(True, -1)
                    focus_row_init()
                    continue

                elif _action_type == 'P':
                    move_art_prbl(False, -1)
                    focus_row_init()
                    continue

            elif key == u.KEY_RIGHT:
                if _action_type == 'B':
                    ci = somdal.get_bible_chapter_count_by_book(_bNumber)
                    if _cNumber >= ci[0]:
                        continue
                    _cNumber += 1

                    query = "{0} {1}".format(_bNumber, _cNumber)
                    s = get_bible_search(_action_bbname, query, _action_type_sf, _action_order_by, _action_fav_filter, should_add=False)
                    _wm_util.fill_window(s, 0, _queryExpr)
                    focus_row_init()
                    continue

                elif _action_type == 'A':
                    move_art_prbl(True, 1)
                    focus_row_init()
                    continue

                elif _action_type == 'P':
                    move_art_prbl(False, 1)
                    focus_row_init()
                    continue

            elif key in (u.KEY_F(2), u.KEY_F(3), u.KEY_F(6), 98, 66, 115, 83, 102, 70):   # b B, s S, f F
                u.panel_below(panel_main)
                u.update_panels()
                u.doupdate()

                if key in (u.KEY_F(3), 115, 83):
                    search_type = "S"
                elif key in (u.KEY_F(2), 98, 66):
                    search_type = "B"
                else:
                    search_type = "F"

                bbname, query, search_type_sf, order_by, fav_filter = show_search(search_type)
                if bbname is None and query is None:
                    focus_row(0)
                    continue

                s = get_bible_search(bbname, query, search_type_sf, order_by, fav_filter)
                if len(s) == 0:
                    reset_window(panel_main, win_main)
                    show_history(_history, _wm_util.s_line_pos)
                    continue

                reset_window(panel_main, win_main)
                _wm_util.fill_window(s, _wm_util.s_line_pos, _queryExpr)
                focus_row_init()
                continue

            elif key in (u.KEY_F(4), 97, 65, 104, 72):  # a A, h H
                art_name_filter = "ART_APP_HELP" if key in (104, 72) else None
                u.panel_below(panel_main)

                art_name, art_ref, art_verbose_name = show_art_prbl(True, art_name_filter)
                if art_name is None:
                    continue

                save_action("A", _bbName, art_name, 2, -1)
                save_sub_title(art_verbose_name)
                show_title_and_subtitle()

                s, art_verbose_name = get_article(art_name)
                reset_window(panel_main, win_main)
                _queryExpr = ""
                _wm_util.fill_window(s, 0, _queryExpr)
                focus_row_init()
                continue

            elif key in (u.KEY_F(5), 112, 80):  # p P
                u.panel_below(panel_main)

                prbl_name, prbl_digits, prbl_verbose_name = show_art_prbl(False, None)
                if prbl_name is None:
                    continue

                digits = prbl_digits.split(" ")
                _bNumber, _cNumber, verse_number, verse_number_to = int(digits[0]), int(digits[1]), int(digits[2]), int(digits[3])

                save_action("P", _bbName, prbl_name, 2, -1)
                save_sub_title(prbl_verbose_name)
                show_title_and_subtitle()

                s = somdal.get_verses(_delimiterVerse, _tbbName, _bNumber, _cNumber, verse_number, verse_number_to)
                reset_window(panel_main, win_main)
                _queryExpr = ""
                _wm_util.fill_window(s, 0, _queryExpr)
                focus_row_init()
                continue

            elif key in (114, 82):  # r R
                restart(False)

            elif key in (u.KEY_F(10), 113, 81):  # q Q
                show_status("{0}: {1}".format(res("QUIT"), res("CONFIRM")), _colorTheme, True)

                quit_key = u.wgetch(_win_status)
                u.flushinp()

                if quit_key == 10:
                    save_config()
                    finish(0)

                clear_status()
                continue

            elif key == u.KEY_HOME:
                _wm_util.fill_window(None, 0, _queryExpr)
                focus_row_init()
                continue

            elif key in (109, 77):  # m M
                menu()
                focus_row(0)
                continue

    except Exception as ex:
        print_ex(ex)


if __name__ == '__main__':
    main()


"""
Not used
--------

def f4():
    height = _maxY
    width = _maxX
    win = newwin(height, width, 2, 0)
    wbkgd(win, " ", _colorThemeDialog)

    row_pos = 3
    item_width = 25
    max_item_by_row = floor(width / item_width)
    books = libs.get_list_book_by_name(item_width, _bbName, True, "")
    mvwaddstr(win, row_pos, 0, "", _colorTheme)
    i = 1
    for b in books:
        waddstr(win, b, _colorTheme)
        if i >= max_item_by_row:
            i = 1
            row_pos += 1
            mvwaddstr(win, row_pos, 0, "", _colorTheme)
        else:
            i += 1

    panel = new_panel(win)
    panel_above(panel)
    update_panels()
    doupdate()

    mvwaddstr(win, 1, 1, _("BOOK"), _colorTheme)
    echo()
    wgetstr(win)
    noecho()
    delwin(win)
# -----------------------------------------------------------------------        
               
# debug
# region Description
# if len(sys.argv) != 4:
#     sys.argv.append("f")
#     sys.argv.append(1)
#     sys.argv.append(1)
#
# sys.argv.pop(0)
# lang = sys.argv.pop(0)
# if lang == "e":
#     _bbName = "k"
# elif lang == "f":
#     _bbName = "l"
# elif lang == "s":
#     _bbName = "v"
# elif lang == "i":
#     _bbName = "d"
# else:
#     sys.stderr.write("usage: som_main.py <lang> <bNumber> <cNumber>")
#     exit(1)
# _bNumber = int(sys.argv.pop(0))
# _cNumber = int(sys.argv.pop(0))
# endregion
#
# locale.setlocale(locale.LC_ALL, '')
# code = locale.getpreferredencoding()
#
# try:
# from unicurses import * was here
# except:
# pass
# -----------------------------------------------------------------------        
               
# elif key == KEY_F(4):
#     panel_below(panel_search)
#
#     f4()
#
#     panel_above(panel_search)
#     update_panels()
#     doupdate()
#     fill_window(win_main, win_search_lines, s_line_pos, _queryExpr)
"""
