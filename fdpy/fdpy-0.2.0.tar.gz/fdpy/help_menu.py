class LongHelp:
    """
    Parameters:
        pattern
                the search pattern which is either a regular expression (default) or a glob pattern (if
                glob is used).
        path (optional)
                The directory where the filesystem search is rooted (optional). If omitted, search the
                current working directory.
    Kwargs:
        hidden:
                Include hidden directories and files in the search results (default: hidden files and
                directories are skipped). Files and directories are considered to be hidden if their name
                starts with a `.` sign (dot).
        no_ignore:
                Show search results from files and directories that would otherwise be ignored by
                '.gitignore', '.ignore', '.fdignore', or the global ignore file.
            no_ignore_vcs:
                Show search results from files and directories that would otherwise be ignored by
                '.gitignore' files.
        unrestricted:
                Alias for 'no_ignore=True'.

        case_sensitive:
                Perform a case_sensitive search. By default, fd uses case_insensitive searches, unless the
                pattern contains an uppercase character (smart case).
        ignore_case:
                Perform a case_insensitive search. By default, fd uses case_insensitive searches, unless
                the pattern contains an uppercase character (smart case).
        glob:
                Perform a glob_based search instead of a regular expression search.

            regex:
                Perform a regular_expression based search (default). This can be used to override 'glob=True'.

        fixed_strings:
                Treat the pattern as a literal string instead of a regular expression. Note that this also
                performs substring comparison. If you want to match on an exact filename, consider using
                'glob=True'.
        absolute_path:
                Shows the full path starting from the root as opposed to relative paths.

        list_details:
                Use a detailed listing format like 'ls -l' in shell. This is basically an alias for 'exec_batch
                ls -l' with some additional 'ls' options. This can be used to see more metadata, to show
                symlink targets and to achieve a deterministic sort order.
        follow:
                By default, fd does not descend into symlinked directories. Using this flag, symbolic
                links are also traversed.
        full_path:
                By default, the search pattern is only matched against the filename (or directory name).
                Using this flag, the pattern is matched against the full path.
        print0:
                Separate search results by the null character (instead of newlines).
            prune:
                Do not traverse into matching directories.

        one:
                Limit the search to a single result and quit immediately. This is an alias for 'max_
                results=1'.
            show_errors:
                Enable the display of filesystem errors for situations such as insufficient permissions or
                dead symlinks.
            one_file_system:
                By default, fd will traverse the file system tree as far as other options dictate. With
                this flag, fd ensures that it does not descend into a different file system than the one
                it started in. Comparable to the -mount or -xdev filters of find(1) in shell.


    Options:
        max_depth <depth>
                Limit the directory traversal to a given depth. By default, there is no limit on the
                search depth.
            min_depth <depth>
                Only show search results starting at the given depth. See also: 'max_depth' and
                'exact_depth'
            exact_depth <depth>
                Only show search results at the exact given depth. This is an alias for 'min_depth
                <depth> max_depth <depth>'.
            type <filetype>...
                Filter the search by type (multiple allowable filetypes can be specified):
                  'f' or 'file':         regular files
                  'd' or 'directory':    directories
                  'l' or 'symlink':      symbolic links
                  'x' or 'executable':   executables
                  'e' or 'empty':        empty files or directories
                  's' or 'socket':       socket
                  'p' or 'pipe':         named pipe (FIFO)
            extension <ext>...
                (Additionally) filter search results by their file extension. Multiple allowable file
                extensions can be specified.
                If you want to search for files without extension, you can use the regex '^[^.]+$' as a
                normal search pattern.
            exec <cmd>
                Execute a command for each search result.
                All arguments following exec are taken to be arguments to the command until the argument
                ';' is encountered.
                Each occurrence of the following placeholders is substituted by a path derived from the
                current search result before the command is executed:
                  '{}':   path
                  '{/}':  basename
                  '{//}': parent directory
                  '{.}':  path without file extension
                  '{/.}': basename without file extension
            exec_batch <cmd>
                Execute a command with all search results at once.
                All arguments following exec_batch are taken to be arguments to the command until the
                argument ';' is encountered.
                A single occurrence of the following placeholders is authorized and substituted by the
                paths derived from the search results before the command is executed:
                  '{}':   path
                  '{/}':  basename
                  '{//}': parent directory
                  '{.}':  path without file extension
                  '{/.}': basename without file extension
            exclude <pattern>...
                Exclude files/directories that match the given glob pattern. This overrides any other
                ignore logic. Multiple exclude patterns can be specified.

                Examples:
                  exclude '*.pyc'
                  exclude node-modules
            ignore_file <path>...
                Add a custom ignore_file in '.gitignore' format. These files have a low precedence.

            threads <num>
                Set number of threads to use for searching & executing (default: number of available CPU
                cores)
            size <size>...
                Limit results based on the size of files using the format <+-><NUM><UNIT>.
                   '+': file size must be greater than or equal to this
                   '-': file size must be less than or equal to this
                If neither '+' nor '-' is specified, file size must be exactly equal to this.
                   'NUM':  The numeric size (e.g. 500)
                   'UNIT': The units for NUM. They are not case_sensitive.
                Allowed unit values:
                    'b':  bytes
                    'k':  kilobytes (base ten, 10^3 = 1000 bytes)
                    'm':  megabytes
                    'g':  gigabytes
                    't':  terabytes
                    'ki': kibibytes (base two, 2^10 = 1024 bytes)
                    'mi': mebibytes
                    'gi': gibibytes
                    'ti': tebibytes
            changed_within <date|dur>
                Filter results based on the file modification time. The argument can be provided as a
                specific point in time (YYYY-MM-DD HH:MM:SS) or as a duration (10h, 1d, 35min). 'change_
                newer_than' can be used as an alias.
                Examples:
                    changed_within 2weeks
                    change_newer_than '2018-10-27 10:00:00'
            changed_before <date|dur>
                Filter results based on the file modification time. The argument can be provided as a
                specific point in time (YYYY-MM-DD HH:MM:SS) or as a duration (10h, 1d, 35min). 'change_
                older_than' can be used as an alias.
                Examples:
                    changed_before '2018-10-27 10:00:00'
                    change_older_than 2weeks
            max_results <count>
                Limit the number of search results to 'count' and quit immediately.

            base_directory <path>
                Change the current working directory of fd to the provided path. This means that search
                results will be shown with respect to the given base path. Note that relative paths which
                are passed to fd via the positional <path> argument or the 'search_path' option will
                also be resolved relative to this directory.
            path_separator <separator>
                Set the path separator to use when printing file paths. The default is the OS_specific
                separator ('/' on Unix, '\' on Windows).
            search_path <search_path>...
                Provide paths to search as an alternative to the positional <path> argument. Changes the
                usage to `fd [FLAGS/OPTIONS] search_path <path> search_path <path2> [<pattern>]`
            owner <user:group>
                Filter files by their user and/or group. Format: [(user|uid)][:(group|gid)]. Either side
                is optional. Precede either side with a '!' to exclude files instead.
                Examples:
                    owner john
                    owner :students
                    owner '!john:students'

    Note: `fd.h()` prints a short and concise overview while `fd.help()` gives all details.
    """


class ShortHelp:
    """
    ARGS:
        pattern           the search pattern (a regular expression, unless 'glob=True' is used)
        path (optional)   the root directory for the filesystem search

    KWARGS:
        hidden            Search hidden files and directories
        no_ignore         Do not respect .(git|fd)ignore files
        case_sensitive    Case_sensitive search (default: smart case)
        ignore_case       Case_insensitive search (default: smart case)
        glob              Glob_based search (default: regular expression)
        absolute_path     Show absolute instead of relative paths
        list_details      Use a long listing format with file metadata
        follow            Follow symbolic links
        full_path         Search full path (default: file_/dirname only)
        print0            Separate results by the null character

    OPTIONS:
        max_depth <depth>            Set maximum search depth (default: none)
        type <filetype>...
                Filter by type: file (f), directory (d), symlink (l),
                executable (x), empty (e), socket (s), pipe (p)
        extension <ext>...           Filter by file extension
        exec <cmd>                   Execute a command for each search result
        exec_batch <cmd>
                Execute a command with all search results at once

        exclude <pattern>...
                Exclude entries that match the given glob pattern

        size <size>...               Limit results based on the size of files.
            changed_within <date|dur>
                Filter by file modification time (newer than)

            changed_before <date|dur>
                Filter by file modification time (older than)

        owner <user:group>           Filter by owning user and/or group

    Note: `fd.h()` prints a short and concise overview while `fd.help()` gives all details.
    """
