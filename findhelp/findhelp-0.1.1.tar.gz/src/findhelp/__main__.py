import argparse
from findhelp.finder import go_search

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Arguments for searching
    parser.add_argument("-p", "--path", type=str,
                        help="Root path to look for, default = current directory", default=".")
    parser.add_argument("-s", "--stringsearch", type=str,
                        help="The string to look for", default="")
    parser.add_argument("-i", "--ignorecase", action="store_true",
                        help="Indicates whether or not searching is case-sensitive")
    parser.add_argument("-c", "--ignoreaccents",
                        action="store_true", help="Ignore accents")
    parser.add_argument("-r", "--regexp", action="store_true",
                        help="Searches by regular expresion")
    parser.add_argument("-e", "--ext", nargs="+",
                        help="List of extensions to limit the search")
    parser.add_argument("-a", "--all", action="store_true",
                        help="Searchs on all folders, ignores 'ignore_folders' switch on config.yaml")
    parser.add_argument("-f", "--onlyfiles", action="store_true",
                        help="Searches only for files (not directories)")
    parser.add_argument("-d", "--onlydirs", action="store_true",
                        help="Searches only for directories (not files)")
    parser.add_argument("-ds", "--directoryseparator", help="Just for results purposes: which separator use for paths",
                        type=str, choices=("/", "\\\\", "\\"), default="/")

    # Arguments for outuput results
    parser.add_argument("-o", "--output", choices=("console",
                        "txt", "csv", "json", "df", "obj_list", "list"), default="console", help="Indicates if results appears on console or are written to a file")
    parser.add_argument("-dl", "--delimiter", type=str, default="\t",
                        help="Delimiter used for exporting, when output is different than 'console'")
    parser.add_argument("-m", "--outputpath", type=str,
                        help="Output (results) path", default=".")
    parser.add_argument("-n", "--outputfilename", type=str,
                        help="Output (results) filename (with no extension)")

    # Parse args
    full_args = vars(parser.parse_args())
    print(full_args)

    go_search(full_args)
