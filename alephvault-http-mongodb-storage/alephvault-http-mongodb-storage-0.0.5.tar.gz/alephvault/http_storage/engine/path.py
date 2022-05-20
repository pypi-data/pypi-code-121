from typing import Optional, List


def parse_path(paths_dsn: Optional[dict] = None, extra_path: Optional[List[str]] = None):
    """
    Parses a path, which can be understood as an URL chunk. The extra_path
    is a path obtained by something like this:

    @app.route('/', defaults={'extra_path': ''})
    @app.route("/<path:extra_path>", methods=[...])
    def some_handler(extra_path: str):
        ...

    :param extra_path: The path to parse. By this point, the path comes
      as a flak arbitrary path (a string, already url-decoded).
    :param paths_dsn: The paths DSN being used. By this point, the dsn
      format is completely valid.
    :return: If the parse was appropriate (in format and in contrast
      to the DSN in use), returns the path and a flag telling whether
      the parse was successful. Otherwise, returns (None, False).
    """

    # Converting the path to a list, by splitting by /, and removing
    # all the empty elements.
    extra_path = [part for part in (extra_path or '').split('/') if part]
    # Then, starting the logic (one out of two logics will be used,
    # depending on when the DSN is available or not).
    if paths_dsn:
        # A path should be present.
        if not extra_path:
            return None, False

        result = []
        expecting_dict_key = False
        expecting_optional_list_index = False
        try:
            it = iter(extra_path)
            while True:
                # First, a prior check: if it was expecting an index,
                # which is only optional of the last element was a list,
                # then resolve the index now.
                if expecting_optional_list_index:
                    # Add the next chunk as an integer index.
                    result.append(int(next(it)))
                    # Clear the flag to not expect a subscript anymore.
                    expecting_optional_list_index = False

                # Then, if the current resource cannot be found among
                # the list of the (current level's) paths_dsn, fail.
                # This covers even when such list/set/mapping is empty.
                chunk = next(it)
                path_dsn = paths_dsn.get(chunk, {})
                if not path_dsn:
                    return None, False
                # Extract the field to use from database, and also the
                # expected type of the field.
                field_name = path_dsn['field_name']
                field_type = path_dsn['field_type']
                result.append(field_name)
                if field_type == 'scalar':
                    # The field will be treated as scalar (despite its
                    # true type). Nothing else to do here.
                    pass
                elif field_type == 'list':
                    # The field will be treated as list (and it will be
                    # expected to be a list in the document, and expect
                    # an integer index as the next chunk). Mark the flag
                    # to expect a subscript.
                    expecting_optional_list_index = True
                elif field_type == 'dict':
                    # The field will be treated as dict (and it will be
                    # expected to be a dict in the document, and expect
                    # a string index as the next chunk). Mark the flag
                    # to expect a subscript.
                    expecting_dict_key = True
                    # Add the next chunk as an integer index.
                    result.append(next(it))
                    # Clear the flag to not expect a subscript anymore.
                    expecting_dict_key = False
                else:
                    # This is just a marker - it will NEVER be reached.
                    return None, False
                # Finally, take the child DSN, if any.
                paths_dsn = path_dsn.get("children", {})
        except StopIteration:
            # The process stopped appropriately, unless it expected
            # a key or index. In that case, then fail.
            if expecting_dict_key:
                return None, False
            # Return appropriately, otherwise.
            return result, True
        except Exception:
            # No exception should be tolerated.
            return None, False
    else:
        # No path should be present.
        if extra_path:
            return None, False
        return None, True
